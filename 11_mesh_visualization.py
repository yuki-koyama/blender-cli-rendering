# blender --background --python 11_mesh_visualization.py -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.getcwd())

import utils

def set_scene_objects():
	bpy.ops.mesh.primitive_ico_sphere_add()
	current_object = bpy.context.object
	mat = bpy.data.materials.new("Material_Visualization")
	mat.use_nodes = True
	utils.clean_nodes(mat.node_tree.nodes)
	current_object.data.materials.append(mat)

	output_node = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
	principled_node = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
	mat.node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

	bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
	focus_target = bpy.context.object

	return focus_target

def set_camera_params(camera, dof_target):
	camera.data.sensor_fit = 'HORIZONTAL'
	camera.data.sensor_width = 36.0
	camera.data.sensor_height = 24.0
	camera.data.lens = 72
	camera.data.dof_object = dof_target
	camera.data.cycles.aperture_type = 'RADIUS'
	camera.data.cycles.aperture_size = 0.100
	camera.data.cycles.aperture_blades = 6

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

## Object
focus_target = set_scene_objects()

## Camera
bpy.ops.object.camera_add(view_align=False, location=[0.0, - 10.0, 0.0])
camera = bpy.context.object

utils.add_track_to_constraint(camera, focus_target)
set_camera_params(camera, focus_target)

## Lights
utils.build_environmental_light(world, hdri_path)

# Render Setting
utils.set_cycles_renderer(scene, resolution_percentage, output_file_path, camera, num_samples, use_denoising=True, use_transparent_bg=True)

# Render
bpy.ops.render.render(animation=False, write_still=True)
