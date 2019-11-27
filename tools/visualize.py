import numpy as np
from PIL import Image


def hex_to_rgb(hex_str):
    hex_str = hex_str.strip()

    if hex_str[0] == '#':
        hex_str = hex_str[1:]

    if len(hex_str) != 6:
        raise ValueError('Input #{} is not in #RRGGBB format.'.format(hex_str))

    r, g, b = hex_str[:2], hex_str[2:4], hex_str[4:]
    rgb = [int(n, base=16) for n in [r, g, b]]
    return np.array(rgb)


def binary_mask(crop_mask, palette):
    bin_mask = []
    for x in crop_mask:
        temp = []
        for y in x:
            crop = 0
            for i, ch in enumerate(y):
                if ch >= y[crop]:
                    crop = i
            temp.append(hex_to_rgb(palette[crop]))
        bin_mask.append(temp)
    return np.array(bin_mask, dtype=np.uint8)


def read_png(file):
    image = Image.open(file)
    return np.array(image)
