from numba import jit
from scipy.misc import imsave
import gradient
import time

class Renderer():
	def __init__(self, xResMax = 2048, yResMax = 2048, xResMin = 8, yResMin = 8):
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

		self.image = [[gradient.render(x/self.xResMax, y/self.yResMax) for x in range(self.xResMax)] for y in range(self.yResMax)]

		#self.image = []
		#for y in range(self.yResMax):
		#	row = []
		#	for x in range(self.xResMax):
		#		row.append(gradient.render(x/self.xResMax, y/self.yResMax))
		#	self.image.append(row)

		print("Render time was " + str(time.clock()-t) + " seconds.")

class Camera(): # This class is responsible for handling the conversion from pixel position to mathematical space
	def __init__(self, xRes, yRes, xPos = 0, yPos = 0, zoom = 2):
		self.xRes = xRes
		self.yRes = yRes
		self.xPos = xPos
		self.yPos = yPos
		self.zoom = zoom

	def convertPos(x, y):
		aspectRatio = xRes/yRes
		return((x+xRes/2)*zoom*aspectRatio, (y+yRes/2)*zoom/aspectRatio)

Renderer()