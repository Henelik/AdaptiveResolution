from numba import jit

@jit(cache = True)
def render(zReal, zImag, cReal, cImag, maxIter = 100):
	iters = 0
	while True:
		iters += 1
		# Square the real and imaginary components BEFORE checking for divergence
		real2 = zReal*zReal
		imag2 = zImag*zImag
		if real2 + imag2 > 4.0: # Check for divergence against 4 instead of 2 because of squared coordinates
			return iters # Return the number of iterations if this pixel diverges
		zImag = 2 * zImag * zReal + cImag # Finish the required math for this iteration if the pixel has not diverged yet
		zReal = real2 - imag2 + cReal
		if iters >= maxIter:
			return 0 # return 0 if the pixel does not diverge
