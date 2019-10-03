import bpy


def add_subdivision_surface_modifier(mesh, level, is_simple=False):
    modifier = mesh.modifiers.new(name="Subsurf", type='SUBSURF')
    modifier.levels = level
    modifier.render_levels = level
    modifier.subdivision_type = 'SIMPLE' if is_simple else 'CATMULL_CLARK'
