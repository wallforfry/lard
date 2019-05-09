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

    def create_block(self, code, block_type=None, name=random_string(128), data={}, inputs={}, outputs={},
                     on_launch=False):

        class TmpBlock(Block):
            def treatment(self, data={}):
                result = locals()
                result.update(data)
                exec(code, globals(), result)
                exec("result = main(data)", globals(), result)
                return result.get("result", {})

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
            #print(b)
            if b.data.get("from") in json_blocks and b.data.get("to") in json_blocks:
                json_liaisons.append(b.data)
        return {"blocks": json_blocks, "liaisons": json_liaisons}

    def get_cytoscape(self):
        blocks = self.get_json().get("blocks")
        all_nodes = []
        all_edges = []

        for key in blocks:
            block = blocks[key]
            data_dict = {"id": block.get("name"), "name": block.get("name"), "type": block.get("type")}
            block_data = {"data_ready": block.get("data_ready"), "on_launch": block.get("on_launch"), "data": block.get("data")}
            node_dict = {"data": data_dict, "block_data": block_data}
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

                for output_name in source_outputs:
                    if output_name in target_inputs and source_outputs.get(output_name) == target_inputs.get(output_name):
                        data_dict = {"source": liaison.get("from"), "target": liaison.get("to"),
                                     "old_name": output_name, "new_name": output_name}
                        edge_dict = {"data": data_dict}
                        all_edges.append(edge_dict)

        cytoJSON = {"nodes": all_nodes, "edges": all_edges}

        return cytoJSON

    @staticmethod
    def from_cytoscape_to_python_json(cytoscape_format):
        blocks = {}
        liaisons = []
        nodes = cytoscape_format.get("nodes")
        edges = cytoscape_format.get("edges")
        for node in nodes:
            blocks_of_wanted_type = WebBlock.objects.filter(name=node.get("data").get("name")).all()
            if not blocks_of_wanted_type.exists():
                continue
            block_type = blocks_of_wanted_type[0]
            outputs = {}
            for output in block_type.outputs:
                outputs[output.name] = output.value
            inputs = {}
            for inpt in block_type.inputs:
                inputs[inpt.name] = inpt.value
            block = {
                "on_launch": node.get("block_data").get("on_launch"),
                "outputs": outputs,
                "inputs": inputs,
                "type": node.get("data").get("name"),
                "name": node.get("data").get("id"),
                "data_ready": node.get("block_data").get("data_ready"),
                "data": node.get("block_data").get("data")
            }
            blocks[node.get("data").get("id")] = block

        for edge in edges:
            liaison = {"from": edge.get("data").get("source"), "to": edge.get("data").get("target")}
            liaisons.append(liaison)

        return {"blocks": blocks, "liaisons": liaisons}


    def get_outputs(self):
        results = {}
        for name in self.blocks:
            b = self.blocks[name]
            if len(b._observers) == 0:
                results[b.name] = b.to_dict()

        return results

    def get_empty_inputs(self):
        empty_inputs = []
        data = Block.launch_all([self.blocks[name] for name in self.blocks])
        blocks = [data.get("blocks").get(name) for name in data.get("blocks")]
        liaisons = data.get("liaisons")
        for b in blocks:
            n_b = []
            exist = False
            result = set()
            inputs_set = set([(o_name, b.get("inputs").get(o_name)) for o_name in b.get("inputs")])
            for l in liaisons:
                if l.get("to") == b.get("name"):
                    from_block = data.get("blocks").get(l.get("from"))
                    outputs_set = set(
                        [(o_name, from_block.get("outputs").get(o_name)) for o_name in from_block.get("outputs")])
                    result.update(outputs_set ^ inputs_set)
                    exist = True

            if not exist:
                for n in b.get("inputs"):
                    if n in b.get("data") or n not in b.get("data_ready") or (n in b.get("data_ready") and b.get("data_ready").get(n) is None):
                        s = (n, b.get("inputs").get(n))
                        result.add(s)

            for r in result:
                v = b.get("data").get(r[0])
                if v is None:
                    v = ""
                n_b.append({"name": r[0], "type": r[1], "value": v})

            empty_inputs.append({"name": b.get("name"), "empty_inputs": n_b})
        return empty_inputs

    def get_liaisons(self):
        return [l.to_dict() for l in self.liaisons]

    def launch(self):
        Block.launch_all([self.blocks[name] for name in self.blocks])

    def load_json(self, j):
        for block_name in j["blocks"]:
            block = j["blocks"][block_name]
            lard_block = WebBlock.objects.get(name=block.get("type"))
            inputs = {}
            for i in lard_block.inputs.all():
                inputs[i.name] = str(i.value)
            outputs = {}
            for i in lard_block.outputs.all():
                outputs[i.name] = str(i.value)
            data = {}
            data.update(block.get("data"))
            b = self.create_block(code=lard_block.code, name=block.get("name"), data=data, inputs=inputs,
                                  outputs=outputs, on_launch=block.get("on_launch"), block_type=block.get("type"))
        for l in j["liaisons"]:
            try:
                b_from = self.blocks[l.get("from")]
                b_to = self.blocks[l.get("to")]
                self.connect(b_from, b_to, l.get("old_name", None), l.get("new_name", None))
            except Exception as e:
                print("Can't create liaison")
                pass
