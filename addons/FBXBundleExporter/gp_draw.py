import bpy, bmesh
import os
import mathutils
from mathutils import Vector
import math
import random


from . import objects_organise


_draw = None

def get_draw():
	global _draw
	if not _draw or not _draw.is_valid():
		_draw = LineDraw("fence",(0,0.8,1.0))
	return _draw



def clear():
	print("Clear")
	draw = get_draw()
	draw.clear()



def draw_debug():
	# test_grease_pencil()
	padding = bpy.context.scene.FBXBundleSettings.padding

	draw = get_draw()
	draw.clear()

	step = 0
	def add_text(step,text):
		draw.add_text(text, Vector((0,-step,0)), padding)
		return step+1

	step = add_text(step,"abcdefghijklm")
	step = add_text(step,"nopqrstuvwxyz")

	step = add_text(step,"ABCDEFGHIJKLM")
	step = add_text(step,"NOPQRSTUVWXYZ")

	step = add_text(step,"0123456789")
	step = add_text(step,"~!@#$%^&*()")
	step = add_text(step,"_-+\"';:,.<>[](){}\\/?")
	step = add_text(step,"www.renderhjs.net")

	# Draw circles
	# for i in range(1,8):
	# 	draw.add_circle(Vector((4,4,0)), i*0.5, i*3)


