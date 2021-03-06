"""
Project : lard
File : pipeline
Author : DELEVACQ Wallerand
Date : 18/02/19
"""
import json
import sys
import traceback

import cv2

import string
import random

from lard_library.block import Block


def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for m in range(length))


class Pipeline:

    def __init__(self, name=random_string(128)):
        self.name = name
        self.blocks = {}
        self.liaisons = []
        self.logs = []
        self.outputs = []
        self.is_running = False
        self.mercure = None

    def create_block(self, code, block_type=None, name=random_string(128), data={}, inputs={}, outputs={},
                     on_launch=False):

        logs = self.logs

        class TmpBlock(Block):
            def treatment(self, data={}):
                result = locals()
                result.update(data)
                globals().update({"logs": logs})
                exec("def log(m): logs.append({'name': \"" + name + "\", 'message': str(m)})", globals())

                try:
                    globals().update({"pipeline": self.pipeline})
                    exec(code, globals())
                    if self.pipeline.is_running:
                        exec("result = main(data)", globals(), result)
                    m = self.pipeline.mercure
                    if m:
                        m.send(json.dumps({"name": self.name}))
                except Exception as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
                    log("".join(tb[3:]))
                    m = self.pipeline.mercure
                    if m:
                        m.send(json.dumps({"failed_nodes": (self.pipeline.logs[::-1][0]).get("name")}))

                return result.get("result", {})

        b = TmpBlock(name, inputs, outputs, on_launch=on_launch, block_type=block_type, pipeline=self)
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
            # print(b)
            if b.data.get("from") in json_blocks and b.data.get("to") in json_blocks:
                json_liaisons.append(b.data)
        return {"blocks": json_blocks, "liaisons": json_liaisons}

    def get_cytoscape(self):
        blocks = self.get_json().get("blocks")
        all_nodes = []
        all_edges = []

        for key in blocks:
            block = blocks[key]
            data_dict = {"id": block.get("name"), "name": block.get("name"), "type": block.get("type"), "data_ready": block.get("data_ready"), "on_launch": block.get("on_launch"), "data": block.get("data")}
            node_dict = {"data": data_dict}
            all_nodes.append(node_dict)

        liaisons = self.get_json().get("liaisons")
        for liaison in liaisons:
            if "old_name" in liaison and "new_name" in liaison:
                data_dict = {"source": liaison.get("from"), "target": liaison.get("to"),
                             "old_name": liaison.get("old_name"), "new_name": liaison.get("new_name")}
                edge_dict = {"data": data_dict}
                all_edges.append(edge_dict)
            else:
                source_outputs = blocks.get(liaison.get("from")).get("outputs")
                target_inputs = blocks.get(liaison.get("to")).get("inputs")

                if source_outputs == {}:
                    data_dict = {"source": liaison.get("from"), "target": liaison.get("to")}
                    edge_dict = {"data": data_dict}
                    all_edges.append(edge_dict)
                else:
                    for output_name in source_outputs:
                        if output_name in target_inputs and source_outputs.get(output_name) == target_inputs.get(output_name):
                            data_dict = {"source": liaison.get("from"), "target": liaison.get("to"),
                                         "old_name": output_name, "new_name": output_name}
                            edge_dict = {"data": data_dict}
                            all_edges.append(edge_dict)

        cytoJSON = {"nodes": all_nodes, "edges": all_edges}

        return cytoJSON

    def get_outputs(self):
        return self.outputs

    def get_empty_inputs(self):
        empty_inputs = []
        blocks = [self.blocks[name].to_dict() for name in self.blocks]
        liaisons = [l.get("data") for l in self.get_liaisons()]

        for b in blocks:
            inputs_set = set([(o_name, b.get("inputs").get(o_name)) for o_name in b.get("inputs")]) # set([(name, type)])
            outputs_set = set()
            for l in liaisons:
                if l.get("to") == b.get("name"):
                    from_block = self.blocks[l.get("from")].to_dict()
                    outputs_set.update(
                        [(l.get("new_name", o_name), from_block.get("outputs").get(o_name)) for o_name in
                         from_block.get("outputs")])
            n_b = []
            for r in list(inputs_set ^ outputs_set):
                v = b.get("data").get(r[0])
                if v is None:
                    v = ""
                n_b.append({"name": r[0], "type": r[1], "value": v})

            empty_inputs.append({"name": b.get("name"), "empty_inputs": n_b})

        return empty_inputs

    def get_liaisons(self):
        return [l.to_dict() for l in self.liaisons]

    def launch(self):
        self.is_running = True
        result = Block.launch_all([self.blocks[name] for name in self.blocks])
        return result
    
    def load_json(self, j):
        for block_name in j["blocks"]:
            block = j["blocks"][block_name]
            inputs = {}
            for i in block["inputs"]:
                inputs[i] = str(block["inputs"][i])
            outputs = {}
            for i in block["outputs"]:
                outputs[i] = str(block["outputs"][i])
            data = {}
            data.update(block.get("data"))
            b = self.create_block(code=block.get("code"), name=block.get("name"), data=data, inputs=inputs,
                                  outputs=outputs, on_launch=block.get("on_launch"), block_type=block.get("type"))
        for l in j["liaisons"]:
            try:
                b_from = self.blocks[l.get("from")]
                b_to = self.blocks[l.get("to")]
                self.connect(b_from, b_to, l.get("old_name", None), l.get("new_name", None))
            except Exception as e:
                print("Can't create liaison")
                pass