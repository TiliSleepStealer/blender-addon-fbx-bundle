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
	ratio = bpy.props.FloatProperty (
		default=0.35,
		min = 0.01,
		max = 1,
		description="Ratio of triangle count to orginal mesh",
		subtype='FACTOR'
	)

	angle = bpy.props.FloatProperty (
		default=40,
		min = 5,
		max = 55,
		description="Reduction angle in degrees",
		subtype='FACTOR'
	)


class Modifier(modifier.Modifier):
	label = "Collider Mesh"
	id = 'collider'
	url = "http://renderhjs.net/fbxbundle/#modifier_collider"

	def __init__(self):
		super().__init__()


	def draw(self, layout):
		super().draw(layout)
		if(self.get("active")):
			row = layout.row(align=True)
			row.prop( eval("bpy.context.scene."+self.settings_path()) , "ratio", text="Ratio", icon='AUTOMERGE_ON')
			row.prop( eval("bpy.context.scene."+self.settings_path()) , "angle", text="Angle", icon='AUTOMERGE_ON')

			
	def process_objects(self, name, objects):
		# UNITY 	https://docs.unity3d.com/Manual/LevelOfDetail.html
		# UNREAL 	https://docs.unrealengine.com/en-us/Engine/Content/Types/StaticMeshes/HowTo/LODs
		# 			https://answers.unrealengine.com/questions/416995/how-to-import-lods-as-one-fbx-blender.html

		new_objects = []
		for obj in objects:

			new_objects.append(obj)

	
			# Select
			bpy.ops.object.select_all(action="DESELECT")
			obj.select_set(state = True)
			bpy.context.view_layer.objects.active = obj

			# Copy & Decimate modifier
			bpy.ops.object.duplicate()
			bpy.context.object.name = "{}_COLLIDER".format(obj.name)
			copy = bpy.context.object

			# Display as wire
			copy.display_type = 'WIRE'
			copy.show_all_edges = True
			

			# Decimate A
			mod = copy.modifiers.new("RATIO", type='DECIMATE')
			mod.ratio = self.get("ratio")

			# Displace
			mod = copy.modifiers.new("__displace", type='DISPLACE')
			mod.mid_level = 0.85
			mod.show_expanded = False


			# Decimate B
			mod = copy.modifiers.new("ANGLE", type='DECIMATE')
			mod.decimate_type = 'DISSOLVE'
			mod.angle_limit = self.get("angle") * math.pi / 180

			# Triangulate
			mod = copy.modifiers.new("__triangulate", type='TRIANGULATE')
			mod.show_expanded = False

			# Triangulate
			mod = copy.modifiers.new("__shrinkwrap", type='SHRINKWRAP')
			mod.target = obj
			mod.show_expanded = False			








			# bpy.ops.object.modifier_add(type='DECIMATE')
			# bpy.context.object.modifiers["Decimate"].ratio = get_quality(i, self.get("levels"), self.get("quality"))

			new_objects.append(bpy.context.object)

		return new_objects