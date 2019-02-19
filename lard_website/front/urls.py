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
    path('dashboard/', views.protected, name="dashboard"),
    path('editor/', views.editor, name="editor"),
    path('datasets/<str:name>/', views.datasets, name="datasets"),
    path('administration/users', views.admin_users, name="admin_users"),
    path('pipelines/<str:name>', views.pipeline, name="pipeline"),
    path('pipelines/<str:name>/inputs', views.pipeline_empty_inputs, name="pipeline_empty_inputs"),
    path('pipelines/<str:name>/execute', views.pipeline_execute, name="pipeline_execute"),
    path('pipelines/<str:name>/cytoscape', views.get_cytoscape, name="pipeline_get_cytoscape"),
    path('blocks/', views.list_blocks, name="list_blocks"),
    path('blocks/add', views.add_block, name="add_block"),
    path('blocks/<str:name>/edit', views.edit_block, name="edit_block"),
    path('blocks/<str:name>/save', views.save_block, name="save_block"),
    path('blocks/<str:name>/delete', views.delete_block, name="delete_block")
]