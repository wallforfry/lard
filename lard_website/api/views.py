import json
import time

import django
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from front.models import Block, Pipeline, PipelineResult
from front.utils import from_cytoscape_to_python_json, get_docker_client
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
    try:
        r = PipelineResult.objects.get(worker_id=worker_id)
        r.images = json.dumps(context["images"])
        r.logs = json.dumps(context["logs"])
        r.save()

        time.sleep(1)
        get_docker_client().containers.get(context["worker_id"]).remove(force=True)
        return HttpResponse(status=200)

    except PipelineResult.DoesNotExist:
        return django.http.HttpResponseBadRequest()
