"""
Project : lard
File : pipeline
Author : DELEVACQ Wallerand
Date : 18/02/19
"""
import json

import cv2

import string
import random

from front.models import Block as WebBlock
from lard_library.block import Block


def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for m in range(length))

class Pipeline:

    def __init__(self, name=random_string(128)):
        self.name = name
        self.blocks = {}
        self.liaisons = []

    def create_block(self, code, block_type=None, name=random_string(128), data={}, inputs={}, outputs={}, on_launch=False):

        class TmpBlock(Block):
            def treatment(self, data={}):
                result = locals()
                result.update(data)
                exec(code, globals(), result)
                exec("result = main(data)", globals(), result)
                self.data = result.get("result", {})
                return self.data

        b = TmpBlock(name, inputs, outputs, on_launch=on_launch, block_type=block_type)
        b.data = data
        self.blocks[name] = b
        return b

    def remove_block(self, name):
        pass

    def connect(self, prev, next, prev_name=None, next_name=None):
        t_liaison = prev.connect_to(next, prev_name, next_name)
        self.liaisons.append(t_liaison)

    def get_blocks(self):
        print(self.blocks)

    def get_json(self):
        json_blocks = {self.blocks[name].name: self.blocks[name].to_dict() for name in self.blocks}
        json_liaisons = []
        for b in self.liaisons:
            if b.data.get("from") in json_blocks and b.data.get("to") in json_blocks:
                json_liaisons.append(b.data)

        return {"blocks": json_blocks, "liaisons": json_liaisons}

    def get_cytoscape(self):
        cytoJSON = []
        blocks = self.get_json().get("blocks")

        for key in blocks:
            block = blocks[key]
            data_dict = {"id": block.get("name"), "name": block.get("type")}
            node_dict = {"data": data_dict}
            cytoJSON.append(node_dict)

        liaisons = self.get_json().get("liaisons")
        for liaison in liaisons:
            data_dict = {"source": liaison.get("from"), "target": liaison.get("to")}
            edge_dict = {"data": data_dict}
            cytoJSON.append(edge_dict)

        return cytoJSON

    def get_outputs(self):
        results = {}
        for name in self.blocks:
            b = self.blocks[name]
            if len(b._observers) == 0:
                results[b.name] = b.to_dict()

        return results

    def get_liaisons(self):
        return [l.to_dict() for l in self.liaisons]

    def launch(self):
        Block.launch_all([self.blocks[name] for name in self.blocks])

    def load_json(self, j):
        for block_name in j["blocks"]:
            block = j["blocks"][block_name]
            lard_block = WebBlock.objects.get(name=block.get("type"))
            b = self.create_block(code=lard_block.code, name=block.get("name"), data=block.get("data_ready"), inputs=block.get("inputs"),
                               outputs=block.get("outputs"), on_launch=block.get("on_launch"), block_type=block.get("type"))

        for l in j["liaisons"]:
            try:
                b_from = self.blocks[l.get("from")]
                b_to = self.blocks[l.get("to")]
                self.connect(b_from, b_to, l.get("old_name", None), l.get("new_name", None))
            except Exception as e:
                print("Can't create liaison")
                pass
