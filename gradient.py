from numba import jit
from math import sin

@jit(cache = True)
def render(x, y):
	return((max(min(x, 1), 0), max(min(y, 1), 0), max(min(0-x-y, 1), 0)))

#def render(x, y):
#	r = max(min(x, 1), 0)
#	g = max(min(y, 1), 0)
#	b = 0
#	return((r, g, b))

@jit(cache = True)
def renderWire(x, y):
	if x > .95:
		return(1)
	return(0)
