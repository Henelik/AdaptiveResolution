from scipy.misc import imsave
import numpy as np
import os
import cv2
import time
try:
	from renderer import gradient, mandelbrot, cactus, julia
except(ImportError):
	import gradient, mandelbrot, cactus, julia

class FullRenderer(): # a "traditional" per-pixel Mandelbrot renderer
	def __init__(self, xRes = 512, yRes = 512, AA = 0, maxIters = 100):
		self.xRes = xRes
		self.yRes = yRes
		self.AA = min(max(AA-1, 0), 7)
		self.maxIters = maxIters

		self.cam = Camera(xRes, yRes, xPos = -.5)

	def render(self):
		t = time.clock()
		image = np.zeros((self.xRes, self.yRes, 3), dtype=np.uint32)
		for y in range(self.yRes):
			for x in range(self.xRes):
				pix = []
				AAList = [(x+.25, y+.25), (x+.75, y+.75), (x+.25, y+.75), (x+.75, y+.25), (x+.5, y+.1), (x+.5, y+.9), (x+.1, y+.5), (x+.9, y+.5)]
				for i in range(self.AA+1):
					pix.append(self.renderPixel(self.cam.convertPos(AAList[i][0], AAList[i][1])))
				col = sum(pix)
				image[y][x] = (col, col, col)

		print("Render time was " + str(time.clock()-t) + " seconds.")
		return image

	def renderPixel(self, coords):
		return mandelbrot.render(coords[0], coords[1], self.maxIters)


class GradientRenderer(FullRenderer):
	def __init__(self, xRes = 512, yRes = 512, AA = 0, maxIters = 100):
		super().__init__(xRes, yRes, AA, maxIters)
		self.cam.xPos = .5
		self.cam.zoom = 1

	def renderPixel(self, coords):
		return gradient.render(coords[0], coords[1])


class SquareMandelRenderer(FullRenderer):
	def __init__(self, xRes = 512, yRes = 512, AA = 0, maxIters = 100):
		super().__init__(xRes, yRes, AA, maxIters)

	def renderPixel(self, coords):
		return mandelbrot.renderSquare(coords[0], coords[1], self.maxIters)


class JuliaFullRenderer(FullRenderer): # a traditional Julia renderer
	def __init__(self, xRes = 512, yRes = 512, AA = 0, maxIters = 100, cx = 0.3, cy = .5):
		super().__init__(xRes, yRes, AA, maxIters)
		self.cx = cx
		self.cy = cy

	def renderPixel(self, coords):
		return julia.render(coords[0], coords[1], self.cx, self.cy, self.maxIters)


class CactusFullRenderer(FullRenderer): # a traditional Cactus renderer
	def __init__(self, xRes = 512, yRes = 512, AA = 0, maxIters = 100):
		super().__init__(xRes, yRes, AA, maxIters)
		self.cam.xPos = 0

	def renderPixel(self, coords):
		return cactus.render(coords[0], coords[1], self.maxIters)


class QuadRenderer(): # a non-interactive (not ticked) version of the quadtree renderer
	def __init__(self, res = 512, AA = 0, disableMaxResAA = True, subdivMax = 5000, maxIters = 100):
		self.res = res
		self.AA = min(max(AA, 0), 7)
		self.disableMaxResAA = disableMaxResAA
		self.subdivMax = subdivMax
		self.maxIters = maxIters

		self.cam = Camera(res, res, xPos = -.5)

	def sparseRender(self, x, y, size):
		if size == 1 and self.disableMaxResAA:
			return mandelbrot.render(self.cam.convertX(x), self.cam.convertY(y), self.maxIters)
		half = size/2
		pixelList = ((x, y), (x+size, y+size), (x+size, y), (x, y+size), (x+half, y+half), (x+half, y), (x, y+half), (x+half, y+size), (x+size, y+half))
		pix = []
		for i in pixelList:
			if len(pix) > self.AA+2:
				break
			if i in self.sparseArray:
				pix.append(self.sparseArray[i])
			else:
				pix.append(mandelbrot.render(self.cam.convertX(i[0]), self.cam.convertY(i[1]), self.maxIters))
				self.sparseArray[i] = pix[-1]
		return sum(pix)

	def render(self):
		t = time.clock()
		image = [[0 for x in range(self.res)] for y in range(self.res)]
		self.sparseArray = {}

		s = self.res//2
		quadList = [
		Quad(0, 0, s, self.sparseRender(0, 0, s)),
		Quad(0, s, s, self.sparseRender(0, s, s)),
		Quad(s, 0, s, self.sparseRender(s, 0, s)),
		Quad(s, s, s, self.sparseRender(s, s, s))] # start with 4 quads that are 1/2 the image size on a side
		sortLimit = 0 # heuristically limit how often we sort to improve performance
		subdivisions = 0
		while subdivisions < self.subdivMax:
			subdivisions += 1
			sortLimit -= 1
			if sortLimit <= 0 or quadList[0].priority == 0:
				quadList.sort(key = lambda q: q.priority, reverse = True)
				sortLimit = len(quadList)//2
				if quadList[0].priority == 0:
					break
			current = quadList.pop(0)
			newSize = current.size//2
			for j in [(current.x, current.y), (current.x+newSize, current.y), (current.x, current.y+newSize), (current.x+newSize, current.y+newSize)]:
				quadList.append(Quad(j[0], j[1], newSize, self.sparseRender(j[0], j[1], newSize)))
		for q in quadList:
			for y in range(q.y, q.y + q.size):
				for x in range(q.x, q.x + q.size):
					image[y][x] = q.color
		print("Dynamic render time was " + str(time.clock()-t) + " seconds.")
		return image


