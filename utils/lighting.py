import bpy


def create_area_light(location=(0.0, 0.0, 5.0),
                      rotation=(0.0, 0.0, 0.0),
                      size=5.0,
                      color=(1.00, 0.90, 0.80, 1.00),
                      strength=1000.0,
                      name=None):
    bpy.ops.object.lamp_add(type='AREA', location=location, rotation=rotation)
    bpy.context.object.name = "Main Light" if name is None else name
    light = bpy.context.object.data
    light.size = size
    light.use_nodes = True
    light.node_tree.nodes["Emission"].inputs["Color"].default_value = color
    light.node_tree.nodes["Emission"].inputs["Strength"].default_value = strength
    return light
