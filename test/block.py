"""
Project : lard
File : block
Author : DELEVACQ Wallerand
Date : 08/12/18
"""
import abc
import copy
import cv2
import json
import matplotlib.pyplot as plt
import numpy as np
import pickle

# Ignore warning matplotlib
import warnings

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

    def __init__(self, name="Block", block_inputs=dict(), block_outputs=dict(), data={}, on_launch=False):
        self.on_launch = on_launch
        self.name = name
        self._data = data
        self.inputs_dict = block_inputs
        self.outputs_dict = block_outputs
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

        liaison = Liaison(self.name + " to " + block.name, data=names)
        self.attach(liaison)
        liaison.attach(block)

        g_from.append(self.name)
        g_to.append(block.name)

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
        self.data.update(data)

        _data_ready = copy.deepcopy(self.inputs_dict)
        _data_ready = set_dict_to_value(_data_ready, None)

        self._data_ready = {**_data_ready, **self.data}
        if not self.is_ready():
            print(self.name + " Not ready")
        else:
            self.subject_outputs = self.treatment(self.data)

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
        _data_ready = copy.deepcopy(self.inputs_dict)
        _data_ready = set_dict_to_value(_data_ready, None)
        _data_ready.update(self.data)
        self._data_ready = _data_ready

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
        next = []
        for o in self._observers:
            next.append(o._data)

        dumped_data = {
            "name": self.name,
            "on_launch": self.on_launch,
            "type": str(self.__class__.__name__),
            "data": self.data,
            "inputs": self.inputs_dict,
            "ouputs": self.outputs_dict,
            "data_ready": self.data_ready}
            #"next": next}
        return dumped_data

    @staticmethod
    def instanciate(j={}):
        blocks = {}
        for block_name in j["blocks"]:
            block = j["blocks"][block_name]
            b = globals()[block.get("type")](block.get("name"), block_inputs=block.get("inputs"),
                                             block_outputs=block.get("outputs"), data=block.get("data_ready"), on_launch=block.get("on_launch"))

            blocks[block.get("name")] = b
        for l in j["liaisons"]:
            try:
                b_from = blocks[l.get("from")]
                b_to = blocks[l.get("to")]
                b_from.connect_to(b_to, l.get("input", None), l.get("output", None))
            except:
                pass

        return blocks

    @staticmethod
    def load(filename="dump.json"):
        """
        Load blocks from json
        :param filename: string
        """
        with open(filename, mode="rb") as f:
            return json.load(f)

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

class BlockEncoder(json.JSONEncoder):
    def default(self, obj):
        if issubclass(type(obj), Block):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)


class Image(Block):
    def treatment(self, data={}):
        image = cv2.imread(data.get("image_path"))
        return {"image": image}


## Pas changé
class Camera(Block):
    def treatment(self, data=dict()):
        # self.subject_outputs = {"image": "camera_image"}
        self.subject_outputs = data
        print("inputs : " + str(data))
        print("outputs : " + str(self.subject_outputs))
        print()
        return {"block_name": self.name, "inputs": data, "outputs": self.subject_outputs}


class Blur(Block):
    def treatment(self, data={}):
        image = data.get("image")
        ksize = data.get("ksize")
        blured_image = cv2.medianBlur(image, ksize)
        return {"image": blured_image}


class Gradient(Block):
    def treatment(self, data={}):
        image = data.get("image")
        gradient_image = cv2.convertScaleAbs(cv2.Laplacian(image, cv2.CV_64F))
        return {"image": gradient_image}


class Invert(Block):
    def treatment(self, data={}):
        image = data.get("image")
        result = cv2.bitwise_not(image)
        return {"image": result}


class Liaison(Block):
    def treatment(self, data={}):
        # inputs = {**inputs, **self.data.get("inputs")}
        old_name = data.get("old_name")
        new_name = data.get("new_name")
        data = copy.deepcopy(data)
        if old_name and new_name:
            if old_name != new_name:
                print(old_name + " --> " + new_name)
                data[new_name] = data[old_name]
                del data[old_name]
        return data


class Display(Block):
    image_name = "image"

    def treatment(self, data={}):
        image = data.get(self.image_name)

        if image is not None:
            show_images([image], self.name, False)
        else:
            print("No image in " + self.name)


class Display2(Display):
    image_name = "image2"


