import bpy
import mathutils

################################################################################
# Scene
################################################################################

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

def set_cycles_renderer(scene, resolution_percentage, output_file_path, camera, num_samples, use_denoising=True, use_motion_blur=False, use_transparent_bg=False):
	scene.render.image_settings.file_format = 'PNG'
	scene.render.resolution_percentage = resolution_percentage
	scene.render.engine = 'CYCLES'
	scene.render.filepath = output_file_path
	scene.render.use_freestyle = False
	scene.cycles.samples = num_samples
	scene.render.layers[0].cycles.use_denoising = use_denoising
	scene.camera = camera
	scene.render.use_motion_blur = use_motion_blur
	scene.cycles.film_transparent = use_transparent_bg

def set_camera_params(camera, focus_target):
	# Simulate Sony's FE 85mm F1.4 GM
	camera.data.sensor_fit = 'HORIZONTAL'
	camera.data.sensor_width = 36.0
	camera.data.sensor_height = 24.0
	camera.data.lens = 85
	camera.data.dof_object = focus_target
	camera.data.cycles.aperture_type = 'FSTOP'
	camera.data.cycles.aperture_fstop = 1.4
	camera.data.cycles.aperture_blades = 11

################################################################################
# Composition
################################################################################

def add_vignette_node_group():
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

	return group

def create_vignette_node(node_tree):
	vignette_node_group = add_vignette_node_group()

	vignette_node = node_tree.nodes.new(type='CompositorNodeGroup')
	vignette_node.name = "Vignette"
	vignette_node.node_tree = vignette_node_group

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

################################################################################
# Modifiers
################################################################################

def add_subdivision_surface_modifier(mesh, level, is_simple=False):
	modifier = mesh.modifiers.new(name="Subsurf", type='SUBSURF')
	modifier.levels = level
	modifier.render_levels = level
	modifier.subdivision_type = 'SIMPLE' if is_simple else 'CATMULL_CLARK'

################################################################################
# Constraints
################################################################################

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

################################################################################
# Shading
################################################################################

def create_texture_node(node_tree, path, is_color_data):
	# Instantiate a new texture image node
	texture_node = node_tree.nodes.new(type='ShaderNodeTexImage')

	# Open an image and set it to the node
	texture_node.image = bpy.data.images.load(path)

	# Set other parameters
	texture_node.color_space = 'COLOR' if is_color_data else 'NONE'

	# Return the node
	return texture_node

def set_principled_node(
	principled_node,
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
	transmission_roughness=0.0
):
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

def build_pbr_nodes(
	node_tree,
	base_color=(0.6, 0.6, 0.6, 1.0),
	metallic=0.0,
	specular=0.5,
	roughness=0.5,
	sheen=0.0
):
	output_node = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
	principled_node = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
	node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

	set_principled_node(
		principled_node=principled_node,
		base_color=base_color,
		metallic=metallic,
		specular=specular,
		roughness=roughness,
		sheen=sheen
	)

	arrange_nodes(node_tree)

def build_pbr_textured_nodes(
	node_tree,
	color_texture_path="",
	metallic_texture_path="",
	roughness_texture_path="",
	normal_texture_path="",
	displacement_texture_path="",
	ambient_occlusion_texture_path="",
	scale=(1.0, 1.0, 1.0)
):
	output_node = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
	principled_node = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
	node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

	coord_node = node_tree.nodes.new(type='ShaderNodeTexCoord')
	mapping_node = node_tree.nodes.new(type='ShaderNodeMapping')
	mapping_node.vector_type = 'TEXTURE'
	mapping_node.scale = scale
	node_tree.links.new(coord_node.outputs['Generated'], mapping_node.inputs['Vector'])

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

	arrange_nodes(node_tree)

################################################################################
# Armature
################################################################################

