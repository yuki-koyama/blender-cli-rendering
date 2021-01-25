import bpy
import numpy as np


def get_image_pixels_in_numpy(image: bpy.types.Image) -> np.array:
    return np.array(image.pixels[:]).reshape(image.size[0] * image.size[1], image.channels)


def set_image_pixels_in_numpy(image: bpy.types.Image, pixels: np.array) -> None:
    # The sizes should be the same; otherwise, Blender may crush.
    assert len(image.pixels) == pixels.size

    image.pixels = pixels.flatten()
