# blender --background --python 02_suzanne.py -- </path/to/output/image> <resolution_percentage>

import bpy
import sys
import math

# Functions

def reset_scene():
	for item in bpy.data.objects:
		bpy.data.objects.remove(item)

def apply_subdivision_surface(target, level):
	bpy.context.scene.objects.active = target
	bpy.ops.object.modifier_add(type='SUBSURF')
	bpy.context.object.modifiers["Subsurf"].levels = level
	bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")

def set_scene_objects():
	num_suzannes = 15
	for index in range(num_suzannes):
		bpy.ops.mesh.primitive_monkey_add(location=((index - (num_suzannes - 1) / 2) * 3.0, 0.0, 0.0))
		current_object = bpy.context.object
		current_object.name = "Suzanne" + str(index)
		apply_subdivision_surface(current_object, 3)
	return bpy.data.objects["Suzanne" + str(int((num_suzannes - 1) / 2))]

def set_camera_params(camera, dof_target):
	camera.data.sensor_fit = 'HORIZONTAL'
	camera.data.sensor_width = 36.0
	camera.data.lens = 50
	camera.data.dof_object = dof_target
	camera.data.cycles.aperture_type = 'FSTOP'
	camera.data.cycles.aperture_fstop = 1.2

def set_camera_lookat_target(camera, lookat_target):
	bpy.context.scene.objects.active = camera
	bpy.ops.object.constraint_add(type='TRACK_TO')
	camera.constraints["Track To"].target = lookat_target
	camera.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
	camera.constraints["Track To"].up_axis = 'UP_Y'

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

set_camera_lookat_target(camera, center_suzanne)
set_camera_params(camera, center_suzanne)

## Lights

bpy.ops.object.lamp_add(type='SUN', location=[0.0, 0.0, 0.0], rotation=[0.0, math.pi * 0.5, - math.pi * 0.1])

# Render Setting

scene = bpy.data.scenes["Scene"]
set_scene_renderer(scene, resolution_percentage, output_file_path, camera)

# Rendering

bpy.ops.render.render(animation=False, write_still=True)
