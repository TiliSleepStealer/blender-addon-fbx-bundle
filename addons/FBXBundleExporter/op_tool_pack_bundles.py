import bpy, bmesh
import os
import mathutils
import math
from mathutils import Vector
import operator

from . import objects_organise



class op(bpy.types.Operator):
	bl_idname = "fbxbundle.pack_bundles"
	bl_label = "Pack Bundles"
	bl_description = "Pack bundles in a atlas formation"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		print ("Fix Geometry")

		pack_bundles()

		return {'FINISHED'}

def pack_bundles():

	padding = bpy.context.scene.FBXBundleSettings.padding
	bundles = objects_organise.get_bundles() 

	# Store previous settings
	previous_selection = bpy.context.selected_objects.copy()
	previous_active = bpy.context.view_layer.objects.active
	

	
	min_corner = None

	bundle_bbox = {}
	for key,objects in bundles.items():
		# bbox
		bbox = None
		for obj in objects:
			if bbox is None:
				bbox = objects_organise.ObjectBounds(obj)
			else:
				bbox.combine( objects_organise.ObjectBounds(obj) )
		bundle_bbox[key] = bbox

		# min corner
		if min_corner == None:
			min_corner = bbox.min
		else:
			min_corner.x = min(bbox.min.x, min_corner.x)
			min_corner.y = min(bbox.min.y, min_corner.y)
			min_corner.z = min(bbox.min.z, min_corner.z)


	blocks = []
	for key,objects in bundles.items():
		
		# Block for packing
		block = Block(bundle_bbox[key].size.x+padding, bundle_bbox[key].size.y+padding)
		block.key = key
		blocks.append(block)

		print("Pack {} at {:.2f} x {:.2f}".format(key, bbox.size.x, bbox.size.y))

	# Start packing
	sortBlocks(blocks, 'maxside')
	binPacking = BinPacking(blocks)

	for block in blocks:
		key = block.key
		print("Block {} = {} , {}".format(key, block.bin.x, block.bin.y))
		
		bpy.ops.object.select_all(action="DESELECT")
		for obj in bundles[key]:
			move_x = min_corner.x + block.bin.x - (bundle_bbox[key].min.x) # + obj.location.x
			move_y = min_corner.y + block.bin.y - (bundle_bbox[key].min.y ) #+ obj.location.y
			obj.select_set(state = True)
			bpy.ops.transform.translate(value=(move_x , move_y, 0), constraint_axis=(True, True, False), orient_type='GLOBAL', use_proportional_edit = False)

	print("First {}".format(blocks[0].key))

	# Restore previous settings
	bpy.context.view_layer.objects.active = previous_active
	bpy.ops.object.select_all(action='DESELECT')
	for obj in previous_selection:
		obj.select_set(state = True)


class Block(object):
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.bin = None


class Bin(object):
	def __init__(self, x, y, width, height):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.used = None
		self.down = None
		self.right = None




def getSortFun(sortType):
	sortTypes = {}
	sortTypes['width'] = lambda block: -block.width
	sortTypes['height'] = lambda block: -block.height
	sortTypes['area'] = lambda block: -block.width * block.height
	sortTypes['maxside'] = lambda block: -max(block.height, block.height)

	return sortTypes[sortType]

def sortBlocks(blocks, sortType):
	sortFunc = getSortFun(sortType)
	blocks.sort(key = sortFunc)
	return blocks

class BinPacking:
	def __init__(self, blocks):
		assert blocks
		block = blocks[0]

		self._root = Bin(0, 0, block.width, block.height)
		# block.bin = self._root

		self._blocks = blocks

		self._pack()

	def boxSize(self):
		width = self._root.width
		height = self._root.height

		width = math.pow(2, int(math.ceil(math.log(width, 2))))
		height = math.pow(2, int(math.ceil(math.log(height, 2))))
		return (int(width), int(height))


	def _pack(self):
		for block in self._blocks:
			bin = self._findBin(self._root, block.width, block.height)
			if bin:
				block.bin = self._splitBin(bin, block.width, block.height)
			else:
				block.bin = self._growBin(block.width, block.height)

	def _findBin(self, bin, width, height):
		if bin.used:
			return self._findBin(bin.right, width, height) or self._findBin(bin.down, width, height)                
		elif ((width <= bin.width) and (height <= bin.height)):
			return bin
		else:
			return None

	def _splitBin(self, bin, width, height):
		bin.used = True
		bin.down = Bin(bin.x, bin.y + height, bin.width, bin.height - height)
		bin.right = Bin(bin.x + width, bin.y, bin.width - width, bin.height)
		return bin

	def _growBin(self, width, height):
		canGrowDown = (width <= self._root.width)
		canGrowRight = (height <= self._root.height)

		shouldGrowRight = canGrowRight and (self._root.height >= (self._root.width + width))
		shouldGrowDown = canGrowDown and (self._root.width >= (self._root.height + height))

		if shouldGrowRight:
			return self._growRight(width, height)
		elif shouldGrowDown:
			return self._growDown(width, height)
		elif canGrowRight:
			return self._growRight(width, height)
		elif canGrowDown:
			return self._growDown(width, height)
		else:
			raise Exception('error')

	def _growRight(self, width, height):
		root = Bin(0, 0, self._root.width + width, self._root.height)
		root.used = True
		root.down = self._root
		root.right = Bin(self._root.width, 0, width, self._root.height)

		self._root = root
		bin = self._findBin(self._root, width, height)
		if bin:
			return self._splitBin(bin, width, height)
		else:
			raise Exception('error')

	def _growDown(self, width, height):
		root = Bin(0, 0, self._root.width, self._root.height + height)
		root.used = True
		root.down = Bin(0, self._root.height, self._root.width, height)
		root.right = self._root
		
		self._root = root
		bin = self._findBin(self._root, width, height)
		if bin:
			return self._splitBin(bin, width, height)
		else:
			raise Exception('error')

