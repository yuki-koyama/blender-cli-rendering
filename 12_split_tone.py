# blender --background --python 12_split_tone.py -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils


def set_scene_objects():
    mat = bpy.data.materials.new("Material")
    mat.use_nodes = True
    utils.clean_nodes(mat.node_tree.nodes)
    utils.build_pbr_nodes(mat.node_tree, base_color=(0.6, 0.6, 0.6, 1.0))

    bpy.ops.mesh.primitive_monkey_add(location=(-1.8, 0.0, 1.0),
                                      rotation=(0.0, 0.0, -math.pi * 60.0 / 180.0),
                                      calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Suzanne_Left"
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 2)
    current_object.data.materials.append(mat)

    bpy.ops.mesh.primitive_monkey_add(location=(0.0, 0.0, 1.0),
                                      rotation=(0.0, 0.0, -math.pi * 60.0 / 180.0),
                                      calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Suzanne_Center"
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 2)
    current_object.data.materials.append(mat)

    bpy.ops.mesh.primitive_monkey_add(location=(+1.8, 0.0, 1.0),
                                      rotation=(0.0, 0.0, -math.pi * 60.0 / 180.0),
                                      calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Suzanne_Right"
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 2)
    current_object.data.materials.append(mat)

    radius = 100.0
    bpy.ops.mesh.primitive_plane_add(radius=radius, calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Floor"
    floor_mat = bpy.data.materials.new("Material_Plane")
    floor_mat.use_nodes = True
    utils.clean_nodes(floor_mat.node_tree.nodes)
    utils.build_checker_board_nodes(floor_mat.node_tree, 2.0 * radius)
    current_object.data.materials.append(floor_mat)

    bpy.ops.object.lamp_add(type='SUN')
    sun = bpy.context.object.data
    sun.use_nodes = True
    sun.node_tree.nodes["Emission"].inputs["Strength"].default_value = 4.0

    bpy.ops.object.empty_add(location=(0.0, -0.70, 1.0))
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


def set_composition(scene):
    utils.build_scene_composition(scene, dispersion=0.0)

    split_tone_node = scene.node_tree.nodes["SplitTone"]
    split_tone_node.inputs["HighlightsHue"].default_value = 0.1
    split_tone_node.inputs["HighlightsSaturation"].default_value = 0.5
    split_tone_node.inputs["ShadowsHue"].default_value = 0.6
    split_tone_node.inputs["ShadowsSaturation"].default_value = 0.5
    split_tone_node.inputs["Balance"].default_value = 0.6


# Args
output_file_path = str(sys.argv[sys.argv.index('--') + 1])
resolution_percentage = int(sys.argv[sys.argv.index('--') + 2])
num_samples = int(sys.argv[sys.argv.index('--') + 3])

# Scene Building
scene = bpy.data.scenes["Scene"]
world = scene.world

## Reset
utils.clean_objects()

## Object
focus_target = set_scene_objects()

## Camera
bpy.ops.object.camera_add(view_align=False, location=[0.0, -14.0, 5.0])
camera = bpy.context.object

utils.add_track_to_constraint(camera, focus_target)
set_camera_params(camera, focus_target)

## Lights
utils.build_rgb_background(world, rgb=(0.0, 0.0, 0.0, 1.0))

## Composition
set_composition(scene)

# Render Setting
utils.set_cycles_renderer(scene,
                          resolution_percentage,
                          output_file_path,
                          camera,
                          num_samples,
                          use_denoising=True,
                          use_transparent_bg=False)

# Render
bpy.ops.render.render(animation=False, write_still=True)
