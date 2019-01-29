from numba import jit
from scipy.misc import imsave
import gradient, mandelbrot, cactus, julia
import time
from math import ceil, floor
import itertools

class FullRenderer():
	def __init__(self, xRes = 512, yRes = 512, AA = 0, maxIters = 100):
		self.xRes = xRes
		self.yRes = yRes
		self.AA = min(max(AA-1, 0), 7)
		self.maxIters = maxIters

		self.cam = Camera(xRes, yRes, xPos = -.5)

	def render(self):
		t = time.clock()

		#image = [[mandelbrot.render(self.cam.convertX(x), self.cam.convertY(y), maxIters) for x in range(self.xRes)] for y in range(self.yRes)]
		image = [[0 for x in range(self.xRes)] for y in range(self.yRes)]
		for y in range(self.yRes):
			for x in range(self.xRes):
				pix = []
				AAList = [(x+.25, y+.25), (x+.75, y+.75), (x+.25, y+.75), (x+.75, y+.25), (x+.5, y+.1), (x+.5, y+.9), (x+.1, y+.5), (x+.9, y+.5)]
				for i in range(self.AA+1):
					pix.append(mandelbrot.render(self.cam.convertX(AAList[i][0]), self.cam.convertY(AAList[i][1]), self.maxIters))
				image[y][x] = sum(pix)

		print("Render time was " + str(time.clock()-t) + " seconds.")
		return image

class QuadRenderer():
	def __init__(self, res = 512, AA = 0, disableMaxResAA = True, subdivMax = 5000, maxIters = 100):
		self.res = res
		self.AA = min(max(AA, 0), 7)
		self.disableMaxResAA = disableMaxResAA
		self.subdivMax = subdivMax
		self.maxIters = maxIters

		self.cam = Camera(res, res, xPos = -.5)

	def render(self):
		def sparseRender(x, y, size):
			if size == 1 and self.disableMaxResAA:
				return mandelbrot.render(self.cam.convertX(x), self.cam.convertY(y), self.maxIters)
			half = size/2
			pixelList = [(x, y), (x+size, y+size), (x+size, y), (x, y+size), (x+half, y+half), (x+half, y), (x, y+half), (x+half, y+size), (x+size, y+half)]
			pix = []
			for i in pixelList:
				if len(pix) > self.AA+2:
					break
				if i in sparseArray:
					pix.append(sparseArray[i])
				else:
					pix.append(mandelbrot.render(self.cam.convertX(i[0]), self.cam.convertY(i[1]), self.maxIters))
					sparseArray[i] = pix[-1]
			return sum(pix)

		t = time.clock()
		image = [[0 for x in range(self.res)] for y in range(self.res)]
		sparseArray = {}

		s = floor(self.res/2)
		quadList = [
		Quad(0, 0, s, sparseRender(0, 0, s)),
		Quad(0, s, s, sparseRender(0, s, s)),
		Quad(s, 0, s, sparseRender(s, 0, s)),
		Quad(s, s, s, sparseRender(s, s, s))] # start with 4 quads that are 1/2 the image size on a side
		sortLimit = 0 # heuristically limit how often we sort to improve
		subdivisions = 0
		while subdivisions < self.subdivMax:
			subdivisions += 1
			sortLimit -= 1
			if sortLimit <= 0 or quadList[0].priority == 0:
				quadList.sort(key = lambda q: q.priority, reverse = True)
				sortLimit = floor(len(quadList)/2)
				if quadList[0].priority == 0:
					break
			current = quadList.pop(0)
			newSize = floor(current.size/2)
			for j in [(current.x, current.y), (current.x+newSize, current.y), (current.x, current.y+newSize), (current.x+newSize, current.y+newSize)]:
				quadList.append(Quad(j[0], j[1], newSize, sparseRender(j[0], j[1], newSize)))
		for i in range(len(quadList)): # iterate over index so that index maps can be rendered
			q = quadList[i]
			for y in range(q.y, q.y + q.size):
				for x in range(q.x, q.x + q.size):
					image[y][x] = q.color
					#image[y][x] = i
		print("Dynamic render time was " + str(time.clock()-t) + " seconds.")
		return image


class RealtimeQuadRenderer():
	def __init__(self, res = 512, AA = 0, disableMaxResAA = True, subdivMax = 5000, maxIters = 100):
		self.res = res
		self.AA = AA
		self.disableMaxResAA = disableMaxResAA
		self.subdivMax = subdivMax
		self.maxIters = maxIters

		self.cam = Camera(res, res, xPos = -.5)

	def sparseRender(self, x, y, size):
		if size == 1 and self.disableMaxResAA:
			return mandelbrot.render(self.cam.convertX(x), self.cam.convertY(y), maxIters)
		half = size/2
		pixelList = [(x, y), (x+size, y+size), (x+size, y), (x, y+size), (x+half, y+half), (x+half, y), (x, y+half), (x+half, y+size), (x+size, y+half)]
		pix = []
		for i in pixelList:
			if len(pix) > self.AA+2:
				break
			if i in sparseArray:
				pix.append(sparseArray[i])
			else:
				pix.append(mandelbrot.render(self.cam.convertX(i[0]), self.cam.convertY(i[1]), maxIters))
				sparseArray[i] = pix[-1]
		return sum(pix)

	def beginRender(self): # begin or restart the render (e.g. when the position changes)
		self.image = [[0 for x in range(self.res)] for y in range(self.res)]
		self.sparseArray = {}
		s = floor(self.res/2)
		self.quadList = [
		Quad(0, 0, s, self.sparseRender(0, 0, s)),
		Quad(0, s, s, self.sparseRender(0, s, s)),
		Quad(s, 0, s, self.sparseRender(s, 0, s)),
		Quad(s, s, s, self.sparseRender(s, s, s))] # start with 4 quads that are 1/2 the image size on a side

	def tickRenderer(self): # subdivide and update the highest priority quad
		if self.quadList[0].priority == 0:
			print("Can't subdivide further!")
			return
		current = self.quadList.pop(0)
		newSize = floor(current.size/2)
		for j in [(current.x, current.y), (current.x+newSize, current.y), (current.x, current.y+newSize), (current.x+newSize, current.y+newSize)]:
			q = Quad(j[0], j[1], newSize, self.sparseRender(j[0], j[1], newSize))
			inserted = False
			for k in range(len(self.quadList)):
				if self.quadList[k].priority <= q.priority:
					self.quadList.insert(k, q)
					inserted = True
					break
			if not inserted:
				self.quadList.append(q)

	def updateImage(self): # update the image (e.g. to display it while rendering) 
		for i in range(len(self.quadList)): # iterate over index so that index maps can be rendered
			q = self.quadList[i]
			for y in range(q.y, q.y + q.size):
				for x in range(q.x, q.x + q.size):
					self.image[y][x] = q.color
					#self.image[y][x] = i
					#self.image[y][x] = q.priority


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
		if size <= 1:
			self.priority = 0
		else:
			self.priority = size*size*color

if __name__ == "__main__":
	res = 1024
	fullR = FullRenderer(xRes = res, yRes = res, AA = 4)
	quadR = QuadRenderer(res = res, AA = 2, disableMaxResAA = False, subdivMax = 15000)
	imsave('dynamic.png', quadR.render())
	imsave('fullRes.png', fullR.render())
