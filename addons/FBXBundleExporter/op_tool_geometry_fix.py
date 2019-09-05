import bpy, bmesh
import os
import mathutils
from mathutils import Vector
import operator
import math

from . import objects_organise
from . import gp_draw



class op(bpy.types.Operator):
	bl_idname = "fbxbundle.fix_geometry"
	bl_label = "Fix Imported Geometry"
	bl_description = "Remove custom splitnormals, consistent normals, fix exceeding > 8 UV coordinates"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		print ("Fix Geometry")


		objects = bpy.context.selected_objects
		for obj in objects:
			if obj.type == 'MESH':
				# Select object
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.context.view_layer.objects.active = obj
				bpy.ops.object.select_all(action="DESELECT")
				obj.select_set(state = True)
				
				# Enable auto smooth
				bpy.context.object.data.use_auto_smooth = True
				bpy.context.object.data.auto_smooth_angle = 30 * math.pi / 180


				# Clear custom normals data
				bpy.ops.mesh.customdata_custom_splitnormals_clear()

				bpy.ops.object.mode_set(mode='EDIT')

				# Remove doubles
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.mesh.remove_doubles()

				# Smooth faces
				bpy.ops.mesh.faces_shade_smooth()


				# Recalculate Normals
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
				bpy.ops.mesh.normals_make_consistent(inside=False)

				#Limit UV's to not exceed a value
				bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
				uv_layer = bm.loops.layers.uv.verify()
				
				limit = 8.00
				for face in bm.faces:
					for loop in face.loops:
						uv = loop[uv_layer].uv
						if(abs(uv.x) > limit):
							uv.x = limit * abs(uv.x)/uv.x
						if(abs(uv.y) > limit):
							uv.y = limit * abs(uv.y)/uv.y

				bpy.ops.mesh.select_all(action='DESELECT')
			
		# Restore selection
		bpy.ops.object.mode_set(mode = 'OBJECT')
		bpy.ops.object.select_all(action="DESELECT")
		for obj in objects:
			obj.select_set(state = True)

		return {'FINISHED'}

