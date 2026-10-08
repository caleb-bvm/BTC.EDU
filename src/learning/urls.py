from django.urls import path

from . import assessment_views, views

urlpatterns = [
    path("evaluaciones/<int:pk>/", assessment_views.quiz_detail, name="quiz-detail"),
    path("evaluaciones/<int:pk>/empezar/", assessment_views.quiz_start, name="quiz-start"),
    path("intentos/<int:pk>/", assessment_views.attempt_detail, name="quiz-attempt"),
    path("inscripciones/<int:pk>/avance/", views.progress_update, name="progress-update"),
    path("inscribir/<int:version_pk>/", views.enrollment_create, name="enrollment-create"),
    path("recursos/<int:pk>/", views.purchased_resource, name="purchased-resource"),
    path("recursos/<int:pk>/<str:part>/", views.purchased_resource_file, name="purchased-resource-file"),
]
