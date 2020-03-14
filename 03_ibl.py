# blender --background --python 03_ibl.py --render-frame 1 -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils


def set_scene_objects() -> bpy.types.Object:
    num_suzannes = 7
    for index in range(num_suzannes):
        utils.create_smooth_monkey(location=((index - (num_suzannes - 1) / 2) * 2.8, 0.0, 1.0),
                                   name="Suzanne" + str(index))

    utils.create_plane(size=20.0)

    return bpy.data.objects["Suzanne" + str(int((num_suzannes - 1) / 2))]


# Args
output_file_path = str(sys.argv[sys.argv.index('--') + 1])
resolution_percentage = int(sys.argv[sys.argv.index('--') + 2])
num_samples = int(sys.argv[sys.argv.index('--') + 3])

# Parameters
hdri_path = "./assets/HDRIs/green_point_park_2k.hdr"

# Scene Building
scene = bpy.data.scenes["Scene"]
world = scene.world

## Reset
utils.clean_objects()

## Suzannes
center_suzanne = set_scene_objects()

## Camera
bpy.ops.object.camera_add(location=(5.0, -10.0, 2.0))
camera_object = bpy.context.object

utils.add_track_to_constraint(camera_object, center_suzanne)
utils.set_camera_params(camera_object.data, center_suzanne, lens=50, fstop=0.2)

## Lights
utils.build_environment_texture_background(world, hdri_path)

# Render Setting
utils.set_output_properties(scene, resolution_percentage, output_file_path)
utils.set_cycles_renderer(scene, camera_object, num_samples)
