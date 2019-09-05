import bpy, bmesh
import os
import pathlib
import shutil
import mathutils
from mathutils import Vector

from . import objects_organise

class op(bpy.types.Operator):
	bl_idname = "fbxbundle.file_copy_unity_script"
	bl_label = "Copy Unity Script"
	bl_description = "Copy Unity editor script to folder"

	filepath = bpy.props.StringProperty(subtype="FILE_PATH")


	def invoke(self, context, event):
		if self.filepath == "":
			self.filepath = bpy.context.scene.FBXBundleSettings.path

		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}


	def draw(self, context):
		layout = self.layout

		layout.label(text="Choose your Unity Asset directory")


	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		copy_script(self.filepath)
		return {'FINISHED'}



def copy_script(path):
	# https://blenderapi.wordpress.com/2011/09/26/file-selection-with-python/

	# Create Editor Folder
	path = os.path.join( bpy.path.abspath(path), "Editor")
	pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

	# Find Editor Script
	path_script = os.path.join(os.path.dirname(__file__), "resources/PostprocessorMeshes.cs")
	if not os.path.exists(path_script):
		self.report({'ERROR_INVALID_INPUT'}, "Could not find PostprocessorMeshes.cs script" )
		return

	# Copy Editor Script
	shutil.copy(path_script, path)
