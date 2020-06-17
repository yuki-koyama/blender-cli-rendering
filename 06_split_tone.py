# blender --background --python 06_split_tone.py --render-frame 1 -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils


def set_scene_objects():
    mat = utils.add_material("Material", use_nodes=True, make_node_tree_empty=True)
    utils.build_pbr_nodes(mat.node_tree, base_color=(0.6, 0.6, 0.6, 1.0))

    left_object, center_object, right_object = utils.create_three_smooth_monkeys()
    left_object.data.materials.append(mat)
    center_object.data.materials.append(mat)
    right_object.data.materials.append(mat)

    plane_size = 100.0
    current_object = utils.create_plane(size=plane_size, name="Floor")
    floor_mat = utils.add_material("Material_Plane", use_nodes=True, make_node_tree_empty=True)
    utils.build_checker_board_nodes(floor_mat.node_tree, plane_size)
    current_object.data.materials.append(floor_mat)

    sun_object = utils.create_sun_light()
    sun_object.data.use_nodes = True
    sun_object.data.node_tree.nodes["Emission"].inputs["Strength"].default_value = 3.0

    bpy.ops.object.empty_add(location=(0.0, -0.70, 1.0))
    focus_target = bpy.context.object
    return focus_target


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
bpy.ops.object.camera_add(location=(0.0, -14.0, 5.0))
camera_object = bpy.context.object

utils.add_track_to_constraint(camera_object, focus_target)
utils.set_camera_params(camera_object.data, focus_target, lens=72, fstop=0.2)

## Lights
utils.build_rgb_background(world, rgb=(0.0, 0.0, 0.0, 1.0))

## Composition
set_composition(scene)

# Render Setting
utils.set_output_properties(scene, resolution_percentage, output_file_path)
utils.set_cycles_renderer(scene, camera_object, num_samples)
