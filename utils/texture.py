import bpy


def add_clouds_texture(name: str = "Clouds Texture",
                       size: float = 0.25,
                       depth: int = 2,
                       nabla: float = 0.025,
                       brightness: float = 1.0,
                       contrast: float = 1.0) -> bpy.types.CloudsTexture:
    '''
    https://docs.blender.org/api/current/bpy.types.BlendDataTextures.html
    https://docs.blender.org/api/current/bpy.types.Texture.html
    https://docs.blender.org/api/current/bpy.types.CloudsTexture.html
    '''

    # TODO: Check whether the name is already used or not

    tex = bpy.data.textures.new(name, type='CLOUDS')

    tex.noise_scale = size
    tex.noise_depth = depth
    tex.nabla = nabla

    tex.intensity = brightness
    tex.contrast = contrast

    return tex
