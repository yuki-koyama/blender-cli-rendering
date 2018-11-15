# blender --background --python render_cube.py -- </path/to/output/image> <resolution_percentage>

import bpy
import sys

# Args

output_file_path = str(sys.argv[sys.argv.index('--') + 1])
resolution_percentage = int(sys.argv[sys.argv.index('--') + 2])

# Setting

bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.resolution_percentage = resolution_percentage
bpy.data.scenes["Scene"].render.engine = 'CYCLES'
bpy.data.scenes["Scene"].render.filepath = output_file_path
bpy.context.scene.render.use_freestyle = False

# Rendering

bpy.ops.render.render(animation=False, write_still=True)
