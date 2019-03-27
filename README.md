# Adaptive Resolution
An adaptive resolution fractal renderer in Python 3.6.

The program iteratively renders a fractal by starting with a low-resolution quadtree, rendering the corners of each quad, and subdividing quads which have the highest brightness multiplied by size.

Kivy allows this application to run interactively in realtime.

A more traditional per-pixel fractal renderer is included for testing purposes, and will probably be used to render the high-resolution animations in the final application.

# Package Dependencies:
 - Scipy
 - Numba
 - Kivy
 - Numpy
 - OpenCV (cv2)

# To Do:
 - Create a formula to control the iteration count and degree multiplier based on zoom
 - Add generalized iteration algorithm so users can input iterative functions without modifying code
 - Add full rendering within application (save image button)
 - Add code in the Kivy application to adaptively change the number of ticks based on the time it takes to tick and update
