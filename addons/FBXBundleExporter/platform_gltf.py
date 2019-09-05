import bpy
import bmesh
import operator
import mathutils
import addon_utils

from . import platform

class Platform(platform.Platform):
	extension = 'gltf'


	def __init__(self):
		super().__init__()
		

	def is_valid(self):
		# Plugin available for FLTF?
		mode = bpy.context.scene.FBXBundleSettings.target_platform
		if 'io_scene_gltf2' not in addon_utils.addons_fake_modules:
			return False, "GLTF addon not installed"

		if not addon_utils.check("io_scene_gltf2")[1]:
			return False, "GLTF addon not enabled"

		return True, ""


	def file_export(self, path):
		bpy.ops.export_scene.gltf(
			filepath		=path, 
			export_selected	=True, 
			
			export_apply=True
		)

		'''
		bpy.ops.export_scene.gltf(
			export_morph=True,
			export_colors=True,
			export_skins=True,
			export_morph_normal=True,
			export_force_sampling=False,
			export_frame_range=True,
			export_displacement=False,
			export_force_indices=False,
			export_copyright="",
			export_texcoords=True,
			export_bake_skins=False,
			export_indices='UNSIGNED_INT',
			export_tangents=True,
			export_apply=False,
			export_camera_infinite=False,
			export_animations=True,
			export_embed_images=False,
			export_cameras=False,
			export_yup=True,
			export_morph_tangent=True,
			export_frame_step=1,
			export_lights=False,
			export_materials=True,
			export_normals=True,
			export_current_frame=True,
			export_extras=False,
			export_layers=True,
			export_move_keyframes=True,
			export_embed_buffers=False,
			export_selected=False,
			filepath="",
			check_existing=True,
			filter_glob="*.gltf"
		)
		'''
