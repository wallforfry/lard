"""
Project : lard
File : urls
Author : DELEVACQ Wallerand
Date : 21/05/2019
"""
from django.conf.urls import url
from django.urls import path

from social import views

urlpatterns = [
    path('profile', views.profile, name="profile"),
    path('profile/<str:username>/', views.profile_username, name="profile_username"),
    path('profile/update', views.profile_update, name="profile_update"),
    url(r'^feed/$', views.feed, name="feed"),
    url(r'^feed/json/(?P<page>[0-9]+)/', views.feed_json, name='feed_json'),
    path('feed/element/<str:elt_id>/', views.feed_element, name='feed_element'),
    path('feed/publish', views.feed_publish, name='feed_publish'),
    path('feed/publish/<str:pub_id>/delete', views.feed_publish_delete, name='feed_publish_delete'),
    path('people/', views.people, name='people'),
    path('people/add/', views.people_add, name='people_add'),
    path('people/delete/', views.people_delete, name='people_delete'),
]
