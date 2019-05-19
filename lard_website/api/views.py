import json
import time
import cv2
import numpy as np

import django
import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils.timesince import timesince
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from front.models import Block, Pipeline, PipelineResult, PipelineResultImage
from front.utils import from_cytoscape_to_python_json, get_docker_client, timesince_seconds
from lard_library.mercure import Mercure
from lard_library.pipeline import Pipeline as LibPipeline


def index(request):
    return HttpResponse("Api")


@login_required
def list_blocks(request):
    blocks = [b.as_json() for b in Block.objects.all()]
    return JsonResponse(blocks, safe=False)


@login_required
@csrf_exempt
def update_pipeline(request):
    pipeline_name = request.POST.get("name")
    pipeline_raw = request.POST.get("pipeline")
    pipeline_dict = from_cytoscape_to_python_json(json.loads(pipeline_raw))
    try:
        pipeline = Pipeline.objects.get(name=pipeline_name)
        pipeline.json_value = json.dumps(pipeline_dict)
        pipeline.save()

    except Pipeline.DoesNotExist:
        return django.http.HttpResponseBadRequest
    return JsonResponse({"result": "ok"})

@csrf_exempt
def update_result(request, worker_id):
    body = request.body.decode("utf-8")
    context = json.loads(body)
    m = Mercure(context["username"])
    m.hub_url = 'http://mercure:80/hub'

    try:
        r = PipelineResult.objects.get(worker_id=worker_id)
        for i in context["images"]:
            addr = "http://" + context["worker_ip"] + ":12300/download"
            rq = requests.post(addr, json={"name": i})
            PipelineResultImage.objects.create(name=i, image=rq.content, pipeline_result=r)

        r.logs = json.dumps(context["logs"])
        r.save()

        if len(context["images"]) == 0:
            m.send(json.dumps({"type": "warning", "title": "Pipeline terminé  : ",
                               "message": "Le pipeline " + r.pipeline.name + " s'est terminé mais n'a pas renvoyé d'image. Cliquez ici pour consulter les logs.",
                               "url": str(reverse("pipeline_results", kwargs={"id": r.id}))}))
        else:
            duration = timesince_seconds(r.created_at, r.updated_at)
            m.send(json.dumps({"type": "success", "title": "Pipeline terminé : ",
                               "message": "Le pipeline <b>" + r.pipeline.name + "</b> s'est correctement terminé avec une durée de <b>"+duration+"</b>. Cliquez ici pour voir le résultat",
                               "url": str(reverse("pipeline_results", kwargs={"id": r.id}))}))

        get_docker_client().containers.get(worker_id).remove(force=True)
        return HttpResponse(status=200)

    except PipelineResult.DoesNotExist:
        m.send(json.dumps({"type": "danger", "title": "Pipeline échoué : ",
                           "message": "Le pipeline a échoué."}))

        get_docker_client().containers.get(worker_id).remove(force=True)
        return django.http.HttpResponseBadRequest()
