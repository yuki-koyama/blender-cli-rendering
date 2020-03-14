# blender --background --python 02_suzanne.py --render-frame 1 -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils


def set_scene_objects() -> bpy.types.Object:
    num_suzannes = 15
    for index in range(num_suzannes):
        utils.create_smooth_monkey(location=((index - (num_suzannes - 1) / 2) * 3.0, 0.0, 0.0),
                                   name="Suzanne" + str(index))
    return bpy.data.objects["Suzanne" + str(int((num_suzannes - 1) / 2))]


# Args
output_file_path = str(sys.argv[sys.argv.index('--') + 1])
resolution_percentage = int(sys.argv[sys.argv.index('--') + 2])
num_samples = int(sys.argv[sys.argv.index('--') + 3])

# Scene Building

## Reset
utils.clean_objects()

## Suzannes
center_suzanne = set_scene_objects()

## Camera
camera_object = utils.create_camera(location=(10.0, -7.0, 0.0))

utils.add_track_to_constraint(camera_object, center_suzanne)
utils.set_camera_params(camera_object.data, center_suzanne, lens=50.0)

## Lights
utils.create_sun_light(rotation=(0.0, math.pi * 0.5, -math.pi * 0.1))

# Render Setting
scene = bpy.data.scenes["Scene"]
utils.set_output_properties(scene, resolution_percentage, output_file_path)
utils.set_cycles_renderer(scene, camera_object, num_samples)
