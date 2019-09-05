import bpy, bmesh
import os
import mathutils
from mathutils import Vector
import math
import random
import re
import operator
import json
import imp

from . import platforms
imp.reload(platforms)


def is_object_valid(obj):
	# Objects to include in a bundle as 'export-able'
	if obj.hide_viewport:
		return False
		
	return obj.type == 'MESH' or obj.type == 'FONT' or obj.type == 'CURVE'


def get_objects():
	objects = []
	for obj in bpy.context.selected_objects:
		objects.append(obj)

	# Include all children?
	if len(objects) > 0 and bpy.context.scene.FBXBundleSettings.include_children:
		
		if bpy.context.scene.FBXBundleSettings.mode_bundle == 'PARENT':
			# Collect parent and children objects
			limit = 100 # max
			roots = []

			# Collect roots from input selection
			for obj in objects:
				root = obj
				for i in range(limit):
					if root.parent:
						root = root.parent
					else:
						break
				if root not in roots:
					roots.append(root)

			def collect_recursive(obj, depth):
				if obj not in objects:
					objects.append(obj)
				
				if depth < limit:#Don't exceed limit on traversal depth
					for child in obj.children:
						collect_recursive(child, depth+1)

			# Traverse loops and its nested elements
			for root in roots:
				collect_recursive(root, 0)

		elif bpy.context.scene.FBXBundleSettings.mode_bundle == 'GROUP':
			# Collect group objects
			groups = []

			# Collect groups from input selection
			for obj in objects:
				for group in obj.users_group:
					if group.name not in groups:
						groups.append(group.name)

			# Collect objects of groups
			for name in groups:
				if name in bpy.data.groups:
					for obj in bpy.data.groups[name].objects:
						if obj not in objects:
							objects.append(obj)

		elif bpy.context.scene.FBXBundleSettings.mode_bundle == 'SCENE':
			# Include all objects of the scene
			for obj in bpy.context.scene.objects:
				if obj not in objects:
					objects.append(obj)

	filtered = []
	for obj in objects:
		if is_object_valid(obj):
			filtered.append(obj)

	return sort_objects_name(filtered)



def sort_objects_name(objects):
	names = {}
	for obj in objects:
		names[obj.name] = obj

	# now sort
	sorted_objects = []
	for key in sorted(names.keys()):
		sorted_objects.append(names[key])

	return sorted_objects



def get_objects_animation(objects):
	# Detect if animation
	use_animation = False
	for obj in objects:
		if get_object_animation(obj):
			use_animation = True
			break
	return use_animation



def get_object_animation(obj):
	if obj:
		#Check for animation data on object
		if obj.animation_data:
			return True

		# Check for armature modifiers
		for mod in obj.modifiers:
			if mod.type == 'ARMATURE':
				return True

	# No animation found
	return False



def recent_store(bundles):
	dic = {}
	dic['selection'] = []
	dic['bundles'] = []
	for name,objects in bundles.items():
		dic['bundles'].append(name)
		for obj in objects:
			dic['selection'].append(obj.name)

	bpy.context.scene.FBXBundleSettings.recent = json.dumps(dic).encode().decode()



def recent_get_label():
	recent = bpy.context.scene.FBXBundleSettings.recent
	mode = bpy.context.scene.FBXBundleSettings.target_platform

	if mode in platforms.platforms:
		if len(recent) > 0:
			dic = json.loads(recent.encode().decode())
			ext = platforms.platforms[mode].extension
			if 'bundles' in dic and len(dic['bundles']) > 0:
				# names = [name+"."+ext for name in dic['bundles']]
				names = [name for name in dic['bundles']]

				return "Re-Export: ".format(len(dic['bundles']))+", ".join(names)

	return "Re-Export"



def recent_load_objects():
	recent = bpy.context.scene.FBXBundleSettings.recent
	if len(recent) > 0:
		dic = json.loads(recent.encode().decode())
		if 'selection' in dic and len(dic['selection']) > 0:
			objects = []
			for name in dic['selection']:
				if name in bpy.data.objects:
					objects.append(bpy.data.objects[name])
			return objects
	return []
	



