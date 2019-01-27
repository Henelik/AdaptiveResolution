from numba import jit
from math import sqrt, log

@jit(cache = True)
def render(zReal, zImag, maxIter = 100):
	real = zReal
	imag = zImag
	for n in range(maxIter):
		# Square the real and imaginary components BEFORE checking for divergence
		real2 = real*real
		imag2 = imag*imag
		if real2 + imag2 > 4.0: # Check for divergence against 4 instead of 2 because of squared coordinates
			return n/maxIter # Return the number of iterations if this pixel diverges
		imag = 2 * real * imag + zImag # Finish the required math for this iteration if the pixel has not diverged yet
		real = real2 - imag2 + zReal
	return 0

@jit(cache = True)
def renderWire(zReal, zImag, maxIter = 100, thresh = 50):
	real = zReal
	imag = zImag
	for n in range(maxIter):
		real2 = real*real
		imag2 = imag*imag
		if real2 + imag2 > 4.0:
			if n > thresh:
				return n
			return 0
		imag = 2 * real * imag + zImag
		real = real2 - imag2 + zReal
	return 0

@jit(cache = True)
def renderDistEst(zReal, zImag, maxIter = 1):
	real = zReal
	imag = zImag
	dZReal = 1
	dZImag = 0

	for n in range(maxIter):
		real2 = real*real
		imag2 = imag*imag

		if real2 + imag2 > 4.0: # If we exceed the limit, stop iterating
			return 0

		dZReal = 2*(real*dZReal - zImag*dZImag)+1 # iterate the derivative
		dZImag = 2*(real*dZImag + zImag*dZReal) # iterate the derivative

		imag = 2 * real * imag + zImag # iterate the quadtric equation
		real = real2 - imag2 + zReal # iterate the quadtric equation

	modZ = sqrt(real*real + imag*imag)
	moddZ = sqrt(dZReal*dZReal + dZImag*dZImag)
	if moddZ == 0:
		return 1
	print(max(0, modZ*log(modZ)/moddZ))

	return min(1, max(0, modZ*log(modZ)/moddZ))
