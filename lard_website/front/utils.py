"""
Project : lard
File : utils
Author : DELEVACQ Wallerand
Date : 17/02/19
"""
import json
import os
import urllib.parse

import docker
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

import calendar
import datetime

from django.utils.html import avoid_wrapping
from django.utils.timezone import is_aware, utc
from django.utils.translation import gettext, ngettext_lazy

TIME_STRINGS = {
    'year': ngettext_lazy('%d year', '%d years'),
    'month': ngettext_lazy('%d month', '%d months'),
    'week': ngettext_lazy('%d week', '%d weeks'),
    'day': ngettext_lazy('%d day', '%d days'),
    'hour': ngettext_lazy('%d hour', '%d hours'),
    'minute': ngettext_lazy('%d minute', '%d minutes'),
    'second': ngettext_lazy('%d second', '%d seconds'),
}

TIMESINCE_CHUNKS = (
    (60 * 60 * 24 * 365, 'year'),
    (60 * 60 * 24 * 30, 'month'),
    (60 * 60 * 24 * 7, 'week'),
    (60 * 60 * 24, 'day'),
    (60 * 60, 'hour'),
    (60, 'minute'),
    (1, 'second'),
)

@register.filter
def timesince_seconds(d, now=None, reversed=False, time_strings=None):
    """
    Take two datetime objects and return the time between d and now as a nicely
    formatted string, e.g. "10 minutes". If d occurs after now, return
    "0 minutes".
    Units used are years, months, weeks, days, hours, and minutes.
    Seconds and microseconds are ignored.  Up to two adjacent units will be
    displayed.  For example, "2 weeks, 3 days" and "1 year, 3 months" are
    possible outputs, but "2 weeks, 3 hours" and "1 year, 5 days" are not.
    `time_strings` is an optional dict of strings to replace the default
    TIME_STRINGS dict.
    Adapted from
    https://web.archive.org/web/20060617175230/http://blog.natbat.co.uk/archive/2003/Jun/14/time_since
    """
    if time_strings is None:
        time_strings = TIME_STRINGS

    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    now = now or datetime.datetime.now(utc if is_aware(d) else None)

    if reversed:
        d, now = now, d
    delta = now - d

    # Deal with leapyears by subtracing the number of leapdays
    leapdays = calendar.leapdays(d.year, now.year)
    if leapdays != 0:
        if calendar.isleap(d.year):
            leapdays -= 1
        elif calendar.isleap(now.year):
            leapdays += 1
    delta -= datetime.timedelta(leapdays)

    # ignore microseconds
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return avoid_wrapping(gettext('0 minutes'))
    for i, (seconds, name) in enumerate(TIMESINCE_CHUNKS):
        count = since // seconds
        if count != 0:
            break
    result = avoid_wrapping(time_strings[name] % count)
    if i + 1 < len(TIMESINCE_CHUNKS):
        # Now get the second item
        seconds2, name2 = TIMESINCE_CHUNKS[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            result += gettext(', ') + avoid_wrapping(time_strings[name2] % count2)
    return result

def from_cytoscape_to_python_json(cytoscape_format):
    blocks = {}
    liaisons = []
    nodes = cytoscape_format.get("nodes")
    edges = cytoscape_format.get("edges")
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
        if "old_name" in edge.get("data") and "new_name" in edge.get("data"):
            liaison = {"from": edge.get("data").get("source"), "to": edge.get("data").get("target"), "old_name": edge.get("data").get("old_name"), "new_name": edge.get("data").get("new_name")}
        else:
            liaison = {"from": edge.get("data").get("source"), "to": edge.get("data").get("target")}
        liaisons.append(liaison)
    return {"blocks": blocks, "liaisons": liaisons}


def create_full_json(j: dict) -> str:
    for b in j.get("blocks").items():
        block = Block.objects.get(name=b[1].get("type"))
        b[1]["code"] = block.code

    return json.dumps(j)

def merge_pipeline_json(p_p1: dict, p_p2: dict) -> dict:
    result = p_p1.copy()
    result["blocks"].update(p_p2["blocks"])
    result["liaisons"] += p_p2["liaisons"]
    return result

def get_docker_client():
    return docker.DockerClient(base_url='unix://var/run/docker.sock')

def spawn_container():
    client = get_docker_client()
    container = client.containers.run('wallforfry/lard-worker', detach=True, auto_remove=True, network="lard_default", environment={"JWT_KEY": os.environ.get("JWT_KEY"), "HUB_URL": 'http://mercure:80/hub'})
    return container
