"""
Project : lard
File : urls
Author : DELEVACQ Wallerand
Date : 17/02/19
"""


from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('register/', views.register_view, name="register"),
    path('dashboard/', views.protected, name="dashboard")
]