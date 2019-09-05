import bpy, bmesh
import os
import mathutils
from mathutils import Vector
import operator

from . import objects_organise
from . import gp_draw



class op(bpy.types.Operator):
	bl_idname = "fbxbundle.fence_draw"
	bl_label = "Draw Fences"
	bl_description = "Draw fences around selected bundles"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if len(bpy.context.selected_objects) > 0:
			return True

		if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
			return False

		return False

	def execute(self, context):

		gp_draw.clear()

		bundles = objects_organise.get_bundles()
		for name,objects in bundles.items():
			if len(objects) > 0:
				bounds_combined = objects_organise.get_bounds_combined(objects)
				draw_bounds(name, objects, bounds_combined)

		return {'FINISHED'}




def draw_bounds(name, objects, bounds):
	print("Fence {}".format(name))

	padding = bpy.context.scene.FBXBundleSettings.padding
	
	
	pos = bounds.center

	_min = bounds.min
	_max = bounds.max
	_min-= Vector((padding,padding,0))
	_max+= Vector((padding,padding,0))
	size = _max - _min

	# Bounds
	draw = gp_draw.get_draw()
	draw.add_line(
		[_min +Vector((0,0,0)),
		_min +Vector((size.x,0,0)),
		_min +Vector((size.x,size.y,0)),
		_min +Vector((0,size.y,0)),
		_min +Vector((0,0,0))]
	)
	draw.add_line([_min +Vector((0,0,0)), _min +Vector((0,0,padding))] )
	draw.add_line([_min +Vector((size.x,0,0)), _min +Vector((size.x,0,padding))] )
	draw.add_line([_min +Vector((size.x,size.y,0)), _min +Vector((size.x,size.y,padding))] )
	draw.add_line([_min +Vector((0,size.y,0)), _min +Vector((0,size.y,padding))] )


	# Draw Text
	label = name
	if len(objects) > 1:
		label = "{} {}x".format(name, len(objects))
	draw.add_text(label.upper(), _min, padding*0.5)

	# Draw pole + Flag
	pivot = objects_organise.get_pivot(objects)
	height = max(padding, size.z)*2.0
	draw.add_line( [ Vector((pivot.x, pivot.y, _min.z)), Vector((pivot.x, pivot.y,_min.z+height))], dash=padding*0.25)
	# Flag
	draw.add_line( [
		Vector((pivot.x, pivot.y, _min.z + height - padding)),
		Vector((pivot.x - padding, pivot.y - padding, _min.z + height - padding/2)),
		Vector((pivot.x, pivot.y, _min.z + height)),
		Vector((pivot.x, pivot.y, _min.z + height - padding))
	] )

	draw.add_circle( pivot, padding, sides=8, alpha = 0.4)
	draw.add_line([pivot+Vector((-padding/2,0,0)), pivot+Vector((padding/2,0,0)) ])
	draw.add_line([pivot+Vector((0,-padding/2,0)), pivot+Vector((0,padding/2,0)) ])
	
	# Draw Grid
	draw_grid(objects, bounds)




