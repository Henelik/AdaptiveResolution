from numba import jit

@jit(cache = True)
def render(zx, zy, maxIter = 100):
	iters = 0
	x = zx
	y = zy
	while True:
		iters += 1
		# Square the x and y components BEFORE checking for divergence
		x2 = x*x
		y2 = y*y
		if x2 + y2 > 4.0: # Check for divergence against 4 instead of 2 because of squared coordinates
			return iters # Return the number of iterations if this pixel diverges
		x, y = (x2 - 3*y2 + zx - 1)*x - y*zy - zx, (3*x2 - y2 + zx - 1)*y + x*zy - zy # Finish the required math for this iteration if the pixel has not diverged yet
		if iters >= maxIter:
			return 0