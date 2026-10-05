from django.urls import path

from . import views

urlpatterns = [
    path("inscripciones/<int:pk>/avance/", views.progress_update, name="progress-update"),
    path("inscribir/<int:version_pk>/", views.enrollment_create, name="enrollment-create"),
    path("recursos/<int:pk>/", views.purchased_resource, name="purchased-resource"),
    path("recursos/<int:pk>/<str:part>/", views.purchased_resource_file, name="purchased-resource-file"),
]
