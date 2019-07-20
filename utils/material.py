import bpy
import utils


def create_texture_node(node_tree, path, is_color_data):
    # Instantiate a new texture image node
    texture_node = node_tree.nodes.new(type='ShaderNodeTexImage')

    # Open an image and set it to the node
    texture_node.image = bpy.data.images.load(path)

    # Set other parameters
    texture_node.color_space = 'COLOR' if is_color_data else 'NONE'

    # Return the node
    return texture_node


def set_principled_node(principled_node,
                        base_color=(0.6, 0.6, 0.6, 1.0),
                        subsurface=0.0,
                        subsurface_color=(0.8, 0.8, 0.8, 1.0),
                        subsurface_radius=(1.0, 0.2, 0.1),
                        metallic=0.0,
                        specular=0.5,
                        specular_tint=0.0,
                        roughness=0.5,
                        anisotropic=0.0,
                        anisotropic_rotation=0.0,
                        sheen=0.0,
                        sheen_tint=0.5,
                        clearcoat=0.0,
                        clearcoat_roughness=0.03,
                        ior=1.45,
                        transmission=0.0,
                        transmission_roughness=0.0):
    principled_node.inputs['Base Color'].default_value = base_color
    principled_node.inputs['Subsurface'].default_value = subsurface
    principled_node.inputs['Subsurface Color'].default_value = subsurface_color
    principled_node.inputs['Subsurface Radius'].default_value = subsurface_radius
    principled_node.inputs['Metallic'].default_value = metallic
    principled_node.inputs['Specular'].default_value = specular
    principled_node.inputs['Specular Tint'].default_value = specular_tint
    principled_node.inputs['Roughness'].default_value = roughness
    principled_node.inputs['Anisotropic'].default_value = anisotropic
    principled_node.inputs['Anisotropic Rotation'].default_value = anisotropic_rotation
    principled_node.inputs['Sheen'].default_value = sheen
    principled_node.inputs['Sheen Tint'].default_value = sheen_tint
    principled_node.inputs['Clearcoat'].default_value = clearcoat
    principled_node.inputs['Clearcoat Roughness'].default_value = clearcoat_roughness
    principled_node.inputs['IOR'].default_value = ior
    principled_node.inputs['Transmission'].default_value = transmission
    principled_node.inputs['Transmission Roughness'].default_value = transmission_roughness


def build_pbr_nodes(node_tree, base_color=(0.6, 0.6, 0.6, 1.0), metallic=0.0, specular=0.5, roughness=0.5, sheen=0.0):
    output_node = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    principled_node = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

    set_principled_node(principled_node=principled_node,
                        base_color=base_color,
                        metallic=metallic,
                        specular=specular,
                        roughness=roughness,
                        sheen=sheen)

    utils.arrange_nodes(node_tree)


def build_checker_board_nodes(node_tree, size):
    output_node = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    principled_node = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    checker_texture_node = node_tree.nodes.new(type='ShaderNodeTexChecker')

    set_principled_node(principled_node=principled_node)
    checker_texture_node.inputs['Scale'].default_value = size

    node_tree.links.new(checker_texture_node.outputs['Color'], principled_node.inputs['Base Color'])
    node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

    utils.arrange_nodes(node_tree)


