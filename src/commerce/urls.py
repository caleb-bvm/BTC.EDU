from django.urls import path

from . import views

urlpatterns = [
    path("crear/ofertas/<int:pk>/revision/", views.offer_review, name="offer-review"),
    path("ofertas/<int:pk>/", views.offer_detail, name="offer-detail"),
    path("ofertas/<int:pk>/comprar/", views.checkout, name="checkout"),
    path("facturas/", views.purchases, name="purchases"),
    path("facturas/<uuid:pk>/", views.invoice_detail, name="invoice-detail"),
    path("facturas/<uuid:pk>/comprobar/", views.invoice_action, name="invoice-action"),
]
