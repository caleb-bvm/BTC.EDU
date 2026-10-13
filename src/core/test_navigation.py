from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase
from django.urls import resolve, reverse

from .navigation import contextual_navigation


class ContextNavigationTests(SimpleTestCase):
    def navigation(self, name, args=None, role=None, approved=True):
        request = RequestFactory().get(reverse(name, args=args))
        request.resolver_match = resolve(request.path)
        request.user = AnonymousUser() if role is None else SimpleNamespace(
            is_authenticated=True, account_type=role,
            creator_profile=SimpleNamespace(status='approved' if approved else 'pending'))
        return contextual_navigation(request)

    def test_public_catalog_does_not_offer_private_student_pages(self):
        data = self.navigation('tutorials')
        self.assertEqual(data['sidebar_context'], 'catalog')
        self.assertEqual([x['label'] for x in data['sidebar_links']], ['Cursos', 'Tutoriales', 'Recursos'])
        self.assertEqual([x['label'] for x in data['sidebar_switches']], ['Entrar'])
        self.assertTrue(data['sidebar_links'][1]['current'])

    def test_sections_and_detail_active_links(self):
        cases = [('workspace', None, 'learning', 'Mi aprendizaje'),
                 ('certificate-detail', ['00000000-0000-0000-0000-000000000001'], 'learning', 'Certificados'),
                 ('invoice-detail', ['00000000-0000-0000-0000-000000000001'], 'payments', 'Compras y facturas'),
                 ('community-thread', [1], 'community', 'Conversaciones'),
                 ('member-profile', [1], 'community', 'Personas'),
                 ('student-profile', None, 'account', 'Perfil de estudiante')]
        for name, args, section, label in cases:
            with self.subTest(name=name):
                data = self.navigation(name, args, 'student')
                self.assertEqual(data['sidebar_context'], section)
                self.assertEqual([x['label'] for x in data['sidebar_links'] if x['current']], [label])

    def test_creator_shared_community_returns_to_studio(self):
        data = self.navigation('members', role='creator')
        self.assertIn('Mi estudio', [x['label'] for x in data['sidebar_switches']])
        self.assertNotIn('Mi aprendizaje', [x['label'] for x in data['sidebar_switches']])

    def test_creator_sections_and_pending_application(self):
        data = self.navigation('creator-course', [1], 'creator')
        self.assertEqual(data['sidebar_context'], 'studio')
        self.assertTrue(data['sidebar_links'][0]['current'])
        data = self.navigation('creator-analytics', role='creator')
        self.assertEqual(data['sidebar_context'], 'teaching')
        self.assertTrue(data['sidebar_links'][1]['current'])
        data = self.navigation('creator-application', role='creator', approved=False)
        self.assertEqual([x['label'] for x in data['sidebar_links']], ['Resumen', 'Perfil de creador', 'Acceso'])

    def test_course_sidebar_uses_exact_version_and_lesson_outline(self):
        data = self.navigation('version-lesson', [1, 3, 7], 'student')
        self.assertEqual(data['sidebar_context'], 'course')
        html = render_to_string('_context_navigation.html', {**data,
            'course': SimpleNamespace(title='Bitcoin', detail_url='/cursos/1/versiones/3/'),
            'lesson': SimpleNamespace(pk=7), 'return_to': '/mi-espacio/'})
        self.assertIn('/cursos/1/versiones/3/?volver=', html)
        self.assertIn('#lesson-syllabus', html)
        self.assertNotIn('Compras y facturas', html)

    def test_recovery_highlights_access_recovery(self):
        data = self.navigation('student-password-reset-done')
        self.assertEqual(data['sidebar_context'], 'auth')
        self.assertTrue(data['sidebar_links'][2]['current'])

    def test_access_links_preserve_purchase_destination(self):
        from urllib.parse import parse_qs, urlsplit
        request = RequestFactory().get(reverse('login'), {'next': '/ofertas/23/?volver=/tutoriales/'})
        request.resolver_match = resolve(request.path)
        request.user = AnonymousUser()
        data = contextual_navigation(request)
        for link in data['sidebar_links'][:2]:
            self.assertEqual(parse_qs(urlsplit(link['url']).query)['next'], ['/ofertas/23/?volver=/tutoriales/'])