def create_armature_mesh(scene, armature_object, mesh_name):
	assert armature_object.type == 'ARMATURE', 'Error'
	assert len(armature_object.data.bones) != 0, 'Error'

	def add_rigid_vertex_group(target_object, name, vertex_indices):
		new_vertex_group = target_object.vertex_groups.new(name)
		for vertex_index in vertex_indices:
			new_vertex_group.add([ vertex_index ], 1.0, 'REPLACE')

	def generate_bone_mesh_pydata(radius, length):
		base_radius = radius
		top_radius = 0.5 * radius

		vertices = [
			# Cross section of the base part
			mathutils.Vector((- base_radius, 0.0, + base_radius)),
			mathutils.Vector((+ base_radius, 0.0, + base_radius)),
			mathutils.Vector((+ base_radius, 0.0, - base_radius)),
			mathutils.Vector((- base_radius, 0.0, - base_radius)),

			# Cross section of the top part
			mathutils.Vector((- top_radius, length, + top_radius)),
			mathutils.Vector((+ top_radius, length, + top_radius)),
			mathutils.Vector((+ top_radius, length, - top_radius)),
			mathutils.Vector((- top_radius, length, - top_radius)),

			# End points
			mathutils.Vector((0.0, - base_radius, 0.0)),
			mathutils.Vector((0.0, length + top_radius, 0.0))
		]

		faces = [
			# End point for the base part
			(8, 1, 0),
			(8, 2, 1),
			(8, 3, 2),
			(8, 0, 3),

			# End point for the top part
			(9, 4, 5),
			(9, 5, 6),
			(9, 6, 7),
			(9, 7, 4),

			# Side faces
			(0, 1, 5, 4),
			(1, 2, 6, 5),
			(2, 3, 7, 6),
			(3, 0, 4, 7)
		]

		return vertices, faces

	armature_data = armature_object.data

	vertices = []
	faces = []
	vertex_groups = []

	for bone in armature_data.bones:
		radius = 0.10 * (0.10 + bone.length)
		temp_vertices, temp_faces = generate_bone_mesh_pydata(radius, bone.length)

		vertex_index_offset = len(vertices)

		temp_vertex_group = { 'name': bone.name, 'vertex_indices': [] }
		for local_index, vertex in enumerate(temp_vertices):
			vertices.append(bone.matrix_local * vertex)
			temp_vertex_group['vertex_indices'].append(local_index + vertex_index_offset)
		vertex_groups.append(temp_vertex_group)

		for face in temp_faces:
			if len(face) == 3:
				faces.append((face[0] + vertex_index_offset, face[1] + vertex_index_offset, face[2] + vertex_index_offset))
			else:
				faces.append((face[0] + vertex_index_offset, face[1] + vertex_index_offset, face[2] + vertex_index_offset, face[3] + vertex_index_offset))

	new_object = create_mesh_from_pydata(scene, vertices, faces, mesh_name, mesh_name)
	new_object.matrix_world = armature_object.matrix_world

	for vertex_group in vertex_groups:
		add_rigid_vertex_group(new_object, vertex_group['name'], vertex_group['vertex_indices'])

	armature_modifier = new_object.modifiers.new('Armature', 'ARMATURE')
	armature_modifier.object = armature_object
	armature_modifier.use_vertex_groups = True

	add_subdivision_surface_modifier(new_object, 1, is_simple=True)
	add_subdivision_surface_modifier(new_object, 2, is_simple=False)

	# Set the armature as the parent of the new object
	bpy.ops.object.select_all(action='DESELECT')
	new_object.select = True
	armature_object.select = True
	bpy.context.scene.objects.active = armature_object
	bpy.ops.object.parent_set(type='OBJECT')

	return new_object

################################################################################
# Mesh
################################################################################

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

################################################################################
# Misc.
################################################################################

def set_smooth_shading(target_object):
	for polygon in target_object.data.polygons:
		polygon.use_smooth = True

def clean_objects():
	for item in bpy.data.objects:
		bpy.data.objects.remove(item)

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
