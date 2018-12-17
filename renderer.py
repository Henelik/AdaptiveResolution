from numba import jit
from scipy.misc import imsave
import gradient, mandelbrot, cactus, julia
import time
from math import ceil

class Renderer():
	def __init__(self, xResMax = 512, yResMax = 512, xResMin = 8, yResMin = 8):
		self.xResMax = xResMax
		self.yResMax = yResMax
		self.xResMin = xResMin
		self.yResMin = yResMin

		self.cam = Camera(xResMax, yResMax)

		self.renderImage()
		self.saveImage('test.png')

	def saveImage(self, name):
		imsave(name, self.image)

	def renderImage(self):
		t = time.clock()

		# The list comprehension is faster, but less flexible
		#self.image = [[mandelbrot.render(self.cam.convertX(x), self.cam.convertY(y), 100) for x in range(self.xResMax)] for y in range(self.yResMax)]
		self.image = []
		for y in range(self.yResMax):
			row = []
			for x in range(self.xResMax):
				row.append(gradient.render(self.cam.convertX(x), self.cam.convertY(y)))
			self.image.append(row)

		print("Render time was " + str(time.clock()-t) + " seconds.")

class Camera(): # This class is responsible for handling the conversion from pixel position to mathematical space
	def __init__(self, xRes, yRes, xPos = 0, yPos = 0, zoom = 2):
		self.xRes = xRes
		self.yRes = yRes
		self.xPos = xPos
		self.yPos = yPos
		self.zoom = zoom
		self.aspectRatio = self.xRes/self.yRes

	def convertPos(self, x, y):
		return((convertX(x), convertY(y)))

	def convertX(self, x):
		return((x-self.xRes/2)*self.zoom*self.aspectRatio/self.xRes+self.xPos)

	def convertY(self, y):
		return((y-self.yRes/2)*self.zoom/self.aspectRatio/self.yRes-self.yPos)

class Quadtree():
	def __init__(self, pos, size):
		self.children = []
		self.pos = pos
		self.size = size

	def render(self):
		if not self.children:
			half = self.size/2
			#change this line to update the appropriate pixels of the image instead of returning
			return(gradient.render(self.pos[0]+half, self.pos[1]+half))
		for c in self.children:
			c.render()

	def subdivide(self):
		if size > 1:
			half = self.size/2
			x, y = self.pos
			self.children.append(Quadtree(self.pos, half))
			self.children.append(Quadtree((x+half, y), half))
			self.children.append(Quadtree((x, y+half), half))
			self.children.append(Quadtree((x+half, y+half), half))
			return(True)
		return(False)

class BoundingBox():
	def __init__(self, coords, size):
		self.coords = coords
		self.size = size

	def containsPoint(self, point):
		if point[0] in range(self.coords[0], self.coords[0]+size):
			if point[1] in range(self.coords[1], self.coords[1]+size):
				return(True)
		return(False)

	def intersectsBB(self, otherBB):
		return(False)

Renderer()
