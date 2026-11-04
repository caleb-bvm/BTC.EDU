"""Opciones de búsqueda derivadas del contenido público del contexto actual."""

from django.utils.translation import gettext

from core.content_translation import translate_content

from .models import CourseLevel


def build_catalog_filters(facets, *, category_cards, all_topics, category_slug, topic_slug,
                          selected_category, selected_topic, category_missing, section,
                          browse_categories, query, level, access, kind, format_labels,
                          uncategorized):
    topic_by_id = {topic.pk: topic for topic in all_topics}
    available_categories = set()
    for topic_id in facets['topics']:
        topic = topic_by_id.get(topic_id)
        available_categories.add(topic.category.slug if topic and topic.category_id else uncategorized)
    category_options = [
        {'value': card['slug'], 'label': translate_content(card['name'])}
        for card in category_cards if card['slug'] in available_categories or card['slug'] == category_slug
    ]
    if category_slug and not any(option['value'] == category_slug for option in category_options):
        category_options.append({'value': category_slug, 'label': gettext('Categoría no disponible')})

    grouped_topics = {}
    for topic in all_topics:
        if topic.pk not in facets['topics'] and topic.slug != topic_slug:
            continue
        name = translate_content(topic.category.name) if topic.category_id else gettext('Por descubrir')
        grouped_topics.setdefault(name, []).append({
            'value': topic.slug, 'label': translate_content(topic.name),
            'category': topic.category.slug if topic.category_id else uncategorized,
        })
    if None in facets['topics'] or topic_slug == uncategorized:
        grouped_topics.setdefault('Por descubrir', []).append({
            'value': uncategorized, 'label': gettext('Sin subcategoría'), 'category': uncategorized,
        })
    unknown_topic = bool(topic_slug and topic_slug != uncategorized and selected_topic is None)
    if unknown_topic:
        name = translate_content(selected_category['name']) if selected_category else gettext('Otros temas')
        grouped_topics.setdefault(name, []).append({
            'value': topic_slug, 'label': gettext('Subcategoría no disponible'), 'category': category_slug,
        })
    topic_groups = [{'name': name, 'topics': options} for name, options in sorted(grouped_topics.items())]
    level_options = [(value, label) for value, label in CourseLevel.choices if value in facets['levels'] or value == level]
    access_options = [(value, label) for value, label in (('gratis', gettext('Con contenido gratis')), ('pago', gettext('Con contenido de pago')), ('membresia', gettext('Incluido en la membresía')))
                      if value in facets['access'] or value == access]
    format_options = [(value, label) for value, label in format_labels.items()
                      if value != 'todos' and (value in facets['formats'] or value == kind)]

    contextual_parent = bool(browse_categories and selected_category and not category_missing)
    # Tutoriales elige la categoría con accesos directos y Recursos el formato con pestañas.
    controls = {
        'show_category': section != 'tutoriales' and not contextual_parent and bool(len(category_options) > 1 or category_slug),
        'show_topic': (not contextual_parent or unknown_topic) and bool(len(facets['topics']) > 1 or topic_slug),
        'show_level': bool(len(level_options) > 1 or level),
        'show_access': bool(len(access_options) > 1 or access != 'todos'),
        'show_format': section != 'recursos' and bool(len(format_options) > 1 or kind != 'todos'),
    }
    active_count = sum((
        bool(category_slug and controls['show_category']),
        bool(topic_slug and controls['show_topic']),
        bool(level and controls['show_level']),
        access != 'todos' and controls['show_access'],
        kind != 'todos' and controls['show_format'],
    ))
    content_label = {'cursos': gettext('cursos'), 'tutoriales': gettext('tutoriales'), 'recursos': gettext('recursos')}.get(section, gettext('contenido'))
    context_name = translate_content(selected_topic.name) if selected_topic and not category_missing else (
        translate_content(selected_category['name']) if selected_category and not category_missing else '')
    if topic_slug == uncategorized and not category_missing:
        context_name = gettext('Sin subcategoría')
    return {
        'search_label': gettext('Buscar %(content)s') % {'content': content_label},
        'search_placeholder': (gettext('Buscar %(content)s en %(context)s') % {'content': content_label, 'context': context_name}) if context_name else gettext('Buscar %(content)s') % {'content': content_label},
        'categories': category_options, 'topic_groups': topic_groups, 'levels': level_options,
        'access': access_options, 'formats': format_options,
        **controls, 'has_controls': any(controls.values()),
        'active_count': active_count, 'has_refinements': bool(query or active_count),
        'scope_count': facets['scope_count'],
    }