def build_matcap_nodes(node_tree, image_path):
    tex_coord_node = node_tree.nodes.new(type='ShaderNodeTexCoord')
    vector_transform_node = node_tree.nodes.new(type='ShaderNodeVectorTransform')
    mapping_node = node_tree.nodes.new(type='ShaderNodeMapping')
    texture_image_node = create_texture_node(node_tree, image_path, True)
    emmission_node = node_tree.nodes.new(type='ShaderNodeEmission')
    output_node = node_tree.nodes.new(type='ShaderNodeOutputMaterial')

    frame = node_tree.nodes.new(type='NodeFrame')
    frame.name = "MatCap UV"
    frame.label = "MatCap UV"
    tex_coord_node.parent = frame
    vector_transform_node.parent = frame
    mapping_node.parent = frame

    vector_transform_node.vector_type = "VECTOR"
    vector_transform_node.convert_from = "OBJECT"
    vector_transform_node.convert_to = "CAMERA"

    mapping_node.vector_type = "TEXTURE"
    mapping_node.translation = (1.0, 1.0, 0.0)
    mapping_node.scale = (2.0, 2.0, 1.0)

    node_tree.links.new(tex_coord_node.outputs['Normal'], vector_transform_node.inputs['Vector'])
    node_tree.links.new(vector_transform_node.outputs['Vector'], mapping_node.inputs['Vector'])
    node_tree.links.new(mapping_node.outputs['Vector'], texture_image_node.inputs['Vector'])
    node_tree.links.new(texture_image_node.outputs['Color'], emmission_node.inputs['Color'])
    node_tree.links.new(emmission_node.outputs['Emission'], output_node.inputs['Surface'])

    utils.arrange_nodes(node_tree)


def build_pbr_textured_nodes(node_tree,
                             color_texture_path="",
                             metallic_texture_path="",
                             roughness_texture_path="",
                             normal_texture_path="",
                             displacement_texture_path="",
                             ambient_occlusion_texture_path="",
                             scale=(1.0, 1.0, 1.0)):
    output_node = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    principled_node = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

    coord_node = node_tree.nodes.new(type='ShaderNodeTexCoord')
    mapping_node = node_tree.nodes.new(type='ShaderNodeMapping')
    mapping_node.vector_type = 'TEXTURE'
    mapping_node.scale = scale
    node_tree.links.new(coord_node.outputs['UV'], mapping_node.inputs['Vector'])

    if color_texture_path != "":
        texture_node = create_texture_node(node_tree, color_texture_path, True)
        node_tree.links.new(mapping_node.outputs['Vector'], texture_node.inputs['Vector'])
        if ambient_occlusion_texture_path != "":
            ao_texture_node = create_texture_node(node_tree, ambient_occlusion_texture_path, False)
            node_tree.links.new(mapping_node.outputs['Vector'], ao_texture_node.inputs['Vector'])
            mix_node = node_tree.nodes.new(type='ShaderNodeMixRGB')
            mix_node.blend_type = 'MULTIPLY'
            node_tree.links.new(texture_node.outputs['Color'], mix_node.inputs['Color1'])
            node_tree.links.new(ao_texture_node.outputs['Color'], mix_node.inputs['Color2'])
            node_tree.links.new(mix_node.outputs['Color'], principled_node.inputs['Base Color'])
        else:
            node_tree.links.new(texture_node.outputs['Color'], principled_node.inputs['Base Color'])

    if metallic_texture_path != "":
        texture_node = create_texture_node(node_tree, metallic_texture_path, False)
        node_tree.links.new(mapping_node.outputs['Vector'], texture_node.inputs['Vector'])
        node_tree.links.new(texture_node.outputs['Color'], principled_node.inputs['Metallic'])

    if roughness_texture_path != "":
        texture_node = create_texture_node(node_tree, roughness_texture_path, False)
        node_tree.links.new(mapping_node.outputs['Vector'], texture_node.inputs['Vector'])
        node_tree.links.new(texture_node.outputs['Color'], principled_node.inputs['Roughness'])

    if normal_texture_path != "":
        texture_node = create_texture_node(node_tree, normal_texture_path, False)
        node_tree.links.new(mapping_node.outputs['Vector'], texture_node.inputs['Vector'])
        normal_map_node = node_tree.nodes.new(type='ShaderNodeNormalMap')
        node_tree.links.new(texture_node.outputs['Color'], normal_map_node.inputs['Color'])
        node_tree.links.new(normal_map_node.outputs['Normal'], principled_node.inputs['Normal'])

    if displacement_texture_path != "":
        texture_node = create_texture_node(node_tree, displacement_texture_path, False)
        node_tree.links.new(mapping_node.outputs['Vector'], texture_node.inputs['Vector'])
        node_tree.links.new(texture_node.outputs['Color'], output_node.inputs['Displacement'])

    utils.arrange_nodes(node_tree)
