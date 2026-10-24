from collections import Counter

from django.core.paginator import Paginator
from django.db.models import Case, Count, F, Prefetch, Q, When
from django.db.models.functions import Coalesce
from django.urls import reverse

from .catalog_filters import build_catalog_filters
from .identity import public_creator_name
from .models import (
    AccessType,
    Category,
    Chapter,
    Course,
    CourseKind,
    CourseLevel,
    ExternalReference,
    Lesson,
    Material,
    PublicationStatus,
    Topic,
    Video,
)


def course_tree(preview=False):
    chapters = Chapter.objects.order_by('position', 'pk')
    lessons = Lesson.objects.defer('body').order_by('position', 'pk')
    if not preview:
        chapters = chapters.filter(status=PublicationStatus.PUBLISHED)
        lessons = lessons.filter(status=PublicationStatus.PUBLISHED)
    return chapters.prefetch_related(Prefetch('lessons', queryset=lessons, to_attr='visible_lessons'))


def access_label(free, paid):
    if free and paid:
        return 'Gratis + lecciones de pago'
    if paid:
        return 'Lecciones de pago'
    return 'Gratis' if free else 'Temario en preparación'


def course_summary(course):
    lessons = [lesson for chapter in course.visible_chapters for lesson in chapter.visible_lessons]
    free = sum(lesson.access_type == AccessType.FREE for lesson in lessons)
    paid = len(lessons) - free
    return {'lessons': lessons, 'free_count': free, 'paid_count': paid, 'access_label': access_label(free, paid)}


def published_courses():
    visible = Q(chapters__status=PublicationStatus.PUBLISHED, chapters__lessons__status=PublicationStatus.PUBLISHED)
    return Course.objects.filter(status=PublicationStatus.PUBLISHED).select_related('creator__creator_profile', 'topic', 'current_version__topic').defer('objective', 'requirements', 'current_version__objective', 'current_version__requirements').annotate(
        public_title=Coalesce('current_version__title', 'title'), public_description=Coalesce('current_version__description', 'description'),
        public_kind=Coalesce('current_version__kind', 'kind'), public_level=Coalesce('current_version__level', 'level'),
        public_topic_id=Case(When(current_version__isnull=False, then=F('current_version__topic_id')), default=F('topic_id')),
        free_count=Case(When(current_version__isnull=False, then=Count('current_version__chapters__lessons', filter=Q(current_version__chapters__lessons__content__access_type=AccessType.FREE), distinct=True)), default=Count('chapters__lessons', filter=visible & Q(chapters__lessons__access_type=AccessType.FREE), distinct=True)),
        paid_count=Case(When(current_version__isnull=False, then=Count('current_version__chapters__lessons', filter=Q(current_version__chapters__lessons__content__access_type=AccessType.PAID), distinct=True)), default=Count('chapters__lessons', filter=visible & Q(chapters__lessons__access_type=AccessType.PAID), distinct=True)),
    )


UNCATEGORIZED_TOPIC = "~sin-categoria"


