import bpy
import bmesh
import operator
import mathutils
from mathutils import Vector


class Platform:
	label = "Platform"
	extension = 'fbx'

	def __init__(self):
		pass


	def get_filename(self, filename):
		return "{}.{}".format(filename, self.extension)


	def is_valid(self):
		return True, ""


	def file_export(self, path):
		print("{} export {}".format(self.label, path))
		



		'''
		# Axis vectors for different platforms
		axis_forward, axis_up = 'Y', 'Z' #Default
		if target_platform == 'UNITY':
			axis_forward = '-Z'
			axis_up = 'Y'

        # Space transform baking. Info: https://docs.blender.org/api/blender_python_api_2_70_5/bpy.ops.export_scene.html
		bake_transform = False #Default
		if target_platform == 'UNITY':
			bake_transform = True 
		
		# Scale options
		scale_options = 'FBX_SCALE_ALL' #Default
		if target_platform == 'UNREAL':
			scale_options = 'FBX_SCALE_NONE'
		elif target_platform == 'UNITY':
			scale_options = 'FBX_SCALE_ALL'

		# Smooth type
		smooth_type = 'OFF' #Default
		if target_platform == 'UNREAL':
			smooth_type = 'FACE'
		elif target_platform == 'UNITY':
			smooth_type = 'FACE'


		# Export selected as FBX
		bpy.ops.export_scene.fbx(
			filepath=path + ".fbx", 
			use_selection=True, 
			
			axis_forward=axis_forward, 
			axis_up=axis_up, 

			object_types={'ARMATURE', 'MESH', 'EMPTY'},

			apply_scale_options = scale_options,
			global_scale =1.00, 
			apply_unit_scale=True,

			use_mesh_modifiers=True, 
			mesh_smooth_type = smooth_type, 
			batch_mode='OFF', 
			use_custom_props=False,

 			bake_space_transform = bake_transform
		)
		'''

	# def file_import(self, path)
	# 	print("import {}".format(path))








	# def file_import(self, path):
	# 	print("{} import {}".format(self.label, path))

