# blender --background --python 01_cube.py -- </path/to/output/image> <resolution_percentage>

import bpy
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils


def get_output_file_path() -> str:
    return str(sys.argv[sys.argv.index('--') + 1])


def get_resolution_percentage() -> int:
    return int(sys.argv[sys.argv.index('--') + 2])


if __name__ == "__main__":
    # Args
    output_file_path = get_output_file_path()
    resolution_percentage = get_resolution_percentage()

    # Setting
    default_scene = bpy.context.scene
    default_camera_object = bpy.data.objects["Camera"]
    num_samples = 32
    utils.set_cycles_renderer(default_scene, resolution_percentage, output_file_path, default_camera_object,
                              num_samples)

    # Rendering
    bpy.ops.render.render(animation=False, write_still=True)
