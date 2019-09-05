import bpy, bmesh
import os
import mathutils
from mathutils import Vector

from . import gp_draw

class op(bpy.types.Operator):
	bl_idname = "fbxbundle.fence_clear"
	bl_label = "Clear Fences"
	bl_description = "Clears all drawn fences in the scene"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		gp_draw.clear()
		return {'FINISHED'}
