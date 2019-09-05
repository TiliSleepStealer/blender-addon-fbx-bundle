import bpy, bmesh
import imp
import string
import random
from mathutils import Vector


from . import objects_organise

from . import modifier
imp.reload(modifier) 

class Settings(modifier.Settings):
	active = bpy.props.BoolProperty (
		name="Active",
		default=False
	)
	merge_verts = bpy.props.BoolProperty (
		name="Merge",
		description="Split meshes by material after merging.",
		default=False
	)
	merge_by_material = bpy.props.BoolProperty (
		name="By Material",
		description="Split meshes by material after merging.",
		default=False
	)

	merge_distance = bpy.props.FloatProperty (
		name="Dist.",
		default=0,
		min = 0,
		description="Minimum distance of verts to merge. Set to 0 to disable.",
		subtype='DISTANCE'
	)
	# consistent_normals = bpy.props.BoolProperty (
	# 	name="Make consistent Normals",
	# 	default=True
	# )



class Modifier(modifier.Modifier):
	label = "Merge Meshes"
	id = 'merge'
	url = "http://renderhjs.net/fbxbundle/#modifier_merge"
	
	def __init__(self):
		super().__init__()


	def draw(self, layout):
		super().draw(layout)
		if(self.get("active")):
			col = layout.column(align=True)

			row = col.row(align=True)
			row.separator()
			row.separator()
			row.prop( eval("bpy.context.scene."+self.settings_path()) , "merge_verts", text="Merge Verts")
			row_freeze = row.row()
			row_freeze.enabled = self.get("merge_verts")
			row_freeze.prop( eval("bpy.context.scene."+self.settings_path()) , "merge_distance")

			row = col.row(align=True)
			row.separator()
			row.separator()
			row.prop( eval("bpy.context.scene."+self.settings_path()) , "merge_by_material", text="Split by Material")


			
			


	def process_objects(self, name, objects):

		# Merge objects into single item
		if not objects_organise.get_objects_animation(objects):


			bpy.ops.object.join()
			bpy.context.object.name = name #assign bundle name
			bpy.context.scene.cursor.location = Vector((0,0,0)) 
			bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

			# Convert to mesh
			bpy.ops.object.convert(target='MESH')

			# Apply rotation
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
			

			# Merge Vertices?
			if self.get("merge_verts") and self.get("merge_distance") > 0:

				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
				bpy.ops.mesh.select_all(action='SELECT')

				bpy.ops.mesh.remove_doubles(threshold = self.get("merge_distance"))

				bpy.ops.mesh.quads_convert_to_tris()

				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')

			
			# if self.get("consistent_normals") :
			# 	bpy.ops.object.mode_set(mode='EDIT')
			# 	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
			# 	bpy.ops.mesh.select_all(action='SELECT')

			# 	bpy.ops.mesh.normals_make_consistent(inside=False)

			# 	bpy.ops.mesh.select_all(action='DESELECT')
			# 	bpy.ops.object.mode_set(mode='OBJECT')


			if self.get("merge_by_material") :
				# TODO: Split faces by materials

				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
				
				# Rename with unique ID
				prefix = "{}_{}".format( name, id_generator() )
				
				

				mats = {}
				for i in range(0, len(bpy.context.object.material_slots)):

					slot = bpy.context.object.material_slots[i]
					if slot.material and slot.material not in mats:
						# Store prefx by material
						prefix_mat = "{}_{}".format(prefix, slot.material.name)
						
						bpy.context.object.name = prefix_mat

						mat = slot.material 
						mats[mat] = prefix_mat

						if len(bpy.context.object.data.vertices) > 0:
							bpy.ops.mesh.select_all(action='DESELECT')
							bpy.context.object.active_material_index = i
							bpy.ops.object.material_slot_select()
							if len( [v for v in bpy.context.active_object.data.vertices if v.select] ) > 0:
								bpy.ops.mesh.separate(type='SELECTED')

				
				bpy.ops.object.mode_set(mode='OBJECT')

				mat_objs = []
				for obj in bpy.context.scene.objects:
					if prefix in obj.name:
						if len(obj.data.vertices) == 0:
							bpy.ops.object.select_all(action='DESELECT')
							obj.select_set(state = True)
							bpy.ops.object.delete()
						else:
							mat_objs.append(obj)

				# Combine & Rename by materials
				for mat in mats:
					prefix_mat = mats[mat]
					for obj in mat_objs:

						bpy.ops.object.select_all(action='DESELECT')
						bpy.context.view_layer.objects.active = obj
						obj.select_set(state = True)

						if prefix_mat in obj.name:

							for i in range( len(obj.material_slots)-1 ):
								bpy.ops.object.material_slot_remove()
							obj.material_slots[0].material = mat

							obj.name = "{}_{}".format(name, mat.name)

				# return material objects
				return mat_objs

			# Re-assign array
			objects = [bpy.context.object]


		return objects


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))