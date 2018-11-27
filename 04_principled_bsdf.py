# blender --background --python 04_principled_bsdf.py -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math

# Functions

def reset_scene():
	for item in bpy.data.objects:
		bpy.data.objects.remove(item)

def reset_nodes(nodes):
	for node in nodes:
		nodes.remove(node)

def apply_subdivision_surface(target, level):
	bpy.context.scene.objects.active = target
	bpy.ops.object.modifier_add(type='SUBSURF')
	bpy.context.object.modifiers["Subsurf"].levels = level
	bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")

def set_principled_node_as_rough_blue(principled_node):
	principled_node.inputs['Base Color'].default_value = (0.1, 0.2, 0.6, 1.0)
	principled_node.inputs['Subsurface'].default_value = 0.0
	principled_node.inputs['Subsurface Color'].default_value = (0.9, 0.9, 0.9, 1.0)
	principled_node.inputs['Subsurface Radius'].default_value = (1.0, 1.0, 1.0)
	principled_node.inputs['Metallic'].default_value = 0.5
	principled_node.inputs['Specular'].default_value = 0.5
	principled_node.inputs['Specular Tint'].default_value = 0.0
	principled_node.inputs['Roughness'].default_value = 0.9
	principled_node.inputs['Anisotropic'].default_value = 0.0
	principled_node.inputs['Anisotropic Rotation'].default_value = 0.0
	principled_node.inputs['Sheen'].default_value = 0.0
	principled_node.inputs['Sheen Tint'].default_value = 0.5
	principled_node.inputs['Clearcoat'].default_value = 0.0
	principled_node.inputs['Clearcoat Roughness'].default_value = 0.030
	principled_node.inputs['IOR'].default_value = 1.450
	principled_node.inputs['Transmission'].default_value = 0.0

def set_principled_node_as_ceramic(principled_node):
	principled_node.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
	principled_node.inputs['Subsurface'].default_value = 0.1
	principled_node.inputs['Subsurface Color'].default_value = (0.9, 0.9, 0.9, 1.0)
	principled_node.inputs['Subsurface Radius'].default_value = (1.0, 1.0, 1.0)
	principled_node.inputs['Metallic'].default_value = 0.2
	principled_node.inputs['Specular'].default_value = 0.5
	principled_node.inputs['Specular Tint'].default_value = 0.0
	principled_node.inputs['Roughness'].default_value = 0.0
	principled_node.inputs['Anisotropic'].default_value = 0.0
	principled_node.inputs['Anisotropic Rotation'].default_value = 0.0
	principled_node.inputs['Sheen'].default_value = 0.0
	principled_node.inputs['Sheen Tint'].default_value = 0.5
	principled_node.inputs['Clearcoat'].default_value = 0.9
	principled_node.inputs['Clearcoat Roughness'].default_value = 0.030
	principled_node.inputs['IOR'].default_value = 1.450
	principled_node.inputs['Transmission'].default_value = 0.0

def set_principled_node_as_gold(principled_node):
	principled_node.inputs['Base Color'].default_value = (1.00, 0.75, 0.35, 1.0)
	principled_node.inputs['Subsurface'].default_value = 0.0
	principled_node.inputs['Subsurface Color'].default_value = (0.3, 0.1, 0.1, 1.0)
	principled_node.inputs['Subsurface Radius'].default_value = (1.0, 1.0, 1.0)
	principled_node.inputs['Metallic'].default_value = 1.0
	principled_node.inputs['Specular'].default_value = 0.5
	principled_node.inputs['Specular Tint'].default_value = 0.0
	principled_node.inputs['Roughness'].default_value = 0.0
	principled_node.inputs['Anisotropic'].default_value = 0.0
	principled_node.inputs['Anisotropic Rotation'].default_value = 0.0
	principled_node.inputs['Sheen'].default_value = 0.0
	principled_node.inputs['Sheen Tint'].default_value = 0.5
	principled_node.inputs['Clearcoat'].default_value = 0.5
	principled_node.inputs['Clearcoat Roughness'].default_value = 0.030
	principled_node.inputs['IOR'].default_value = 1.450
	principled_node.inputs['Transmission'].default_value = 0.0

