import os

import numpy as np
from PIL import Image

prefix = "resources/ampis/"
images = [fn for fn in os.listdir(prefix) if fn[-4:] in [".png", ".PNG"]]

all_img_data = np.zeros((1080, 1920, 3), np.float)

for img in images:
    img_data = np.asarray(Image.open(prefix + img))

    # drop the alpha channel if present cause images from ubi photo site lack it :(
    if img_data.shape[2] == 4:
        img_data = img_data[:, :, :3]

    all_img_data += (img_data / len(images))

all_img_data = np.array(np.round(all_img_data), dtype=np.uint8)

result = Image.fromarray(all_img_data)
result.save("ampis.png")

result.show()
