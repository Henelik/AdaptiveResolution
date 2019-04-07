import imageio
import numpy as np
import os
import cv2
import time
import sys
sys.path.append("..")
from quadrenderer import gradient, mandelbrot, cactus, julia

class FullRenderer(): # a "traditional" per-pixel Mandelbrot renderer
	def __init__(self, xRes = 512, yRes = 512, AA = 0, maxIters = 100):
		self.xRes = xRes
		self.yRes = yRes
		self.AA = min(max(AA-1, 0), 7)
		self.maxIters = maxIters

		self.cam = Camera(xRes, yRes, xPos = -.5)

	def render(self):
		t = time.clock()
		image = np.zeros((self.xRes, self.yRes, 3), dtype=np.uint8)
		for y in range(self.yRes):
			for x in range(self.xRes):
				pix = []
				AAList = [(x+.25, y+.25), (x+.75, y+.75), (x+.25, y+.75), (x+.75, y+.25), (x+.5, y+.1), (x+.5, y+.9), (x+.1, y+.5), (x+.9, y+.5)]
				for i in range(self.AA):
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



class ScanRenderer():
	def __init__(self, res = 512, AA = 0, maxIters = 100):
		self.res = res
		self.AA = min(AA, 7)
		self.maxIters = maxIters
		self.colorProfile = ColorConverter()
		self.colorDivisor = maxIters/3**.5
		self.colorSlice = 0

		self.cam = Camera(res, res, xPos = -.5)

	def renderPixel(self, coords):
		return mandelbrot.render(coords[0], coords[1], self.maxIters)

	def begin(self): # begin or restart the render (e.g. when the position changes)
		self.image = np.zeros(shape=(self.res, self.res, 3), dtype=np.uint8)
		self.currentX = 0
		self.currentY = 0

	def tick(self): # render and update a pixel
		for i in range(16):
			if self.currentY >= self.res:
				return False
			pix = []
			x, y = self.currentX, self.currentY
			AAList = [(x+.25, y+.25), (x+.75, y+.75), (x+.25, y+.75), (x+.75, y+.25), (x+.5, y+.1), (x+.5, y+.9), (x+.1, y+.5), (x+.9, y+.5)]
			for i in range(self.AA):
				pix.append(self.renderPixel(self.cam.convertPos(AAList[i][0], AAList[i][1])))
			color = sum(pix)/len(pix)
			c = self.colorProfile.convert((color/self.colorDivisor)%1)
			self.image[self.currentY][self.currentX] = np.append(c[self.colorSlice:], c[:self.colorSlice])
			self.currentX += 1
			if self.currentX >= self.res:
				self.currentX = 0
				self.currentY += 1
		return True

	def updateImage(self):
		pass

	def fullUpdateImage(self):
		pass


class CactusScanRenderer(ScanRenderer):
	def renderPixel(self, coords):
		return cactus.render(coords[0], coords[1], self.maxIters)


class JuliaScanRenderer(ScanRenderer):
	def renderPixel(self, coords):
		return julia.render(coords[0], coords[1], .3, .5, self.maxIters)



class RealtimeQuadRenderer(): # the realtime quadtree renderer
	def __init__(self, res = 512, AA = 0, maxIters = 100):
		self.res = res
		self.AA = AA
		self.maxIters = maxIters
		self.colorProfile = ColorConverter()
		self.colorDivisor = maxIters/3**.5
		self.colorSlice = 0

		self.cam = Camera(res, res, xPos = -.5)

	def sparseRender(self, x, y, size):
		# render a quad, referencing the sparse array if applicable
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
		return pix

	def renderPixel(self, coords):
		return mandelbrot.render(coords[0], coords[1], self.maxIters)

	def begin(self): # begin or restart the render (e.g. when the position changes)
		self.image = np.zeros(shape=(self.res, self.res, 3), dtype=np.uint8)
		self.sparseArray = {}
		self.sortLimit = 10
		s1 = self.res//2
		s2 = self.res//4
		s3 = s1+s2
		self.quadList = [
		Quad(0 , 0 , s2, self.sparseRender(0 , 0 , s2)),
		Quad(0 , s1, s2, self.sparseRender(0 , s1, s2)),
		Quad(s1, 0 , s2, self.sparseRender(s1, 0 , s2)),
		Quad(s1, s1, s2, self.sparseRender(s1, s1, s2)), # the 4 top left subdivisions

		Quad(s2, 0 , s2, self.sparseRender(s2, 0 , s2)),
		Quad(s2, s1, s2, self.sparseRender(s2, s1, s2)),
		Quad(s3, 0 , s2, self.sparseRender(s3, 0 , s2)),
		Quad(s3, s1, s2, self.sparseRender(s3, s1, s2)), # the 4 top right subdivisions

		Quad(0 , s2, s2, self.sparseRender(0 , s2, s2)),
		Quad(0 , s3, s2, self.sparseRender(0 , s3, s2)),
		Quad(s1, s2, s2, self.sparseRender(s1, s2, s2)),
		Quad(s1, s3, s2, self.sparseRender(s1, s3, s2)), # the 4 bottom left subdivisions

		Quad(s2, s2, s2, self.sparseRender(s2, s2, s2)),
		Quad(s2, s3, s2, self.sparseRender(s2, s3, s2)),
		Quad(s3, s2, s2, self.sparseRender(s3, s2, s2)),
		Quad(s3, s3, s2, self.sparseRender(s3, s3, s2))] # the 4 bottom right subdivisions

	def tick(self): # subdivide and update the highest priority quad
		self.sortLimit -= 1
		if self.sortLimit <= 0 or self.quadList[0].priority == 0:
			self.quadList.sort(key = lambda q: int(q.priority), reverse = True)
			self.sortLimit = len(self.quadList)//2
		if self.quadList[0].priority == 0:
			return False
		current = self.quadList.pop(0)
		newSize = current.size//2
		for j in [(current.x, current.y), (current.x+newSize, current.y), (current.x, current.y+newSize), (current.x+newSize, current.y+newSize)]:
			self.quadList.append(Quad(j[0], j[1], newSize, self.sparseRender(j[0], j[1], newSize)))
		return True

	def updateImage(self): # update the image (e.g. to display it while rendering)
		for q in self.quadList:
			if not q.updated:
				c = self.colorProfile.convert((q.color/self.colorDivisor)%1)
				self.image[q.y:q.y+q.size, q.x:q.x+q.size] = np.append(c[self.colorSlice:], c[:self.colorSlice])
				q.updated = True

	def fullUpdateImage(self): # update the entire image (e.g. when the color changes)
		# This is a VERY expensive operation, and can take upwards of a second on a 1024x1024 image
		for q in self.quadList:
			c = self.colorProfile.convert((q.color/self.colorDivisor)%1)
			self.image[q.y:q.y+q.size, q.x:q.x+q.size] = np.append(c[self.colorSlice:], c[:self.colorSlice])
			q.updated = True


