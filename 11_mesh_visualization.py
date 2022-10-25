# blender --background --python 11_mesh_visualization.py --render-frame 1 -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os
import random

import mathutils
import numpy as np
from typing import List, Tuple

working_dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_dir_path)

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


def set_scene_objects(model_path: str = None,
                      model_location: mathutils.Vector = (0.0, 0.0, 0.0),
                      model_rotation: mathutils.Vector = (0.0, 0.0, 0.0),
                      model_scale: mathutils.Vector = (1, 1, 1),
                      subdivision_level: int = 1) -> bpy.types.Object:
    # Instantiate a floor plane
    utils.create_plane(size=200.0, location=(0.0, 0.0, -1.0))

    # Instantiate a triangle mesh
    if model_path is None:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivision_level)
    else:
        utils.import_mesh(model_path, "mesh_visualization")

    current_object = bpy.context.object
    if current_object is None:
        return None

    # Set RTS
    current_object.rotation_euler = model_rotation * 1.0 / 180.0 * np.pi
    current_object.scale = model_scale

    mesh = current_object.data

    # Add modifier
    utils.add_wireframe_modifier(current_object, 0.007)

    return bpy.context.object


if __name__ == "__main__":
    # Args
    parser = utils.ArgumentParserForBlender()
    parser.add_argument("--input_model", type=str,
                        default='/Users/lihongbo/Desktop/code/BlenderToolbox/meshes/spot.ply',
                        help='Input model path')
    parser.add_argument("--output_path", type=str, default='out/mesh_visualization_', help='Output path for the file')
    parser.add_argument("--resolution_percentage", type=int, default='50',
                        help='Resolution percentage for output image')
    parser.add_argument("--num_samples", type=int, default='200', help='Sampes')
    parser.add_argument("--purpose", type=str, default="both")

    opt = parser.parse_args()

    output_file_path = os.path.join(os.getcwd(), opt.output_path)
    resolution_percentage = opt.resolution_percentage
    num_samples = opt.num_samples

    # Parameters
    hdri_path = os.path.join(working_dir_path, "assets/HDRIs/white.jpeg")

    # Scene Building
    scene = bpy.data.scenes["Scene"]
    world = scene.world

    ## Reset
    utils.clean_objects()

    ## Object
    focus_target_object = set_scene_objects(model_path=opt.input_model,
                                            model_location=mathutils.Vector((1.12, -0.14, 0)),
                                            model_rotation=mathutils.Vector((90, 0, 227)),
                                            model_scale=mathutils.Vector((1.5, 1.5, 1.5)))
    if focus_target_object is None:
        print("Import Model Failed.")

    ## Camera
    camera_object = utils.create_camera(location=(4, 0, 3))

    # utils.add_track_to_constraint(camera_object, focus_target_object)
    utils.set_camera_params(camera_object.data, focus_target_object, lens=45, fstop=0.5)

    ## Lights
    utils.build_environment_texture_background(world, hdri_path)

    # Render Setting
    utils.set_output_properties(scene, resolution_percentage, output_file_path)
    utils.set_cycles_renderer(scene, camera_object, num_samples, prefer_cuda_use=False, use_transparent_bg=True)

    lookAtLocation = (0, 0, 1)
    utils.look_at(camera_object, mathutils.Vector(lookAtLocation))

    if opt.purpose == "save_blend":
        bpy.ops.wm.save_mainfile(filepath=os.path.join(os.getcwd(), "out/test.blend"))
    elif opt.purpose == "rendering":
        bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.wm.save_mainfile(filepath=os.path.join(os.getcwd(), "out/test.blend"))
        bpy.ops.render.render(write_still=True)
