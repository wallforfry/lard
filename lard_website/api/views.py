from django.http import HttpResponse, JsonResponse

# Create your views here.
from front.models import Block


def index(request):
    return HttpResponse("Api")

def list_blocks(request):
    blocks = [b.as_json() for b in Block.objects.all()]
    return JsonResponse(blocks, safe=False)