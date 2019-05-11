"""
Project : lard
File : worker
Author : DELEVACQ Wallerand
Date : 11/05/19
"""
import base64
import json

import cv2
import requests
from gevent import monkey

from lard_library.mercure import Mercure

monkey.patch_all()

import grequests as async_requests
from flask import Flask, request, Response

from lard_library.pipeline import Pipeline

app = Flask(__name__)

@app.route("/")
def main():
    j = {'name': 'PipeName', 'blocks': {'Output': {'on_launch': False, 'outputs': {'output': 'image'}, 'inputs': {'image': 'image'}, 'type': 'Output', 'name': 'Output', 'data_ready': {}, 'data': {'image': None}, 'code': 'import cv2\r\n\r\ndef main(data):\r\n    return {"output": data.get("image")}'}, 'Blur': {'on_launch': False, 'outputs': {'image': 'image'}, 'inputs': {'image': 'image', 'ksize': 'int'}, 'type': 'Blur', 'name': 'Blur', 'data_ready': {}, 'data': {'ksize': 13, 'image': None}, 'code': 'import cv2\r\n\r\ndef main(data):\r\n    log("Attention je blur")\r\n    image = data.get("image")\r\n    ksize = data.get("ksize")\r\n    blured_image = cv2.medianBlur(image, ksize)\r\n    return {"image": blured_image}'}, 'Image': {'on_launch': True, 'outputs': {'image': 'image'}, 'inputs': {'image_path': 'string'}, 'type': 'Image', 'name': 'Image', 'data_ready': {}, 'data': {'image_path': 'shark.png'}, 'code': 'import cv2\r\nimport ast\r\n\r\ndef main(data):\r\n    log("Message de log")\r\n    import requests\r\n    return {"image": cv2.imread(data.get("image_path"))}'}}, 'liaisons': [{'from': 'Blur', 'to': 'Output'}, {'from': 'Image', 'to': 'Blur'}]}

    return str(requests.post(url="http://localhost:12300/run", json=j).text)

@app.route("/up")
def up():
    return "yes"

@app.route("/run", methods=['POST'])
def run():
    j = request.json
    name = j.get("name")

    try:
        update_url = j.get("update_url")
        p = Pipeline(name)
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

        result = {"name": name, "images": frames_b64, "logs": p.logs, "worker_id": j.get("worker_id"), "username": j.get("username")}
        requests.post(update_url, json=result)
    except Exception as e:
        print(e)
        m = Mercure(j["username"])
        m.hub_url = 'http://mercure:80/hub'
        m.send(json.dumps({"type": "danger", "title": "Pipeline échoué : ", "message": "Le pipeline " + name + " a échoué."}))

    return Response(status=200)