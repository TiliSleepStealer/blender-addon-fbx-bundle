import bpy, bmesh
import imp

from . import modifier
imp.reload(modifier) 


class Settings(modifier.Settings):
	active = bpy.props.BoolProperty (
		name="Active",
		default=False
	)
	source = bpy.props.StringProperty()



class Modifier(modifier.Modifier):
	label = "Copy Modifiers"
	id = 'copy_modifiers'
	url = "http://renderhjs.net/fbxbundle/#modifier_modifiers"

	def __init__(self):
		super().__init__()


	# def register(self):
		# exec("bpy.types.Scene."+self.settings_path() + " = bpy.props.PointerProperty(type=Settings)")

		

	def draw(self, layout):
		super().draw(layout)
		if(self.get("active")):
			# Alternatively: https://blender.stackexchange.com/questions/75185/limit-prop-search-to-specific-types-of-objects
			
			row = layout.row(align=True)
			row.separator()
			row.separator()


			row.prop_search(eval("bpy.context.scene."+self.settings_path()), "source",  bpy.context.scene, "objects", text="Source")

			if self.get('source') in bpy.data.objects:
				row = layout.row()
				row.enabled = False

				row.separator()
				count = len(bpy.data.objects[self.get('source')].modifiers)
				row.label(text="copyies {}x modifiers".format(count))



	def process_objects(self, name, objects):
		if self.get('source') in bpy.data.objects:
			source = bpy.data.objects[ self.get('source') ]
			source.select_set(state = True)
			old = bpy.context.view_layer.objects.active
			bpy.context.view_layer.objects.active = source

			bpy.ops.object.make_links_data(type='MODIFIERS')
			source.select_set(state = False)
			bpy.context.view_layer.objects.active = old
		return objects

		