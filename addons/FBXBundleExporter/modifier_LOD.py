import bpy, bmesh
import math
import imp

from . import modifier
imp.reload(modifier) 




class Settings(modifier.Settings):
	active = bpy.props.BoolProperty (
		name="Active",
		default=False
	)
	levels = bpy.props.IntProperty (
		default=3,
		min=2,
		max=6,
		subtype='FACTOR'
	)
	quality = bpy.props.FloatProperty (
		default=0.05,
		min = 0.01,
		max = 1,
		description="Maximum quality ratio.",
		subtype='FACTOR'
	)


def get_quality(index, count, max_quality):
	return 1 - (index)/(count-1) * (1 - max_quality)


class Modifier(modifier.Modifier):
	label = "LOD"
	id = 'lod'
	url = "http://renderhjs.net/fbxbundle/#modifier_lod"

	def __init__(self):
		super().__init__()


	def draw(self, layout):
		super().draw(layout)
		if(self.get("active")):
			row = layout.row(align=True)
			row.prop( eval("bpy.context.scene."+self.settings_path()) , "levels", text="Steps", icon='AUTOMERGE_ON')
			row.prop( eval("bpy.context.scene."+self.settings_path()) , "quality", text="Quality", icon='AUTOMERGE_ON')

			col = layout.column(align=True)
			for i in range(0, self.get("levels")):
				r = col.row()
				r.enabled = False
				icon = 'MESH_UVSPHERE' if i==0 else 'MESH_ICOSPHERE'
				r.label(text="LOD{}".format(i), icon=icon)
				r = r.row()
				r.enabled = False
				r.alignment = 'RIGHT'
				r.label(text="{}%".format( math.ceil(get_quality(i, self.get("levels"), self.get("quality"))*100) ))
			# row_freeze = row.row()
			# row_freeze.enabled = self.get("merge_active")
			# row_freeze.prop( eval("bpy.context.scene."+self.settings_path()) , "merge_distance")


	def process_objects(self, name, objects):
		# UNITY 	https://docs.unity3d.com/Manual/LevelOfDetail.html
		# UNREAL 	https://docs.unrealengine.com/en-us/Engine/Content/Types/StaticMeshes/HowTo/LODs
		# 			https://answers.unrealengine.com/questions/416995/how-to-import-lods-as-one-fbx-blender.html

		new_objects = []
		for obj in objects:
			prefix = obj.name

			obj.name = "{}_LOD{}".format(prefix, 0)
			new_objects.append(obj)

			for i in range(1, self.get("levels")):

				# Select
				bpy.ops.object.select_all(action="DESELECT")
				obj.select_set(state = True)
				bpy.context.view_layer.objects.active = obj

				# Copy & Decimate modifier
				bpy.ops.object.duplicate()
				bpy.context.object.name = "{}_LOD{}".format(prefix, i)
				bpy.ops.object.modifier_add(type='DECIMATE')
				bpy.context.object.modifiers["Decimate"].ratio = get_quality(i, self.get("levels"), self.get("quality"))

				new_objects.append(bpy.context.object)

		return new_objects