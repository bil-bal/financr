from django.urls import path
from . import views

urlpatterns = [
    path("home.html", views.home, name="home"),
    path("", views.home, name="home"),
    path("register", views.register, name="register"),
    path("confirm_register", views.confirm_register, name="confirm_register"),
    path("login", views.login, name="login")
]