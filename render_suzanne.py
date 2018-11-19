# blender --background --python render_suzanne.py -- </path/to/output/image> <resolution_percentage>

import bpy
import sys
import math

# Args

output_file_path = str(sys.argv[sys.argv.index('--') + 1])
resolution_percentage = int(sys.argv[sys.argv.index('--') + 2])

# Scene Building

## Reset

for item in bpy.data.objects:
	bpy.data.objects.remove(item)

## Suzannes

num_suzannes = 15

for index in range(num_suzannes):
	bpy.ops.mesh.primitive_monkey_add(location=((index - (num_suzannes - 1) / 2) * 3.0, 0.0, 0.0))
	bpy.context.object.name = "Suzanne" + str(index)
	bpy.ops.object.modifier_add(type='SUBSURF')
	bpy.context.object.modifiers["Subsurf"].levels = 3
	bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")

center_suzanne = bpy.data.objects["Suzanne" + str(int((num_suzannes - 1) / 2))]

## Camera

bpy.ops.object.camera_add(view_align=False, location=[10.0, - 7.0, 0.0])
camera = bpy.context.object

bpy.ops.object.constraint_add(type='TRACK_TO')
camera.constraints["Track To"].target = center_suzanne
camera.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
camera.constraints["Track To"].up_axis = 'UP_Y'

camera.data.sensor_fit = 'HORIZONTAL'
camera.data.sensor_width = 36.0
camera.data.lens = 50
camera.data.dof_object = center_suzanne
camera.data.cycles.aperture_type = 'FSTOP'
camera.data.cycles.aperture_fstop = 1.2

# Render Setting

scene = bpy.data.scenes["Scene"]

scene.render.image_settings.file_format = 'PNG'
scene.render.resolution_percentage = resolution_percentage
scene.render.engine = 'CYCLES'
scene.render.filepath = output_file_path
scene.render.use_freestyle = False
scene.camera = camera

## Lights

bpy.ops.object.lamp_add(type='SUN', location=[0.0, 0.0, 0.0], rotation=[0.0, math.pi * 0.5, - math.pi * 0.1])

# Rendering

bpy.ops.render.render(animation=False, write_still=True)
