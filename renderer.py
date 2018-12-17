from numba import jit
from scipy.misc import imsave
import gradient, mandelbrot, cactus, julia
import time

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

		self.image = [[gradient.render(self.cam.convertX(x), self.cam.convertY(y)) for x in range(self.xResMax)] for y in range(self.yResMax)]

		print("Render time was " + str(time.clock()-t) + " seconds.")

class Camera(): # This class is responsible for handling the conversion from pixel position to mathematical space
	def __init__(self, xRes, yRes, xPos = 0, yPos = 0, zoom = 4):
		self.xRes = xRes
		self.yRes = yRes
		self.xPos = xPos
		self.yPos = yPos
		self.zoom = zoom
		self.aspectRatio = self.xRes/self.yRes

	def convertPos(self, x, y):
		return((x+self.xPos-self.xRes/2)*self.zoom*self.aspectRatio/self.xRes, (y+self.yPos-self.yRes/2)*self.zoom/self.aspectRatio/self.yRes)

	def convertX(self, x):
		return((x+self.xPos-self.xRes/2)*self.zoom*self.aspectRatio/self.xRes)

	def convertY(self, y):
		return((y+self.yPos-self.yRes/2)*self.zoom/self.aspectRatio/self.yRes)

Renderer()
