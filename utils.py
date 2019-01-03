import bpy

# Modifiers

def add_subdivision_surface_modifier(mesh, level, is_simple=False):
	modifier = mesh.modifiers.new(name="Subsurf", type='SUBSURF')
	modifier.levels = level
	modifier.render_levels = level
	modifier.subdivision_type = 'SIMPLE' if is_simple else 'CATMULL_CLARK'

# Constraints

def add_track_to_constraint(camera, track_to_target):
	constraint = camera.constraints.new(type='TRACK_TO')
	constraint.target = track_to_target
	constraint.track_axis = 'TRACK_NEGATIVE_Z'
	constraint.up_axis = 'UP_Y'
