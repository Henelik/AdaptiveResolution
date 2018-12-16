from numba import jit

@jit(cache = True)
def render(x, y):
	r = max(min(x, 1), 0)
	g = max(min(y, 1), 0)
	b = 0
	return((r, g, b))

@jit(cache = True)
def renderWire(x, y):
	return(x)