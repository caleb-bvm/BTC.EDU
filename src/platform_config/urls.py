from django.contrib import admin
from django.urls import include, path

from accounts.views import (
    StudentLoginView,
    StudentLogoutView,
    register,
    student_profile,
)
from content.version_views import (
    attachment_file,
    course_version_detail,
    version_lesson_detail,
)
from content.views import (
    course_detail,
    lesson_content,
    lesson_detail,
    reference_detail,
    resource_detail,
    resource_file,
)
from core import views
from creators.views import public_profile

urlpatterns = [
    path("", views.home, name="home"),
    path("explorar/", views.explore, name="explore"),
    path("cursos/", views.academy_catalog, {"section": "cursos"}, name="courses"),
    path("cursos/selector/", views.course_selector, name="course-selector"),
    path("tutoriales/", views.academy_catalog, {"section": "tutoriales"}, name="tutorials"),
    path("recursos/", views.academy_catalog, {"section": "recursos"}, name="resources"),
    path("referencias/<int:pk>/", reference_detail, name="reference-detail"),
    path("para-creadores/", views.creators, name="creators"),
    path("crear/", include("creators.urls")),
    path("creadores/<int:pk>/", public_profile, name="creator-public-profile"),
    path("mi-espacio/", views.workspace, name="workspace"),
    path("cuenta/entrar/", StudentLoginView.as_view(), name="login"),
    path("cuenta/registro/", register, name="student-signup"),
    path("cuenta/perfil/", student_profile, name="student-profile"),
    path("cuenta/", include("accounts.urls")),
    path("cuenta/salir/", StudentLogoutView.as_view(), name="logout"),
    path("health/", views.health, name="health"),
    path("lecciones/<int:pk>/contenido/", lesson_content, name="lesson-content"),
    path("cursos/<int:pk>/", course_detail, name="course-detail"),
    path("cursos/<int:course_pk>/versiones/<int:number>/", course_version_detail, name="course-version"),
    path("cursos/<int:course_pk>/versiones/<int:number>/lecciones/<int:lesson_pk>/", version_lesson_detail, name="version-lesson"),
    path("adjuntos/<int:pk>/<str:part>/", attachment_file, name="attachment-file"),
    path("recursos/<str:kind>/<int:pk>/revisiones/<int:number>/<str:part>/", resource_file, name="resource-file"),
    path("lecciones/<int:pk>/", lesson_detail, name="lesson-detail"),
    path("recursos/<str:kind>/<int:pk>/", resource_detail, name="resource-detail"),
    path("admin/", admin.site.urls),
]
admin.site.site_header = "Administración de BTC.EDU"
admin.site.site_title = "BTC.EDU"
