# blender --background --python 10_mocap.py -- </path/to/input/bvh> </path/to/output/directory>/<name> <resolution_percentage> <num_samples>
# ffmpeg -r 24 -i </path/to/output/directory>/<name>%04d.png -pix_fmt yuv420p out.mp4

import bpy
import sys
import math
import os

sys.path.append(os.getcwd())

import utils

def create_armature_from_bvh(scene, bvh_path):
	bpy.ops.import_anim.bvh(
		filepath=bvh_path,
		axis_forward='-Z',
		axis_up='Y',
		target='ARMATURE',
		global_scale=0.056444,
		frame_start=1,
		use_fps_scale=True,
		update_scene_fps=False,
		update_scene_duration=True
	)
	armature = bpy.context.object
	return armature

def build_scene(scene, input_bvh_path):
	mat = bpy.data.materials.new("BlueMetal")
	mat.use_nodes = True
	utils.clean_nodes(mat.node_tree.nodes)
	output_node = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
	principled_node = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
	principled_node.inputs['Base Color'].default_value = (0.1, 0.2, 0.7, 1.0)
	principled_node.inputs['Metallic'].default_value = 0.9
	principled_node.inputs['Roughness'].default_value = 0.1
	mat.node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
	utils.arrange_nodes(mat.node_tree)

	armature = create_armature_from_bvh(scene, bvh_path=input_bvh_path)
	armature_mesh = utils.create_armature_mesh(scene, armature, 'Mesh')
	armature_mesh.data.materials.append(mat)

	mat = bpy.data.materials.new("Concrete07")
	mat.use_nodes = True
	utils.clean_nodes(mat.node_tree.nodes)
	utils.build_pbr_textured_nodes(
		mat.node_tree,
		color_texture_path="./assets/textures/[2K]Concrete07/Concrete07_col.jpg",
		roughness_texture_path="./assets/textures/[2K]Concrete07/Concrete07_rgh.jpg",
		normal_texture_path="./assets/textures/[2K]Concrete07/Concrete07_nrm.jpg",
		displacement_texture_path="./assets/textures/[2K]Concrete07/Concrete07_disp.jpg",
		ambient_occlusion_texture_path="./assets/textures/[2K]Concrete07/Concrete07_AO.jpg",
		scale=(0.25, 0.25, 0.25)
	)

	bpy.ops.mesh.primitive_plane_add(radius=8.0, calc_uvs=True)
	current_object = bpy.context.object
	current_object.name = "Floor"
	current_object.data.materials.append(mat)

	bpy.ops.mesh.primitive_plane_add(radius=8.0, calc_uvs=True)
	current_object = bpy.context.object
	current_object.name = "Wall"
	current_object.data.materials.append(mat)
	current_object.location = (0.0, 6.0, 0.0)
	current_object.rotation_euler = (0.5 * math.pi, 0.0, 0.0)

	bpy.ops.object.empty_add(location=(0.0, 0.0, 0.8))
	focus_target = bpy.context.object
	utils.add_copy_location_constraint(copy_to_object=focus_target, copy_from_object=armature, use_x=True, use_y=True, use_z=False, bone_name='Hips')

	return focus_target

# Args
input_bvh_path = str(sys.argv[sys.argv.index('--') + 1])         # "./assets/motion/102_01.bvh"
output_file_path = str(sys.argv[sys.argv.index('--') + 2])       # "./"
resolution_percentage = int(sys.argv[sys.argv.index('--') + 3])  # 100
num_samples = int(sys.argv[sys.argv.index('--') + 4])            # 128

# Parameters
hdri_path = "./assets/HDRIs/green_point_park_2k.hdr"

# Scene Building
scene = bpy.data.scenes["Scene"]
world = scene.world

## Reset
utils.clean_objects()

# Animation Setting
utils.set_animation(scene, fps=24, frame_start=1, frame_end=40)  # frame_end will be overriden later

## Scene
focus_target = build_scene(scene, input_bvh_path)

## Camera
bpy.ops.object.camera_add(view_align=False, location=[0.0, - 10.0, 1.0])
camera = bpy.context.object

utils.add_copy_location_constraint(copy_to_object=camera, copy_from_object=focus_target, use_x=True, use_y=False, use_z=False)
utils.add_track_to_constraint(camera, focus_target)
utils.set_camera_params(camera, focus_target)

## Lights
utils.build_environmental_light(world, hdri_path)

## Composition
utils.build_scene_composition(scene)

# Render Setting
utils.set_cycles_renderer(scene, resolution_percentage, output_file_path, camera, num_samples, use_denoising=True, use_motion_blur=True)

# Render
bpy.ops.render.render(animation=True)