def set_principled_node_as_glass(principled_node):
	principled_node.inputs['Base Color'].default_value = (0.92, 0.92, 0.95, 1.0)
	principled_node.inputs['Subsurface'].default_value = 0.0
	principled_node.inputs['Subsurface Color'].default_value = (0.3, 0.1, 0.1, 1.0)
	principled_node.inputs['Subsurface Radius'].default_value = (1.0, 1.0, 1.0)
	principled_node.inputs['Metallic'].default_value = 0.0
	principled_node.inputs['Specular'].default_value = 0.5
	principled_node.inputs['Specular Tint'].default_value = 0.0
	principled_node.inputs['Roughness'].default_value = 0.0
	principled_node.inputs['Anisotropic'].default_value = 0.0
	principled_node.inputs['Anisotropic Rotation'].default_value = 0.0
	principled_node.inputs['Sheen'].default_value = 0.0
	principled_node.inputs['Sheen Tint'].default_value = 0.5
	principled_node.inputs['Clearcoat'].default_value = 0.5
	principled_node.inputs['Clearcoat Roughness'].default_value = 0.030
	principled_node.inputs['IOR'].default_value = 1.450
	principled_node.inputs['Transmission'].default_value = 1.0

def set_scene_objects():
	bpy.ops.mesh.primitive_monkey_add(location=(- 3.0, 0.0, 1.0))
	current_object = bpy.context.object
	current_object.name = "Suzanne_Left"
	apply_subdivision_surface(current_object, 4)
	mat = bpy.data.materials.new("Material_Left")
	mat.use_nodes = True
	nodes = mat.node_tree.nodes
	links = mat.node_tree.links
	reset_nodes(nodes)
	output_node = nodes.new(type='ShaderNodeOutputMaterial')
	principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
	set_principled_node_as_glass(principled_node)
	links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
	current_object.data.materials.append(mat)

	bpy.ops.mesh.primitive_monkey_add(location=(0.0, 0.0, 1.0))
	current_object = bpy.context.object
	current_object.name = "Suzanne_Center"
	apply_subdivision_surface(current_object, 4)
	mat = bpy.data.materials.new("Material_Center")
	mat.use_nodes = True
	nodes = mat.node_tree.nodes
	links = mat.node_tree.links
	reset_nodes(nodes)
	output_node = nodes.new(type='ShaderNodeOutputMaterial')
	principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
	set_principled_node_as_gold(principled_node)
	links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
	current_object.data.materials.append(mat)

	bpy.ops.mesh.primitive_monkey_add(location=(+ 3.0, 0.0, 1.0))
	current_object = bpy.context.object
	current_object.name = "Suzanne_Right"
	apply_subdivision_surface(current_object, 4)
	mat = bpy.data.materials.new("Material_Center")
	mat.use_nodes = True
	nodes = mat.node_tree.nodes
	links = mat.node_tree.links
	reset_nodes(nodes)
	output_node = nodes.new(type='ShaderNodeOutputMaterial')
	principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
	set_principled_node_as_rough_blue(principled_node)
	links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
	current_object.data.materials.append(mat)

	bpy.ops.mesh.primitive_plane_add(radius=10.0)
	current_object = bpy.context.object
	current_object.name = "Floor"
	mat = bpy.data.materials.new("Material_Center")
	mat.use_nodes = True
	nodes = mat.node_tree.nodes
	links = mat.node_tree.links
	reset_nodes(nodes)
	output_node = nodes.new(type='ShaderNodeOutputMaterial')
	principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
	set_principled_node_as_ceramic(principled_node)
	links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
	current_object.data.materials.append(mat)

	return bpy.data.objects["Suzanne_Center"]

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
num_samples = int(sys.argv[sys.argv.index('--') + 3])

# Parameters

hdri_path = "./assets/HDRIs/green_point_park_2k.hdr"

# Scene Building

scene = bpy.data.scenes["Scene"]
world = scene.world

## Reset

reset_scene()

## Suzannes

center_suzanne = set_scene_objects()

## Camera

bpy.ops.object.camera_add(view_align=False, location=[0.0, - 15.0, 2.0])
camera = bpy.context.object

set_camera_lookat_target(camera, center_suzanne)
set_camera_params(camera, center_suzanne)

## Lights

set_background_light(world, hdri_path)

# Render Setting

set_scene_renderer(scene, resolution_percentage, output_file_path, camera, num_samples)

# Rendering

bpy.ops.render.render(animation=False, write_still=True)
