# blender --background --python 08_animation.py -- </path/to/output/directory>/<name> <resolution_percentage> <num_samples>
# ffmpeg -r 24 -i </path/to/output/directory>/<name>%04d.png -pix_fmt yuv420p out.mp4

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils
import assets


def set_scene_objects():
    bpy.ops.mesh.primitive_monkey_add(location=(0.0, 0.0, 1.0),
                                      rotation=(0.0, 0.0, -math.pi * 60.0 / 180.0),
                                      calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Suzanne_Center"
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 2)
    mat = bpy.data.materials.new("Material_Center")
    mat.use_nodes = True
    utils.clean_nodes(mat.node_tree.nodes)
    assets.build_pbr_textured_nodes(mat.node_tree, "Metal07")
    current_object.data.materials.append(mat)

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

    bpy.ops.mesh.primitive_plane_add(radius=6.0, calc_uvs=True)
    current_object = bpy.context.object
    current_object.name = "Floor"
    mat = bpy.data.materials.new("Material_Plane")
    mat.use_nodes = True
    utils.clean_nodes(mat.node_tree.nodes)
    assets.build_pbr_textured_nodes(mat.node_tree, "Marble01")
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

# Animation Setting
utils.set_animation(scene, fps=24, frame_start=1, frame_end=48)

# Render Setting
utils.set_cycles_renderer(scene,
                          resolution_percentage,
                          output_file_path,
                          camera,
                          num_samples,
                          use_denoising=True,
                          use_motion_blur=True)

# Render
bpy.ops.render.render(animation=True)
