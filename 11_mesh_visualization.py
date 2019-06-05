# blender --background --python 11_mesh_visualization.py -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os
import random

sys.path.append(os.getcwd())

import utils


def get_random_numbers(length):
    numbers = []
    for i in range(length):
        numbers.append(random.random())
    return numbers


def get_color(x):
    colors = [
        (0.776470, 0.894117, 0.545098),
        (0.482352, 0.788235, 0.435294),
        (0.137254, 0.603921, 0.231372),
    ]

    a = x * (len(colors) - 1)
    t = a - math.floor(a)
    c0 = colors[math.floor(a)]
    c1 = colors[math.ceil(a)]

    return ((1.0 - t) * c0[0] + t * c1[0], (1.0 - t) * c0[1] + t * c1[1],
            (1.0 - t) * c0[2] + t * c1[2])


def set_scene_objects():
    # Instantiate a floor plane
    bpy.ops.mesh.primitive_plane_add(location=(0.0, 0.0, -1.0), radius=100)

    # Instantiate a triangle mesh
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3)
    current_object = bpy.context.object

    # Assign random colors for each triangle
    mesh = current_object.data
    mesh.vertex_colors.new(name='Col')
    random_numbers = get_random_numbers(len(mesh.vertex_colors['Col'].data))
    for index, vertex_color in enumerate(mesh.vertex_colors['Col'].data):
        vertex_color.color = get_color(random_numbers[index // 3])

    # Setup a material with wireframe visualization and per-face colors
    mat = bpy.data.materials.new("Material_Visualization")
    mat.use_nodes = True
    utils.clean_nodes(mat.node_tree.nodes)
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

    mat.node_tree.links.new(attrib_node.outputs['Color'],
                            principled_node.inputs['Base Color'])
    mat.node_tree.links.new(principled_node.outputs['BSDF'],
                            mix_node.inputs[1])
    mat.node_tree.links.new(rgb_node.outputs['Color'],
                            wire_mat_node.inputs['Color'])
    mat.node_tree.links.new(wire_mat_node.outputs['BSDF'], mix_node.inputs[2])
    mat.node_tree.links.new(wire_node.outputs['Fac'], mix_node.inputs['Fac'])
    mat.node_tree.links.new(mix_node.outputs['Shader'],
                            output_node.inputs['Surface'])

    utils.arrange_nodes(mat.node_tree)

    bpy.ops.object.empty_add(location=(0.0, -0.8, 0.0))
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
bpy.ops.object.camera_add(view_align=False, location=[0.0, -10.0, 0.0])
camera = bpy.context.object

utils.add_track_to_constraint(camera, focus_target)
set_camera_params(camera, focus_target)

## Lights
utils.build_environmental_light(world, hdri_path)

# Render Setting
utils.set_cycles_renderer(scene,
                          resolution_percentage,
                          output_file_path,
                          camera,
                          num_samples,
                          use_denoising=True,
                          use_transparent_bg=True)

# Render
bpy.ops.render.render(animation=False, write_still=True)
