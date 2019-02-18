"""
Project : lard
File : context_processors
Author : DELEVACQ Wallerand
Date : 17/02/19
"""
from front.models import Pipeline
from lard_website import settings


def app_processor(request):
    title = "Lard"
    description = "Lard est un projet étudiant"

    registration_enabled = settings.ENABLE_REGISTRATION

    if request.user.is_authenticated:
        pipelines = Pipeline.objects.filter(owner=request.user).all()
    else:
        pipelines = []

    return {"title": title, "description": description, "registration_enabled": registration_enabled, "pipelines": pipelines}