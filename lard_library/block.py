"""
Project : lard
File : block
Author : DELEVACQ Wallerand
Date : 18/02/19
"""
import abc
import copy
import cv2
import json
import matplotlib.pyplot as plt
import numpy as np
import click
import networkx as nx

# Ignore warning matplotlib
import warnings

# Outputs Settings
OUTPUT_BLOCK_TYPE = ["OUTPUT", "Output"]
OUTPUT_BLOCK_OUTPUT_NAME = ["output"]

warnings.filterwarnings(
    action='ignore', module='matplotlib.figure', category=UserWarning,
    message=('This figure includes Axes that are not compatible with tight_layout, '
             'so results might be incorrect.')
)


class Subject:
    """
    Know its observers. Any number of Observer objects may observe a
    subject.
    Send a notification to its observers when its state changes.
    """

    def __init__(self):
        self._observers = set()
        self._subject_outputs = {}

    def attach(self, observer):
        observer._subject = self
        self._observers.add(observer)

    def detach(self, observer):
        if observer not in self._observers:
            raise Exception("Observer is not registered")
        observer._subject = None
        self._observers.discard(observer)

    def detach_all(self):
        for observer in set(self._observers):
            self.detach(observer)
        self._observers = set()

    def _notify(self):
        for observer in self._observers:
            observer.update(self._subject_outputs)

    @property
    def subject_outputs(self):
        return self._subject_outputs

    @subject_outputs.setter
    def subject_outputs(self, arg):
        self._subject_outputs = arg
        self._notify()


class Observer(metaclass=abc.ABCMeta):
    """
    Define an updating interface for objects that should be notified of
    changes in a subject.
    """

    def __init__(self):
        self._subject = None
        self._observer_inputs = None

    @abc.abstractmethod
    def update(self, arg):
        pass


class Block(Subject, Observer):
    """
    Implement Observer and Subject
    All Blocks must redefine treatment() method
    """
    blocks = []
    liaisons = []
    global g_from
    global g_to
    g_from = []
    g_to = []

    def __init__(self, name="Block", block_inputs=dict(), block_outputs=dict(), data={}, on_launch=False, block_type=None, pipeline=None):
        if block_type is None:
            self.type = str(self.__class__.__name__)
        else:
            self.type = block_type

        self.on_launch = on_launch
        self.name = name
        self._data = data
        self.inputs_dict = block_inputs
        self.outputs_dict = block_outputs
        self.pipeline = pipeline
        self._data_ready = set_dict_to_value(self.inputs_dict, None)
        super().__init__()
        if isinstance(self, Liaison):
            Block.liaisons.append(self)
        else:
            Block.blocks.append(self)

    def update(self, inputs):
        self._observer_inputs = inputs
        self._treat(inputs)

    def connect_to(self, block, output_name=None, input_name=None):
        """
        Use to connect a block to another
        :param block: Block to connect
        :param output_name: name of the output to connect
        :param input_name: name of the input to connect
        """
        names = {"from": self.name, "to": block.name}
        if output_name and input_name:
            names.update({"old_name": output_name, "new_name": input_name})

        liaison = Liaison(self.name + " to " + block.name, data=names, pipeline=self.pipeline)
        self.attach(liaison)
        liaison.attach(block)

        g_from.append(self.name)
        g_to.append(block.name)
        return liaison

    def attach(self, observer):
        super().attach(observer)

    def detach(self, observer):
        super().detach(observer)
        for f, t, i in zip(g_from, g_to, range(0, len(g_from))):
            if self.name == f and observer.name == t:
                # g_from.pop(i)
                g_to[i] = None

    def launch(self, data={}):
        """
        Use launch on initials blocks
        :param data:
        """
        self._treat(data)

    def _treat(self, data={}):
        for n in self.data:
            for m in self.data_ready:
                if n == m and self.data.get(n) is not None:
                    self.data_ready.update({n: self.data.get(n)})
        for n in data:
            for m in self.data_ready:
                if n == m and data.get(n) is not None:
                    self.data_ready.update({n: data.get(n)})
        if not self.is_ready():
            print(self.name + " Not ready")
        else:
            result = self.treatment(self.data_ready)
            self._data_ready = result

            for o in OUTPUT_BLOCK_OUTPUT_NAME:
                if o in result:
                    if result[o] is not None:
                        self.pipeline.outputs.append({"name": self.name, "value": result[o]})
                        if self.type in OUTPUT_BLOCK_TYPE:
                            self._data_ready = set_dict_to_value(self.inputs_dict, None)
            self.subject_outputs = result

    @abc.abstractmethod
    def treatment(self, data={}):
        pass

    def is_ready(self):
        """
        Check if all required datas are ready
        :return:
        """
        return self._is_ready(self._data_ready)

    def _is_ready(self, d):
        # Attention ne fonctionne pas en récursif pour le moment
        for k, v in d.items():
            if isinstance(v, dict):
                pass
                if not self._is_ready(v):
                    return False
            else:
                if d[k] is None:
                    return False
        return True

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, arg):
        self._data = arg

    @property
    def data_ready(self):
        return self._data_ready

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        """
        Serialize Block
        :return: dict()
        """

        dumped_data = {
            "name": self.name,
            "on_launch": self.on_launch,
            "type": self.type,
            "data": self.data,
            "inputs": self.inputs_dict,
            "outputs": self.outputs_dict,
            "data_ready": self.data_ready}
        # "next": next}
        return dumped_data

    @staticmethod
    def instanciate(j={}):
        blocks = {}
        for block_name in j["blocks"]:
            block = j["blocks"][block_name]
            b = globals()[block.get("type")](block.get("name"), block_inputs=block.get("inputs"),
                                             block_outputs=block.get("outputs"), data=block.get("data_ready"),
                                             on_launch=block.get("on_launch"))

            blocks[block.get("name")] = b
        for l in j["liaisons"]:
            try:
                b_from = blocks[l.get("from")]
                b_to = blocks[l.get("to")]
                b_from.connect_to(b_to, l.get("old_name", None), l.get("new_name", None))
            except:
                pass

        return blocks

    @staticmethod
    def load(filename="dump.json"):
        """
        Load blocks from json
        :param filename: string
        """
        with open(filename, mode="r") as f:
            return json.load(f)

    @staticmethod
    def write_cyto_graph(blocks_dict, graph_file_name="graph.json"):
        """
        Write a json repesentation of a cytoscape graph
        :param filename: string
        """
        cytoJSON = []
        blocks = blocks_dict.get("blocks")

        for key in blocks:
            block = blocks[key]
            data_dict = {"id": block.get("name"), "name": block.get("type")}
            node_dict = {"data": data_dict}
            cytoJSON.append(node_dict)

        liaisons = blocks_dict.get("liaisons")
        for liaison in liaisons:
            data_dict = {"source": liaison.get("from"), "target": liaison.get("to")}
            edge_dict = {"data": data_dict}
            cytoJSON.append(edge_dict)

        with open(graph_file_name, mode="w") as f:
            json.dump(cytoJSON, f, indent=4)
        return  cytoJSON

    @staticmethod
    def load_and_instanciate(filename="dump.json"):
        """
        Load blocks and instanciate
        :param filename: string
        :return: list(Block)
        """
        j = Block.load(filename)
        return Block.instanciate(j)

    @staticmethod
    def dump(blocks, filename="dump.json"):
        """
        Dump blocks to file
        :param blocks: list(blocks)
        :param filename: string
        """
        json_blocks = {b.name: b.to_dict() for b in blocks}
        json_liaisons = []
        for b in Block.liaisons:
            if b.data.get("from") in json_blocks and b.data.get("to") in json_blocks:
                json_liaisons.append(b.data)

        with open(filename, mode="w") as f:
            json.dump({"blocks": json_blocks, "liaisons": json_liaisons}, f, indent=4)

    @staticmethod
    def launch_all(blocks=[]):
        if not blocks:
            blocks = Block.blocks
        for b in blocks:
            if b.on_launch:
                b.launch()

        json_blocks = {b.name: b.to_dict() for b in blocks}
        json_liaisons = []
        for b in Block.liaisons:
            if b.data.get("from") in json_blocks and b.data.get("to") in json_blocks:
                json_liaisons.append(b.data)
        return {"blocks": json_blocks, "liaisons": json_liaisons}

