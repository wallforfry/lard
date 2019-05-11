"""
Project : lard
File : utils
Author : DELEVACQ Wallerand
Date : 17/02/19
"""
import json
import urllib.parse

import requests

from front.models import Block
from lard_website import settings


def check_recaptcha(request):
    URIReCaptcha = 'https://www.google.com/recaptcha/api/siteverify'
    recaptchaResponse = request.POST.get('recaptchaResponse')
    private_recaptcha = settings.RECAPTCHA_SECRET_KEY
    params = urllib.parse.urlencode({
        'secret': private_recaptcha,
        'response': recaptchaResponse,
    })

    # print params
    data = requests.get(URIReCaptcha, params)
    result = json.loads(data.content)
    success = result.get('success', None)
    return success


from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def from_cytoscape_to_python_json(cytoscape_format):
    blocks = {}
    liaisons = []
    nodes = cytoscape_format.get("nodes")
    edges = cytoscape_format.get("edges")
    print(nodes)
    for node in nodes:
        blocks_of_wanted_type = Block.objects.filter(name=node.get("data").get("type")).all()
        if not blocks_of_wanted_type.exists():
            continue
        block_type = blocks_of_wanted_type[0]
        outputs = {}
        for output in block_type.outputs.all():
            outputs[output.name] = output.value.value
        inputs = {}
        for inpt in block_type.inputs.all():
            inputs[inpt.name] = inpt.value.value
        block = {
            "on_launch": node.get("block_data").get("on_launch"),
            "outputs": outputs,
            "inputs": inputs,
            "type": node.get("data").get("type"),
            "name": node.get("data").get("id"),
            "data_ready": node.get("block_data").get("data_ready"),
            "data": node.get("block_data").get("data")
        }
        blocks[node.get("data").get("id")] = block

    for edge in edges:
        liaison = {"from": edge.get("data").get("source"), "to": edge.get("data").get("target")}
        liaisons.append(liaison)

    return {"blocks": blocks, "liaisons": liaisons}

def load_json(pipeline, j):
    for block_name in j["blocks"]:
        block = j["blocks"][block_name]
        lard_block = Block.objects.get(name=block.get("type"))
        inputs = {}
        for i in lard_block.inputs.all():
            inputs[i.name] = str(i.value)
        outputs = {}
        for i in lard_block.outputs.all():
            outputs[i.name] = str(i.value)
        data = {}
        data.update(block.get("data"))
        b = pipeline.create_block(code=lard_block.code, name=block.get("name"), data=data, inputs=inputs,
                              outputs=outputs, on_launch=block.get("on_launch"), block_type=block.get("type"))
    for l in j["liaisons"]:
        try:
            b_from = pipeline.blocks[l.get("from")]
            b_to = pipeline.blocks[l.get("to")]
            pipeline.connect(b_from, b_to, l.get("old_name", None), l.get("new_name", None))
        except Exception as e:
            print("Can't create liaison")
            pass
