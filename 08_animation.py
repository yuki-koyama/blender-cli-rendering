# blender --background --python 08_animation.py --render-anim -- </path/to/output/directory>/<name> <resolution_percentage> <num_samples>
# ffmpeg -r 24 -i </path/to/output/directory>/<name>%04d.png -pix_fmt yuv420p out.mp4

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils
import external.cc0assetsloader as loader


def set_scene_objects():
    loader.build_pbr_textured_nodes_from_name("Metal07")
    loader.build_pbr_textured_nodes_from_name("Marble01")

    current_object = utils.create_smooth_monkey(location=(0.0, 0.0, 1.0), rotation=(0.0, 0.0, -math.pi * 60.0 / 180.0))
    current_object.data.materials.append(bpy.data.materials["Metal07"])

    # Keyframes
    current_object.location = (0.0, 0.0, 0.2)
    current_object.scale = (0.0, 0.0, 0.0)
    current_object.rotation_euler = (0.0, 0.0, -math.pi * (360.0 * 3.0 + 60.0) / 180.0)
    current_object.keyframe_insert(data_path='location', frame=4)
    current_object.keyframe_insert(data_path='scale', frame=4)
    current_object.keyframe_insert(data_path='rotation_euler', frame=4)
    current_object.location = (0.0, 0.0, 1.0)
    current_object.scale = (1.0, 1.0, 1.0)
    current_object.rotation_euler = (0.0, 0.0, -math.pi * 60.0 / 180.0)
    current_object.keyframe_insert(data_path='location', frame=42)
    current_object.keyframe_insert(data_path='scale', frame=42)
    current_object.keyframe_insert(data_path='rotation_euler', frame=42)

    current_object = utils.create_plane(size=12.0, name="Floor")
    current_object.data.materials.append(bpy.data.materials["Marble01"])

    bpy.ops.object.empty_add(location=(0.0, -0.70, 1.0))
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

## Suzannes
focus_target = set_scene_objects()

## Camera
bpy.ops.object.camera_add(location=(0.0, -16.0, 2.0))
camera_object = bpy.context.object

utils.add_track_to_constraint(camera_object, focus_target)
utils.set_camera_params(camera_object.data, focus_target, lens=85, fstop=0.5)

## Lights
utils.build_environment_texture_background(world, hdri_path)

## Composition
utils.build_scene_composition(scene)

# Animation Setting
utils.set_animation(scene, fps=24, frame_start=1, frame_end=48)

# Render Setting
utils.set_output_properties(scene, resolution_percentage, output_file_path)
utils.set_cycles_renderer(scene, camera_object, num_samples, use_motion_blur=True)
