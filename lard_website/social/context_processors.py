"""
Project : lard
File : context_processors
Author : DELEVACQ Wallerand
Date : 21/05/2019
"""
from social.models import UserProfile


def social_processor(request):
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
    else:
        user_profile = []

    return {"user_profile": user_profile, "scopes": UserProfile.SCOPE_CHOICES}