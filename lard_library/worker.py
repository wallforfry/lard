"""
Project : lard
File : worker
Author : DELEVACQ Wallerand
Date : 11/05/19
"""
import base64
import io
import json
import sys

import cv2
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from gevent import monkey

from lard_library.mercure import Mercure

monkey.patch_all()

import grequests as async_requests
from flask import Flask, request, Response, send_file

from lard_library.pipeline import Pipeline

app = Flask(__name__)

@app.route("/")
def main():
    j = {'name': 'PipeName', 'blocks': {'Output': {'on_launch': False, 'outputs': {'output': 'image'}, 'inputs': {'image': 'image'}, 'type': 'Output', 'name': 'Output', 'data_ready': {}, 'data': {'image': None}, 'code': 'import cv2\r\n\r\ndef main(data):\r\n    return {"output": data.get("image")}'}, 'Blur': {'on_launch': False, 'outputs': {'image': 'image'}, 'inputs': {'image': 'image', 'ksize': 'int'}, 'type': 'Blur', 'name': 'Blur', 'data_ready': {}, 'data': {'ksize': 13, 'image': None}, 'code': 'import cv2\r\n\r\ndef main(data):\r\n    log("Attention je blur")\r\n    image = data.get("image")\r\n    ksize = data.get("ksize")\r\n    blured_image = cv2.medianBlur(image, ksize)\r\n    return {"image": blured_image}'}, 'Image': {'on_launch': True, 'outputs': {'image': 'image'}, 'inputs': {'image_path': 'string'}, 'type': 'Image', 'name': 'Image', 'data_ready': {}, 'data': {'image_path': 'shark.png'}, 'code': 'import cv2\r\nimport ast\r\n\r\ndef main(data):\r\n    log("Message de log")\r\n    import requests\r\n    return {"image": cv2.imread(data.get("image_path"))}'}}, 'liaisons': [{'from': 'Blur', 'to': 'Output'}, {'from': 'Image', 'to': 'Blur'}]}

    return str(requests.post(url="http://localhost:12300/run", json=j).text)

@app.route("/up")
def up():
    return "yes"

@app.route("/download", methods=['POST'])
def download():
    j = request.json
    with open(j["name"], 'rb') as bites:
        return send_file(
                     io.BytesIO(bites.read()),
                     attachment_filename=j["name"],
                     mimetype='image/png'
            )

@app.route("/run", methods=['POST'])
def run():
    j = request.json
    name = j.get("name")
    try:
        update_url = j.get("update_url")

        m = Mercure(name+"/"+j["username"])

        p = Pipeline(name)
        p.mercure = m
        p.load_json(j)

        f = p.launch()
        results = p.get_outputs()

        images_names = []
        for r in results:
            try:
                cv2.imwrite(r["name"]+".png", r["value"])
                images_names.append(r["name"]+".png")
            except Exception as e:
                print(e)
                p.logs.append({"name": "LARD", "message": "Can't get correct \"image\" value"})

        result = {"name": name, "images": images_names, "logs": p.logs, "worker_id": j.get("worker_id"), "username": j.get("username"), "worker_ip": j.get("worker_ip")}

        requests.post(update_url, json=result)
        del result
        del p
    except Exception as e:
        print(e)
        result = {"name": name, "images": [], "logs": [], "worker_id": j.get("worker_id"),
                  "username": j.get("username")}
        requests.post(update_url, json=result)
        del result
        m = Mercure(j["username"])
        m.send(json.dumps({"type": "danger", "title": "Pipeline échoué : ", "message": "Le pipeline " + name + " a échoué."}))
        sys.exit(str(e))
    del j
    return Response(status=200)
