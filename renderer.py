from numba import jit
from scipy.misc import imsave
import gradient, mandelbrot, cactus, julia
import time
from math import ceil, floor

class Renderer():
	def __init__(self, xResMax = 1024, yResMax = 1024, xResMin = 2, yResMin = 2):
		self.xResMax = xResMax
		self.yResMax = yResMax
		self.xResMin = xResMin
		self.yResMin = yResMin

		self.cam = Camera(xResMax, yResMax, xPos = -.5)

		weightImage = [[mandelbrot.renderWire(self.cam.convertX(x*2), self.cam.convertY(y*2)) for x in range(floor(self.xResMax/2))] for y in range(floor(self.yResMax/2))]
		imsave('weightImage.png', weightImage)

		imsave('dynamic.png', self.renderQuadImage(weightImage))

		imsave('fullRes.png', self.renderImage())

	def renderImage(self):
		t = time.clock()

		# The list comprehension is faster, but less flexible
		image = [[mandelbrot.render(self.cam.convertX(x), self.cam.convertY(y)) for x in range(self.xResMax)] for y in range(self.yResMax)]
		#image = []
		#for y in range(self.yResMax):
		#	row = []
		#	for x in range(self.xResMax):
		#		row.append(mandelbrot.render(self.cam.convertX(x), self.cam.convertY(y)))
		#	image.append(row)

		print("Render time was " + str(time.clock()-t) + " seconds.")
		return image

	def renderQuadImage(self, weightImage):
		t = time.clock()
		image = [[0 for x in range(self.xResMax)] for y in range(self.yResMax)]
		quadSize = floor(self.xResMax/self.xResMin)
		for y in range(self.yResMin):
			for x in range(self.xResMin):
				q = Quadtree((x*quadSize, y*quadSize), quadSize, weightImage)
				q.render(image, self.cam)
		print("Dynamic render time was " + str(time.clock()-t) + " seconds.")
		return image

class Camera(): # This class is responsible for handling the conversion from pixel position to mathematical space
	def __init__(self, xRes, yRes, xPos = 0, yPos = 0, zoom = 2):
		self.xRes = xRes
		self.yRes = yRes
		self.xPos = xPos
		self.yPos = yPos
		self.zoom = zoom

	def convertPos(self, x, y):
		return((convertX(x), convertY(y)))

	def convertX(self, x):
		return (x-self.xRes/2)*self.zoom/self.xRes+self.xPos

	def convertY(self, y):
		return (y-self.yRes/2)*self.zoom/self.yRes-self.yPos

class Quadtree():
	def __init__(self, pos, size, weightImage):
		self.children = []
		self.pos = pos
		self.size = size
		# Check if the weightImage asks for more subdivision
		if size > 1:
			for x in range(floor(self.pos[0]/2), floor((self.pos[0]+self.size)/2)):
				for y in range(floor(self.pos[1]/2), floor((self.pos[1]+self.size)/2)):
					if weightImage[y][x] > 0:
						self.subdivide(weightImage)
						return

	def render(self, image, cam):
		if not self.children: # If this quad is not subdivided
			half = floor(self.size/2)
			#change this line to update the appropriate pixels of the image instead of returning
			#return(gradient.render(self.pos[0]+half, self.pos[1]+half))
			col = mandelbrot.render(cam.convertX(self.pos[0]+half), cam.convertY(self.pos[1]+half))
			for x in range(self.pos[0], self.pos[0]+self.size):
				for y in range(self.pos[1], self.pos[1]+self.size):
					image[y][x] = col
		else:
			for c in self.children:
				c.render(image, cam)

	def subdivide(self, weightImage):
		half = floor(self.size/2)
		x, y = self.pos
		self.children.append(Quadtree(self.pos, half, weightImage))
		self.children.append(Quadtree((x+half, y), half, weightImage))
		self.children.append(Quadtree((x, y+half), half, weightImage))
		self.children.append(Quadtree((x+half, y+half), half, weightImage))

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
