"""
Project : lard
File : context_processors
Author : DELEVACQ Wallerand
Date : 17/02/19
"""
def app_processor(request):
    title = "Lard"
    description = "Lard est un projet étudiant"

    return {"title": title, "description": description}