class JuliaQuadRenderer(QuadRenderer):
	def __init__(self, res = 512, AA = 0, disableMaxResAA = True, subdivMax = 5000, maxIters = 100, cx = 0.3, cy = .5):
		super().__init__(res, AA, disableMaxResAA, subdivMax, maxIters)
		self.cx = cx
		self.cy = cy

	def sparseRender(self, x, y, size):
		if size == 1 and self.disableMaxResAA:
			return julia.render(self.cam.convertX(x), self.cam.convertY(y), self.cx, self.cy, self.maxIters)
		half = size/2
		pixelList = ((x, y), (x+size, y+size), (x+size, y), (x, y+size), (x+half, y+half), (x+half, y), (x, y+half), (x+half, y+size), (x+size, y+half))
		pix = []
		for i in pixelList:
			if len(pix) > self.AA+2:
				break
			if i in self.sparseArray:
				pix.append(self.sparseArray[i])
			else:
				pix.append(julia.render(self.cam.convertX(i[0]), self.cam.convertY(i[1]), self.cx, self.cy, self.maxIters))
				self.sparseArray[i] = pix[-1]
		return sum(pix)


class RealtimeQuadRenderer(): # the realtime quadtree renderer
	def __init__(self, res = 512, AA = 0, subdivMax = 5000, maxIters = 100):
		self.res = res
		self.AA = AA
		self.subdivMax = subdivMax
		self.maxIters = maxIters
		self.colorProfile = ColorConverter()
		self.colorDivisor = maxIters/3

		self.cam = Camera(res, res, xPos = -.5)

	def sparseRender(self, x, y, size):
		half = size/2
		pixelList = [(x, y), (x+size, y+size), (x+size, y), (x, y+size), (x+half, y+half), (x+half, y), (x, y+half), (x+half, y+size), (x+size, y+half)]
		pix = []
		for i in pixelList:
			if len(pix) > self.AA+2:
				break
			if i in self.sparseArray:
				pix.append(self.sparseArray[i])
			else:
				pix.append(self.renderPixel(self.cam.convertPos(i[0], i[1])))
				self.sparseArray[i] = pix[-1]
		return sum(pix)/len(pix)

	def renderPixel(self, coords):
		return mandelbrot.render(coords[0], coords[1], self.maxIters)

	def begin(self): # begin or restart the render (e.g. when the position changes)
		self.image = np.zeros(shape=(self.res, self.res, 3), dtype=np.uint8)
		self.sparseArray = {}
		s = self.res//2
		self.sortLimit = 10
		self.quadList = [
		Quad(0, 0, s, self.sparseRender(0, 0, s)),
		Quad(0, s, s, self.sparseRender(0, s, s)),
		Quad(s, 0, s, self.sparseRender(s, 0, s)),
		Quad(s, s, s, self.sparseRender(s, s, s))] # start with 4 quads that are 1/2 the image size on a side

	def tick(self): # subdivide and update the highest priority quad
		t = time.clock()
		self.sortLimit -= 1
		if self.sortLimit <= 0 or self.quadList[0].priority == 0:
			self.quadList.sort(key = lambda q: int(q.priority), reverse = True)
			self.sortLimit = len(self.quadList)//2
		if self.quadList[0].priority == 0:
			print("Can't subdivide further!")
			return False
		current = self.quadList.pop(0)
		newSize = current.size//2
		for j in [(current.x, current.y), (current.x+newSize, current.y), (current.x, current.y+newSize), (current.x+newSize, current.y+newSize)]:
			self.quadList.append(Quad(j[0], j[1], newSize, self.sparseRender(j[0], j[1], newSize)))
		#print("Tick time was " + str(time.clock() - t))
		return True

	def updateImage(self): # update the image (e.g. to display it while rendering)
		t = time.clock()
		for i in range(len(self.quadList)):
			if not self.quadList[i].updated:
				q = self.quadList[i]
				if self.colorProfile.profileName != "greyscale":
					c = self.colorProfile.convert((q.color/self.colorDivisor)%1)
				else:
					c = (q.color/self.maxIters)*16384
				for y in range(q.y, q.y + q.size):
					for x in range(q.x, q.x + q.size):
						self.image[y][x] = c
				q.updated = True
		#print("Image update time was " + str(time.clock() - t))


