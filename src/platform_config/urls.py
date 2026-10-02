from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from content.views import lesson_content
from core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("explorar/", views.explore, name="explore"),
    path("para-creadores/", views.creators, name="creators"),
    path("mi-espacio/", views.workspace, name="workspace"),
    path("cuenta/entrar/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("cuenta/salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("health/", views.health, name="health"),
    path("lecciones/<int:pk>/contenido/", lesson_content, name="lesson-content"),
    path("admin/", admin.site.urls),
]
admin.site.site_header = "Administración de BTC.EDU"
admin.site.site_title = "BTC.EDU"