class RealtimeJuliaQuadRenderer(RealtimeQuadRenderer):
	def __init__(self, res = 512, AA = 0, maxIters = 100, cx = .3, cy = .5):
		super().__init__(res, AA, maxIters)
		self.cx = cx
		self.cy = cy
		self.cam.xPos = 0

	def renderPixel(self, coords):
		return julia.render(coords[0], coords[1], self.cx, self.cy, self.maxIters)


class RealtimeCactusQuadRenderer(RealtimeQuadRenderer):
	def __init__(self, res = 512, AA = 0, maxIters = 100):
		super().__init__(res, AA, maxIters)
		self.cam = Camera(res, res, xPos = 0)

	def renderPixel(self, coords):
		return cactus.render(coords[0], coords[1], self.maxIters)


class RealtimeGradientQuadRenderer(RealtimeQuadRenderer):
	def __init__(self, res = 512, AA = 0, maxIters = 100):
		super().__init__(res, AA, maxIters)
		self.cam = Camera(res, res, xPos = .5, zoom = 1)

	def renderPixel(self, coords):
		return gradient.render(coords[0], coords[1], self.maxIters)


class Quad():
	def __init__(self, x, y, size, colorList):
		self.x = x
		self.y = y
		self.size = size
		self.color = sum(colorList)/len(colorList) # the scalar color of the quad (based on iterations till convergence)
		self.updated = False # each quad keeps track of whether it has been added to the image or not
		if size <= 1:
			self.priority = 0
		else:
			if len(set(colorList)) > 1:
				self.priority = self.color*size*size
			else:
				self.priority = 0


class ColorConverter():
	def __init__(self, profileName = "greyscale"):
		self.loadProfile(profileName)

	def loadProfile(self, profileName):
		self.profileName = profileName
		if profileName != "greyscale":
			self.ramp = cv2.imread("color_profiles/" + profileName + ".bmp")[0]

	def convert(self, scalar): # take a ratio and convert it to an RGB int ala Blender's Color Ramp node
		if scalar == 0: # exception for converging quads
			return(0, 0, 0)
		if self.profileName == "greyscale":
			l = 256
			c = int(scalar**(.25)*l*3%l)
			return (c, c, c)
		l = len(self.ramp)
		return self.ramp[int(scalar**(.25)*l*3%l)]


class Camera(): # This class is responsible for handling the conversion from pixel position to mathematical space
	def __init__(self, xRes, yRes, xPos = 0, yPos = 0, zoom = 2):
		self.xRes = xRes
		self.yRes = yRes
		self.xPos = xPos
		self.yPos = yPos
		self.zoom = zoom

		# convert the center coordinates to lower left coordinates for Kivy compatibility
		self.xPos = xPos-zoom/2
		self.yPos = yPos+zoom/2

	def convertPos(self, x, y):
		return((self.convertX(x), self.convertY(y)))

	def convertX(self, x): # convert an x coordinate from math to pixel space
		return x*self.zoom/self.xRes+self.xPos

	def convertY(self, y): # convert a y coordinate from math to pixel space
		return y*self.zoom/self.yRes-self.yPos


if __name__ == "__main__":
	if not os.path.exists('renders'):
		os.makedirs('renders')
	for res in (16, 32, 64, 128, 256, 512, 1024):
		#renderer = RealtimeQuadRenderer(res = res, AA = 8, maxIters = 1000)
		#renderer = ScanRenderer(res = res, AA = 8, maxIters = 1000)
		#renderer = RealtimeJuliaQuadRenderer(res = res, AA = 8, maxIters = 1000)
		#renderer = JuliaScanRenderer(res = res, AA = 8, maxIters = 1000)
		#renderer = RealtimeCactusQuadRenderer(res = res, AA = 8, maxIters = 1000)
		renderer = CactusScanRenderer(res = res, AA = 8, maxIters = 1000)
		t = time.time()
		renderer.begin()
	
		while renderer.tick():
			pass
	
		renderer.updateImage()
		print("Render time at " + str(res) + " "*(4-len(str(res))) + " was " + str(time.time() - t))
	imageio.imwrite('renders/julia.png', renderer.image)