class LineDraw:
	
	name = ""
	color = (0,0,0)

	gp = None
	gp_layer = None
	gp_palette = None
	gp_color = None
	gp_frame = None


	def __init__(self, name, color):
		self.name = name
		self.color = color
		self.setup_gp()


	def clear(self):
		self.gp_layer.clear()


	def add_box(self, position, size=1.0):
		print("Box")

		self.add_line([
			position + Vector((-0.5,-0.5,-0.5)) * size,
			position + Vector((+0.5,-0.5,-0.5)) * size,
			position + Vector((+0.5,+0.5,-0.5)) * size,
			position + Vector((-0.5,+0.5,-0.5)) * size,
			position + Vector((-0.5,-0.5,-0.5)) * size,
		])
		self.add_line([
			position + Vector((-0.5,-0.5,-0.5)) * size,
			position + Vector((-0.5,-0.5,+0.5)) * size,
		])
		self.add_line([
			position + Vector((+0.5,-0.5,-0.5)) * size,
			position + Vector((+0.5,-0.5,+0.5)) * size,
		])
		self.add_line([
			position + Vector((+0.5,+0.5,-0.5)) * size,
			position + Vector((+0.5,+0.5,+0.5)) * size,
		])
		self.add_line([
			position + Vector((-0.5,+0.5,-0.5)) * size,
			position + Vector((-0.5,+0.5,+0.5)) * size,
		])
		self.add_line([
			position + Vector((-0.5,-0.5,+0.5)) * size,
			position + Vector((+0.5,-0.5,+0.5)) * size,
			position + Vector((+0.5,+0.5,+0.5)) * size,
			position + Vector((-0.5,+0.5,+0.5)) * size,
			position + Vector((-0.5,-0.5,+0.5)) * size,
		])


	# def add_cross(self, position, size=1.0):
	# 	print("...")


	def add_circle(self, position, radius = 1, sides = 8, alpha = 1.0, dash = 0.0):

		for i in range(sides):
			a0 = ((i+0) * (360 / sides))*math.pi/180
			a1 = ((i+1) * (360 / sides))*math.pi/180
			A = position + Vector((math.cos(a0), math.sin(a0), 0))*radius
			B = position + Vector((math.cos(a1), math.sin(a1), 0))*radius
			self.add_line([A,B], alpha = alpha, dash = dash)




	def add_lines(self, lines, alpha=1.0, dash=0.0):
		for line in lines:
			self.add_line(line, alpha, dash)


	def add_line(self, points, alpha=1.0, dash=0.0):
		
		if dash == 0:
			stroke = self.get_gp_stroke()
			offset = len(stroke.points)

			stroke.points.add(len(points))
			for i in range(len(points)):
				index = offset+i
				stroke.points[index].co = points[i]
				stroke.points[index].select   = True
				stroke.points[index].pressure = 1
				stroke.points[index].strength = alpha

		else:
			for i in range(len(points)-1):
				# stroke = self.get_gp_stroke()
				length = (points[i] - points[i-1]).magnitude
				steps = math.floor((length / dash)/2)
				A = points[i]
				B = points[i+1]

				for s in range(steps):
					stroke = self.get_gp_stroke()
					stroke.points.add(2)
					stroke.points[-2].co = A + (B-A).normalized() * (s*(dash*2))
					stroke.points[-2].select   = True
					stroke.points[-2].pressure = 1
					stroke.points[-2].strength = alpha

					stroke.points[-1].co = A + (B-A).normalized() * (s*(dash*2)+ dash)
					stroke.points[-1].select   = True
					stroke.points[-1].pressure = 1
					stroke.points[-1].strength = alpha



	def add_text(self, text, pos=Vector((0,0,0)), size=1.0):
		# text = text.upper()
		size_xy = Vector((0.66,1)) * size
		padding = size_xy.x/2

		offset = 0

		def add_character(strokes):
			nonlocal offset

			for stroke in strokes:
				path = []
				for id in stroke:
					x = (id % 3) * (size_xy.x/2) + (offset * (size_xy.x*1.5)) + padding
					y = math.floor(id/3) * size_xy.y/2 + padding
					path.append(pos + Vector((x,-size_xy.y-2* padding + y,0)))
				
				# add_mesh_edges(bm, path)
				self.add_line(path)

		# 6 -- 7 -- 8
		# |    |    |
		# 3 -- 4 -- 5
		# |    |    |
		# 0 -- 1 -- 2
		# |    |    |
		#-3 - -2 - -1
		chars = {
			'a':[[0,3,5,1,0],[5,2]],
			'b':[[6,0,2,5,3]],
			'c':[[5,3,0,2]],
			'd':[[8,2,0,3,5]],
			'e':[[5,3,0,5],[0,2]],
			'f':[[7,3,0],[3,4]],
			'g':[[2,5,3,0,2,-2,-3]],
			'h':[[6,0],[3,5,2]],
			'i':[[4,1],[7,8]],
			'j':[[4,1,-3],[7,8]],
			'k':[[6,0],[3,4],[3,1]],
			'l':[[6,3,1]],
			'm':[[0,3,5,2],[4,1]],
			'n':[[0,3,2,5]],
			'o':[[0,3,5,2,0]],
			'p':[[-3,3,5,2,0]],
			'q':[[-1,5,3,0,2]],
			'r':[[3,0,4,5]],
			's':[[5,4,0,2,-2,-3]],
			't':[[3,5],[4,1]],
			'u':[[3,0,2,5]],
			'v':[[3,1,5]],
			'w':[[3,0,4,1,5]],
			'x':[[3,2],[0,5]],
			'y':[[3,1],[5,-3]],
			'z':[[3,5,0,2]],

			# Alhabet Uppercase
			'A':[[0,3,7,5,2],[3,5]],
			'B':[[0,6,8,4,2,0],[3,4]],
			'C':[[2,1,3,7,8]],
			'D':[[0,6,7,5,1,0]],
			'E':[[2,0,6,8],[3,4]],
			'F':[[0,6,8],[3,4]],
			'G':[[4,5,2,0,3,7,8]],
			'H':[[0,6],[3,5],[2,8]],
			'I':[[0,2],[1,7],[6,8]],
			'J':[[6,8,5,1,0,3]],
			'K':[[6,0],[3,4,8],[4,2]],
			'L':[[6,0,2]],
			'M':[[0,6,4,8,2]],
			'N':[[0,6,2,8]],
			'O':[[1,3,7,5,1]],
			'P':[[0,6,7,5,3]],
			'Q':[[1,3,7,5,1],[4,2]],
			'R':[[0,6,8,4,2],[3,4]],
			'S':[[0,1,5,3,7,8]],
			'T':[[6,8],[7,1]],
			'U':[[6,0,2,8]],
			'V':[[6,3,1,5,8]],
			'W':[[6,0,4,2,8]],
			'X':[[6,2],[0,8]],
			'Y':[[6,4,8],[4,1]],
			'Z':[[6,8,0,2]],

			# Special
			' ':[],
			'.':[[1,2]],
			',':[[1,-2]],
			'+':[[3,5],[7,1]],
			'-':[[3,5]],
			'_':[[0,2]],
			'|':[[1,7]],
			'/':[[0,8]],
			'\\':[[6,2]],
			'\'':[[7,4]],
			'*':[[0,8],[3,5],[6,2],[1,7]],
			'%':[[6,3],[8,0],[5,2]],
			'"':[[6,4],[7,5]],
			'~':[[3,7,4,8]],
			'@':[[0,6,8,2,1,4]],
			'$':[[0,1,5,3,7,8],[7,1]],
			'^':[[3,7,5]],
			':':[[4,5],[1,2]],
			';':[[4,5],[1,-3]],
			# '&':[[2,3,6,7,4,3,0,5]],

			# Pairs
			'(':[[1,3,7]],
			')':[[7,5,1]],
			'[':[[7,6,0,1]],
			']':[[7,8,2,1]],
			'<':[[8,3,2]],
			'>':[[6,5,0]],
		
			# Numbers
			'0':[[6,8,2,0,6],[0,8]],		
			'1':[[0,2],[1,7,6]],
			'2':[[6,7,5,3,0,2]],
			'3':[[6,8,4,2,0]],
			'4':[[6,3,5],[8,2]],
			'5':[[8,6,3,5,1,0]],
			'6':[[8,7,3,0,2,5,3]],
			'7':[[3,6,8,5,1]],
			'8':[[6,2,0,8,6]],
			'9':[[5,3,6,8,5,1,0]],
			
			# Unknown
			'?':[[3,6,8,5,4,1]]
		}
		for char in text:
			if char in chars:
				add_character(chars[char])
			else:
				# unknown character
				add_character(chars['?'])
			offset+=1

	def is_valid(self):
		if not self.gp:
			return False
		if not bpy.context.scene.grease_pencil or self.gp != bpy.context.scene.grease_pencil:
			return False
		if not self.gp_layer:
			return False
		if not self.gp_palette:
			return False

		return True

	def setup_gp(self):
		# Documentation https://wiki.blender.org/index.php/User:Antoniov/Grease_Pencil_Api_Changes
		id_grease = "id_grease"
		id_layer = "id_layer"
		id_palette = "id_palette"

		# 
		# bpy.context.space_data.show_grease_pencil = True

		# gp = scene.grease_pencil
		# if not gp:
		# 	gp = bpy.data.grease_pencil.get(gname, None)
		# 	if not gp:
		# 		gp = bpy.data.grease_pencil.new(gname)
		# 		print("Created new Grease Pencil", gp.name)
		# 	scene.grease_pencil = gp
		# 	print("Added Grease Pencil %s to current scene" % (gp.name) ) 
		# return gp

		# Grease Pencil
		self.gp = bpy.context.scene.grease_pencil
		if not self.gp:
			if id_grease in bpy.context.scene.objects:
				self.gp = bpy.context.scene.objects[id_grease]
			else:
				# self.gp = bpy.data.grease_pencil.new(id_grease)
				bpy.ops.object.gpencil_add( align='WORLD', location=(0, 0, 0), type='EMPTY')
				# rename grease pencil
				bpy.context.scene.objects[-1].name = id_grease
				self.gp = bpy.context.scene.objects[-1]

		# Get grease pencil layer or create one if none exists
		if self.gp.data.layers and id_layer in self.gp.data.layers:
			self.gp_layer = self.gp.data.layers[id_layer]
		else:
			self.gp_layer = self.gp.data.layers.new(id_layer, set_active=True)



		# Palette
		
		
		# Frame
		if len(self.gp_layer.frames) == 0:
			self.gp_frame = self.gp_layer.frames.new(bpy.context.scene.frame_current)
		else:
			self.gp_frame = self.gp_layer.frames[0]


	def get_gp_stroke(self, id_grease="fance", id_layer="lines", id_palette="colors"):
		stroke  = self.gp_frame.strokes.new()
		stroke.display_mode = '3DSPACE'
		stroke.line_width = 10
		return stroke
