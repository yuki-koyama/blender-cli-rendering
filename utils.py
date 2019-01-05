import bpy

# Scene

def set_animation(scene, fps=24, frame_start=1, frame_end=48, frame_current=1):
	scene.render.fps = fps
	scene.frame_start = frame_start
	scene.frame_end = frame_end
	scene.frame_current = frame_current

def build_environmental_light(world, hdri_path):
	world.use_nodes = True
	node_tree = world.node_tree

	environment_texture_node = node_tree.nodes.new(type="ShaderNodeTexEnvironment")
	environment_texture_node.image = bpy.data.images.load(hdri_path)

	node_tree.links.new(environment_texture_node.outputs["Color"], node_tree.nodes["Background"].inputs["Color"])

	arrange_nodes(node_tree)

def set_cycles_renderer(scene, resolution_percentage, output_file_path, camera, num_samples, use_denoising=True, use_motion_blur=False):
	scene.render.image_settings.file_format = 'PNG'
	scene.render.resolution_percentage = resolution_percentage
	scene.render.engine = 'CYCLES'
	scene.render.filepath = output_file_path
	scene.render.use_freestyle = False
	scene.cycles.samples = num_samples
	scene.render.layers[0].cycles.use_denoising = use_denoising
	scene.camera = camera
	scene.render.use_motion_blur = use_motion_blur

# Composition

def define_vignette_node():
	group = bpy.data.node_groups.new(type="CompositorNodeTree", name="Vignette")

	input_node = group.nodes.new("NodeGroupInput")
	group.inputs.new("NodeSocketColor", "Image")
	group.inputs.new("NodeSocketFloat", "Amount")
	group.inputs["Amount"].default_value = 0.2
	group.inputs["Amount"].min_value = 0.0
	group.inputs["Amount"].max_value = 1.0

	lens_distortion_node = group.nodes.new(type="CompositorNodeLensdist")
	lens_distortion_node.inputs["Distort"].default_value = 1.000

	separate_rgba_node = group.nodes.new(type="CompositorNodeSepRGBA")

	blur_node = group.nodes.new(type="CompositorNodeBlur")
	blur_node.filter_type = 'GAUSS'
	blur_node.size_x = 300
	blur_node.size_y = 300
	blur_node.use_extended_bounds = True

	mix_node = group.nodes.new(type="CompositorNodeMixRGB")
	mix_node.blend_type = 'MULTIPLY'

	output_node = group.nodes.new("NodeGroupOutput")
	group.outputs.new("NodeSocketColor", "Image")

	group.links.new(input_node.outputs["Amount"], mix_node.inputs["Fac"])
	group.links.new(input_node.outputs["Image"], mix_node.inputs[1])
	group.links.new(input_node.outputs["Image"], lens_distortion_node.inputs["Image"])
	group.links.new(lens_distortion_node.outputs["Image"], separate_rgba_node.inputs["Image"])
	group.links.new(separate_rgba_node.outputs["A"], blur_node.inputs["Image"])
	group.links.new(blur_node.outputs["Image"], mix_node.inputs[2])
	group.links.new(mix_node.outputs["Image"], output_node.inputs["Image"])

	arrange_nodes(group)

def create_vignette_node(node_tree):
	define_vignette_node()

	vignette_node = node_tree.nodes.new(type='CompositorNodeGroup')
	vignette_node.name = "Vignette"
	vignette_node.node_tree = bpy.data.node_groups['Vignette']

	return vignette_node

