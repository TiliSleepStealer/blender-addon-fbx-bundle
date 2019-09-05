
if "bpy" in locals():
	import imp
	imp.reload(gp_draw)
	imp.reload(objects_organise)

	imp.reload(op_fence_clear)
	imp.reload(op_fence_draw)
	imp.reload(op_file_copy_unity_script)
	imp.reload(op_file_export)
	imp.reload(op_file_export_recent)
	imp.reload(op_file_export_recent_clear)
	imp.reload(op_file_import)
	imp.reload(op_file_open_folder)
	imp.reload(op_pivot_ground)
	imp.reload(op_tool_geometry_fix)
	imp.reload(op_tool_pack_bundles)
	
	imp.reload(modifiers) 
	imp.reload(platforms)


else:
	from . import gp_draw
	from . import objects_organise

	from . import op_fence_clear
	from . import op_fence_draw
	from . import op_file_copy_unity_script
	from . import op_file_export
	from . import op_file_export_recent
	from . import op_file_export_recent_clear
	from . import op_file_import
	from . import op_file_open_folder
	from . import op_pivot_ground
	from . import op_tool_geometry_fix
	from . import op_tool_pack_bundles

	from . import modifiers
	from . import platforms


import bpy, bmesh
import os
import mathutils
from mathutils import Vector
import math
import bpy.utils.previews



import os
import traceback



bl_info = {
	"name": "FBX Bundle",
	"description": "Export object selections in FBX bundles",
	"author": "renderhjs",
	"blender": (2, 80, 0),
	"version": (1, 5, 1),
	"category": "3D View",
	"location": "View3D",
	"warning": "",
	"wiki_url": "http://renderhjs.net/fbxbundle/",
	"tracker_url": "",
}

from bpy.props import (
	StringProperty,
	BoolProperty,
	IntProperty,
	FloatProperty,
	FloatVectorProperty,
	EnumProperty,
	PointerProperty,
)



class Panel_Preferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	def draw(self, context):
		layout = self.layout


		box = layout.box()
		row = box.row()
		row.label(text="Unity Editor script")
		row.operator(op_file_copy_unity_script.op.bl_idname, icon='FILE_NEW')
		col = box.column(align=True)
		col.label(text="Copies a Unity Editor script to automatically assign")
		col.label(text="existing materials by name matching names in Blender")

		box = layout.box()
		row = box.row()
		row.label(text="Keyboard shortcuts")
		col = box.column(align=True)
		col.label(text="Ctrl + E = Export selected")
		col.label(text="Ctrl + Shift + E = Export recent")



class FBXBundleSettings(bpy.types.PropertyGroup):
	path: bpy.props.StringProperty (
		name="Output Path",
		default="",
		description="Define the path where to export or import from",
		subtype='DIR_PATH'
	)
	padding: bpy.props.FloatProperty (
		name="Padding",
		default=0.15,
		min = 0,
		description="Padding for fences or space bundling",
		subtype='DISTANCE'
	)
	collapseBundles: bpy.props.BoolProperty (
		name="Collapse",
		default=False,
		description="Compact list view"
	)
	include_children: bpy.props.BoolProperty (
		name="Incl. Children",
		default=False,
		description="Include nested children in bundles, e.g parent or group."
	)
	recent: bpy.props.StringProperty (
		name="Recent export",
		default=""
	)


	mode_bundle: bpy.props.EnumProperty(items= 
		[('NAME', 'Name', "Bundle by matching object names"), 
		('PARENT', 'Parent', "Bundle by the parent object"), 
		# ('SPACE', 'Space', "Bundle by shared space"), 
		('GROUP', 'Group', "Bundle by 'Groups'"),
		('MATERIAL', 'Material', "Bundle by matching material names"),
		('SCENE', 'Scene', "Bundle by current scene")
		], name = "Bundle Mode", default = 'NAME'
	)
	mode_pivot: bpy.props.EnumProperty(items=[
		('OBJECT_FIRST', 'First Name', "Pivot at the first object sorted by name"), 
		('OBJECT_LOWEST', 'Lowest Object', "Pivot at the lowest Z object's pivot"),
		('BOUNDS_BOTTOM', 'Bottom Center', "Pivot at the bottom center of the bounds of the bundle"), 
		('SCENE', 'Scene 0,0,0', "Pivot at the Scene center 0,0,0'"),
		('PARENT', 'Parent', "Pivot from the parent object"),
		('EMPTY', 'Empty Gizmo', "Empty gizmo object of: Arrow, Plain Axes, Single Arrow")
		], name = "Pivot From", default = 'OBJECT_FIRST'
	)
	target_platform: bpy.props.EnumProperty(items= 
		[	
			('UNITY', 'Unity ', 'Unity engine export, fixes axis rotation issues'),
			('UNREAL', 'Unreal ', 'Unreal engine export'),
			('BLENDER', 'Collada', 'Default Blender *.DAE export'),
			('GLTF', 'glTF', 'GL Transmission Format')
		], 
		description="Target platform for the FBX exports.",
		name = "Target Platform", 
		default = 'UNITY'
	)



