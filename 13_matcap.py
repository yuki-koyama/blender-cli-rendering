# blender --background --python 13_matcap.py -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils


def set_scene_objects():
    image_path = "./assets/matcaps/blue.png"

    mat = bpy.data.materials.new("MatCap")
    mat.use_nodes = True
    utils.clean_nodes(mat.node_tree.nodes)
    utils.build_matcap_nodes(mat.node_tree, image_path)

    bpy.ops.mesh.primitive_monkey_add(location=(1.2, 0.0, 0.0), calc_uvs=True)
    current_object = bpy.context.object
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 2)
    current_object.data.materials.append(mat)

    bpy.ops.mesh.primitive_uv_sphere_add(location=(-1.2, 0.0, 0.0), calc_uvs=True)
    current_object = bpy.context.object
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 2)
    current_object.data.materials.append(mat)

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
    camera.data.cycles.aperture_size = 0.0
    camera.data.cycles.aperture_blades = 6


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
bpy.ops.object.camera_add(view_align=False, location=[0.0, -12.0, 0.0])
camera = bpy.context.object

utils.add_track_to_constraint(camera, focus_target)
set_camera_params(camera, focus_target)

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
utils.set_cycles_renderer(scene,
                          resolution_percentage,
                          output_file_path,
                          camera,
                          num_samples,
                          use_denoising=False,
                          use_transparent_bg=False)

# Render
bpy.ops.render.render(animation=False, write_still=True)
