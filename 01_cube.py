# blender --background --python 01_cube.py --render-frame 1 -- </path/to/output/image> <resolution_percentage>

import bpy
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils


def get_output_file_path() -> str:
    return str(sys.argv[sys.argv.index('--') + 1])


def get_resolution_percentage() -> int:
    return int(sys.argv[sys.argv.index('--') + 2])


def get_num_samples() -> int:
    return int(sys.argv[sys.argv.index('--') + 3])


if __name__ == "__main__":
    # Args
    output_file_path = get_output_file_path()
    resolution_percentage = get_resolution_percentage()
    num_samples = get_num_samples()

    # Setting
    scene = bpy.context.scene
    camera_object = bpy.data.objects["Camera"]
    utils.set_output_properties(scene, resolution_percentage, output_file_path)
    utils.set_cycles_renderer(scene, camera_object, num_samples)
