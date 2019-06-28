# blender --background --python 12_split_tone.py -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.getcwd())

import utils


def set_scene_objects():

    materials = {
        "Leather05": {
            "color": "./assets/textures/[2K]Leather05/Leather05_col.jpg",
            "metallic": "",
            "roughness": "./assets/textures/[2K]Leather05/Leather05_rgh.jpg",
            "normal": "./assets/textures/[2K]Leather05/Leather05_nrm.jpg",
            "displacement":
            "./assets/textures/[2K]Leather05/Leather05_disp.jpg",
        },
        "Metal07": {
            "color": "./assets/textures/[2K]Metal07/Metal07_col.jpg",
            "metallic": "./assets/textures/[2K]Metal07/Metal07_met.jpg",
            "roughness": "./assets/textures/[2K]Metal07/Metal07_rgh.jpg",
            "normal": "./assets/textures/[2K]Metal07/Metal07_nrm.jpg",
            "displacement": "./assets/textures/[2K]Metal07/Metal07_disp.jpg",
        },
        "Fabric02": {
            "color": "./assets/textures/[2K]Fabric02/Fabric02_col.jpg",
            "metallic": "",
            "roughness": "./assets/textures/[2K]Fabric02/Fabric02_rgh.jpg",
            "normal": "./assets/textures/[2K]Fabric02/Fabric02_nrm.jpg",
            "displacement": "./assets/textures/[2K]Fabric02/Fabric02_disp.jpg",
        },
        "Marble01": {
            "color": "./assets/textures/[2K]Marble01/Marble01_col.jpg",
            "metallic": "",
            "roughness": "./assets/textures/[2K]Marble01/Marble01_rgh.jpg",
            "normal": "./assets/textures/[2K]Marble01/Marble01_nrm.jpg",
            "displacement": "./assets/textures/[2K]Marble01/Marble01_disp.jpg",
        },
    }

    def build_pbr_textured_nodes_from_material_name(node_tree, name):
        utils.build_pbr_textured_nodes(
            node_tree,
            color_texture_path=materials[name]["color"],
            metallic_texture_path=materials[name]["metallic"],
            roughness_texture_path=materials[name]["roughness"],
            normal_texture_path=materials[name]["normal"],
            displacement_texture_path=materials[name]["displacement"],
        )

    bpy.ops.mesh.primitive_monkey_add(location=(-1.8, 0.0, 1.0),
                                      rotation=(0.0, 0.0,
                                                -math.pi * 60.0 / 180.0),
                                      calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Suzanne_Left"
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 3)
    mat = bpy.data.materials.new("Material_Left")
    mat.use_nodes = True
    utils.clean_nodes(mat.node_tree.nodes)
    build_pbr_textured_nodes_from_material_name(mat.node_tree, "Leather05")
    current_object.data.materials.append(mat)

    bpy.ops.mesh.primitive_monkey_add(location=(0.0, 0.0, 1.0),
                                      rotation=(0.0, 0.0,
                                                -math.pi * 60.0 / 180.0),
                                      calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Suzanne_Center"
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 3)
    mat = bpy.data.materials.new("Material_Center")
    mat.use_nodes = True
    utils.clean_nodes(mat.node_tree.nodes)
    build_pbr_textured_nodes_from_material_name(mat.node_tree, "Metal07")
    current_object.data.materials.append(mat)

    bpy.ops.mesh.primitive_monkey_add(location=(+1.8, 0.0, 1.0),
                                      rotation=(0.0, 0.0,
                                                -math.pi * 60.0 / 180.0),
                                      calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Suzanne_Right"
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 3)
    mat = bpy.data.materials.new("Material_Right")
    mat.use_nodes = True
    utils.clean_nodes(mat.node_tree.nodes)
    build_pbr_textured_nodes_from_material_name(mat.node_tree, "Fabric02")
    current_object.data.materials.append(mat)

    bpy.ops.mesh.primitive_plane_add(radius=6.0, calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Floor"
    mat = bpy.data.materials.new("Material_Plane")
    mat.use_nodes = True
    utils.clean_nodes(mat.node_tree.nodes)
    build_pbr_textured_nodes_from_material_name(mat.node_tree, "Marble01")
    current_object.data.materials.append(mat)

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
bpy.ops.object.camera_add(view_align=False, location=[0.0, -14.0, 2.0])
camera = bpy.context.object

utils.add_track_to_constraint(camera, focus_target)
set_camera_params(camera, focus_target)

## Lights
utils.build_environmental_light(world, hdri_path)

## Composition
utils.build_scene_composition(scene)
split_tone_node = scene.node_tree.nodes["SplitTone"]
split_tone_node.inputs["HighlightsHue"].default_value = 0.1
split_tone_node.inputs["HighlightsSaturation"].default_value = 0.2
split_tone_node.inputs["ShadowsHue"].default_value = 0.6
split_tone_node.inputs["ShadowsSaturation"].default_value = 0.4
split_tone_node.inputs["Balance"].default_value = 0.3

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
