# blender --background --python 03_ibl.py -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.getcwd())

import utils


def set_scene_objects():
    num_suzannes = 7
    for index in range(num_suzannes):
        bpy.ops.mesh.primitive_monkey_add(location=((index - (num_suzannes - 1) / 2) * 3.0, 0.0, 1.0))
        current_object = bpy.context.object
        current_object.name = "Suzanne" + str(index)
        utils.set_smooth_shading(current_object)
        utils.add_subdivision_surface_modifier(current_object, 3)
    bpy.ops.mesh.primitive_plane_add(radius=10.0)
    return bpy.data.objects["Suzanne" + str(int((num_suzannes - 1) / 2))]


def set_camera_params(camera, dof_target):
    camera.data.sensor_fit = 'HORIZONTAL'
    camera.data.sensor_width = 36.0
    camera.data.sensor_height = 24.0
    camera.data.lens = 50
    camera.data.dof_object = dof_target
    camera.data.cycles.aperture_type = 'RADIUS'
    camera.data.cycles.aperture_size = 0.2


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
bpy.ops.object.camera_add(view_align=False, location=[6.0, -12.0, 2.0])
camera = bpy.context.object

utils.add_track_to_constraint(camera, center_suzanne)
set_camera_params(camera, center_suzanne)

## Lights
utils.build_environmental_light(world, hdri_path)

# Render Setting
utils.set_cycles_renderer(scene, resolution_percentage, output_file_path, camera, num_samples)

# Rendering
bpy.ops.render.render(animation=False, write_still=True)
