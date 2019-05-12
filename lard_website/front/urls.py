"""
Project : lard
File : urls
Author : DELEVACQ Wallerand
Date : 17/02/19
"""
from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('register/', views.register_view, name="register"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('editor/', views.editor, name="editor"),
    path('datasets/<str:name>/', views.datasets, name="datasets"),
    path('administration/users', views.admin_users, name="admin_users"),
    path('pipelines/', views.list_piplines, name="list_pipelines"),
    path('results/', views.pipeline_results_list, name="pipelines_results_list"),
    path('results/<str:id>', views.pipeline_results, name="pipeline_results"),
    path('results/<str:id>/cancel', views.pipeline_cancel, name="pipeline_cancel"),
    url(r'^results/(?P<id>[\w]+)/delete$', views.pipeline_result_delete, name='pipeline_result_delete'),
    path('pipelines/add', views.pipeline_add, name="pipeline_add"),
    path('pipelines/<str:name>', views.pipeline, name="pipeline"),
    path('pipelines/<str:name>/edit/block/<str:block_name>/<str:block_id>', views.pipeline_edit_inputs, name="pipeline_edit_inputs"),
    path('pipelines/<str:name>/edit/edge/<str:edge_source>/<str:edge_target>/<str:edge_id>/<str:old_name>/<str:new_name>', views.pipeline_edit_edge_inputs, name="pipeline_edit_edge_inputs"),
    path('pipelines/<str:name>/info/block/<str:block_name>/<str:block_id>', views.pipeline_info_block, name="pipeline_info_block"),
    path('pipelines/<str:name>/inputs', views.pipeline_empty_inputs, name="pipeline_empty_inputs"),
    path('pipelines/<str:name>/execute', views.pipeline_execute, name="pipeline_execute"),
    path('pipelines/<str:name>/cytoscape', views.get_cytoscape, name="pipeline_get_cytoscape"),
    path('pipelines/<str:name>/edit', views.pipeline_edit, name="pipeline_edit"),
    path('pipelines/<str:name>/info/edit', views.pipeline_info_edit, name="pipeline_info_edit"),
    path('pipelines/<str:name>/delete', views.pipeline_delete, name="pipeline_delete"),
    path('blocks/', views.list_blocks, name="list_blocks"),
    path('blocks/add', views.add_block, name="add_block"),
    path('blocks/import', views.import_block, name="import_block"),
    path('blocks/<str:name>/edit', views.edit_block, name="edit_block"),
    path('blocks/<str:name>/save', views.save_block, name="save_block"),
    path('blocks/<str:name>/delete', views.delete_block, name="delete_block"),
    path('blocks/<str:name>/export', views.export_block, name="export_block"),

]
