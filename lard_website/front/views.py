from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from front.backend import EmailOrUsernameModelBackend
from django.http import HttpResponse
from django.shortcuts import render, redirect


# Create your views here.
def index(request):
    return render(request, "index.html")

@login_required
def protected(request):
    return HttpResponse("Protected")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("email", "")
        password = request.POST.get("password", "")
        next = request.GET.get("next")
        user = EmailOrUsernameModelBackend.authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if next:
                return redirect(next)
            else:
                return redirect(reverse(index))
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect(reverse(index))