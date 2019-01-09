# blender --background --python 09_armature.py -- </path/to/output/directory>/<name> <resolution_percentage> <num_samples>
# ffmpeg -r 24 -i </path/to/output/directory>/<name>%04d.png -pix_fmt yuv420p out.mp4

import bpy
import sys
import math
import os

sys.path.append(os.getcwd())

import utils

def create_skinned_object():
	# Edit mode
	bpy.ops.object.add(type='ARMATURE', enter_editmode=True, location=(0.0, 0.0, 0.0))
	armature = bpy.context.object
	bone1 = armature.data.edit_bones.new('Bone1')
	bone1.head = (0.0, 0.0, 0.0)
	bone1.tail = (0.0, 0.0, 1.0)
	bone2 = armature.data.edit_bones.new('Bone2')
	bone2.parent = bone1
	bone2.use_connect = True
	bone2.tail = (0.0, 0.0, 2.0)

	# Pose mode
	bpy.ops.object.mode_set(mode='POSE')
	bone2 = armature.pose.bones['Bone2']
	bone2.rotation_mode = 'XYZ'
	bone2.rotation_euler = (0.0, 0.0, 0.0)
	bone2.keyframe_insert(data_path='rotation_euler', frame=4)
	bone2.rotation_euler = (+ math.pi * 30.0 / 180.0, 0.0, 0.0)
	bone2.keyframe_insert(data_path='rotation_euler', frame=12)
	bone2.rotation_euler = (- math.pi * 30.0 / 180.0, 0.0, 0.0)
	bone2.keyframe_insert(data_path='rotation_euler', frame=20)
	bone2.rotation_euler = (+ math.pi * 30.0 / 180.0, 0.0, 0.0)
	bone2.keyframe_insert(data_path='rotation_euler', frame=28)
	bone2.rotation_euler = (0.0, 0.0, 0.0)
	bone2.keyframe_insert(data_path='rotation_euler', frame=36)

	# Object mode
	bpy.ops.object.mode_set(mode='OBJECT')

	# Mesh
	bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 1.0), calc_uvs=True)
	cube = bpy.context.object
	cube.name = "Cuboid"
	cube.scale = (0.5, 0.5, 1.0)
	utils.add_subdivision_surface_modifier(cube, 3, is_simple=True)
	utils.add_subdivision_surface_modifier(cube, 3, is_simple=False)
	utils.set_smooth_shading(cube)
	mat = bpy.data.materials.new("Metal07")
	mat.use_nodes = True
	utils.clean_nodes(mat.node_tree.nodes)
	utils.build_pbr_textured_nodes(
		mat.node_tree, 
		color_texture_path="./assets/textures/[2K]Metal07/Metal07_col.jpg", 
		metallic_texture_path="./assets/textures/[2K]Metal07/Metal07_met.jpg", 
		roughness_texture_path="./assets/textures/[2K]Metal07/Metal07_rgh.jpg", 
		normal_texture_path="./assets/textures/[2K]Metal07/Metal07_nrm.jpg", 
		displacement_texture_path="./assets/textures/[2K]Metal07/Metal07_disp.jpg"
	)
	cube.data.materials.append(mat)

	# Set the armature as the parent of the cube using the "Automatic Weight" armature option
	bpy.ops.object.select_all(action='DESELECT')
	cube.select = True
	armature.select = True
	bpy.context.scene.objects.active = armature
	bpy.ops.object.parent_set(type='ARMATURE_AUTO')

	return armature

def set_scene_objects():
	current_object = create_skinned_object()
	current_object.rotation_euler = (0.0, 0.0, math.pi * 60.0 / 180.0)

	bpy.ops.mesh.primitive_plane_add(radius=6.0, calc_uvs=True)
	current_object = bpy.context.object
	current_object.name = "Floor"
	mat = bpy.data.materials.new("Marble01")
	mat.use_nodes = True
	utils.clean_nodes(mat.node_tree.nodes)
	utils.build_pbr_textured_nodes(
		mat.node_tree,
		color_texture_path="./assets/textures/[2K]Marble01/Marble01_col.jpg",
		roughness_texture_path="./assets/textures/[2K]Marble01/Marble01_rgh.jpg",
		normal_texture_path="./assets/textures/[2K]Marble01/Marble01_nrm.jpg",
		displacement_texture_path="./assets/textures/[2K]Marble01/Marble01_disp.jpg"
	)
	current_object.data.materials.append(mat)

	bpy.ops.object.empty_add(location=(0.0, 0.0, 1.0))
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

## Suzannes
focus_target = set_scene_objects()

## Camera
bpy.ops.object.camera_add(view_align=False, location=[0.0, - 12.0, 2.0])
camera = bpy.context.object

utils.add_track_to_constraint(camera, focus_target)
set_camera_params(camera, focus_target)

## Lights
utils.build_environmental_light(world, hdri_path)

## Composition
utils.build_scene_composition(scene)

# Animation Setting
utils.set_animation(scene, fps=24, frame_start=1, frame_end=40)

# Render Setting
utils.set_cycles_renderer(scene, resolution_percentage, output_file_path, camera, num_samples, use_denoising=True, use_motion_blur=True)

# Render
bpy.ops.render.render(animation=True)
