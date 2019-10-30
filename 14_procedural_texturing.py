# blender --background --python 14_procedural_texturing.py -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils


def set_floor_and_lights() -> None:
    size = 200.0
    current_object = utils.create_plane(size=size, name="Floor")
    floor_mat = bpy.data.materials.new("Material_Plane")
    floor_mat.use_nodes = True
    utils.clean_nodes(floor_mat.node_tree.nodes)
    utils.build_checker_board_nodes(floor_mat.node_tree, size)
    current_object.data.materials.append(floor_mat)

    utils.create_area_light(location=(6.0, 0.0, 4.0),
                            rotation=(0.0, math.pi * 60.0 / 180.0, 0.0),
                            size=5.0,
                            color=(1.00, 0.70, 0.60, 1.00),
                            strength=1500.0,
                            name="Main Light")
    utils.create_area_light(location=(-6.0, 0.0, 2.0),
                            rotation=(0.0, -math.pi * 80.0 / 180.0, 0.0),
                            size=5.0,
                            color=(0.30, 0.42, 1.00, 1.00),
                            strength=1000.0,
                            name="Sub Light")


def set_scene_objects() -> bpy.types.Object:
    set_floor_and_lights()

    mat = bpy.data.materials.new("Peeling Paint Metal")
    mat.use_nodes = True
    utils.clean_nodes(mat.node_tree.nodes)

    utils.build_peeling_paint_metal_nodes(mat.node_tree)

    current_object = utils.create_smooth_monkey(location=(0.0, 0.0, 1.0))
    current_object.data.materials.append(mat)

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

## Object
focus_target_object = set_scene_objects()

## Camera
camera_object = utils.create_camera(location=(0.0, -10.0, 2.2))

utils.add_track_to_constraint(camera_object, focus_target_object)
utils.set_camera_params(camera_object.data, focus_target_object)

## Background
utils.build_rgb_background(world, rgb=(0.0, 0.0, 0.0, 1.0))

## Composition
utils.build_scene_composition(scene)

# Render Setting
utils.set_cycles_renderer(scene,
                          resolution_percentage,
                          output_file_path,
                          camera_object,
                          num_samples,
                          use_denoising=True,
                          use_transparent_bg=False)

# Render
bpy.ops.render.render(animation=False, write_still=True)
