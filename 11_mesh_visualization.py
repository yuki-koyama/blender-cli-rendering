# blender --background --python 11_mesh_visualization.py --render-frame 1 -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os
import random
from typing import List, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils


def get_random_numbers(length: int) -> List[float]:
    numbers = []
    for i in range(length):
        numbers.append(random.random())
    return numbers


def get_color(x: float) -> Tuple[float, float, float]:
    colors = [
        (0.776470, 0.894117, 0.545098),
        (0.482352, 0.788235, 0.435294),
        (0.137254, 0.603921, 0.231372),
    ]

    a = x * (len(colors) - 1)
    t = a - math.floor(a)
    c0 = colors[math.floor(a)]
    c1 = colors[math.ceil(a)]

    return ((1.0 - t) * c0[0] + t * c1[0], (1.0 - t) * c0[1] + t * c1[1], (1.0 - t) * c0[2] + t * c1[2])


def set_scene_objects() -> bpy.types.Object:
    # Instantiate a floor plane
    utils.create_plane(size=200.0, location=(0.0, 0.0, -1.0))

    # Instantiate a triangle mesh
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3)
    current_object = bpy.context.object

    # Assign random colors for each triangle
    mesh = current_object.data
    mesh.vertex_colors.new(name='Col')
    random_numbers = get_random_numbers(len(mesh.vertex_colors['Col'].data))
    for index, vertex_color in enumerate(mesh.vertex_colors['Col'].data):
        vertex_color.color = get_color(random_numbers[index // 3]) + tuple([1.0])

    # Setup a material with wireframe visualization and per-face colors
    mat = utils.add_material("Material_Visualization", use_nodes=True, make_node_tree_empty=True)
    current_object.data.materials.append(mat)

    output_node = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    principled_node = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    rgb_node = mat.node_tree.nodes.new(type='ShaderNodeRGB')
    mix_node = mat.node_tree.nodes.new(type='ShaderNodeMixShader')
    wire_node = mat.node_tree.nodes.new(type='ShaderNodeWireframe')
    wire_mat_node = mat.node_tree.nodes.new(type='ShaderNodeBsdfDiffuse')
    attrib_node = mat.node_tree.nodes.new(type='ShaderNodeAttribute')

    attrib_node.attribute_name = 'Col'
    rgb_node.outputs['Color'].default_value = (0.1, 0.1, 0.1, 1.0)

    mat.node_tree.links.new(attrib_node.outputs['Color'], principled_node.inputs['Base Color'])
    mat.node_tree.links.new(principled_node.outputs['BSDF'], mix_node.inputs[1])
    mat.node_tree.links.new(rgb_node.outputs['Color'], wire_mat_node.inputs['Color'])
    mat.node_tree.links.new(wire_mat_node.outputs['BSDF'], mix_node.inputs[2])
    mat.node_tree.links.new(wire_node.outputs['Fac'], mix_node.inputs['Fac'])
    mat.node_tree.links.new(mix_node.outputs['Shader'], output_node.inputs['Surface'])

    utils.arrange_nodes(mat.node_tree)

    bpy.ops.object.empty_add(location=(0.0, -0.8, 0.0))
    focus_target = bpy.context.object

    return focus_target


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
focus_target_object = set_scene_objects()

## Camera
camera_object = utils.create_camera(location=(0.0, -10.0, 0.0))

utils.add_track_to_constraint(camera_object, focus_target_object)
utils.set_camera_params(camera_object.data, focus_target_object, lens=72, fstop=0.5)

## Lights
utils.build_environment_texture_background(world, hdri_path)

# Render Setting
utils.set_output_properties(scene, resolution_percentage, output_file_path)
utils.set_cycles_renderer(scene, camera_object, num_samples, use_transparent_bg=True)
