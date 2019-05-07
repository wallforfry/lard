import json

import django
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from front.models import Block, Pipeline
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

    pipeline_dict = LibPipeline.from_cytoscape_to_python_json(json.loads(pipeline_raw))

    try:
        pipeline = Pipeline.objects.get(name=pipeline_name)
        pipeline.json_value = json.dumps(pipeline_dict)
        pipeline.save()

    except Pipeline.DoesNotExist:
        return django.http.HttpResponseBadRequest
    return JsonResponse({"result": "ok"})
