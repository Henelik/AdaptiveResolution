# Adaptive Resolution
An adaptive resolution fractal renderer in Python 3.6.

The program iteratively renders a fractal by starting with a low-resolution quadtree, rendering the corners of each quad, and subdividing quads which have the highest brightness multiplied by size.  The goal is to make this quadtree-based renderer run in a realtime application explicitly for exploring fractals and setting animation paths to be rendered later by a higher quality renderer.  This will probably be done in pygame.

A more traditional per-pixel fractal renderer is included for testing purposes, and will probably be used to render the high-resolution animations in the final application.

# Package Dependencies:
 - Scipy (planning to remove)
 - Numba
 - Kivy
 - Numpy

# To Do:
 - make both renderers faster by making better use of the fast functions in numpy and scipy
 - find a good formula to calculate an efficient subdivision limit based on image size to render decent quality images in the least amount of time
