import ast
import base64
import json
import socket
import time

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
from django.urls import reverse, reverse_lazy
import requests
from django.utils.datastructures import MultiValueDictKeyError

from api.views import update_result
from front.utils import create_full_json, spawn_container, get_docker_client, merge_pipeline_json
from lard_library.mercure import Mercure
from lard_library.pipeline import Pipeline as LibPipeline
from front import utils
from front.backend import EmailOrUsernameModelBackend
from django.shortcuts import render, redirect

# Create your views here.
from front.models import Pipeline, Block, InputOutputType, InputOutput, PipelineResult, Vote, PipelineResultImage
from lard_website import settings
from django.views.decorators.csrf import csrf_exempt


@login_required
def index(request):
    return redirect(reverse(dashboard))  # render(request, "index.html")


@login_required
def editor(request):
    return render(request, "editor.html")


@login_required
def datasets(request, name):
    data = """{}"""
    data = json.loads(data)
    return JsonResponse(data, safe=False)


@login_required
def list_pipelines(request):
    return render(request, "pipelines_list.html",
                  context={"pipelines_list": Pipeline.objects.filter(Q(is_public=True) | Q(owner=request.user))})


@login_required
def pipeline(request, name):
    m = Mercure(str(request.user))
    config = {"hubURLPipeline": m.hub_url, "topicPipeline": name + "/" + request.user.username}
    context = {
        "name": name,
        "blocks": Block.objects.all().order_by('name'),
        "pipelines": Pipeline.objects.filter(is_public=True),
        "pipeline": Pipeline.objects.get(name=name),
        "pipeline_mercure_config": config
    }
    """p = Pipeline.objects.get(name=name)
    j = json.loads(p.json_value)
    p = LibPipeline(name)
    p.load_json(j)"""

    return render(request, 'pipeline.html', context=context)


@login_required
@csrf_exempt
def pipeline_merge(request, name):
    pipeline_name = name

    m = Mercure(request.user.username)
    m.hub_url = 'http://mercure:80/hub'

    try:
        to_merge_name = request.POST.get("to_merge")
        p = Pipeline.objects.get(name=pipeline_name, owner=request.user)
        to_merge = Pipeline.objects.get(name=to_merge_name)

        merged = merge_pipeline_json(json.loads(p.json_value), json.loads(to_merge.json_value))

        p.json_value = json.dumps(merged)
        p.save()

        m.send(json.dumps({"type": "info", "title": "Pipeline merged : ",
                           "message": "Les deux pipelines ont bien été fusionnés"}))

        p = Pipeline.objects.get(name=name)
        j = json.loads(p.json_value)
        p = LibPipeline(name)
        # j = json.loads(create_full_json(j))
        p.load_json(j)
        return JsonResponse(p.get_cytoscape(), safe=False)
    except Exception:
        m.send(json.dumps({"type": "danger", "title": "Pipeline merged : ",
                           "message": "Echec de la fusion"}))
        return HttpResponseBadRequest()


@login_required
def pipeline_edit_inputs(request, name, block_name, block_id):
    p = Pipeline.objects.get(name=name)
    data = json.loads(p.json_value)

    block = data.get("blocks").get(block_name)
    context = {
        "block_id": block_id,
        "block": block,
    }

    return render(request, "pipeline_edit_blocks_modal.html", context=context)


@login_required
def pipeline_info_block(request, name, block_name, block_id):
    p = Pipeline.objects.get(name=name)
    data = json.loads(p.json_value)

    block = data.get("blocks").get(block_name)
    context = {
        "block": block,
        "block_id": block_id,
        'block_base': Block.objects.get(name=block.get("type"))
    }

    return render(request, "pipeline_block_info_modal.html", context=context)


@login_required
def pipeline_edit_edge_inputs(request, name, edge_source, edge_target, edge_id, old_name, new_name):
    p = Pipeline.objects.get(name=name)
    data = json.loads(p.json_value)

    edge_from = ""
    edge_to = ""
    for i in data.get("liaisons"):
        if i.get("from") == edge_source:
            edge_from = i.get("from")

    for i in data.get("liaisons"):
        if i.get("to") == edge_target:
            edge_to = i.get("to")

    block_from = data.get("blocks").get(edge_from)
    block_to = data.get("blocks").get(edge_to)
    context = {
        "edge_id": edge_id,
        "block_from": block_from,
        "block_to": block_to,
        "input_block_from": Block.objects.get(name=block_from.get("type")),
        "input_block_to": Block.objects.get(name=block_to.get("type")),
        "old_name": old_name,
        "new_name": new_name
    }

    return render(request, "pipeline_edit_edge_modal.html", context=context)


