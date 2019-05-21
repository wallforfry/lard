from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from social.models import UserProfile


@login_required
def profile(request):
    context = {
        "profile": UserProfile.objects.get(user=request.user),
        "genders": UserProfile.GENRE_CHOICES,
        "scopes": UserProfile.SCOPE_CHOICES
    }
    return render(request, 'profile.html', context=context)

@login_required
def profile_update(request):
    if request.method == 'POST':
        up = UserProfile.objects.get(user=request.user)

        location = request.POST.get("location", "")
        gender = request.POST.get("gender", "")
        scope = request.POST.get("scope", "")
        print(gender)
        up.locality = location
        up.genre = gender
        up.scope = scope

        up.save()
        return redirect(profile)

    return HttpResponse(status=403)