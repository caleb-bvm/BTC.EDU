from django.urls import path

from accounts.recovery import recovery_patterns
from accounts.views import CreatorLoginView, CreatorLogoutView, register
from commerce.views import creator_offer, creator_offers
from learning import assessment_views

from . import views

urlpatterns = [
    path("lecciones/<int:lesson_pk>/evaluacion/", assessment_views.quiz_edit, name="creator-quiz"),
    path("cursos/<int:course_pk>/resultados/", assessment_views.quiz_results, name="creator-quiz-results"),
    path("intentos/<int:pk>/autorizar/", assessment_views.quiz_grant, name="creator-quiz-grant"),
    path("ofertas/", creator_offers, name="creator-offers"),
    path("ofertas/<int:pk>/", creator_offer, name="creator-offer"),
    *recovery_patterns(creator=True),
    path("entrar/", CreatorLoginView.as_view(), name="creator-login"),
    path("registro/", register, {"creator": True}, name="creator-signup"),
    path("salir/", CreatorLogoutView.as_view(), name="creator-logout"),
    path("", views.dashboard, name="creator-dashboard"),
    path("solicitud/", views.application, name="creator-application"),
    path("cursos/nuevo/", views.course_edit, name="creator-course-new"),
    path("cursos/<int:pk>/", views.course_edit, name="creator-course"),
    path("cursos/<int:pk>/vista-previa/", views.course_preview, name="creator-course-preview"),
    path("cursos/<int:course_pk>/capitulos/nuevo/", views.chapter_edit, name="creator-chapter-new"),
    path("cursos/<int:course_pk>/capitulos/<int:pk>/", views.chapter_edit, name="creator-chapter"),
    path("capitulos/<int:chapter_pk>/lecciones/nueva/", views.lesson_edit, name="creator-lesson-new"),
    path("capitulos/<int:chapter_pk>/lecciones/<int:pk>/", views.lesson_edit, name="creator-lesson"),
    path("recursos/<str:kind>/nuevo/", views.resource_edit, name="creator-resource-new"),
    path("recursos/<str:kind>/<int:pk>/", views.resource_edit, name="creator-resource"),
    path("recursos/<str:kind>/<int:pk>/vista-previa/", views.resource_preview, name="creator-resource-preview"),
    path("archivos/", views.files, name="creator-files"),
    path("archivos/<int:pk>/", views.own_file, name="creator-file"),
    path("enviar/<str:kind>/<int:pk>/", views.send, name="creator-send"),
    path("revision/<int:pk>/", views.review, name="creator-review"),
    path("revision/<int:pk>/retirar/", views.withdraw, name="creator-withdraw"),
    path("revision/<int:pk>/archivo/<int:asset_pk>/", views.review_file, name="creator-review-file"),
]
