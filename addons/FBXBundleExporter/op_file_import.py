import bpy, bmesh
import os
import mathutils
from mathutils import Vector

from . import objects_organise

class op(bpy.types.Operator):
	bl_idname = "fbxbundle.file_import"
	bl_label = "Import"
	bl_description = "Import multiple objects"

	@classmethod
	def poll(cls, context):

		if context.space_data.local_view:
			return False
		
		if bpy.context.scene.FBXBundleSettings.path == "":
			return False
			
		return True

	def execute(self, context):
		import_files(bpy.context.scene.FBXBundleSettings.path)
		return {'FINISHED'}



def import_files(path):
	# https://blender.stackexchange.com/questions/5064/how-to-batch-import-wavefront-obj-files
	# http://ricardolovelace.com/batch-import-and-export-obj-files-in-blender.html
	path = bpy.path.abspath(path)

	extensions = ['fbx', 'obj', '3ds']


	filenames = sorted(os.listdir(path))
	filenames_valid = []

	for filename in filenames:
		for ext in extensions:
			if filename.lower().endswith('.{}'.format(ext)):
				filenames_valid.append(filename)
				break


	for name in filenames_valid:
		file_path = os.path.join(path, name)
		extension = (os.path.splitext(file_path)[1])[1:].lower()
		print("- {} = {}".format(extension, file_path))

		try:
			# https://docs.blender.org/api/2.78a/bpy.ops.import_scene.html
			if extension == 'fbx':
				if hasattr(bpy.types, bpy.ops.import_scene.fbx.idname()):
					bpy.ops.import_scene.fbx(filepath = file_path)

			elif extension == 'obj':
				if hasattr(bpy.types, bpy.ops.import_scene.obj.idname()):
					bpy.ops.import_scene.obj(filepath = file_path)
					
			elif extension == '3ds':
				if hasattr(bpy.types, bpy.ops.import_scene.autodesk_3ds.idname()):
					bpy.ops.import_scene.autodesk_3ds(filepath = file_path)
					
		except RuntimeError:
			print("Error importing {}".format(file_path))
