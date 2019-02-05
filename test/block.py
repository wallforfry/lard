"""
Project : lard
File : block
Author : DELEVACQ Wallerand
Date : 08/12/18
"""
import abc
import copy
import cv2
import matplotlib.pyplot as plt
import numpy as np


class Subject:
    """
    Know its observers. Any number of Observer objects may observe a
    subject.
    Send a notification to its observers when its state changes.
    """

    def __init__(self):
        self._observers = set()
        self._subject_outputs = None

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
    Implement the Observer updating interface to keep its state
    consistent with the subject's.
    Store state that should stay consistent with the subject's.
    """

    def __init__(self, name="Block", block_inputs=dict(), block_outputs=dict()):
        self.name = name
        self.data = {"inputs": {}, "outputs": {}}
        self.inputs_dict = block_inputs
        self.outputs_dict = block_outputs
        self._data_ready = {"inputs": {}, "outputs": {}}
        super().__init__()

    def update(self, inputs):
        self._observer_inputs = inputs
        self.treat(inputs)

    def attach(self, observer):
        super().attach(observer)
        g_from.append(self.name)
        g_to.append(observer.name)

    def detach(self, observer):
        super().detach(observer)
        for f,t,i in zip(g_from, g_to, range(0, len(g_from))):
            if self.name == f and observer.name == t:
                #g_from.pop(i)
                g_to[i] = None

    @abc.abstractmethod
    def treat(self, data=dict()):
        pass

    def is_ready(self):
        self._is_ready(self._data_ready)

    def _is_ready(self, d):
        for k, v in d.items():
            if isinstance(v, dict):
                self._is_ready(v)
            else:
                return d[k] is True
        return True

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, arg):
        self._data = arg
        self._data_ready = copy.deepcopy(self._data)
        self._data_ready = set_dict_to_value(self._data_ready.copy(), False)

    @property
    def data_ready(self):
        return self._data_ready

class Image(Block):
    def treat(self, data=dict()):
        #print(self.is_ready())
        inputs = data.get("inputs")
        inputs = {**inputs, **self.data.get("inputs")}
        image = cv2.imread(inputs.get("image_path"))
        self.subject_outputs = {**data, "outputs": {"image": image}}


class Camera(Block):
    def treat(self, data=dict()):
        # self.subject_outputs = {"image": "camera_image"}
        self.subject_outputs = data
        print("inputs : " + str(data))
        print("outputs : " + str(self.subject_outputs))
        print()
        return {"block_name": self.name, "inputs": data, "outputs": self.subject_outputs}


class Blur(Block):
    def treat(self, data=dict()):
        inputs = data.get("outputs")
        inputs = {**inputs, **self.data.get("inputs")}
        image = inputs.get("image")
        ksize = inputs.get("ksize")
        blured_image = cv2.medianBlur(image, ksize)
        self.subject_outputs = {**data, "outputs": {"image": blured_image}}


class Gradient(Block):
    def treat(self, data=dict()):
        inputs = data.get("outputs")
        inputs = {**inputs, **self.data.get("inputs")}
        image = inputs.get("image")
        gradient_image = cv2.convertScaleAbs(cv2.Laplacian(image, cv2.CV_64F))
        self.subject_outputs = {"inputs": inputs, "outputs": {"image": gradient_image}}

class Liaison(Block):
    def treat(self, data=dict()):
        inputs = data.get("outputs")
        inputs = {**inputs, **self.data.get("inputs")}
        old_name = inputs.get("old_name")
        new_name = inputs.get("new_name")
        self.subject_outputs = {**data, "outputs": {new_name: inputs.get(old_name)}}
        print(self.subject_outputs)


class Display(Block):
    def treat(self, data=dict()):
        image = data.get("outputs").get("image")
        show_images([image], False)

class Display2(Block):
    def treat(self, data=dict()):
        image = data.get("outputs").get("image2")
        print(data.get("outputs").get("image2"))
        show_images([image], False)

class Mask(Block):
    def treat(self, data=dict()):
        inputs = data.get("outputs")
        inputs = {**inputs, **self.data.get("inputs")}
        color = inputs.get("color")
        amplitude = inputs.get("amplitude")
        low_threshold = inputs.get("low_threshold")

        type = inputs.get("type")

        if type == "grey":
            image = inputs.get("mask")
            res = self.get_mask_grey(image, color, amplitude, low_threshold)
        elif type == "grey_inverted":
            image = inputs.get("mask")
            res = self.get_mask_grey_inverted(image, color, amplitude, low_threshold)
        else:
            image = inputs.get("image")
            res = self.get_mask(image, color, amplitude, low_threshold)

        self.subject_outputs = {"inputs": inputs, "outputs": {"mask": res}}

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
    def treat(self, data=dict()):
        inputs = data.get("outputs")
        self.data = {"inputs": {**inputs, **self.data.get("inputs")}}
        #TODO: réussir à lier plusieurs entrées ...

        if None in self.data:
            return
        image = self.data.get("image")
        mask = self.data.get("mask")
        res = cv2.bitwise_and(image, image, mask=cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY))
        self.subject_outputs = {"inputs": inputs, "outputs": {"image": res}}


def show_images(images, cv=False):
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
                plt.title("Source"), plt.xticks([]), plt.yticks([])
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
        nx.draw(G, with_labels=True, node_size=2000, node_color="skyblue", node_shape="s")
    plt.show()

def set_dict_to_value(d, value):
    for k, v in d.items():
        if isinstance(v, dict):
            set_dict_to_value(v, value)
        else:
            d[k] = value
    return d


if __name__ == "__main__":
    global g_from
    global g_to
    g_from = []
    g_to = []

    #Define datas
    image_data = {"inputs": {"image_path": "shark.png"}}
    blur_data = {"inputs": {"ksize": 21}}
    mask_data = {"inputs": {"color": [45, 175, 230], "amplitude": 10, "low_threshold": 50, "type": "default"}}
    mask_grey_data = {"inputs": {"color": [45, 175, 230], "amplitude": 10, "low_threshold": 50, "type": "grey"}}
    mask_grey_inverted_data = {"inputs": {"color": [45, 175, 230], "amplitude": 10, "low_threshold": 50, "type": "grey_inverted"}}
    suppress_with_mask_data = {"inputs": {}, "outputs": {}}

    #Define blocks
    blockImage = Image("IMAGE")
    blockGradient = Gradient("GRADIENT")
    blockDisplay = Display("DISPLAY")
    blockBlur = Blur("BLUR")
    blockMask = Mask("MASK")
    blockMaskGrey = Mask("MASK GREY")
    blockMaskGreyInverted = Mask("MASK GREY INVERTED")
    blockSuppressWithMask = SuppressWithMask("SUPPRESS WITH MASK")

    blockLiaison = Liaison("LIAISON")
    blockLiaison.data = {"inputs": {"old_name": "image", "new_name": "image2"}, "outputs": {}}
    blockDisplay2 = Display2("DISPLAY 2")

    #Set data
    #blockImage.data = image_data
    blockBlur.data = blur_data
    blockMask.data = mask_data
    blockMaskGrey.data = mask_grey_data
    blockMaskGreyInverted.data = mask_grey_inverted_data
    blockSuppressWithMask.data = suppress_with_mask_data

    blockImage.attach(blockDisplay)

    blockImage.attach(blockGradient)
    blockGradient.attach(blockDisplay)

    blockImage.attach(blockLiaison)
    blockLiaison.attach(blockDisplay2)

    #blockImage.attach(blockBlur)
    #blockBlur.attach(blockDisplay)


    #Link blocks
    #blockImage.attach(blockDisplay)
    #blockMask.attach(blockMaskGrey)
    #blockMaskGrey.attach(blockMaskGreyInverted)
    #blockMaskGreyInverted.attach(blockSuppressWithMask)
    #blockSuppressWithMask.attach(blockDisplay)

    draw_graph(g_from, g_to)
    blockImage.treat(image_data)
    print("End")
