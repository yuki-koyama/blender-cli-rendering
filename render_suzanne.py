# blender --background --python render_suzanne.py -- </path/to/output/image> <resolution_percentage>

import bpy
import sys
from math import pi

# Args

output_file_path = str(sys.argv[sys.argv.index('--') + 1])
resolution_percentage = int(sys.argv[sys.argv.index('--') + 2])

# Render Setting

bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.resolution_percentage = resolution_percentage
bpy.data.scenes["Scene"].render.engine = 'CYCLES'
bpy.data.scenes["Scene"].render.filepath = output_file_path
bpy.context.scene.render.use_freestyle = False

# Scene Building

for item in bpy.data.objects:
	bpy.data.objects.remove(item)

for index in range(5):
	bpy.ops.mesh.primitive_monkey_add(location=((index - 2) * 3.0, 0, 0))

bpy.ops.object.camera_add(view_align=False, location=[0.0, -15.0, 0.0], rotation=[pi * 0.5, 0.0, 0.0])
bpy.context.scene.camera = bpy.context.object

bpy.ops.object.lamp_add(type='SUN', location=[0.0, 0.0, 0.0], rotation=[0.0, pi * 0.5, 0.0])

# Rendering

bpy.ops.render.render(animation=False, write_still=True)