def get_bundles():
	objects = get_objects()

	# Collect groups by key
	groups = []
	for obj in objects:
		key = get_key(obj)

		if(len(groups) == 0):
			groups.append([obj])
		else:
			isFound = False
			for group in groups:
				if key == get_key(group[0]):
					group.append(obj)
					isFound = True
					break
			if not isFound:
				groups.append([obj])

	# Sort keys alphabetically
	keys = [get_key(group[0]) for group in groups]
	keys.sort()
	bundles = {}
	for key in keys:
		if key not in bundles:
			bundles[key] = []

		for group in groups:
			if key == get_key(group[0]):
				bundles[key] = group
				break

	if len(bundles) == 1 and 'UNDEFINED' in bundles:
		bundles.clear() 

	return bundles



def get_bounds_combined(objects):
	bounds = ObjectBounds(objects[0])
	if len(objects) > 1:
		for i in range(1,len(objects)):
			bounds.combine( ObjectBounds(objects[i]) )
	return bounds



def get_pivot(objects):
	mode_pivot = bpy.context.scene.FBXBundleSettings.mode_pivot

	if len(objects):
		if mode_pivot == 'OBJECT_FIRST':
			if len(objects) > 0:
				return objects[0].location

		elif mode_pivot == 'BOUNDS_BOTTOM':
			bounds = get_bounds_combined(objects)
			return Vector((
				bounds.min.x + bounds.size.x/2,
				bounds.min.y + bounds.size.y/2,
				bounds.min.z
			))
		elif mode_pivot == 'OBJECT_LOWEST':

			obj_bounds = {}
			for obj in objects:
				b = ObjectBounds(obj)
				obj_bounds[obj] = b.min.z

			# Sort
			ordered = sorted(obj_bounds.items(), key=operator.itemgetter(1))
			return ordered[0][0].location


		elif mode_pivot == 'SCENE':
			return Vector((0,0,0))
		
		elif mode_pivot == 'PARENT':
			if len(objects) > 0:
				if objects[0].parent:
					return objects[0].parent.location
				else:
					return objects[0].location

		elif mode_pivot == 'EMPTY':
			# Empty Gizmo, not part of bundle selection but rather scene selection
			for obj in bpy.context.selected_objects:
				if obj.type == 'EMPTY':
					if obj.empty_display_type == 'SINGLE_ARROW' or obj.empty_display_type == 'PLAIN_AXES' or obj.empty_display_type == 'ARROWS':
						return obj.location

	# Default
	return Vector((0,0,0))



split_chars = ['',' ','_','.','-']


def encode(name):
	name = name.replace("<","")
	name = name.replace(">","")

	# Split Camel Case
	split = re.sub('(?!^)([A-Z][a-z]+)', r' \1', name).split()
	name = '<0>'.join(split)

	# Split
	for i in range(len(split_chars)):
		char = split_chars[i]
		if len(char) > 0:
			name = name.replace(char,'<{}>'.format(i))
	

	split = name.split("<")
	fill = []
	elem = []
	for i in range(len(split)):
		element = split[i]

		if i == 0 :
			elem.append( split[i] )

		elif i > 0:
			char = split_chars[int(element[0:1])] 
			e = split[i][2:]
			# Don't add empty elements (e.g. double split sequences)
			if e != "":
				elem.append( e )
				fill.append( char )


	
	return " ".join(elem), fill


def decode(name, fill):

	n = ""
	split = name.split(" ")
	for i in range(len(split)):
		n+=split[i]
		if i < len(split)-1:
			n+=fill[i]

	return n



