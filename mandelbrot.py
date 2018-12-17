from numba import jit

@jit(cache = True)
def render(zReal, zImag, maxIter = 500):
	real = zReal
	imag = zImag
	for n in range(maxIter):
		# Square the real and imaginary components BEFORE checking for divergence
		real2 = real*real
		imag2 = imag*imag
		if real2 + imag2 > 4.0: # Check for divergence against 4 instead of 2 because of squared coordinates
			return n # Return the number of iterations if this pixel diverges
		imag = 2 * real * imag + zImag # Finish the required math for this iteration if the pixel has not diverged yet
		real = real2 - imag2 + zReal
	return 0

@jit(cache = True)
def renderWire(x, y, maxIter = 20, margin = .5):
	x1 = x
	y1 = y
	for i in range(maxIter):
		x1, y1 = x1*x1-y1*y1+x, 2*x1*y1+y
	test = x1*x1+y1*y1
	if test > 4-margin and test < 4+margin:
		return(1)
	return(0)