def show_images(images, first_name="Source", cv=False):
    """
            Display list of images with matplotlib
            :type images: Array of cv2 image
            """
    if not cv:
        sqrt = np.sqrt(len(images))
        width = np.ceil(sqrt)
        height = np.ceil(len(images) / width)
        for image, i in zip(images, range(1, len(images) + 1)):
            plt.subplot(height, width, i)
            convert = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            plt.imshow(convert, cmap='gray')
            if i == 1:
                plt.title(first_name), plt.xticks([]), plt.yticks([])
            else:
                plt.title('Image ' + str(i - 1)), plt.xticks([]), plt.yticks([])

        plt.show()
    else:
        for image, i in zip(images, range(1, len(images) + 1)):
            if i == 1:
                cv2.imshow('Source', image)
            else:
                cv2.imshow('Image ' + str(i), image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            exit(0)


def draw_graph(v_from, v_to, spectral=False):
    G = nx.DiGraph()
    for f, t in zip(v_from, v_to):
        G.add_node(f)
        if t is not None:
            G.add_edge(f, t)
            G.add_node(t)
    if spectral:
        nx.draw_spectral(G, with_labels=True, node_size=2000, node_color="skyblue", node_shape="s")
    else:
        nx.draw_shell(G, with_labels=True, node_size=2000, node_color="skyblue", node_shape="s")
    plt.show()


def set_dict_to_value(d, value):
    d = copy.deepcopy(d)
    for k, v in d.items():
        if isinstance(v, dict):
            set_dict_to_value(v, value)
        else:
            d[k] = value
    return d


def find_block_in_blocks(name, blocks):
    for block in blocks:
        if name == block.name:
            return block
    return None


def find_block_by_type(type, blocks):
    result = []
    for block in blocks:
        if isinstance(type, list):
            if block.__class__.__name__ in type:
                result.append(block)
        else:
            if block.__class__.__name__ == type:
                result.append(block)
    return result


class Liaison(Block):
    def treatment(self, data={}):
        m = self.pipeline.mercure
        if m:
            m.send(json.dumps({"source": self._data.get("from", None), "target": self._data.get("to", None),
                               "old_name": self._data.get("old_name", None),
                               "new_name": self._data.get("new_name", None), "name": self.name}))
        data = self._observer_inputs
        old_name = data.get("old_name")
        new_name = data.get("new_name")
        data = copy.deepcopy(data)
        if old_name and new_name:
            if old_name != new_name:
                print(old_name + " --> " + new_name)
                data[new_name] = data[old_name]
                del data[old_name]
        return data