def get_key(obj):
	mode_bundle = bpy.context.scene.FBXBundleSettings.mode_bundle

	if mode_bundle == 'NAME':

		name = obj.name
		# Remove blender naming digits, e.g. cube.001, cube.002,...
		if len(name)>= 4 and name[-4] == '.' and name[-3].isdigit() and name[-2].isdigit() and name[-1].isdigit():
			name = name[:-4]

		name, fill = encode(name)

		# Combine
		split = name.split(' ')
		if len(split) > 1:
			name = ' '.join(split[0:-1])
		else:
			name = split[0]

		return decode(name, fill)

	elif mode_bundle == 'PARENT':
		# Use group name
		if obj.parent:
			limit = 100
			obj_parent = obj.parent
			for i in range(limit):
				if obj_parent.parent:
					obj_parent = obj_parent.parent
				else:
					break
			return obj_parent.name
		else:
			return obj.name

	elif mode_bundle == 'GROUP':
		# Use group name
		if len(obj.users_group) >= 1:
			return obj.users_group[0].name

	elif mode_bundle == 'MATERIAL':
		# Use material name
		if len(obj.material_slots) >= 1:
			return obj.material_slots[0].name

	elif mode_bundle == 'SCENE':
		# Use scene name
		return bpy.context.scene.name

	elif mode_bundle == 'SPACE':
		# print("_________")

		# Do objects share same space with bounds?
		objects = get_objects()
		clusters = []

		for o in objects: 
			clusters.append({'bounds':ObjectBounds(o), 'objects':[o], 'merged':False})


		for clusterA in clusters:
			if len(clusterA['objects']) > 0:

				for clusterB in clusters:
					if clusterA != clusterB and len(clusterB['objects']) > 0:

						boundsA = clusterA['bounds']
						boundsB = clusterB['bounds']
						if boundsA.is_colliding(boundsB):
							
							# print("Merge {} --> {}x = {}".format(nA, len(clusterB['objects']), ",".join( [o.name for o in clusterB['objects'] ] )   ))
							for o in clusterB['objects']:
								clusterA['objects'].append( o )
							clusterB['objects'].clear()
							
							boundsA.combine(boundsB)

		for cluster in clusters:
			if obj in cluster['objects']:
				return cluster['objects'][0].name

	return "UNDEFINED"



class ObjectBounds:
	obj = None
	min = Vector((0,0,0))
	max = Vector((0,0,0))
	size = Vector((0,0,0))
	center = Vector((0,0,0))

	def __init__(self, obj):
		self.obj = obj
		corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

		self.min = Vector((corners[0].x, corners[0].y, corners[0].z))
		self.max = Vector((corners[0].x, corners[0].y, corners[0].z))
		for corner in corners:
			self.min.x = min(self.min.x, corner.x)
			self.min.y = min(self.min.y, corner.y)
			self.min.z = min(self.min.z, corner.z)
			self.max.x = max(self.max.x, corner.x)
			self.max.y = max(self.max.y, corner.y)
			self.max.z = max(self.max.z, corner.z)

		self.size = self.max - self.min
		self.center = self.min+(self.max-self.min)/2


	def combine(self, other):
		self.min.x = min(self.min.x, other.min.x)
		self.min.y = min(self.min.y, other.min.y)
		self.min.z = min(self.min.z, other.min.z)
		self.max.x = max(self.max.x, other.max.x)
		self.max.y = max(self.max.y, other.max.y)
		self.max.z = max(self.max.z, other.max.z)

		self.size = self.max - self.min
		self.center = self.min+(self.max-self.min)/2

	def is_colliding(self, other):
		def is_collide_1D(A_min, A_max, B_min, B_max):
			# One line is inside the other
			length_A = A_max-A_min
			length_B = B_max-B_min
			center_A = A_min + length_A/2
			center_B = B_min + length_B/2
			return abs(center_A - center_B) <= (length_A+length_B)/2

		collide_x = is_collide_1D(self.min.x, self.max.x, other.min.x, other.max.x)
		collide_y = is_collide_1D(self.min.y, self.max.y, other.min.y, other.max.y)
		collide_z = is_collide_1D(self.min.z, self.max.z, other.min.z, other.max.z)
		return collide_x and collide_y and collide_z