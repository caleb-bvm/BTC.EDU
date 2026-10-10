from django.urls import path

from . import assessment_views, community_views, essential_views, views

urlpatterns = [
    path("comunidad/", community_views.spaces, name="community-spaces"),
    path("comunidad/versiones/<int:version_pk>/", community_views.space, name="community-space"),
    path("comunidad/versiones/<int:version_pk>/moderacion/", community_views.moderation, name="community-moderation"),
    path("comunidad/versiones/<int:version_pk>/decision/", community_views.decision, name="community-decision"),
    path("comunidad/conversaciones/<int:pk>/", community_views.thread, name="community-thread"),
    path("comunidad/mensajes/<int:pk>/reportar/", community_views.report, name="community-report"),
    path("certificados/", essential_views.certificates_list, name="certificates"),
    path("inscripciones/<int:enrollment_pk>/certificado/", essential_views.certificate_request, name="certificate-request"),
    path("certificados/<uuid:pk>/", essential_views.certificate_detail, name="certificate-detail"),
    path("certificados/<uuid:pk>/pdf/", essential_views.certificate_pdf, name="certificate-pdf"),
    path("certificados/<uuid:pk>/datos/", essential_views.certificate_data, name="certificate-data"),
    path("certificados/<uuid:pk>/compartir/", essential_views.certificate_share, name="certificate-share"),
    path("verificar/<uuid:pk>/", essential_views.certificate_verify, name="certificate-verify"),
    path("verificar/<uuid:pk>/datos/", essential_views.certificate_public_data, name="certificate-public-data"),
    path("certificados/<uuid:pk>/revocar/", essential_views.certificate_revoke, name="certificate-revoke"),
    path("preguntas/", essential_views.student_questions, name="student-questions"),
    path("lecciones/<int:lesson_pk>/preguntar/", essential_views.question_create, name="question-create"),
    path("preguntas/<int:pk>/", essential_views.question_detail, name="student-question"),
    path("avisos/", essential_views.notifications, name="notifications"),
    path("avisos/<int:pk>/leer/", essential_views.notification_read, name="notification-read"),
    path("evaluaciones/<int:pk>/", assessment_views.quiz_detail, name="quiz-detail"),
    path("evaluaciones/<int:pk>/empezar/", assessment_views.quiz_start, name="quiz-start"),
    path("intentos/<int:pk>/", assessment_views.attempt_detail, name="quiz-attempt"),
    path("inscripciones/<int:pk>/avance/", views.progress_update, name="progress-update"),
    path("inscribir/<int:version_pk>/", views.enrollment_create, name="enrollment-create"),
    path("recursos/<int:pk>/", views.purchased_resource, name="purchased-resource"),
    path("recursos/<int:pk>/<str:part>/", views.purchased_resource_file, name="purchased-resource-file"),
]
