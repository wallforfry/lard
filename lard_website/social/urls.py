"""
Project : lard
File : urls
Author : DELEVACQ Wallerand
Date : 21/05/2019
"""
from django.urls import path

from social import views

urlpatterns = [
    path('profile', views.profile, name="profile"),
    path('profile/update', views.profile_update, name="profile_update"),
]