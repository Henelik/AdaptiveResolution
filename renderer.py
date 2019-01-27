from numba import jit
from scipy.misc import imsave
import gradient, mandelbrot, cactus, julia
import time
from math import ceil, floor
import itertools

class Renderer():
	def __init__(self, xRes = 512, yRes = 512):
		self.xRes = xRes
		self.yRes = yRes

		self.cam = Camera(xRes, yRes, xPos = -.5)

		imsave('dynamic.png', self.renderQuadImage(2000, 100))
		imsave('fullRes.png', self.renderImage(100))

	def renderImage(self, maxIters):
		t = time.clock()

		image = [[mandelbrot.render(self.cam.convertX(x), self.cam.convertY(y), maxIters) for x in range(self.xRes)] for y in range(self.yRes)]

		print("Render time was " + str(time.clock()-t) + " seconds.")
		return image

	def renderQuadImage(self, subdivMax, maxIters):
		def sparseRender(x, y, size):
			corn = []
			for i in [(x, y), (x+size, y), (x, y+size), (x+size, y+size)]:
				if i in sparseArray:
					corn.append(sparseArray[i])
				else:
					corn.append(mandelbrot.render(self.cam.convertX(i[0]), self.cam.convertY(i[1]), maxIters))
					sparseArray[i] = corn[-1]
			return(sum(corn)/4)

		t = time.clock()
		image = [[0 for x in range(self.xRes)] for y in range(self.yRes)]
		sparseArray = {}

		s = floor(self.xRes/2)
		quadList = [
		Quad(0, 0, 1, sparseRender(0, 0, s)),
		Quad(0, s, 1, sparseRender(0, s, s)),
		Quad(s, 0, 1, sparseRender(s, 0, s)),
		Quad(s, s, 1, sparseRender(s, s, s))]
		for i in range(subdivMax):
			quadList.sort(key = lambda q: q.priority)
			if quadList[0].priority == 0:
				break
			current = quadList.pop(0)
			newSize = floor(current.size/2)
			for j in [(current.x, current.y), (current.x+newSize, current.y), (current.x, current.y+newSize), (current.x+newSize, current.y+newSize)]:
				quadList.append(Quad(j[0], j[1], newSize, sparseRender(j[0], j[1], newSize)))
		for q in quadList:
			for y in range(q.y, q.y + SIZE_LIST[q.size]):
				for x in range(q.x, q.x + SIZE_LIST[q.size]):
					image[y][x] = q.x
		print("Dynamic render time was " + str(time.clock()-t) + " seconds.")
		return(image)


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


class Quad():
	def __init__(self, x, y, size, color):
		self.x = x
		self.y = y
		self.size = size
		self.color = color
		self.priority = size*color


Renderer()