def build_scene_composition(scene):
	scene.use_nodes = True
	clean_nodes(scene.node_tree.nodes)

	render_layer_node = scene.node_tree.nodes.new(type="CompositorNodeRLayers")

	vignette_node = create_vignette_node(scene.node_tree)

	lens_distortion_node = scene.node_tree.nodes.new(type="CompositorNodeLensdist")
	lens_distortion_node.inputs["Distort"].default_value = - 0.020
	lens_distortion_node.inputs["Dispersion"].default_value = 0.050

	color_correction_node = scene.node_tree.nodes.new(type="CompositorNodeColorCorrection")
	color_correction_node.master_saturation = 1.10
	color_correction_node.master_gain = 1.10

	glare_node = scene.node_tree.nodes.new(type="CompositorNodeGlare")
	glare_node.glare_type = 'FOG_GLOW'
	glare_node.quality = 'HIGH'

	composite_node = scene.node_tree.nodes.new(type="CompositorNodeComposite")

	scene.node_tree.links.new(render_layer_node.outputs['Image'], vignette_node.inputs['Image'])
	scene.node_tree.links.new(vignette_node.outputs['Image'], lens_distortion_node.inputs['Image'])
	scene.node_tree.links.new(lens_distortion_node.outputs['Image'], color_correction_node.inputs['Image'])
	scene.node_tree.links.new(color_correction_node.outputs['Image'], glare_node.inputs['Image'])
	scene.node_tree.links.new(glare_node.outputs['Image'], composite_node.inputs['Image'])

	arrange_nodes(scene.node_tree)

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

def add_copy_location_constraint(copy_to_object, copy_from_object, use_x, use_y, use_z, bone_name=''):
	constraint = copy_to_object.constraints.new(type='COPY_LOCATION')
	constraint.target = copy_from_object
	constraint.use_x = use_x
	constraint.use_y = use_y
	constraint.use_z = use_z
	if bone_name:
		constraint.subtarget = bone_name

# Node tree

def create_texture_node(node_tree, path, is_color_data):
	# Instantiate a new texture image node
	texture_node = node_tree.nodes.new(type='ShaderNodeTexImage')

	# Open an image and set it to the node
	texture_node.image = bpy.data.images.load(path)

	# Set other parameters
	texture_node.color_space = 'COLOR' if is_color_data else 'NONE'

	# Return the node
	return texture_node

def build_pbr_textured_nodes(
	node_tree, 
	color_texture_path="", 
	metallic_texture_path="", 
	roughness_texture_path="", 
	normal_texture_path="", 
	displacement_texture_path=""
):
	output_node = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
	principled_node = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
	node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

	if color_texture_path != "":
		texture_node = create_texture_node(node_tree, color_texture_path, True)
		node_tree.links.new(texture_node.outputs['Color'], principled_node.inputs['Base Color'])

	if metallic_texture_path != "":
		texture_node = create_texture_node(node_tree, metallic_texture_path, False)
		node_tree.links.new(texture_node.outputs['Color'], principled_node.inputs['Metallic'])

	if roughness_texture_path != "":
		texture_node = create_texture_node(node_tree, roughness_texture_path, False)
		node_tree.links.new(texture_node.outputs['Color'], principled_node.inputs['Roughness'])

	if normal_texture_path != "":
		texture_node = create_texture_node(node_tree, normal_texture_path, False)
		normal_map_node = node_tree.nodes.new(type='ShaderNodeNormalMap')
		node_tree.links.new(texture_node.outputs['Color'], normal_map_node.inputs['Color'])
		node_tree.links.new(normal_map_node.outputs['Normal'], principled_node.inputs['Normal'])

	if displacement_texture_path != "":
		texture_node = create_texture_node(node_tree, displacement_texture_path, False)
		node_tree.links.new(texture_node.outputs['Color'], output_node.inputs['Displacement'])

	arrange_nodes(node_tree)

# Misc.

def clean_nodes(nodes):
	for node in nodes:
		nodes.remove(node)

def arrange_nodes(node_tree):
	max_num_iters = 1000
	epsilon = 1e-05
	min_space = 50
	factor = 0.5

	# Gauss-Seidel-style iterations
	# Warning: Currently this function cares only simple horizontal overlaps
	for i in range(max_num_iters):
		total_energy = 0.0
		for link in node_tree.links:
			x_from = link.from_node.location[0]
			x_to = link.to_node.location[0]
			w_from = link.from_node.width
			current_space = x_to - x_from - w_from
			deviation = max(0.0, min_space - current_space)
			link.from_node.location[0] -= factor * (deviation / 2.0)
			link.to_node.location[0] += factor * (deviation / 2.0)
			total_energy += deviation * deviation
		if total_energy < epsilon:
			break
