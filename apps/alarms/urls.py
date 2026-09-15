from django.urls import path

from . import views

urlpatterns = [
    path("", views.overview, name="alarm-overview"),
    path("overview/", views.overview, name="alarm-overview-alias"),
]
