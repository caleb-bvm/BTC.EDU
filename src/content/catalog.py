from django.core.paginator import Paginator
from django.db.models import Case, Count, F, Prefetch, Q, When
from django.db.models.functions import Coalesce
from django.urls import reverse

from .models import (
    AccessType,
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
    return Course.objects.filter(status=PublicationStatus.PUBLISHED).select_related('creator', 'topic', 'current_version__topic').defer('objective', 'requirements', 'current_version__objective', 'current_version__requirements').annotate(
        public_title=Coalesce('current_version__title', 'title'), public_description=Coalesce('current_version__description', 'description'),
        public_kind=Coalesce('current_version__kind', 'kind'), public_level=Coalesce('current_version__level', 'level'),
        public_topic_id=Case(When(current_version__isnull=False, then=F('current_version__topic_id')), default=F('topic_id')),
        free_count=Case(When(current_version__isnull=False, then=Count('current_version__chapters__lessons', filter=Q(current_version__chapters__lessons__content__access_type=AccessType.FREE), distinct=True)), default=Count('chapters__lessons', filter=visible & Q(chapters__lessons__access_type=AccessType.FREE), distinct=True)),
        paid_count=Case(When(current_version__isnull=False, then=Count('current_version__chapters__lessons', filter=Q(current_version__chapters__lessons__content__access_type=AccessType.PAID), distinct=True)), default=Count('chapters__lessons', filter=visible & Q(chapters__lessons__access_type=AccessType.PAID), distinct=True)),
    )


def catalog_context(params, section=None):
    categories = {'todos': 'Todo', 'cursos': 'Cursos', 'tutoriales': 'Tutoriales', 'videos': 'Videos', 'materiales': 'Materiales', 'referencias': 'Enlaces externos'}
    allowed = {'cursos': ('cursos',), 'tutoriales': ('tutoriales',), 'recursos': ('videos', 'materiales', 'referencias')}.get(section, tuple(categories)[1:])
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
    query = params.get('q', '').strip()[:200]
    catalog_items = []
    topic_ids = set()
    for kind, model, label in (
        ('cursos', Course, 'Curso'), ('tutoriales', Course, 'Tutorial'),
        ('videos', Video, 'Video'), ('materiales', Material, 'Material'),
        ('referencias', ExternalReference, 'Enlace externo'),
    ):
        if kind not in allowed:
            continue
        items = published_courses() if model == Course else model.objects.filter(status=PublicationStatus.PUBLISHED).select_related('topic')
        if model == Course:
            items = items.filter(public_kind=CourseKind.TUTORIAL if kind == 'tutoriales' else CourseKind.COURSE)
        elif model != ExternalReference:
            items = items.select_related('creator', 'revision').defer('revision__body').annotate(public_title=Coalesce('revision__title', 'title'), public_description=Coalesce('revision__description', 'description'), public_access=Coalesce('revision__access_type', 'access_type'))
        topic_field = 'public_topic_id' if model == Course else 'topic_id'
        topic_ids.update(items.exclude(**{topic_field: None}).values_list(topic_field, flat=True))
        if category != 'todos' and category != kind:
            continue
        if query:
            items = items.filter(Q(title__icontains=query) | Q(description__icontains=query)) if model == ExternalReference else items.filter(Q(public_title__icontains=query) | Q(public_description__icontains=query))
        if topic_slug:
            items = items.filter(**{topic_field + '__in': Topic.objects.filter(slug=topic_slug).values('pk')})
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
    topics = list(Topic.objects.filter(pk__in=topic_ids))
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
                url = reverse('resource-detail', args=[kind, item.pk])
            creator = item.source_name if model == ExternalReference else item.creator.get_full_name().strip() or 'Creador de BTC.EDU'
            cards.append({'item': item, 'category': kind, 'kind': label, 'creator': creator, 'url': url, 'summary': summary, 'access_label': summary['access_label'] if summary else 'Fuente externa' if model == ExternalReference else item.get_access_type_display()})
    cards.sort(key=lambda card: (card['item'].title.casefold(), card['category'], card['item'].pk))
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
        'levels': CourseLevel.choices, 'level_filter': level, 'cards': page.object_list,
        'all_cards': cards, 'groups': list(groups.items()), 'page_obj': page, 'result_count': len(cards),
        'filter_query': link_params.urlencode() if hasattr(link_params, 'urlencode') else '',
        'filtered': bool(query or access != 'todos' or topic_slug or level or category != 'todos'),
        'has_search_filters': bool(query or access != 'todos' or topic_slug or level),
        'type_links': type_links,
        'topic_missing': bool(topic_slug and all(topic.slug != topic_slug for topic in topics)),
        'show_level': section in (None, 'cursos', 'tutoriales'),
    }
