import bpy
import bmesh
import operator
import mathutils

from . import platform

class Platform(platform.Platform):
	extension = 'fbx'


	def __init__(self):
		super().__init__()


	def is_valid(self):
		if bpy.context.scene.unit_settings.system != 'METRIC':
			return False, "Scene units not metric"

		elif bpy.context.scene.unit_settings.scale_length != 1.00:
			return False, "Unit scale is not set to 1.00"

		return True, ""


	def file_export(self, path):
		bpy.ops.export_scene.fbx(
			filepath		=path, 
			use_selection	=True, 
			
			axis_forward	='-Z', 
			axis_up			='Y', 

			object_types={'ARMATURE', 'MESH', 'EMPTY'},

			apply_scale_options = 'FBX_SCALE_ALL' ,
			global_scale =1.00, 
			apply_unit_scale=True,

			use_mesh_modifiers=True, 
			mesh_smooth_type = 'FACE', 
			batch_mode='OFF', 
			use_custom_props=False,

 			bake_space_transform = True
		)
