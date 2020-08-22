import bpy


def add_boolean_modifier(mesh_object: bpy.types.Object,
                         another_mesh_object: bpy.types.Object,
                         operation: str = "DIFFERENCE") -> None:
    '''
    https://docs.blender.org/api/current/bpy.types.BooleanModifier.html
    '''

    modifier: bpy.types.SubsurfModifier = mesh_object.modifiers.new(name="Boolean", type='BOOLEAN')

    modifier.object = another_mesh_object
    modifier.operation = operation


def add_subdivision_surface_modifier(mesh_object: bpy.types.Object, level: int, is_simple: bool = False) -> None:
    '''
    https://docs.blender.org/api/current/bpy.types.SubsurfModifier.html
    '''

    modifier: bpy.types.SubsurfModifier = mesh_object.modifiers.new(name="Subsurf", type='SUBSURF')

    modifier.levels = level
    modifier.render_levels = level
    modifier.subdivision_type = 'SIMPLE' if is_simple else 'CATMULL_CLARK'


def add_solidify_modifier(mesh_object: bpy.types.Object,
                          thickness: float = 0.01,
                          flip_normal: bool = False,
                          fill_rim: bool = True,
                          material_index_offset: int = 0,
                          shell_vertex_group: str = "",
                          rim_vertex_group: str = "") -> None:
    '''
    https://docs.blender.org/api/current/bpy.types.SolidifyModifier.html
    '''

    modifier: bpy.types.SolidifyModifier = mesh_object.modifiers.new(name="Solidify", type='SOLIDIFY')

    modifier.material_offset = material_index_offset
    modifier.thickness = thickness
    modifier.use_flip_normals = flip_normal
    modifier.use_rim = fill_rim

    # TODO: Check whether shell_vertex_group is either empty or defined
    # TODO: Check whether rim_vertex_group is either empty or defined

    modifier.shell_vertex_group = shell_vertex_group
    modifier.rim_vertex_group = rim_vertex_group


def add_displace_modifier(mesh_object: bpy.types.Object,
                          texture_name: str,
                          vertex_group: str = "",
                          mid_level: float = 0.5,
                          strength: float = 1.0) -> None:
    '''
    https://docs.blender.org/api/current/bpy.types.DisplaceModifier.html
    '''

    modifier = mesh_object.modifiers.new(name="Displace", type='DISPLACE')

    modifier.mid_level = mid_level
    modifier.strength = strength

    # TODO: Check whether texture_name is properly defined
    modifier.texture = bpy.data.textures[texture_name]

    # TODO: Check whether vertex_group is either empty or defined
    modifier.vertex_group = vertex_group
