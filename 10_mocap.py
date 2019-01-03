# blender --background --python 10_mocap.py -- </path/to/output/directory>/<name> <resolution_percentage> <num_samples>
# ffmpeg -r 24 -i </path/to/output/directory>/<name>%04d.png -pix_fmt yuv420p out.mp4

import bpy
import sys
import math
import mathutils
import os

sys.path.append(os.getcwd())

import utils

def reset_scene():
	for item in bpy.data.objects:
		bpy.data.objects.remove(item)

def set_smooth_shading(target_object):
	for poly in target_object.data.polygons:
		poly.use_smooth = True

def add_rigid_vertex_group(object, name, vertex_indices):
	new_vertex_group = object.vertex_groups.new(name)
	for vertex_index in vertex_indices:
		new_vertex_group.add([ vertex_index ], 1.0, 'REPLACE')

def generate_bone_mesh(radius, length):
	base_radius = radius
	top_radius = 0.5 * radius

	vertices = [
		mathutils.Vector((- base_radius, 0.0, + base_radius)),
		mathutils.Vector((+ base_radius, 0.0, + base_radius)),
		mathutils.Vector((+ base_radius, 0.0, - base_radius)),
		mathutils.Vector((- base_radius, 0.0, - base_radius)),

		mathutils.Vector((- top_radius, length, + top_radius)),
		mathutils.Vector((+ top_radius, length, + top_radius)),
		mathutils.Vector((+ top_radius, length, - top_radius)),
		mathutils.Vector((- top_radius, length, - top_radius)),

		mathutils.Vector((0.0, - base_radius, 0.0)),
		mathutils.Vector((0.0, length + top_radius, 0.0))
	]

	faces = [
		(8, 1, 0),
		(8, 2, 1),
		(8, 3, 2),
		(8, 0, 3),

		(9, 4, 5),
		(9, 5, 6),
		(9, 6, 7),
		(9, 7, 4),

		(0, 1, 5, 4),
		(1, 2, 6, 5),
		(2, 3, 7, 6),
		(3, 0, 4, 7)
	]

	return vertices, faces

def create_armature_mesh(scene, armature_object, mesh_name):
	assert armature_object.type == 'ARMATURE', 'Error'
	assert len(armature_object.data.bones) != 0, 'Error'

	armature_data = armature_object.data

	vertices = []
	faces = []
	vertex_groups = []

	for bone in armature_data.bones:
		radius = 0.10 * (0.10 + bone.length)
		temp_vertices, temp_faces = generate_bone_mesh(radius, bone.length)

		vertex_index_offset = len(vertices)

		temp_vertex_group = { 'name': bone.name, 'vertex_indices': [] }
		for local_index, vertex in enumerate(temp_vertices):
			vertices.append(bone.matrix_local * vertex)
			temp_vertex_group['vertex_indices'].append(local_index + vertex_index_offset)
		vertex_groups.append(temp_vertex_group)

		for face in temp_faces:
			if len(face) == 3:
				faces.append((face[0] + vertex_index_offset, face[1] + vertex_index_offset, face[2] + vertex_index_offset))
			else:
				faces.append((face[0] + vertex_index_offset, face[1] + vertex_index_offset, face[2] + vertex_index_offset, face[3] + vertex_index_offset))

	# Add a new mesh and set vertices and faces
	# In this case, it does not require to set edges
	# After manipulating mesh data, update() needs to be called
	new_mesh = bpy.data.meshes.new(mesh_name)
	new_mesh.from_pydata(vertices, [], faces)
	new_mesh.update()

	new_object = bpy.data.objects.new(mesh_name, new_mesh)
	new_object.matrix_world = armature_object.matrix_world

	for vertex_group in vertex_groups:
		add_rigid_vertex_group(new_object, vertex_group['name'], vertex_group['vertex_indices'])

	armature_modifier = new_object.modifiers.new('Armature', 'ARMATURE')
	armature_modifier.object = armature_object
	armature_modifier.use_vertex_groups = True

	utils.add_subdivision_surface_modifier(new_object, 1, is_simple=True)
	utils.add_subdivision_surface_modifier(new_object, 2, is_simple=False)

	scene.objects.link(new_object)

	# Set the armature as the parent of the new object
	bpy.ops.object.select_all(action='DESELECT')
	new_object.select = True
	armature_object.select = True
	bpy.context.scene.objects.active = armature_object
	bpy.ops.object.parent_set(type='OBJECT')

	return new_object

def create_armature_from_bvh(scene, bvh_path):
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

	return armature

def build_scene(scene):
	armature = create_armature_from_bvh(scene, bvh_path='./assets/motion/131_03.bvh')
	create_armature_mesh(scene, armature, 'Mesh')

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
reset_scene()

## Suzannes
focus_target = build_scene(scene)

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