class Panel_Core(bpy.types.Panel):
	bl_idname = "FBX_bundle_panel_core"
	bl_label = " "
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "FBX Bundle"
	bl_options = {'HIDE_HEADER'}

	def draw(self, context):
		layout = self.layout
		box = layout.box()

		row = box.row(align=True)
		row.label(text='Settings', icon='PREFERENCES')

		icon = icon_get(bpy.context.scene.FBXBundleSettings.target_platform.lower())
		row.prop(bpy.context.scene.FBXBundleSettings, "target_platform", text="", icon_value=icon)
		row.operator("wm.url_open", text="", icon='QUESTION').url = "http://renderhjs.net/fbxbundle/#settings_platform"


		mode = bpy.context.scene.FBXBundleSettings.target_platform

		if bpy.app.debug_value != 0:
			row = box.row(align=True)
			row.alert = True
			row.operator(op_debug_setup.bl_idname, text="Setup", icon='COLOR')
			row.operator(op_debug_lines.bl_idname, text="Draw", icon='GREASEPENCIL')


		col = box.column(align=True)

		row = col.row(align=True)
		if context.scene.FBXBundleSettings.path == "":
			row.alert = True
		row.prop(context.scene.FBXBundleSettings, "path", text="")
		if context.scene.FBXBundleSettings.path != "":
			row = row.row(align=True)
			row.operator(op_file_open_folder.op.bl_idname, text="", icon='FILE_FOLDER')

		row = col.row(align=True)
		row.prop(context.scene.FBXBundleSettings, "mode_bundle", text="Bundle by", icon='GROUP')
		row.operator("wm.url_open", text="", icon='QUESTION').url = "http://renderhjs.net/fbxbundle/#settings_bundle"


		row = col.row(align=True)
		row.prop(context.scene.FBXBundleSettings, "mode_pivot", text="Pivot at", icon='OUTLINER_DATA_EMPTY', expand=False)
		row.operator("wm.url_open", text="", icon='QUESTION').url = "http://renderhjs.net/fbxbundle/#settings_pivot"


		col = box.column(align=True)
		row = col.row(align=True)
		row.prop(context.scene.FBXBundleSettings, "padding", text="Padding", expand=True)
		row.prop(context.scene.FBXBundleSettings, "include_children", text="Include children", expand=True)

		# Warnings

		if context.space_data.local_view:
			box = col.box()
			box.label(text="Can't export in local view mode.", icon='CANCEL')

		if context.active_object and context.active_object.mode != 'OBJECT':
			box = col.box()
			box.label(text="Requires object mode to export.", icon='CANCEL')

		if context.scene.FBXBundleSettings.path == "":
			box = col.box()
			box.label(text="No output path defined.", icon='CANCEL')

		elif mode not in platforms.platforms:
			box = col.box()
			box.label(text="Platform not implemented", icon='CANCEL')
		
		elif context.scene.FBXBundleSettings.mode_bundle == 'GROUP' and len(bpy.data.groups) == 0:
			box = col.box()
			box.label(text="No groups available", icon='CANCEL')

		elif not platforms.platforms[mode].is_valid()[0]:
			box = col.box()
			box.label(text=platforms.platforms[mode].is_valid()[1], icon='CANCEL')			

		
		


