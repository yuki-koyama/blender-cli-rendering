# blender --background --python 13_matcap.py --render-frame 1 -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils


def set_scene_objects():
    image_path = "./assets/matcaps/blue.png"

    mat = utils.add_material("MatCap", use_nodes=True, make_node_tree_empty=True)
    utils.build_matcap_nodes(mat.node_tree, image_path)

    current_object = utils.create_smooth_monkey(location=(1.2, 0.0, 0.0))
    current_object.data.materials.append(mat)

    current_object = utils.create_smooth_sphere(location=(-1.2, 0.0, 0.0), subdivision_level=2)
    current_object.data.materials.append(mat)

    bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
    focus_target = bpy.context.object
    return focus_target


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
bpy.ops.object.camera_add(location=(0.0, -12.0, 0.0))
camera_object = bpy.context.object

utils.add_track_to_constraint(camera_object, focus_target)
utils.set_camera_params(camera_object.data, focus_target, lens=72, fstop=128.0)

## Background
utils.build_rgb_background(world, rgb=(0.89, 0.93, 1.00, 1.00))


## Composition
def build_scene_composition(scene):
    scene.use_nodes = True
    utils.clean_nodes(scene.node_tree.nodes)

    render_layer_node = scene.node_tree.nodes.new(type="CompositorNodeRLayers")

    filter_node = scene.node_tree.nodes.new(type="CompositorNodeFilter")
    filter_node.filter_type = "SHARPEN"
    filter_node.inputs["Fac"].default_value = 0.1

    color_correction_node = scene.node_tree.nodes.new(type="CompositorNodeColorCorrection")
    color_correction_node.master_saturation = 1.10
    color_correction_node.master_gain = 1.20
    color_correction_node.midtones_gain = 1.20
    color_correction_node.shadows_gain = 1.50

    split_tone_node = utils.create_split_tone_node(scene.node_tree)
    split_tone_node.inputs["ShadowsHue"].default_value = 0.6
    split_tone_node.inputs["ShadowsSaturation"].default_value = 0.1

    composite_node = scene.node_tree.nodes.new(type="CompositorNodeComposite")

    scene.node_tree.links.new(render_layer_node.outputs['Image'], filter_node.inputs['Image'])
    scene.node_tree.links.new(filter_node.outputs['Image'], color_correction_node.inputs['Image'])
    scene.node_tree.links.new(color_correction_node.outputs['Image'], split_tone_node.inputs['Image'])
    scene.node_tree.links.new(split_tone_node.outputs['Image'], composite_node.inputs['Image'])

    utils.arrange_nodes(scene.node_tree)


build_scene_composition(scene)

# Render Setting
utils.set_output_properties(scene, resolution_percentage, output_file_path)
utils.set_cycles_renderer(scene, camera_object, num_samples, use_denoising=False)
