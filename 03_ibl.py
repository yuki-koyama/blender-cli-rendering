# blender --background --python 03_ibl.py -- </path/to/output/image> <resolution_percentage>

import bpy
import sys
import math

# Functions

def reset_scene():
	for item in bpy.data.objects:
		bpy.data.objects.remove(item)

def add_subdivision_surface_modifier(target_object, level):
	modifier = target_object.modifiers.new(name="Subsurf", type='SUBSURF')
	modifier.levels = level
	modifier.render_levels = level

def set_scene_objects():
	num_suzannes = 7
	for index in range(num_suzannes):
		bpy.ops.mesh.primitive_monkey_add(location=((index - (num_suzannes - 1) / 2) * 3.0, 0.0, 1.0))
		current_object = bpy.context.object
		current_object.name = "Suzanne" + str(index)
		add_subdivision_surface_modifier(current_object, 3)
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

def set_camera_lookat_target(camera, lookat_target):
	bpy.context.scene.objects.active = camera
	bpy.ops.object.constraint_add(type='TRACK_TO')
	camera.constraints["Track To"].target = lookat_target
	camera.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
	camera.constraints["Track To"].up_axis = 'UP_Y'

def set_background_light(world, hdri_path):
	world.use_nodes = True
	node_tree = world.node_tree
	environment_texture_node = node_tree.nodes.new(type="ShaderNodeTexEnvironment")
	environment_texture_node.image = bpy.data.images.load(hdri_path)
	node_tree.links.new(environment_texture_node.outputs["Color"], node_tree.nodes["Background"].inputs["Color"])

def set_scene_renderer(scene, resolution_percentage, output_file_path, camera, num_samples):
	scene.render.image_settings.file_format = 'PNG'
	scene.render.resolution_percentage = resolution_percentage
	scene.render.engine = 'CYCLES'
	scene.render.filepath = output_file_path
	scene.render.use_freestyle = False
	scene.cycles.samples = num_samples
	scene.camera = camera

# Args

output_file_path = str(sys.argv[sys.argv.index('--') + 1])
resolution_percentage = int(sys.argv[sys.argv.index('--') + 2])

# Parameters

num_samples = 512
hdri_path = "./assets/HDRIs/green_point_park_2k.hdr"

# Scene Building

scene = bpy.data.scenes["Scene"]
world = scene.world

## Reset

reset_scene()

## Suzannes

center_suzanne = set_scene_objects()

## Camera

bpy.ops.object.camera_add(view_align=False, location=[6.0, - 12.0, 2.0])
camera = bpy.context.object

set_camera_lookat_target(camera, center_suzanne)
set_camera_params(camera, center_suzanne)

## Lights

set_background_light(world, hdri_path)

# Render Setting

set_scene_renderer(scene, resolution_percentage, output_file_path, camera, num_samples)

# Rendering

bpy.ops.render.render(animation=False, write_still=True)
