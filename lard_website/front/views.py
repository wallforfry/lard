from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse

from front import utils
from front.backend import EmailOrUsernameModelBackend
from django.shortcuts import render, redirect


# Create your views here.
from lard_website import settings


def index(request):
    return render(request, "index.html")

@login_required
def protected(request):
    return render(request, "dashboard.html", context={"page": "Dashboard"})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("email", "")
        password = request.POST.get("password", "")
        next = request.GET.get("next")

        if utils.check_recaptcha(request):
            user = EmailOrUsernameModelBackend.authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                if not request.POST.get('remember_me'):
                    request.session.set_expiry(0)
                if next:
                    return redirect(next)
                else:
                    return redirect(reverse(index))
        else:
            messages.error(request, "Vous êtes un robot..")
    return render(request, "login.html", context={"page": "Login", "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY})

def register_view(request):
    if not settings.ENABLE_REGISTRATION:
        return redirect(reverse(index))

    if request.method == "POST":
        username = request.POST.get("username", "")
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm", "")
        agree = request.POST.get("agree", False)
        next = request.GET.get("next")

        if utils.check_recaptcha(request):
            if agree:
                if password == confirm:
                    try:
                        try:
                            User.objects.get(email=email)
                            messages.error(request, "Cette adresse email est déjà prise")
                        except:
                            user = User.objects.create_user(email=email, username=username, password=password)
                            user.save()
                            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                            return redirect(reverse(index))
                    except IntegrityError:
                        messages.error(request, "Ce nom d'utilisateur est déjà utilisé")
                else:
                    messages.error(request, "Les mot de passes ne correspondent pas")
            else:
                messages.error(request, "Vous devez accepter les termes et conditions d'utilisation")

    return render(request, "register.html", context={"page": "Register", "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY})

def logout_view(request):
    logout(request)
    return redirect(reverse(index))