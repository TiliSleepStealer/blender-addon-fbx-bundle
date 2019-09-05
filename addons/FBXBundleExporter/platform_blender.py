import bpy
import bmesh
import operator
import mathutils

from . import platform

class Platform(platform.Platform):
	label = "Blender"
	extension = 'dae'

	def __init__(self):
		super().__init__()
		

	def file_export(self, path):
		# bpy.ops.export_scene.selected(exporter_str="BLEND", use_file_browser=True)
		bpy.ops.wm.collada_export(
			filepath		= path,
			selected 		= True,
			apply_modifiers = True,

			include_children =False,
			include_armatures=False,
			include_shapekeys=True
		)
		'''
		bpy.ops.wm.collada_export(
			filepath="",
			check_existing=True,
			filter_blender=False,
			filter_backup=False,
			filter_image=False,
			filter_movie=False,
			filter_python=False,
			filter_font=False,
			filter_sound=False,
			filter_text=False,
			filter_btx=False,
			filter_collada=True,
			filter_alembic=False,
			filter_folder=True,
			filter_blenlib=False,
			filemode=8,
			display_type='DEFAULT',
			sort_method='FILE_SORT_ALPHA',
			apply_modifiers=False,
			export_mesh_type=0,
			export_mesh_type_selection='view',
			selected=False,
			include_children=False,
			include_armatures=False,
			include_shapekeys=True,
			deform_bones_only=False,
			active_uv_only=False,
			use_texture_copies=True,
			triangulate=True,
			use_object_instantiation=True,
			use_blender_profile=True,
			sort_by_name=False,
			export_transformation_type=0,
			export_transformation_type_selection='matrix',
			export_texture_type=0,
			export_texture_type_selection='mat',
			open_sim=False,
			limit_precision=False,
			keep_bind_info=False
		)
		'''