class Panel_Tools(bpy.types.Panel):
	bl_idname = "FBX_bundle_panel_tools"
	bl_label = "Tools"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "FBX Bundle"
	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		col = layout.column()

		


		
		# Get bundles
		bundles = objects_organise.get_bundles()

		row = col.row(align=True)
		row.scale_y = 1.85
		row.operator(op_fence_draw.op.bl_idname, text="Draw Fences", icon='SELECT_SET')
		row.operator(op_fence_clear.op.bl_idname, text="", icon='PANEL_CLOSE')

		col.separator()

		col = col.column(align=True)

		col.operator(op_pivot_ground.op.bl_idname, text="Pivot at Ground", icon='OUTLINER_DATA_EMPTY')
		col.operator(op_tool_geometry_fix.op.bl_idname, text="Fix imp. Geometry", icon='MESH_ICOSPHERE')
		
		if bpy.app.debug_value != 0:
			col.operator(op_tool_pack_bundles.op.bl_idname, text="Pack & Arrange", icon='UGLYPACKAGE')
		


			row = layout.row(align=True)
			row.alert =True
			row.operator(op_fence_clear.op.bl_idname, text="Pack", icon='IMGDISPLAY')
			row.operator(op_fence_clear.op.bl_idname, text="Align Z", icon='TRIA_DOWN_BAR')
			layout.separator()





class Panel_Modifiers(bpy.types.Panel):
	bl_idname = "FBX_bundle_panel_modifiers"
	bl_label = "Modifiers"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "FBX Bundle"
	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		col = layout.column()

		for modifier in modifiers.modifiers:
			box = col.box()
			modifier.draw(box)

		r = col.row()
		r.enabled = False

		count = 0
		for modifier in modifiers.modifiers:
			if modifier.get("active"):
				count+=1

		if count > 0:
			r.label(text="{}x modifiers are applied upon export".format(count))


class Panel_Files(bpy.types.Panel):
	bl_idname = "FBX_bundle_panel_files"
	bl_label = "Bundles"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "FBX Bundle"
	bl_context = "objectmode"
	# bl_options = {'HIDE_HEADER'}

	def draw(self, context):
		layout = self.layout
		
		# Get bundles
		bundles = objects_organise.get_bundles()

		icon = icon_get(bpy.context.scene.FBXBundleSettings.target_platform.lower())


		col = layout.column(align=True)	
		row = col.row(align=True)

		split = row.split(factor=0.4, align=True)

		c = split.column(align=True)
		c.scale_y = 1.85
		c.operator(op_file_import.op.bl_idname, text="Import", icon='IMPORT')
		
		c = split.column(align=True)
		c.scale_y = 1.85
		c.operator(op_file_export.op.bl_idname, text="Export {}x".format(len(bundles)), icon_value=icon)
		

		if len(bpy.context.scene.FBXBundleSettings.recent) > 0:
			if len(objects_organise.recent_load_objects()) > 0:
				row = col.row(align=True)
				row.scale_y = 1.3

				r = row.row(align=True)
				r.operator(op_file_export_recent.op.bl_idname, text=objects_organise.recent_get_label(), icon='RECOVER_LAST')
				
				r = r.row(align=True)
				# r.alert = True
				r.operator(op_file_export_recent_clear.op.bl_idname, text="", icon='X')



		layout.separator()

		
		mode = bpy.context.scene.FBXBundleSettings.target_platform

		
		if(len(bundles) > 0):
			# box_files = layout.box()
			# box_files.active = False
			row = layout.row()
			if len(bundles) == 1:
				row.label(text = "1x Bundle")
			else:
				row.label(text = "{}x Bundles".format(len(bundles)))

			row.prop(context.scene.FBXBundleSettings, "collapseBundles", text="Compact", expand=True)


			folder = os.path.dirname( bpy.path.abspath( bpy.context.scene.FBXBundleSettings.path ))

			# Display bundles
			for fileName,objects in bundles.items():

				# row = layout.row(align=True)
				box = layout.box()
				# box.scale_y = 0.8
				column = box.column(align=True)

				row = column.row(align=True)
				if(fileName == "unknown"):
					row.alert = True

				# Process object name via modifiers
				path_folder = folder
				path_name = fileName
				for modifier in modifiers.modifiers:
					if modifier.get("active"):
						path_folder = modifier.process_path(path_name, path_folder)
						path_name = modifier.process_name(path_name)
	
				# Show label for FBX bundle
				label = fileName
				if mode in platforms.platforms:
					label = platforms.platforms[mode].get_filename(path_name)

				if(len(objects) > 1):
					label = "{}  {}x".format(label, len(objects));

				row.operator(op_select.bl_idname,icon_value=icon, emboss=False, text=label).key = fileName
				r = row.row(align=True)
				r.alert = True
				r.operator(op_remove.bl_idname,text="", icon='X').key = fileName


				if not context.scene.FBXBundleSettings.collapseBundles:
					for i in range(0,len(objects)):
						row = column.row(align=True)
						row.label(text=objects[i].name)






