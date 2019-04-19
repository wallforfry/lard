from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from front.models import Block


def index(request):
    return HttpResponse("Api")

def list_blocks(request):
    return HttpResponse(serializers.serialize('json', Block.objects.all()))