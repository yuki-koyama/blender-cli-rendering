# blender --background --python 07_texturing.py -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils
import external.cc0assetsloader as loader


def set_scene_objects():
    loader.build_pbr_textured_nodes_from_name("Leather05")
    loader.build_pbr_textured_nodes_from_name("Metal07")
    loader.build_pbr_textured_nodes_from_name("Fabric02")
    loader.build_pbr_textured_nodes_from_name("Marble01")

    bpy.ops.mesh.primitive_monkey_add(location=(-1.8, 0.0, 1.0),
                                      rotation=(0.0, 0.0, -math.pi * 60.0 / 180.0),
                                      calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Suzanne_Left"
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 2)
    current_object.data.materials.append(bpy.data.materials["Leather05"])

    bpy.ops.mesh.primitive_monkey_add(location=(0.0, 0.0, 1.0),
                                      rotation=(0.0, 0.0, -math.pi * 60.0 / 180.0),
                                      calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Suzanne_Center"
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 2)
    current_object.data.materials.append(bpy.data.materials["Metal07"])

    bpy.ops.mesh.primitive_monkey_add(location=(+1.8, 0.0, 1.0),
                                      rotation=(0.0, 0.0, -math.pi * 60.0 / 180.0),
                                      calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Suzanne_Right"
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 2)
    current_object.data.materials.append(bpy.data.materials["Fabric02"])

    bpy.ops.mesh.primitive_plane_add(radius=6.0, calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Floor"
    current_object.data.materials.append(bpy.data.materials["Marble01"])

    bpy.ops.mesh.primitive_plane_add(radius=6.0,
                                     location=(0.0, 4.0, 0.0),
                                     rotation=(math.pi * 90.0 / 180.0, 0.0, 0.0),
                                     calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Wall"
    current_object.data.materials.append(bpy.data.materials["Marble01"])

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

## Suzannes
focus_target = set_scene_objects()

## Camera
bpy.ops.object.camera_add(view_align=False, location=[0.0, -14.0, 2.0])
camera = bpy.context.object

utils.add_track_to_constraint(camera, focus_target)
set_camera_params(camera, focus_target)

## Lights
utils.build_environment_texture_background(world, hdri_path)

## Composition
utils.build_scene_composition(scene)

# Render Setting
utils.set_cycles_renderer(scene, resolution_percentage, output_file_path, camera, num_samples, use_denoising=True)

# Render
bpy.ops.render.render(animation=False, write_still=True)
