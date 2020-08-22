from django.urls import path
from . import views

urlpatterns = [
    path("start/", views.start, name="start"),
    path("logout/", views.logout, name="logout"),
    path("add/", views.add, name="add"),
    path("view/", views.view, name="view"),
    path("graphs/", views.graphs, name="graphs")
]