"""
Project : lard
File : test
Author : DELEVACQ Wallerand
Date : 18/02/19
"""
from lard_library.pipeline import Pipeline

if __name__ == "__main__":
    p = Pipeline("Nom du Pipeline")

    code = """
import cv2
def main(data):
    return {"image": cv2.imread(data.get("image_path"))}
"""
    data = {"image_path": "shark.png"}

    code = compile(code, "<string>", "exec")

    p.create_block(code, "Hello", data, {}, {}, True)


    print(p.launch())
