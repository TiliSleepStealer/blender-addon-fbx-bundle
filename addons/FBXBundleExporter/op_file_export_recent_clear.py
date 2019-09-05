import bpy, bmesh
import os
import mathutils
import math

class op(bpy.types.Operator):
	bl_idname = "fbxbundle.file_export_recent_clear"
	bl_label = "Clear recent"
	bl_description = "Clear recent Re-Export."

	@classmethod
	def poll(cls, context):

		if len(bpy.context.scene.FBXBundleSettings.recent) == 0:
			return False

		return True

	def execute(self, context):
		bpy.context.scene.FBXBundleSettings.recent = ""
		return {'FINISHED'}
