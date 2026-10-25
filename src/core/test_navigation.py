from html.parser import HTMLParser
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth.models import AnonymousUser
from django.template.defaultfilters import urlencode
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase
from django.urls import resolve, reverse

from .navigation import contextual_navigation


class CurrentPageLinks(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.urls = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("aria-current") == "page":
            self.urls.append(attrs.get("href"))


class ContextNavigationTests(SimpleTestCase):
    def navigation(self, name, args=None, role=None, status="approved"):
        request = RequestFactory().get(reverse(name, args=args))
        request.resolver_match = resolve(request.path)
        request.user = AnonymousUser() if role is None else SimpleNamespace(
            is_authenticated=True, account_type=role,
            creator_profile=SimpleNamespace(status=status))
        return contextual_navigation(request)

    def test_public_navigation_never_offers_private_destinations(self):
        data = self.navigation("tutorials")
        self.assertEqual([x["name"] for x in data["sidebar_links"]], ["courses", "tutorials", "resources", "learning-paths", "membership", "creators"])
        self.assertEqual(data["sidebar_local_links"], [])
        self.assertEqual(data["sidebar_secondary_links"], [])
        self.assertEqual(data["section_navigation_links"], [])
        self.assertIn(reverse("login"), data["navigation_signin_url"])

    def test_public_teaching_entry_highlights_its_destination(self):
        data = self.navigation("creators")
        self.assertEqual([x["name"] for x in data["sidebar_links"] if x["current"]], ["creators"])

    def test_student_destinations_stay_stable_across_the_journey(self):
        cases = [("workspace", None), ("invoice-detail", ["00000000-0000-0000-0000-000000000001"]),
                 ("community-thread", [1]), ("member-profile", [1]), ("student-profile", None),
                 ("question-create", [1]), ("notifications", None), ("version-lesson", [1, 3, 7])]
        expected = ["courses", "tutorials", "resources", "learning-paths", "membership", "workspace", "purchases", "community-spaces"]
        for name, args in cases:
            with self.subTest(route=name):
                self.assertEqual([x["name"] for x in self.navigation(name, args, "student")["sidebar_links"]], expected)

    def test_creator_destinations_stay_stable_in_editing_and_accompaniment(self):
        expected = ["creator-dashboard", "creator-content", "creator-questions", "community-spaces", "creator-analytics"]
        cases = [("creator-course", [1]), ("creator-certificate-policy", [1]),
                 ("creator-quiz", [1]), ("creator-questions", None),
                 ("creator-analytics", None), ("members", None)]
        for name, args in cases:
            with self.subTest(route=name):
                data = self.navigation(name, args, "creator")
                self.assertEqual([x["name"] for x in data["sidebar_links"]], expected)
                self.assertEqual([x["name"] for x in data["sidebar_secondary_links"]], ["courses", "tutorials", "resources", "learning-paths"])

    def test_creator_can_explore_without_replacing_studio_destinations(self):
        for name, args, expected in [("explore", None, ["courses"]), ("creator-public-profile", [1], []), ("course-version", [1, 3], ["courses"]), ("tutorials", None, ["tutorials"]), ("resources", None, ["resources"])]:
            with self.subTest(route=name):
                data = self.navigation(name, args, "creator")
                self.assertFalse(any(link["current"] for link in data["sidebar_links"]))
                self.assertEqual([x["name"] for x in data["sidebar_secondary_links"] if x["current"]], expected)

    def test_configuration_stays_in_content_results_in_students_sales_in_sales(self):
        for name, args, active in [
            ("creator-quiz", [1], "creator-content"),
            ("creator-certificate-policy", [1], "creator-content"),
            ("creator-quiz-results", [1], "creator-questions"),
            ("creator-offers", None, "creator-analytics"),
        ]:
            with self.subTest(route=name):
                data = self.navigation(name, args, "creator")
                self.assertEqual([x["name"] for x in data["sidebar_links"] if x["current"]], [active])

    def test_questions_remain_in_learning_including_creation(self):
        data = self.navigation("question-create", [1], "student")
        self.assertEqual(data["sidebar_context"], "learning")
        self.assertEqual([x["name"] for x in data["sidebar_links"] if x["current"]], ["workspace"])
        self.assertEqual([x["name"] for x in data["section_navigation_links"]], ["workspace", "student-questions", "student-practices"])
        self.assertEqual([x["name"] for x in data["section_navigation_links"] if x["current"]], ["student-questions"])

    def test_pending_and_suspended_creator_cannot_see_work_tools(self):
        for status in ("pending", "suspended"):
            data = self.navigation("creator-application", role="creator", status=status)
            self.assertEqual([x["name"] for x in data["sidebar_links"]],
                             ["creator-application"])
            self.assertEqual(data["sidebar_local_links"], [])
            self.assertEqual(data["section_navigation_links"], [])
            self.assertEqual([x["name"] for x in data["sidebar_secondary_links"]], [] if status == "suspended" else ["courses", "tutorials", "resources", "learning-paths"])
            self.assertEqual(data["navigation_home_url"], reverse("creator-application"))

    def test_sidebar_contains_no_course_or_account_utilities(self):
        data = self.navigation("version-lesson", [1, 3, 7], "student")
        html = render_to_string("_context_navigation.html", {**data,
            "course": SimpleNamespace(title="Bitcoin", detail_url="/cursos/1/versiones/3/"),
            "lesson": SimpleNamespace(pk=7), "return_to": "/mi-espacio/"})
        self.assertNotIn("/cursos/1/versiones/3/?volver=", html)
        self.assertNotIn("#lesson-syllabus", html)
        self.assertNotIn("Mi cuenta", html)
        self.assertNotIn("Ayuda", html)
        self.assertIn(reverse("purchases"), html)

    def test_course_highlight_uses_enrollment_instead_of_url_shape(self):
        for name, args in [("course-detail", [1]), ("course-version", [1, 3]), ("version-lesson", [1, 3, 7])]:
            data = self.navigation(name, args, "student")
            for kind, catalog in [("course", "courses"), ("tutorial", "tutorials")]:
                for enrolled, expected in [(False, catalog), (True, "workspace")]:
                    with self.subTest(route=name, enrolled=enrolled, kind=kind):
                        html = render_to_string("_context_navigation.html", {**data, "enrolled": enrolled, "course": SimpleNamespace(kind=kind)})
                        self.assertEqual(CurrentPageLinks(html).urls, [reverse(expected)])

    def test_reader_keeps_exact_version_and_outline_outside_sidebar(self):
        data = self.navigation("version-lesson", [1, 3, 7], "student")
        html = render_to_string("content/lesson.html", {**data,
            "course": SimpleNamespace(title="Bitcoin", detail_url="/cursos/1/versiones/3/", visible_chapters=[]),
            "lesson": SimpleNamespace(pk=7, title="Lección", chapter=SimpleNamespace(title="Capítulo")),
            "return_to": "/mi-espacio/", "enrolled": True})
        self.assertIn("/cursos/1/versiones/3/?volver=/mi-espacio/", html)
        self.assertIn('id="lesson-syllabus"', html)
        self.assertIn('aria-label="Lecciones del curso"', html)

    def test_signin_link_preserves_purchase_destination(self):
        request = RequestFactory().get(reverse("login"), {"next": "/ofertas/23/?leccion=7"})
        request.resolver_match = resolve(request.path)
        request.user = AnonymousUser()
        data = contextual_navigation(request)
        self.assertEqual(parse_qs(urlsplit(data["navigation_signin_url"]).query)["next"], ["/ofertas/23/?leccion=7"])

    def test_catalog_account_and_editors_do_not_duplicate_existing_tabs(self):
        for name, args, role in [
            ("explore", None, None), ("course-selector", None, "student"),
            ("student-account", None, "student"), ("workspace", None, "student"),
            ("creator-course", [1], "creator"), ("creator-quiz", [1], "creator"),
            ("creator-certificate-policy", [1], "creator"), ("creator-account", None, "creator"),
        ]:
            with self.subTest(route=name):
                self.assertEqual(self.navigation(name, args, role)["section_navigation_links"], [])

    def test_section_navigation_uses_clear_labels_and_correct_selection(self):
        for name, args, role, names, active in [
            ("cart", None, "student", ["purchases", "cart", "student-tips"], "cart"),
            ("purchases", None, "student", ["purchases", "cart", "student-tips"], "purchases"),
            ("offer-detail", [1], "student", ["purchases", "cart", "student-tips"], None),
            ("members", None, "student", ["community-spaces", "members"], "members"),
            ("creator-content", None, "creator", ["creator-content", "creator-files"], "creator-content"),
            ("creator-files", None, "creator", ["creator-content", "creator-files"], "creator-files"),
            ("student-practice", [1], "student", ["workspace", "student-questions", "student-practices"], "student-practices"),
            ("creator-practice-delivery", [1], "creator", ["creator-questions", "creator-results", "creator-practices"], "creator-practices"),
            ("creator-results", None, "creator", ["creator-questions", "creator-results", "creator-practices"], "creator-results"),
            ("creator-offer", [1], "creator", ["creator-analytics", "creator-offers", "creator-coupons", "creator-tips"], "creator-offers"),
        ]:
            with self.subTest(route=name):
                data = self.navigation(name, args, role)
                self.assertEqual([x["name"] for x in data["section_navigation_links"]], names)
                html = render_to_string("_section_navigation.html", data)
                self.assertIn(data["section_navigation_label"], html)
                self.assertEqual(CurrentPageLinks(html).urls, [reverse(active)] if active else [])

    def test_workspace_keeps_questions_recoverable_next_to_library_sections(self):
        data = self.navigation("workspace", role="student")
        html = render_to_string("core/workspace.html", {**data, "learning_section": "continuar"})
        self.assertInHTML(f'<a href="{reverse("student-questions")}">Mis preguntas</a>', html)
        self.assertEqual(html.count('aria-label="Secciones de Mi aprendizaje"'), 1)

    def test_catalog_resources_and_purchase_views_highlight_their_area(self):
        for name, args, active in [
            ("resource-detail", ["videos", 1], "resources"), ("reference-detail", [1], "resources"),
            ("purchased-resource", [1], "workspace"), ("offer-detail", [1], "purchases"),
            ("cart", None, "purchases"), ("cart-checkout", None, "purchases"),
            ("invoice-detail", ["00000000-0000-0000-0000-000000000001"], "purchases"),
        ]:
            with self.subTest(route=name):
                data = self.navigation(name, args, "student")
                self.assertEqual([x["name"] for x in data["sidebar_links"] if x["current"]], [active])

    def test_each_catalog_has_its_own_active_destination(self):
        for route in ("courses", "tutorials", "resources"):
            for role in (None, "student", "creator"):
                with self.subTest(route=route, role=role):
                    data = self.navigation(route, role=role)
                    html = render_to_string("_context_navigation.html", data)
                    self.assertEqual(CurrentPageLinks(html).urls, [reverse(route)])

    def test_legacy_explore_urls_select_the_corresponding_catalog(self):
        for query, expected in [({}, "courses"), ({"seccion": "tutoriales"}, "tutorials"),
                                ({"tipo": "materiales"}, "resources"), ({"tipo": "tutoriales"}, "tutorials"),
                                ({"seccion": "recursos", "tipo": "tutoriales"}, "resources"),
                                ({"seccion": "desconocida"}, "courses")]:
            with self.subTest(query=query):
                request = RequestFactory().get(reverse("explore"), query)
                request.resolver_match = resolve(request.path)
                request.user = AnonymousUser()
                data = contextual_navigation(request)
                self.assertEqual([link["name"] for link in data["sidebar_links"] if link["current"]], [expected])

    def test_notifications_do_not_change_primary_navigation(self):
        data = self.navigation("notifications", role="student")
        self.assertEqual(data["sidebar_context"], "notifications")
        self.assertFalse(any(x["current"] for x in data["sidebar_links"]))
        self.assertEqual(data["sidebar_local_links"], [])
        self.assertTrue(data["navigation_notifications_current"])
        self.assertFalse(data["navigation_account_current"])

    def test_account_and_cart_highlight_the_header_control(self):
        for name, role, key in [("student-account-support", "student", "navigation_account_current"),
                                ("creator-account-security", "creator", "navigation_account_current"),
                                ("cart", "student", "navigation_cart_current")]:
            with self.subTest(route=name):
                self.assertTrue(self.navigation(name, role=role)[key])
        self.assertFalse(self.navigation("creator-application", role="creator", status="pending")["navigation_account_current"])

    def test_enrolled_course_keeps_its_community_access_in_the_content(self):
        data = self.navigation("course-version", [1, 3], "student")
        html = render_to_string("content/course.html", {**data, "enrolled": True,
            "course": SimpleNamespace(pk=1, title="Bitcoin", kind="course", detail_url="/cursos/1/versiones/3/", visible_chapters=[]),
            "version": SimpleNamespace(pk=47), "summary": {"lessons": []}})
        self.assertIn(reverse("community-space", args=[47]), html)
        self.assertIn("Comunidad del curso", html)

    def test_public_educator_profile_does_not_expose_internal_navigation(self):
        for role in (None, "student"):
            data = self.navigation("creator-public-profile", [1], role)
            self.assertEqual(data["sidebar_context"], "catalog")
            self.assertFalse(any(link["name"].startswith("creator-") for link in data["sidebar_local_links"]))
            self.assertIn(reverse("login"), data["navigation_signin_url"])
            self.assertNotIn(reverse("creator-login"), data["navigation_signin_url"])


class AuthNavigationLayoutTests(SimpleTestCase):
    def render_auth(self, route, template, args=None, **context):
        request = RequestFactory().get(reverse(route, args=args))
        request.resolver_match = resolve(request.path)
        request.user = AnonymousUser()
        view_context = getattr(request.resolver_match.func, "view_initkwargs", {}).get("extra_context", {})
        return render_to_string(template, {
            **contextual_navigation(request), **view_context,
            "user": request.user, **context,
        })

    def assert_public_auth_frame(self, html):
        self.assertEqual(html.count('class="auth-page"'), 1)
        self.assertNotIn('id="academy-navigation"', html)
        self.assertNotIn('class="academy-layout"', html)
        self.assertNotIn("nav-toggle", html)
        self.assertInHTML(f'<a href="{reverse("explore")}">Explorar</a>', html)

    def test_student_and_creator_login_and_signup_share_public_frame(self):
        for route, template in [
            ("login", "registration/login.html"), ("student-signup", "registration/register.html"),
            ("creator-login", "creators/login.html"), ("creator-signup", "creators/register.html"),
        ]:
            with self.subTest(route=route):
                html = self.render_auth(route, template)
                self.assert_public_auth_frame(html)
                self.assertIn('<form method="post"', html)

    def test_student_access_and_signup_preserve_purchase_return(self):
        destination = "/ofertas/23/?leccion=7"
        for route, template, other, label in [
            ("login", "registration/login.html", "student-signup", "Crear cuenta de estudiante"),
            ("student-signup", "registration/register.html", "login", "Entrar como estudiante"),
        ]:
            with self.subTest(route=route):
                html = self.render_auth(route, template, next=destination)
                self.assertInHTML(f'<input type="hidden" name="next" value="{destination}">', html)
                self.assertInHTML(f'<a href="{reverse(other)}?next={urlencode(destination)}">{label}</a>', html)

    def test_login_recovery_links_and_creator_return_are_preserved(self):
        for route, template, recovery in [
            ("login", "registration/login.html", "student-password-reset"),
            ("creator-login", "creators/login.html", "creator-password-reset"),
        ]:
            with self.subTest(route=route):
                html = self.render_auth(route, template, next="/crear/contenido/")
                self.assertInHTML(f'<a href="{reverse(recovery)}">Recuperar contraseña</a>', html)
                self.assertInHTML('<input type="hidden" name="next" value="/crear/contenido/">', html)

    def test_all_recovery_steps_use_public_frame_and_correct_account_login(self):
        for prefix, login_route in [("student", "login"), ("creator", "creator-login")]:
            for suffix, template, args in [
                ("", "registration/reset_request.html", None),
                ("-done", "registration/reset_done.html", None),
                ("-confirm", "registration/reset_confirm.html", ["MQ", "invalid-token"]),
                ("-complete", "registration/reset_complete.html", None),
            ]:
                route = f"{prefix}-password-reset{suffix}"
                with self.subTest(route=route):
                    html = self.render_auth(route, template, args)
                    self.assert_public_auth_frame(html)
                    self.assertIn(f'href="{reverse(login_route)}"', html)
