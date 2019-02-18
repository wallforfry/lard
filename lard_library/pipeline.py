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

    def get_outputs(self):
        results = {}
        for name in self.blocks:
            b = self.blocks[name]
            if len(b._observers) == 0:
                results[b.name] = b.to_dict()

        return results
        #return [self.blocks[name].to_dict() for name in self.blocks]

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
