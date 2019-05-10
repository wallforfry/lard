import base64
import json
import numpy as np

import cv2
import django
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.files import File
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.urls import reverse
import requests
from django.utils.datastructures import MultiValueDictKeyError

from lard_library.pipeline import Pipeline as LibPipeline
from front import utils
from front.backend import EmailOrUsernameModelBackend
from django.shortcuts import render, redirect

# Create your views here.
from front.models import Pipeline, Block, InputOutputType, InputOutput
from lard_website import settings
from django.views.decorators.csrf import csrf_exempt

@login_required
def index(request):
    return render(request, "index.html")


@login_required
def editor(request):
    return render(request, "editor.html")


@login_required
def datasets(request, name):
    data = """{}"""
    data = json.loads(data)
    return JsonResponse(data, safe=False)


@login_required
def list_piplines(request):
    return render(request, "pipelines_list.html",
                  context={"pipelines_list": Pipeline.objects.filter(Q(is_public=True) | Q(owner=request.user))})


@login_required
def pipeline(request, name):
    context = {
        "name": name,
        "blocks": Block.objects.all()
    }
    """p = Pipeline.objects.get(name=name)
    j = json.loads(p.json_value)
    p = LibPipeline(name)
    p.load_json(j)"""

    return render(request, 'pipeline.html', context=context)


@login_required
def pipeline_edit_inputs(request, name, block_name, block_id):
    p = Pipeline.objects.get(name=name)
    data = json.loads(p.json_value)

    block = data.get("blocks").get(block_name)
    context = {
        "block_id": block_id,
        "block": block,
    }

    return render(request, "pipeline_edit_modal.html", context=context)

@login_required
def pipeline_edit_edge_inputs(request, source, target, id):
    context = {
        "blocks": Block.objects.all(),
        "source": Block.objects.all().filter(name=source),
        "target": Block.objects.all().filter(name=target),
        "id":id
    }

    return render(request, "pipeline_edit_edge_modal.html", context=context)


@login_required
def pipeline_edit(request, name):
    if request.method == 'POST':
        j = json.loads(request.body)
        p = Pipeline.objects.get(name=name)
        p.json_value = json.dumps(j)
        p.save()
        p = LibPipeline(name)
        p.load_json(p.json_value)
        return HttpResponse(str(p.get_json()))
    return HttpResponse("ERROR")
    # return render(request, 'pipeline.html', context=context)


@login_required
def pipeline_empty_inputs(request, name):
    context = {
        "name": name
    }

    p = Pipeline.objects.get(name=name)
    j = json.loads(p.json_value)
    p = LibPipeline(name)
    p.load_json(j)
    context["blocks"] = p.get_empty_inputs()
    return render(request, "pipeline_inputs_modal.html", context=context)


@login_required
@csrf_exempt
def pipeline_execute(request, name):

    blocks_names = request.POST.getlist("blocks_names")
    inputs_names = request.POST.getlist("inputs_names")
    inputs_values = request.POST.getlist("inputs_values")
    inputs_types = request.POST.getlist("inputs_types")
    files = request.FILES.getlist("inputs_values")


    file_cptr = 0
    inputs_cptr = 0
    for i in inputs_types:
        if i == "image":
            inputs_values.insert(inputs_cptr, cv2.imdecode(np.fromstring(files[file_cptr].read(), dtype=np.uint8), 1).tolist())
            file_cptr += 1
        inputs_cptr += 1

    p = Pipeline.objects.get(name=name)
    j = json.loads(p.json_value)
    for b, n, v, t in zip(blocks_names, inputs_names, inputs_values, inputs_types):
        d = v
        if t == "float":
            d = float(v)
        elif t == "int":
            d = int(v)

        j.get("blocks").get(b).get("data")[n] = d
    p.json_value = json.dumps(j)
    p.save()

    p = LibPipeline(name)
    p.load_json(j)

    f = p.launch()
    results = p.get_outputs()

    frames_b64 = []
    for r in results:
        try:
            ret, img = cv2.imencode('.png', r["value"])
            frame_b64 = base64.b64encode(img).decode("utf-8")
            frames_b64.append({"name": r["name"], "image": frame_b64})
        except Exception as e:
            p.logs.append({"name": "LARD", "message": "Can't get correct \"image\" value"})

    p_model = Pipeline.objects.get(name=name)
    pipeline_raw = json.loads(p_model.json_value)
    for bl in pipeline_raw["blocks"].items():
        b = bl[1]
        for i in b["inputs"].items():
            if i[1] == "image":
                b["data"][i[0]] = None

    p_model.json_value = json.dumps(pipeline_raw)
    p_model.save()

    return render(request, 'pipeline_result_modal.html', context={"name": name, "images": frames_b64, "logs": p.logs})


@login_required
def dashboard(request):
    return render(request, "dashboard.html", context={"page": "Dashboard", "total_users": User.objects.count(),
                                                      "total_pipelines": Pipeline.objects.count(),
                                                      "total_blocks": Block.objects.count()})


@login_required
def add_block(request):
    name = request.POST.get("name")
    description = request.POST.get("description")
    code = """
import cv2
def main(data):
    resultat = data.get("%nom_input%")
    return {"%nom_output%": "resultat"}
"""
    b = Block.objects.create(name=name, description=description, code=code)

    b.save()

    return redirect('edit_block', name=name)


