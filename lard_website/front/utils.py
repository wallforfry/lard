"""
Project : lard
File : utils
Author : DELEVACQ Wallerand
Date : 17/02/19
"""
import json
import urllib.parse

import requests

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