class op_debug_lines(bpy.types.Operator):
	bl_idname = "fbxbundle.debug_lines"
	bl_label = "Debug"

	def execute(self, context):
		print ("Debug Operator")

		gp_draw.draw_debug()

		return {'FINISHED'}


class op_debug_setup(bpy.types.Operator):
	bl_idname = "fbxbundle.debug_setup"
	bl_label = "Setup"

	def execute(self, context):
		print ("Debug Setup Operator")

		# Disable grid
		bpy.context.space_data.show_axis_x = False
		bpy.context.space_data.show_axis_y = False
		bpy.context.space_data.show_axis_z = False
		bpy.context.space_data.grid_lines = 6
		bpy.context.space_data.grid_subdivisions = 1
		bpy.context.space_data.grid_scale = 1
		bpy.context.space_data.show_floor = False

		bpy.context.space_data.show_all_objects_origin = True


		return {'FINISHED'}


class op_select(bpy.types.Operator):
	bl_idname = "fbxbundle.select"
	bl_label = "Select"
	key: bpy.props.StringProperty (name="Key")
	def execute(self, context):
		bundles = objects_organise.get_bundles()
		if self.key in bundles:
			bpy.ops.object.select_all(action='DESELECT')
			for obj in bundles[self.key]:
				obj.select_set(state = True)
		return {'FINISHED'}



class op_remove(bpy.types.Operator):
	bl_idname = "fbxbundle.remove"
	bl_label = "Remove"
	key: bpy.props.StringProperty (name="Key")
	def execute(self, context):
		bundles = objects_organise.get_bundles()
		if self.key in bundles:
			for obj in bundles[self.key]:
				obj.select_set(state = False)
		return {'FINISHED'}




def icon_get(name):
	if name not in preview_icons:
		print("Icon '{}' not found ".format(name))
	return preview_icons[name].icon_id


preview_icons = None
def icon_register(fileName):
	name = fileName.split('.')[0]   # Don't include file extension
	icons_dir = os.path.join(os.path.dirname(__file__), "icons")
	preview_icons.load(name, os.path.join(icons_dir, fileName), 'IMAGE')

def icons_unregister():
	global preview_icons
	bpy.utils.previews.remove(preview_icons)
	preview_icons = None


from . import auto_load
auto_load.init()

addon_keymaps = []

classes = (Panel_Preferences, FBXBundleSettings, Panel_Core, Panel_Tools, Panel_Modifiers, Panel_Files, op_debug_lines, op_debug_setup, op_select, op_remove)

def register():
	# bpy.utils.register_module(__name__)

	auto_load.register()
	for cls in classes:
		bpy.utils.register_class(cls)

	# Register scene settings
	bpy.types.Scene.FBXBundleSettings= bpy.props.PointerProperty(type=FBXBundleSettings)

	# Register modifier settings
	for modifier in modifiers.modifiers:
		print("loop name: {}".format(modifier.__module__))
		modifier.register()

	# Register Icons
	global preview_icons
	preview_icons = bpy.utils.previews.new()

	icons = [
		"unity.png", 
		"unreal.png", 
		"blender.png",
		"gltf.png"
	]
	for icon in icons:
		icon_register(icon)

	# handle the keymap
	km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
	kmi = km.keymap_items.new(op_file_export.op.bl_idname, 'E', 'PRESS', ctrl=True, shift=False)
	kmi = km.keymap_items.new(op_file_export_recent.op.bl_idname, 'E', 'PRESS', ctrl=True, shift=True)
	# kmi.properties.total = 4
	addon_keymaps.append(km)





def unregister():
	# bpy.utils.unregister_module(__name__)
	for cls in reversed(classes):
		# print("unregister " + cls)
		bpy.utils.unregister_class(cls)
	auto_load.unregister()

	#Unregister Settings
	del bpy.types.Scene.FBXBundleSettings

	# Unregister modifier settings
	for modifier in modifiers.modifiers:
		modifier.unregister()

	# Remove icons
	icons_unregister()

	# handle the keymap
	for km in addon_keymaps:
		bpy.context.window_manager.keyconfigs.addon.keymaps.remove(km)
	del addon_keymaps[:]


if __name__ == "__main__":
	register()

