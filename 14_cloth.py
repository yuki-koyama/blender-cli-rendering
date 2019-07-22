# blender --background --python 14_cloth.py -- </path/to/output/directory>/<name> <resolution_percentage> <num_samples>
# ffmpeg -r 24 -i </path/to/output/directory>/<name>%04d.png -pix_fmt yuv420p out.mp4

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils
import external.cc0assetsloader as loader


def set_floor_and_lights():
    radius = 100.0
    bpy.ops.mesh.primitive_plane_add(radius=radius, calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Floor"
    floor_mat = bpy.data.materials.new("Material_Plane")
    floor_mat.use_nodes = True
    utils.clean_nodes(floor_mat.node_tree.nodes)
    utils.build_checker_board_nodes(floor_mat.node_tree, 2.0 * radius)
    current_object.data.materials.append(floor_mat)

    bpy.ops.object.lamp_add(type='AREA', location=(6.0, 0.0, 4.0), rotation=(0.0, math.pi * 60.0 / 180.0, 0.0))
    bpy.context.object.name = "Main Light"
    main_light = bpy.context.object.data
    main_light.size = 5.0
    main_light.use_nodes = True
    main_light.node_tree.nodes["Emission"].inputs["Color"].default_value = (1.00, 0.70, 0.60, 1.00)
    main_light.node_tree.nodes["Emission"].inputs["Strength"].default_value = 1500.0

    bpy.ops.object.lamp_add(type='AREA', location=(-6.0, 0.0, 2.0), rotation=(0.0, -math.pi * 80.0 / 180.0, 0.0))
    bpy.context.object.name = "Sub Light"
    sub_light = bpy.context.object.data
    sub_light.size = 5.0
    sub_light.use_nodes = True
    sub_light.node_tree.nodes["Emission"].inputs["Color"].default_value = (0.30, 0.42, 1.00, 1.00)
    sub_light.node_tree.nodes["Emission"].inputs["Strength"].default_value = 1000.0


def set_scene_objects():
    loader.build_pbr_textured_nodes_from_name("Fabric02")
    loader.build_pbr_textured_nodes_from_name("Fabric03")
    bpy.data.materials["Fabric02"].node_tree.nodes["Principled BSDF"].inputs["Sheen"].default_value = 4.0
    bpy.data.materials["Fabric03"].node_tree.nodes["Principled BSDF"].inputs["Sheen"].default_value = 4.0

    set_floor_and_lights()

    bpy.ops.mesh.primitive_monkey_add(location=(0.0, 0.0, 1.0), calc_uvs=True)
    current_object = bpy.context.object
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 2)
    current_object.data.materials.append(bpy.data.materials["Fabric03"])
    bpy.ops.object.modifier_add(type='COLLISION')

    bpy.ops.mesh.primitive_grid_add(x_subdivisions=75,
                                    y_subdivisions=75,
                                    radius=1.5,
                                    calc_uvs=True,
                                    location=(0.0, 0.0, 2.5))
    cloth_object = bpy.context.object
    cloth_object.name = "Cloth"
    bpy.ops.object.modifier_add(type='CLOTH')
    cloth_object.modifiers["Cloth"].collision_settings.use_collision = True
    cloth_object.modifiers["Cloth"].collision_settings.use_self_collision = True
    cloth_object.modifiers["Cloth"].settings.quality = 10
    utils.set_smooth_shading(cloth_object)
    utils.add_subdivision_surface_modifier(cloth_object, 2)
    cloth_object.data.materials.append(bpy.data.materials["Fabric02"])

    bpy.ops.object.empty_add(location=(0.0, -0.75, 1.05))
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

## Animation
utils.set_animation(scene, fps=24, frame_start=1, frame_end=48)

## Object
focus_target = set_scene_objects()

## Camera
bpy.ops.object.camera_add(view_align=False, location=[0.0, -12.5, 2.2])
camera = bpy.context.object
utils.add_track_to_constraint(camera, focus_target)
utils.set_camera_params(camera, focus_target)

## Background
utils.build_rgb_background(world, rgb=(0.0, 0.0, 0.0, 1.0))

## Composition
utils.build_scene_composition(scene, dispersion=0.0)

# Render Setting
utils.set_cycles_renderer(scene,
                          resolution_percentage,
                          output_file_path,
                          camera,
                          num_samples,
                          use_denoising=True,
                          use_motion_blur=True,
                          use_transparent_bg=False)

# Render
bpy.ops.render.render(animation=True, write_still=False)
