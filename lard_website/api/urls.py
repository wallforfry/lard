"""
Project : lard
File : urls
Author : DELEVACQ Wallerand
Date : 17/02/19
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('blocks/list', views.list_blocks),
    path('piplines/update', views.update_pipeline),
    path('result/<str:worker_id>/update', views.update_result)
]