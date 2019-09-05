import bpy, bmesh
import os
import mathutils
import math
from mathutils import Vector

from . import objects_organise

class op(bpy.types.Operator):
	bl_idname = "fbxbundle.file_open_folder"
	bl_label = "Open Folder"
	bl_description = "Open the specified folder"

	@classmethod
	def poll(cls, context):
		if bpy.context.scene.FBXBundleSettings.path == "":
			return False

		return True

	def execute(self, context):
		open_folder(self, bpy.context.scene.FBXBundleSettings.path)
		
		return {'FINISHED'}



def open_folder(self, path):

	path = os.path.dirname( bpy.path.abspath( path ))
	
	# Warnings
	if not os.path.exists(path):
		self.report({'ERROR_INVALID_INPUT'}, "Path doesn't exist." )
		return

	# Open Folder
	os.startfile(path)


	print("Open path on system "+path)