def catalog_context(params, section=None, creator=None, browse_categories=False):
    categories = {'todos': 'Todo', 'cursos': 'Cursos', 'tutoriales': 'Tutoriales', 'videos': 'Videos', 'materiales': 'Materiales', 'referencias': 'Enlaces externos'}
    allowed = {'cursos': ('cursos',), 'tutoriales': ('tutoriales',), 'recursos': ('videos', 'materiales', 'referencias')}.get(section, tuple(categories)[1:])
    if creator is not None:
        allowed = tuple(kind for kind in allowed if kind != 'referencias')
    category = params.get('tipo', 'todos')
    if category not in ('todos', *allowed):
        category = 'todos'
    access = params.get('acceso', 'todos')
    if access not in ('todos', 'gratis', 'pago'):
        access = 'todos'
    level = params.get('nivel', '')
    if level not in CourseLevel.values:
        level = ''
    topic_slug = params.get('tema', '')[:100]
    category_slug = params.get('categoria', '')[:100]
    parent_categories = list(Category.objects.all())
    all_topics = list(Topic.objects.select_related('category'))
    topic_by_slug = {topic.slug: topic for topic in all_topics}
    selected_topic = topic_by_slug.get(topic_slug)
    # Los enlaces anteriores con solo «tema» conservan su destino.
    if not category_slug and selected_topic:
        category_slug = selected_topic.category.slug if selected_topic.category_id else UNCATEGORIZED_TOPIC
    if topic_slug == UNCATEGORIZED_TOPIC and not category_slug:
        category_slug = UNCATEGORIZED_TOPIC
    parent = next((item for item in parent_categories if item.slug == category_slug), None)
    category_missing = bool(category_slug and not parent and category_slug != UNCATEGORIZED_TOPIC)
    if topic_slug == UNCATEGORIZED_TOPIC and category_slug != UNCATEGORIZED_TOPIC:
        category_missing = True
    if selected_topic and category_slug:
        expected_parent = selected_topic.category.slug if selected_topic.category_id else UNCATEGORIZED_TOPIC
        category_missing = category_missing or expected_parent != category_slug
    parent_topic_ids = [topic.pk for topic in all_topics if
                        (topic.category_id == parent.pk if parent else topic.category_id is None)]
    query = params.get('q', '').strip()[:200]
    filtered = bool(query or access != 'todos' or topic_slug or category_slug or level or category != 'todos')
    show_categories = browse_categories and not (filtered or params.get('vista') == 'todos' or params.get('pagina'))
    catalog_items = []
    topic_counts = Counter()
    facets = {'topics': set(), 'levels': set(), 'access': set(), 'formats': set(), 'scope_count': 0}
    for kind, model, label in (
        ('cursos', Course, 'Curso'), ('tutoriales', Course, 'Tutorial'),
        ('videos', Video, 'Video'), ('materiales', Material, 'Material'),
        ('referencias', ExternalReference, 'Enlace externo'),
    ):
        if kind not in allowed:
            continue
        items = published_courses() if model == Course else model.objects.filter(status=PublicationStatus.PUBLISHED).select_related('topic')
        if creator is not None:
            items = items.filter(creator=creator)
        if model == Course:
            items = items.filter(public_kind=CourseKind.TUTORIAL if kind == 'tutoriales' else CourseKind.COURSE)
        elif model != ExternalReference:
            items = items.select_related('creator__creator_profile', 'revision__topic').defer('revision__body').annotate(public_title=Coalesce('revision__title', 'title'), public_description=Coalesce('revision__description', 'description'), public_access=Coalesce('revision__access_type', 'access_type'), public_topic_id=Case(When(revision__isnull=False, then=F('revision__topic_id')), default=F('topic_id')))
        topic_field = 'topic_id' if model == ExternalReference else 'public_topic_id'
        counts = items.order_by().values(topic_field).annotate(topic_count=Count('pk', distinct=True))
        for row in counts:
            topic_counts[row[topic_field]] += row['topic_count']
        if show_categories:
            continue
        if query:
            items = items.filter(Q(title__icontains=query) | Q(description__icontains=query)) if model == ExternalReference else items.filter(Q(public_title__icontains=query) | Q(public_description__icontains=query))
        if category_missing:
            items = items.none()
        elif category_slug == UNCATEGORIZED_TOPIC:
            items = items.filter(Q(**{topic_field + '__in': parent_topic_ids}) | Q(**{topic_field + '__isnull': True}))
        elif parent:
            items = items.filter(**{topic_field + '__in': parent_topic_ids})
        if topic_slug == UNCATEGORIZED_TOPIC:
            items = items.filter(**{topic_field + '__isnull': True})
        elif topic_slug:
            items = items.filter(**{topic_field: selected_topic.pk}) if selected_topic else items.none()
        # Las opciones siguen disponibles al aplicar nivel, acceso o formato.
        # Solo se leen metadatos públicos; los cuerpos de las revisiones quedan fuera.
        facet_fields = (topic_field, 'public_level', 'free_count', 'paid_count') if model == Course else (
            (topic_field,) if model == ExternalReference else (topic_field, 'public_access'))
        for row in items.values(*facet_fields):
            facets['scope_count'] += 1
            facets['topics'].add(row[topic_field])
            facets['formats'].add(kind)
            if model == Course:
                if row['public_level']:
                    facets['levels'].add(row['public_level'])
                if row['free_count']:
                    facets['access'].add('gratis')
                if row['paid_count']:
                    facets['access'].add('pago')
            elif model != ExternalReference:
                facets['access'].add('gratis' if row['public_access'] == AccessType.FREE else 'pago')
        if category != 'todos' and category != kind:
            continue
        if level:
            if model != Course:
                continue
            items = items.filter(public_level=level)
        if model == Course:
            if access == 'gratis':
                items = items.filter(free_count__gt=0)
            elif access == 'pago':
                items = items.filter(paid_count__gt=0)
        elif model == ExternalReference:
            if access != 'todos':
                continue
        elif access != 'todos':
            items = items.filter(public_access=AccessType.FREE if access == 'gratis' else AccessType.PAID)
        catalog_items.append((kind, model, label, items))
    topics = [topic for topic in all_topics if topic.category_id or topic_counts[topic.pk]]
    topic_missing = bool(topic_slug and topic_slug != UNCATEGORIZED_TOPIC and all(topic.slug != topic_slug for topic in topics))
    category_counts = Counter()
    for topic in all_topics:
        category_counts[topic.category_id] += topic_counts[topic.pk]
    uncategorized_count = category_counts[None] + topic_counts[None]
    category_cards = [{'name': item.name, 'slug': item.slug, 'description': item.description,
                       'image': item.category_image, 'count': category_counts[item.pk],
                       'topics': [topic for topic in topics if topic.category_id == item.pk]}
                      for item in parent_categories]
    if uncategorized_count:
        category_cards.append({'name': 'Por descubrir', 'slug': UNCATEGORIZED_TOPIC,
                               'description': 'Contenido que todavía no tiene una categoría asignada.',
                               'image': 'images/categories/general.svg', 'count': uncategorized_count,
                               'topics': [topic for topic in topics if topic.category_id is None]})
    selected_category = next((card for card in category_cards if card['slug'] == category_slug), None)
    topic_groups = [{'name': card['name'], 'topics': card['topics']} for card in category_cards if card['topics']]
    subcategory_cards = [{'name': topic.name, 'slug': topic.slug, 'count': topic_counts[topic.pk]}
                         for topic in selected_category['topics']] if selected_category and not category_missing else []
    catalog_filters = build_catalog_filters(
        facets, category_cards=category_cards, all_topics=all_topics,
        category_slug=category_slug, topic_slug=topic_slug, selected_category=selected_category,
        selected_topic=selected_topic, category_missing=category_missing,
        section=section, browse_categories=browse_categories, query=query,
        level=level, access=access, kind=category, format_labels=categories,
        uncategorized=UNCATEGORIZED_TOPIC,
    )
    cards = []
    for kind, model, label, items in catalog_items:
        for item in items:
            summary = None
            if model == Course:
                if item.current_version_id:
                    for field in ('title', 'description', 'kind', 'level', 'topic', 'estimated_minutes'):
                        setattr(item, field, getattr(item.current_version, field))
                summary = {'free_count': item.free_count, 'paid_count': item.paid_count, 'lesson_count': item.free_count + item.paid_count, 'access_label': access_label(item.free_count, item.paid_count)}
                url = reverse('course-detail', args=[item.pk])
            elif model == ExternalReference:
                url = reverse('reference-detail', args=[item.pk])
            else:
                if item.revision_id:
                    item.title, item.description, item.access_type = item.revision.title, item.revision.description, item.revision.access_type
                    item.topic = item.revision.topic
                url = reverse('resource-detail', args=[kind, item.pk])
            creator = item.source_name if model == ExternalReference else public_creator_name(item.creator)
            cards.append({'item': item, 'category': kind, 'kind': label, 'creator': creator, 'url': url, 'summary': summary, 'access_label': summary['access_label'] if summary else 'Fuente externa' if model == ExternalReference else item.get_access_type_display()})
    cards.sort(key=lambda card: (card['item'].title.casefold(), card['category'], card['item'].pk))
    from commerce.models import Offer
    course_ids = [card['item'].current_version_id for card in cards if card['summary'] and card['item'].current_version_id]
    resource_ids = [card['item'].revision_id for card in cards if card['category'] in ('videos', 'materiales') and card['item'].revision_id]
    prices = {}
    price_kinds = {}
    ranks = {'course': 3, 'chapter': 2, 'lesson': 1, 'resource': 1}
    offers = Offer.objects.filter(status='active', creator__is_active=True, creator__creator_profile__status='approved').filter(Q(course_version_id__in=course_ids) | Q(resource_id__in=resource_ids)).values('amount_sats', 'course_version_id', 'resource_id', 'kind')
    for offer in offers:
        key = ('course', offer['course_version_id']) if offer['course_version_id'] else ('resource', offer['resource_id'])
        rank = ranks.get(offer['kind'], 0)
        previous_rank = ranks.get(price_kinds.get(key), -1)
        if rank > previous_rank or (rank == previous_rank and offer['amount_sats'] < prices[key]):
            prices[key] = offer['amount_sats']
            price_kinds[key] = offer['kind']
    for card in cards:
        key = ('course', card['item'].current_version_id) if card['summary'] else ('resource', getattr(card['item'], 'revision_id', None))
        card['price'] = prices.get(key)
        card['price_label'] = {'course': f"{card['kind']} completo", 'chapter': 'Capítulo', 'lesson': 'Lección individual'}.get(price_kinds.get(key), '')
    link_params = params.copy()
    link_params.pop('pagina', None)
    link_params.pop('curso', None)
    page = Paginator(cards, 12).get_page(params.get('pagina', 1))
    type_links = []
    for value, label in categories.items():
        if value != 'todos' and value not in allowed:
            continue
        type_params = link_params.copy()
        type_params['tipo'] = value
        type_links.append((value, label, type_params.urlencode() if hasattr(type_params, 'urlencode') else ''))
    groups = {}
    for card in page.object_list:
        heading = card['item'].topic.name if card['item'].topic else 'Por descubrir'
        groups.setdefault(heading, []).append(card)
    return {
        'category': category, 'categories': {key: value for key, value in categories.items() if key == 'todos' or key in allowed},
        'access_filter': access, 'query': query, 'topics': topics, 'topic_filter': topic_slug,
        'category_filter': category_slug, 'category_missing': category_missing,
        'catalog_filters': catalog_filters,
        'selected_topic': selected_topic, 'topic_groups': topic_groups, 'subcategory_cards': subcategory_cards,
        'levels': CourseLevel.choices, 'level_filter': level, 'cards': page.object_list,
        'all_cards': cards, 'groups': list(groups.items()), 'page_obj': page, 'result_count': len(cards),
        'filter_query': link_params.urlencode() if hasattr(link_params, 'urlencode') else '',
        'filtered': filtered,
        'show_clear_filters': filtered and (category_missing or topic_missing or not browse_categories or not selected_category or bool(query or access != 'todos' or level or category != 'todos')),
        'has_search_filters': bool(query or access != 'todos' or topic_slug or category_slug or level),
        'type_links': type_links,
        'topic_missing': topic_missing,
        'show_level': section in (None, 'cursos', 'tutoriales'),
        'category_browsing': browse_categories, 'show_categories': show_categories,
        'category_cards': category_cards, 'catalog_total': sum(topic_counts.values()),
        'selected_category': selected_category,
        'uncategorized_topic': UNCATEGORIZED_TOPIC, 'uncategorized_count': uncategorized_count,
        'unassigned_count': topic_counts[None],
    }