def draw_grid(objects, bounds_group):
	draw = gp_draw.get_draw()
	padding = bpy.context.scene.FBXBundleSettings.padding

	bounds_objects = {}
	for o in objects:
		bounds_objects[o] = objects_organise.ObjectBounds(o)

	grid_x = SortedGridAxis(objects, bounds_objects, 'x') 
	grid_y = SortedGridAxis(objects, bounds_objects, 'y') 

	# Draw grids
	for i in range(len(grid_x.groups)-1):
		A = grid_x.bounds[i][1] #End first item
		B = grid_x.bounds[i+1][0] #Start next item
		center = A + (B-A)/2

		draw.add_line([
			Vector((center, bounds_group.min.y, bounds_group.min.z+padding)),
			Vector((center, bounds_group.min.y, bounds_group.min.z)),
			Vector((center, bounds_group.max.y, bounds_group.min.z)),
			Vector((center, bounds_group.max.y, bounds_group.min.z+padding))
		], alpha=0.4)

	for i in range(len(grid_y.groups)-1):
		A = grid_y.bounds[i][1] #End first item
		B = grid_y.bounds[i+1][0] #Start next item
		center = A + (B-A)/2

		draw.add_line([
			Vector((bounds_group.min.x, center, bounds_group.min.z+padding)),
			Vector((bounds_group.min.x, center, bounds_group.min.z)),
			Vector((bounds_group.max.x, center, bounds_group.min.z)),
			Vector((bounds_group.max.x, center, bounds_group.min.z+padding))
		], alpha=0.4)

	# Draw grids
	# for i in range(len(grid_x.groups)):
	# 	A = grid_x.bounds[i][0]
	# 	B = grid_x.bounds[i][1]
	# 	# center = A + (B-A)/2
	# 	# center = grid_x.bounds[i][0]

	# 	draw.add_line([
	# 		Vector((A, bounds_group.min.y, bounds_group.min.z)),
	# 		Vector((A, bounds_group.max.y, bounds_group.min.z))
	# 	], padding)

	# 	draw.add_line([
	# 		Vector((B, bounds_group.min.y, bounds_group.min.z)),
	# 		Vector((B, bounds_group.max.y, bounds_group.min.z))
	# 	], padding)


	# 	draw.add_text(str(i)+"A", Vector((A, bounds_group.min.y-padding*1.5, bounds_group.min.z)), padding*0.5)
	# 	draw.add_text(str(i)+"B", Vector((B, bounds_group.min.y-padding*1.5, bounds_group.min.z)), padding*0.5)

	


class SortedGridAxis:
	groups = []
	bounds = []

	def __init__(self, objects, bounds, axis_var='x'):
		self.groups = [[o] for o in objects]
		self.bounds = [[getattr(bounds[o].min, axis_var), getattr(bounds[o].max, axis_var)] for o in objects]
		# self.setup_gp()

		# Calculate clusters

		for i in range(len(self.groups)):
			print("i {}. / {}".format(i, len(self.groups)))

			j = 0
			for x in range(len(self.groups)):
				print("  j {}. / {}".format(j, len(self.groups)))

				if i != j and i < len(self.groups) and j < len(self.groups):
					g0 = self.groups[i]
					g1 = self.groups[j]
					b0 = self.bounds[i]
					b1 = self.bounds[j]
					# if g0 not in processed:
					if self.is_collide(b0[0], b0[1], b1[0], b1[1]):
						for o in g1:
							g0.append(o)
						b0[0] = min(b0[0], b1[0])
						b0[1] = max(b0[1], b1[1])
						self.groups.remove(g1)
						self.bounds.remove(b1)
						j-=1
						print("    Grp @ {} {} = {}x".format(i,j,len(self.groups)))
						# break
						# j-=1
						# i-=1
						# processed.append(g0)
				j+=1
			# 	j+=1
			# i+=1


		print("Final {} x {}".format(len(self.groups), len(self.bounds)))
		
		# Sort
		values = {(self.bounds.index(b)):(b[0]) for b in self.bounds}
		ordered = sorted(values.items(), key=operator.itemgetter(1))
		if len(self.groups) > 1:
			copy_groups = self.groups.copy()
			copy_bounds = self.bounds.copy()

			index = 0
			for s in ordered:
				print(".. Sorted {} = {}".format(s[0], s[1]))
				self.groups[index] = copy_groups[ s[0] ]
				self.bounds[index] = copy_bounds[ s[0] ]
				index+=1


	def is_collide(self, A_min, A_max, B_min, B_max):
		# One line is inside the other
		length_A = A_max-A_min
		length_B = B_max-B_min
		center_A = A_min + length_A/2
		center_B = B_min + length_B/2
		return abs(center_A - center_B) <= (length_A+length_B)/2