class RealtimeJuliaQuadRenderer(RealtimeQuadRenderer):
	def __init__(self, res = 512, AA = 0, disableMaxResAA = False, subdivMax = 5000, maxIters = 100, cx = .3, cy = .5):
		super().__init__(res, AA, disableMaxResAA, subdivMax, maxIters)
		self.cx = cx
		self.cy = cy
		self.cam.xPos = 0

	def renderPixel(self, coords):
		return julia.render(coords[0], coords[1], self.cx, self.cy, self.maxIters)


class RealtimeCactusQuadRenderer(RealtimeQuadRenderer):
	def __init__(self, res = 512, AA = 0, disableMaxResAA = False, subdivMax = 5000, maxIters = 100):
		super().__init__(res, AA, disableMaxResAA, subdivMax, maxIters)
		self.cam.xPos = 0

	def renderPixel(self, coords):
		return cactus.render(coords[0], coords[1], self.maxIters)


class RealtimeGradientQuadRenderer(RealtimeQuadRenderer):
	def __init__(self, res = 512, AA = 0, disableMaxResAA = False, subdivMax = 5000, maxIters = 100):
		super().__init__(res, AA, disableMaxResAA, subdivMax, maxIters)
		self.cam.xPos = .5
		self.cam.zoom = 1

	def renderPixel(self, coords):
		return gradient.render(coords[0], coords[1])


class Quad():
	def __init__(self, x, y, size, color):
		self.x = x
		self.y = y
		self.size = size
		self.color = color # the scalar color of the quad (based on iterations till convergence)
		self.updated = False # each quad keeps track of whether it has been added to the image or not
		if size <= 1:
			self.priority = 0
		else:
			self.priority = color*size*size


class ColorConverter():
	def __init__(self, profileName = "greyscale"):
		self.loadProfile(profileName)

	def loadProfile(self, profileName):
		self.profileName = profileName
		if profileName != "greyscale":
			self.ramp = cv2.imread("color_profiles/" + profileName + ".bmp")[0]

	def convert(self, scalar): # take a ratio and convert it to an RGB int ala Blender's Color Ramp node
		if scalar == 0:
			return(0, 0, 0)
		l = len(self.ramp)
		i = int(scalar**(.25)*l*3%l)
		return self.ramp[i]


class Camera(): # This class is responsible for handling the conversion from pixel position to mathematical space
	def __init__(self, xRes, yRes, xPos = 0, yPos = 0, zoom = 2):
		self.xRes = xRes
		self.yRes = yRes
		self.xPos = xPos
		self.yPos = yPos
		self.zoom = zoom

		# convert the center coordinates to lower left coordinates (this is a workaround for now)
		self.xPos = xPos-zoom/2
		self.yPos = yPos+zoom/2

	def convertPos(self, x, y):
		return((self.convertX(x), self.convertY(y)))

	def convertX(self, x): # convert a x coordinate from math to pixel space
		return x*self.zoom/self.xRes+self.xPos
		#return ((x-self.xRes/2)*self.zoom/self.xRes)+self.xPos

	def convertY(self, y): # convert a y coordinate from math to pixel space
		return y*self.zoom/self.yRes-self.yPos
		#return ((y-self.yRes/2)*self.zoom/self.yRes)-self.yPos


if __name__ == "__main__":
	res = 1024
	mandelR = FullRenderer(xRes = res, yRes = res, AA = 4, maxIters = 100)
	squareR = SquareMandelRenderer(xRes = res, yRes = res, AA = 4, maxIters = 100)
	juliaR = JuliaFullRenderer(xRes = res, yRes = res, AA = 4, maxIters = 100)
	cactR = CactusFullRenderer(xRes = res, yRes = res, AA = 4, maxIters = 100)
	mandelQuadR = QuadRenderer(res = res, AA = 4, disableMaxResAA = False, subdivMax = 15000)
	juliaQuadR = JuliaQuadRenderer(res = res, AA = 4, disableMaxResAA = False, subdivMax = 15000)

	if not os.path.exists('renders'):
		os.makedirs('renders')
	
	#imsave('renders/mandel.png', mandelR.render())
	#imsave('renders/squareMandel.png', squareR.render())
	#imsave('renders/julia.png', juliaR.render())
	#imsave('renders/cactus.png', cactR.render())
	#imsave('renders/mandelQuad.png', mandelQuadR.render())
	#imsave('renders/juliaQuad.png', juliaQuadR.render())
	imsave('renders/gradient.png', GradientRenderer(xRes = res, yRes = res).render())
