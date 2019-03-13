from numba import jit

@jit(cache = True)
def render(zx, zy, maxIter = 100):
	iters = 0
	x = zx
	y = zy
	while iters < maxIter:
		iters += 1
		# Square the x and y components BEFORE checking for divergence
		x2 = x*x
		y2 = y*y
		if x2 + y2 > 4.0: # Check for divergence against 4 instead of 2 because of squared coordinates
			return iters # Return the number of iterations if this pixel diverges
		y = 2 * x * y + zy # Finish the required math for this iteration if the pixel has not diverged yet
		x = x2 - y2 + zx
	return 0 # return 0 if the pixel does not diverge

@jit(cache = True)
def renderSquare(zx, zy, maxIter = 100):
	iters = 0
	x = zx
	y = zy
	while iters < maxIter:
		iters += 1
		if abs(x) + abs(y) > 2.0: # Check for divergence with Freshman/Manhattan method
			return iters # Return the number of iterations if this pixel diverges
		x2 = x*x
		y2 = y*y
		y = 2 * x * y + zy # Finish the required math for this iteration if the pixel has not diverged yet
		x = x2 - y2 + zx
	return 0 # return 0 if the pixel does not diverge