@login_required
def edit_block(request, name):
    block = Block.objects.get(name=name)
    inputs = block.inputs.all()
    outputs = block.outputs.all()
    var_types = InputOutputType.objects.all()

    context = {
        "code": block.code,
        "file_name": block.name,
        "description": block.description,
        "language": "python",
        "save_url": reverse(save_block, kwargs={"name": name}),
        "inputs": inputs,
        "outputs": outputs,
        "var_types": var_types}
    return render(request, "block_editor.html", context=context)


@login_required
def delete_block(request, name):
    Block.objects.get(name=name).delete()

    return redirect('list_blocks')


@login_required
def save_block(request, name):
    if request.method == "POST":
        name = request.POST.get("name", "")
        block = Block.objects.get(name=name)

        if "code" in request.POST:
            code = request.POST.get("code", "")
            block.code = code
        elif "type" in request.POST:
            if request.POST.get("type") == "inputs":
                names = request.POST.getlist("inputs_names")
                values = request.POST.getlist("inputs_values")
                for i in block.inputs.all():
                    i.delete()
                for i in range(0, len(names)):
                    new_value = InputOutputType.objects.get(value=values[i])
                    new_input = InputOutput.objects.create(name=names[i], value=new_value)
                    block.inputs.add(new_input)
            elif request.POST.get("type") == "outputs":
                names = request.POST.getlist("outputs_names")
                values = request.POST.getlist("outputs_values")
                for i in block.outputs.all():
                    i.delete()
                for i in range(0, len(names)):
                    new_value = InputOutputType.objects.get(value=values[i])
                    new_input = InputOutput.objects.create(name=names[i], value=new_value)
                    block.outputs.add(new_input)
        block.save()
        return redirect('edit_block', name=name)

@login_required
def import_block(request):
    if request.method == 'POST':
        if "data" not in request.FILES:
            return HttpResponseBadRequest()
        if request.FILES['data']:
            data = json.loads(request.FILES['data'].read())
            block_name = data["name"]
            try:
                block = Block.objects.get(name=block_name)
            except Block.DoesNotExist:
                block = Block.objects.create(name=data["name"], description=data["description"], code=data["code"])

            for i in block.inputs.all():
                i.delete()

            for i in data["inputs"]:
                new_value = InputOutputType.objects.get(value=i["value"])
                new_input = InputOutput.objects.create(name=i["name"], value=new_value)
                block.inputs.add(new_input)

            for i in block.outputs.all():
                i.delete()

            for i in data["outputs"]:
                new_value = InputOutputType.objects.get(value=i["value"])
                new_output = InputOutput.objects.create(name=i["name"], value=new_value)
                block.outputs.add(new_output)

            return redirect('edit_block', name=block_name)
        else:
            return HttpResponseBadRequest()
    else:
        return render(request, 'block_import_modal.html')


@login_required
def export_block(request, name):
    try:
        block = Block.objects.get(name=name)
    except Block.DoesNotExist as e:
        return django.http.HttpResponseNotFound()

    response = JsonResponse(block.as_json(), content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=' + name.lower() + '.json'
    return response

@login_required
def list_blocks(request):
    return render(request, "block_list.html", context={"blocks": Block.objects.all()})


@login_required
def get_cytoscape(request, name):
    p = Pipeline.objects.get(name=name)
    j = json.loads(p.json_value)
    p = LibPipeline(name)
    p.load_json(j)
    return JsonResponse(p.get_cytoscape(), safe=False)


def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse(index))
    if request.method == "POST":
        username = request.POST.get("email", "")
        password = request.POST.get("password", "")
        next = request.GET.get("next")

        if utils.check_recaptcha(request):
            user = EmailOrUsernameModelBackend.authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                if not request.POST.get('remember_me'):
                    request.session.set_expiry(0)
                if next:
                    return redirect(next)
                else:
                    return redirect(reverse(index))
        else:
            messages.error(request, "Vous êtes un robot..")
    return render(request, "login.html", context={"page": "Login", "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY})


def register_view(request):
    if not settings.ENABLE_REGISTRATION:
        return redirect(reverse(index))

    if request.method == "POST":
        username = request.POST.get("username", "")
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm", "")
        agree = request.POST.get("agree", False)
        next = request.GET.get("next")

        if utils.check_recaptcha(request):
            if agree:
                if password == confirm:
                    try:
                        try:
                            User.objects.get(email=email)
                            messages.error(request, "Cette adresse email est déjà prise")
                        except:
                            user = User.objects.create_user(email=email, username=username, password=password)
                            user.save()
                            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                            return redirect(reverse(index))
                    except IntegrityError:
                        messages.error(request, "Ce nom d'utilisateur est déjà utilisé")
                else:
                    messages.error(request, "Les mot de passes ne correspondent pas")
            else:
                messages.error(request, "Vous devez accepter les termes et conditions d'utilisation")

    return render(request, "register.html",
                  context={"page": "Register", "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY})


def logout_view(request):
    logout(request)
    return redirect(reverse(index))


@user_passes_test(lambda u: u.is_superuser)
def admin_users(request):
    return render(request, "admin/users.html", context={"users": User.objects.all()})
