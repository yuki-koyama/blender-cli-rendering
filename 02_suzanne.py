# blender --background --python 02_suzanne.py -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils


def set_scene_objects():
    num_suzannes = 15
    for index in range(num_suzannes):
        utils.create_smooth_monkey(location=((index - (num_suzannes - 1) / 2) * 3.0, 0.0, 0.0),
                                   name="Suzanne" + str(index))
    return bpy.data.objects["Suzanne" + str(int((num_suzannes - 1) / 2))]


def set_camera_params(camera, dof_target):
    camera.data.sensor_fit = 'HORIZONTAL'
    camera.data.sensor_width = 36.0
    camera.data.lens = 50
    camera.data.dof_object = dof_target
    camera.data.cycles.aperture_type = 'FSTOP'
    camera.data.cycles.aperture_fstop = 1.2


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
bpy.ops.object.camera_add(view_align=False, location=[10.0, -7.0, 0.0])
camera = bpy.context.object

utils.add_track_to_constraint(camera, center_suzanne)
set_camera_params(camera, center_suzanne)

## Lights
bpy.ops.object.lamp_add(type='SUN', location=[0.0, 0.0, 0.0], rotation=[0.0, math.pi * 0.5, -math.pi * 0.1])

# Render Setting
scene = bpy.data.scenes["Scene"]
utils.set_cycles_renderer(scene, resolution_percentage, output_file_path, camera, num_samples)

# Rendering
bpy.ops.render.render(animation=False, write_still=True)
