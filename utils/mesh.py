import bpy


def set_smooth_shading(target_object):
    for polygon in target_object.data.polygons:
        polygon.use_smooth = True


def create_mesh_from_pydata(scene, vertices, faces, mesh_name, object_name, use_smooth=True):
    # Add a new mesh and set vertices and faces
    # In this case, it does not require to set edges
    # After manipulating mesh data, update() needs to be called
    new_mesh = bpy.data.meshes.new(mesh_name)
    new_mesh.from_pydata(vertices, [], faces)
    new_mesh.update()

    new_object = bpy.data.objects.new(mesh_name, new_mesh)
    scene.objects.link(new_object)

    if use_smooth:
        set_smooth_shading(new_object)

    return new_object


def create_cached_mesh_from_alembic(file_path, name):
    bpy.ops.wm.alembic_import(filepath=file_path, as_background_job=False)
    bpy.context.active_object.name = name

    return bpy.context.active_object
