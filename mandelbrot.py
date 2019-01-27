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
			return n # Return the number of iterations if this pixel diverges
		imag = 2 * real * imag + zImag # Finish the required math for this iteration if the pixel has not diverged yet
		real = real2 - imag2 + zReal
	return 0
