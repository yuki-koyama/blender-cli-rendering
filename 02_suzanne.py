# blender --background --python 02_suzanne.py -- </path/to/output/image> <resolution_percentage>

import bpy
import sys
import math
import os

sys.path.append(os.getcwd())

import utils

def reset_scene():
	for item in bpy.data.objects:
		bpy.data.objects.remove(item)

def set_scene_objects():
	num_suzannes = 15
	for index in range(num_suzannes):
		bpy.ops.mesh.primitive_monkey_add(location=((index - (num_suzannes - 1) / 2) * 3.0, 0.0, 0.0))
		current_object = bpy.context.object
		current_object.name = "Suzanne" + str(index)
		utils.add_subdivision_surface_modifier(current_object, 3)
	return bpy.data.objects["Suzanne" + str(int((num_suzannes - 1) / 2))]

def set_camera_params(camera, dof_target):
	camera.data.sensor_fit = 'HORIZONTAL'
	camera.data.sensor_width = 36.0
	camera.data.lens = 50
	camera.data.dof_object = dof_target
	camera.data.cycles.aperture_type = 'FSTOP'
	camera.data.cycles.aperture_fstop = 1.2

def set_scene_renderer(scene, resolution_percentage, output_file_path, camera):
	scene.render.image_settings.file_format = 'PNG'
	scene.render.resolution_percentage = resolution_percentage
	scene.render.engine = 'CYCLES'
	scene.render.filepath = output_file_path
	scene.render.use_freestyle = False
	scene.camera = camera

# Args

output_file_path = str(sys.argv[sys.argv.index('--') + 1])
resolution_percentage = int(sys.argv[sys.argv.index('--') + 2])

# Scene Building

## Reset

reset_scene()

## Suzannes

center_suzanne = set_scene_objects()

## Camera

bpy.ops.object.camera_add(view_align=False, location=[10.0, - 7.0, 0.0])
camera = bpy.context.object

utils.add_track_to_constraint(camera, center_suzanne)
set_camera_params(camera, center_suzanne)

## Lights

bpy.ops.object.lamp_add(type='SUN', location=[0.0, 0.0, 0.0], rotation=[0.0, math.pi * 0.5, - math.pi * 0.1])

# Render Setting

scene = bpy.data.scenes["Scene"]
set_scene_renderer(scene, resolution_percentage, output_file_path, camera)

# Rendering

bpy.ops.render.render(animation=False, write_still=True)