@login_required
def pipeline_add(request):
    if request.POST:
        name = request.POST.get("name")
        description = request.POST.get("description")
        public = True if "public" in request.POST else False
        value = {"blocks": {}, "liaisons": []}
        owner = request.user

        Pipeline.objects.create(name=name, description=description, owner=owner, is_public=public,
                                json_value=json.dumps(value))
        return redirect('pipeline', name=name)

    else:
        return HttpResponseBadRequest()


@login_required
def pipeline_import(request):
    if request.POST:
        if "data" not in request.FILES:
            print("NoData")
            print(request.FILES)
            print(request.POST)
            return HttpResponseBadRequest()
        if request.FILES['data']:
            data = json.dumps(json.loads(request.FILES['data'].read()))
            name = request.POST.get("name")
            description = request.POST.get("description")
            public = True if "public" in request.POST else False
            owner = request.user

            Pipeline.objects.create(name=name, description=description, owner=owner, is_public=public, json_value=data)
            return redirect('pipeline', name=name)
        else:
            print("NoFile")
            return HttpResponseBadRequest()
    else:
        return render(request, 'pipeline_import_modal.html')


@login_required
def pipeline_export(request, name):
    try:
        p = Pipeline.objects.get(name=name)
    except Pipeline.DoesNotExist as e:
        return django.http.HttpResponseNotFound()

    response = JsonResponse(json.loads(p.json_value), content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=' + name.lower() + '.json'
    return response


@login_required
def pipeline_info_edit(request, name):
    p = Pipeline.objects.get(name=name)
    if request.POST:
        p.name = request.POST.get("name", p.name)
        p.description = request.POST.get("description", p.description)
        p.is_public = True if "public" in request.POST else False
        p.save()

        return redirect('pipeline', name=p.name)
    else:
        return render(request, 'pipeline_edit_info_modal.html', context={"pipeline": p})


# TODO : Cette fonction sert encore ?
@login_required
def pipeline_edit(request, name):
    if request.method == 'POST':
        j = json.loads(request.body)
        p = Pipeline.objects.get(name=name)
        p.json_value = json.dumps(j)
        p.save()
        l_p = LibPipeline(name)
        j = create_full_json(p.json_value)
        l_p.load_json(j)
        return HttpResponse(str(l_p.get_json()))
    return HttpResponse("ERROR")
    # return render(request, 'pipeline.html', context=context)


@login_required
def pipeline_delete(request, name):
    if request.method == 'POST':
        try:
            p = Pipeline.objects.get(name=name, owner=request.user)
            p.delete()
        except Pipeline.DoesNotExist:
            return HttpResponseBadRequest()
    return redirect(reverse(list_pipelines))


@login_required
def pipeline_empty_inputs(request, name):
    context = {
        "name": name
    }

    p = Pipeline.objects.get(name=name)
    j = json.loads(p.json_value)
    l_p = LibPipeline(name)
    # j = json.loads(create_full_json(j))
    l_p.load_json(j)
    context["blocks"] = l_p.get_empty_inputs()
    return render(request, "pipeline_inputs_modal.html", context=context)


@login_required
@csrf_exempt
def pipeline_execute(request, name):
    blocks_names = request.POST.getlist("blocks_names")
    inputs_names = request.POST.getlist("inputs_names")
    inputs_values = request.POST.getlist("inputs_values")
    inputs_types = request.POST.getlist("inputs_types")
    files = request.FILES.getlist("inputs_values")

    m = Mercure(request.user.username)
    m.hub_url = 'http://mercure:80/hub'
    j = {}
    try:
        file_cptr = 0
        inputs_cptr = 0
        for i in inputs_types:
            if i == "image":
                if file_cptr < len(files):
                    img = cv2.imdecode(np.frombuffer(files[file_cptr].read(), dtype=np.uint8), -1)
                    img = img.tolist()
                    inputs_values.insert(inputs_cptr, img)
                file_cptr += 1
            inputs_cptr += 1

        p = Pipeline.objects.get(name=name)
        j = json.loads(p.json_value)

        for b, n, v, t in zip(blocks_names, inputs_names, inputs_values, inputs_types):
            try:
                d = ast.literal_eval(v)
            except ValueError:
                d = v

            j.get("blocks").get(b).get("data")[n] = d

        j = create_full_json(j)
        j["name"] = name

        pr = PipelineResult.objects.create(user=request.user, pipeline=p, images="[]", logs="[]")

        m.send(json.dumps({"type": "info", "title": "Pipeline en cours : ",
                           "message": "Démarrage du container."}))

        container = spawn_container()
        m.send(json.dumps({"type": "info", "title": "Pipeline en cours : ",
                           "message": "Le container a été démarré. Début du traitement."}))

        for l in container.logs(follow=True, stream=True):
            s = str(l, "utf-8")
            if "Running" in s:
                break
        ip = str(container.exec_run("awk 'END{print $1}' /etc/hosts")[1], "utf-8").replace("\n", "")

        worker_id = container.short_id
        pr.worker_id = worker_id
        pr.save()

        local_ip = str(socket.gethostbyname(socket.gethostname()))
        j["worker_id"] = worker_id
        j["worker_ip"] = ip
        j["username"] = str(request.user)
        j["update_url"] = "http://" + local_ip + ":8000" + reverse(update_result, kwargs={'worker_id': worker_id})

        try:
            context = requests.post("http://" + ip + ":12300/run", json=j)
        except Exception as e:
            print(e)

    except AttributeError or ValueError as e:
        print(e)
        m.send(json.dumps({"type": "danger", "title": "Pipeline échoué : ",
                           "message": "Le pipeline a échoué pendant le chargement des inputs."}))
    except Exception as e:
        print(e)
        m.send(json.dumps({"type": "danger", "title": "Pipeline échoué : ",
                           "message": "Le pipeline a échoué."}))

    del j
    del blocks_names
    del inputs_names
    del inputs_values
    del inputs_types
    del files

    return HttpResponse(status=200)


@login_required
@csrf_exempt
def pipeline_cancel(request, id):
    if request.method == "POST":
        pr = PipelineResult.objects.get(id=id)
        m = Mercure(request.user.username)
        m.hub_url = 'http://mercure:80/hub'
        m.send(json.dumps({"type": "info", "title": "Execution annulée : ",
                           "message": "L'execution du pipeline <b>" + pr.pipeline.name + "</b> a été annulée. La page va être rechargée."}))

        get_docker_client().containers.get(pr.worker_id).remove(force=True)
        time.sleep(5)
        return HttpResponse(status=200)
    return HttpResponseBadRequest()


@login_required
@csrf_exempt
def pipeline_score(request, name):
    if request.method == "POST":
        print(request.POST)
        p = Pipeline.objects.get(name=name)
        vote = Vote.objects.get_or_create(pipeline=p, user=request.user)
        vote[0].value = int(request.POST.get("value", 0))
        vote[0].save()
        return HttpResponse(status=200)
    return HttpResponseBadRequest()


@login_required
def pipeline_results_list(request):
    return render(request, "pipelines_results_list.html",
                  context={"results": PipelineResult.objects.filter(user=request.user).order_by("updated_at")})


@login_required
def pipeline_results(request, id):
    r = PipelineResult.objects.get(id=id)
    images = [pri.id for pri in PipelineResultImage.objects.filter(pipeline_result=r)]
    logs = json.loads(r.logs)

    try:
        worker_status = get_docker_client().containers.get(r.worker_id).status
    except Exception:
        worker_status = "removed"

    return render(request, "pipeline_results.html",
                  context={"result": r, "images": images, "logs": logs, "worker_status": worker_status})

@login_required
def pipeline_result_image(request, id, image_id):
    pri = PipelineResultImage.objects.get(id=image_id, pipeline_result_id=id)
    return django.http.FileResponse(pri.image, content_type="image/png", filename=pri.name)

@login_required
def pipeline_result_delete(request, id):
    if request.method == "POST":
        try:
            result = PipelineResult.objects.get(id=id, user=request.user)
            result.delete()
            return redirect(reverse(pipeline_results_list))
        except PipelineResult.DoesNotExist as e:
            return HttpResponseBadRequest()
    else:
        return redirect(reverse(pipeline_results_list))


@login_required
def dashboard(request):
    scores = []
    for p in Pipeline.objects.filter(is_public=True):
        s = p.score_int()
        if s["count"] > 0:
            scores.append({"pipeline": p, "score": s})

    scores = sorted(scores, key=lambda kv: kv["score"]["value"])
    scores = scores[::-1]

    context = {
        "page": "Dashboard",
        "total_users": User.objects.count(),
        "total_pipelines": Pipeline.objects.count(),
        "total_blocks": Block.objects.count(),
        "total_results": PipelineResult.objects.count(),
        "top_5_pipelines": scores[:8],
        "pipelines": Pipeline.objects.filter(owner=request.user)[:4]
    }

    return render(request, "dashboard.html", context=context)


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
                new_value = InputOutputType.objects.get_or_create(value=i["value"])[0]
                new_input = InputOutput.objects.create(name=i["name"], value=new_value)
                block.inputs.add(new_input)

            for i in block.outputs.all():
                i.delete()

            for i in data["outputs"]:
                new_value = InputOutputType.objects.get_or_create(value=i["value"])[0]
                new_output = InputOutput.objects.create(name=i["name"], value=new_value)
                block.outputs.add(new_output)

            block.code = data["code"]
            block.save()

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
    # j = json.loads(create_full_json(j))
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
