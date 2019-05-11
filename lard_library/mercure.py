"""
Project : farmbot_translator
File : mercure
Author : DELEVACQ Wallerand
Date : 03/05/19
"""
import os
import jwt
import requests


class Mercure:

    def __init__(self, short):
        self.targets = [short]
        self.token = jwt.encode(
            {'mercure': {'subscribe': self.targets, 'publish': self.targets}},
            os.environ.get('JWT_KEY', '!UnsecureChangeMe!'),
            algorithm='HS256'
        )

        self.hub_url = os.environ.get('HUB_URL', 'http://localhost:12301/hub')
        self.topic = short

    def send(self, data):
        payload = {'topic': self.topic, 'data': data}
        headers = {
            'Authorization': 'Bearer '+self.token.decode('utf-8')
        }

        r = requests.post(self.hub_url, data=payload, headers=headers)
        return r.status_code
