from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


# Create your views here.

def home(request):
    if request.user.is_authenticated:
        return redirect("start")
    else:
        return render(request, "home.html")


def register(request):
    return render(request, "register.html")


def confirm_register(request):
    if request.method == "POST":
        username = request.POST["username"].strip().lower()
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already taken")
                return redirect("register")
            else:
                user = User.objects.create_user(username = username, password = password1)
                user.save()
        else:
            messages.info(request, "Passwords don't match")
            return redirect("register")
        return redirect("/")
    else:
        return render(request, 'register')


def login(request):
    if request.method == "POST":
        username = request.POST["username"].strip().lower()
        password = request.POST["password"]

        user = auth.authenticate(username = username, password = password)

        if user is not None:
            auth.login(request, user)
            return redirect("start")
        else:
            messages.info(request, "User not found or wrong password")
            return redirect("home")
    else:
        return render(request, "home")

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)