class Mask(Block):
    def treatment(self, data={}):
        color = data.get("color")
        amplitude = data.get("amplitude")
        low_threshold = data.get("low_threshold")

        type = data.get("type")

        image = data.get("image")
        if image is None:
            return

        if type == "grey":
            res = self.get_mask_grey(image, color, amplitude, low_threshold)
        elif type == "grey_inverted":
            res = self.get_mask_grey_inverted(image, color, amplitude, low_threshold)
        else:
            res = self.get_mask(image, color, amplitude, low_threshold)

        return {"mask": res}

    def get_mask(self, image, color, amplitude, low_threshold):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # define range of blue color in HSV
        color_hsv = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_RGB2HSV)

        lower_blue = np.array([color_hsv[0][0][0] - amplitude, low_threshold, low_threshold])
        upper_blue = np.array([color_hsv[0][0][0] + amplitude, 255, 255])
        # Threshold the HSV image to get only blue colors
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(image, image, mask=mask)
        return res

    def get_mask_grey(self, image, color, amplitude, low_threshold):
        mask = self.get_mask(image, color, amplitude, low_threshold)
        mask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
        ret, mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)
        return mask

    def get_mask_grey_inverted(self, image, color, amplitude, low_threshold):
        mask = self.get_mask_grey(image, color, amplitude, low_threshold)
        mask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
        mask_inv = cv2.bitwise_not(mask)
        return mask_inv


class SuppressWithMask(Block):
    def treatment(self, data={}):
        image = data.get("image")
        mask = data.get("mask")
        res = cv2.bitwise_and(image, image, mask=cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY))
        return {"image": res}


class Inpaint(Block):
    def treatment(self, data={}):
        img = data.get("image")
        mask = data.get("mask")
        radius = data.get("radius")
        method = data.get("method")
        mask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
        dst = cv2.inpaint(img, mask, radius, method)
        return {"image": dst}


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
        cv2.waitKey()


def draw_graph(v_from, v_to, spectral=False):
    import networkx as nx
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

if __name__ == "__main__":
    global g_from
    global g_to
    g_from = []
    g_to = []

    # Define datas
    image_data = {"image_path": "shark.png"}
    blur_data = {"ksize": 21}
    mask_data = {"color": [45, 175, 230], "amplitude": 10, "low_threshold": 50, "type": "default"}
    mask_grey_data = {"color": [45, 175, 230], "amplitude": 10, "low_threshold": 50, "type": "grey"}
    mask_grey_inverted_data = {"color": [45, 175, 230], "amplitude": 10, "low_threshold": 50, "type": "grey_inverted"}
    suppress_with_mask_data = {}

    # Define blocks
    blockImage = Image("IMAGE", block_inputs={"image_path": "string"}, block_outputs={"image": "image"}, on_launch=True)

    blockBlur = Blur("BLUR", block_inputs={"image": "image"})
    blockGradient = Gradient("GRADIENT", block_inputs={"image": "image"})

    blockDisplay = Display("DISPLAY", block_inputs={"image": "image"})
    blockDisplay2 = Display2("DISPLAY 2", block_inputs={"image2": "image"})

    blockMask = Mask("MASK", block_inputs={"image": "image"})
    blockMaskGrey = Mask("MASK GREY", block_inputs={"image": "image"})
    blockMaskGreyInverted = Mask("MASK GREY INVERTED", block_inputs={"image": "image"})

    blockSuppressWithMask = SuppressWithMask("SUPPRESS WITH MASK", block_inputs={"image": "image", "mask": "mask"})
    blockInpainting = Inpaint("INPAINT", block_inputs={"mask": "image", "image": "image"},
                              data={"radius": 200, "method": cv2.INPAINT_TELEA})

    blockInvert = Invert("INVERT", block_inputs={"image": "image"})

    # Set data
    blockImage.data = image_data
    blockBlur.data = blur_data
    blockMask.data = mask_data
    blockMaskGrey.data = mask_grey_data
    blockMaskGreyInverted.data = mask_grey_inverted_data
    blockSuppressWithMask.data = suppress_with_mask_data

    # Démo d'inpainting
    """
    imP = Image("PEOPLE", block_inputs={"image_path": "string"}, block_outputs={"image": "image"}, data={"image_path": "picture.png"})
    imP2 = Image("PEOPLE2", block_inputs={"image_path": "string"}, block_outputs={"image": "image"}, data={"image_path": "picture2.png"})
    imP.connect_to(blockDisplay)
    imP.connect_to(blockInpainting)
    imP2.connect_to(blockInpainting, "image", "mask")
    blockInpainting.connect_to(blockDisplay)
    imP._treat()
    imP2._treat()
    #"""

    # Démo de récupération de mask et de suppression avec
    """
    blockImage.connect_to(blockSuppressWithMask)
    blockImage.connect_to(blockMaskGreyInverted)
    blockMaskGreyInverted.connect_to(blockSuppressWithMask)
    blockImage.connect_to(blockDisplay)
    blockSuppressWithMask.connect_to(blockDisplay)
    #blockImage._treat()
    #"""

    # Save list of blocks
    """
    Block.dump([blockImage, blockMaskGreyInverted, blockSuppressWithMask, blockDisplay])
    #"""

    # Load list of block and re-instanciate
    """
    b = Block.load_and_instanciate()
    Block.launch_all([b[name] for name in b])
    # """

    # Draw Graph
    draw_graph(g_from, g_to)

    print("End")
