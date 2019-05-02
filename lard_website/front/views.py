import base64
import json

import cv2
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
import requests
from lard_library.pipeline import Pipeline as LibPipeline
from front import utils
from front.backend import EmailOrUsernameModelBackend
from django.shortcuts import render, redirect


# Create your views here.
from front.models import Pipeline, Block, InputOutputType, InputOutput
from lard_website import settings

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
    return render(request, "pipelines_list.html", context={"pipelines_list": Pipeline.objects.filter(Q(is_public=True) | Q(owner=request.user))})

@login_required
def pipeline(request, name):
    context = {
        "name": name
    }

    lists = 'http://127.0.0.1:8000/api/block/list'
    response_list = requests.get(lists)
    json_list = json.loads(response_list)
    for j in json_list:
        print(j)

    p = Pipeline.objects.get(name=name)
    j = json.loads(p.json_value)
    p = LibPipeline(name)
    p.load_json(j)
    return render(request, 'pipeline.html', context=context)

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
    #return render(request, 'pipeline.html', context=context)

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
def pipeline_execute(request, name):
    blocks_names = request.POST.getlist("blocks_names")
    inputs_names = request.POST.getlist("inputs_names")
    inputs_values = request.POST.getlist("inputs_values")
    inputs_types = request.POST.getlist("inputs_types")

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
    final = results.popitem()[1]

    ret, img = cv2.imencode('.png', final["data_ready"].get("image"))
    frame_b64 = base64.b64encode(img).decode("utf-8")

    return render(request,'pipeline_result_modal.html', context={"name": name, "image": frame_b64})

@login_required
def protected(request):
    return render(request, "dashboard.html", context={"page": "Dashboard"})

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

    return render(request, "register.html", context={"page": "Register", "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY})

def logout_view(request):
    logout(request)
    return redirect(reverse(index))

@user_passes_test(lambda u: u.is_superuser)
def admin_users(request):
    return render(request, "admin/users.html", context={"users": User.objects.all()})