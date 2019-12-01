# Quadtree Renderer
A quadtree based IFF renderer in Python 3.x.

The program iteratively renders a fractal by starting with a low-resolution quadtree, rendering the corners of each quad, and subdividing quads which have the highest brightness multiplied by size.

A more traditional per-pixel fractal renderer is included for testing purposes, and will probably be used to render high-resolution animations in the final application.

# Kivy Application
This repository also includes a Kivy application which allows users to interactively explore fractals.  Users can use mouse or touch to pan and zoom over Mandelbrot, Julia, and Cactus sets.

Just run the "run.bat" file in the root folder to start the application.

# Color ramps
The fractals can be rendered with a color ramp, which converts the integer output of the escape time algorithm to an index of an image for coloration.  Any bitmap image can be added as a ramp to color fractals (only the top row of pixels will be used).

# Package Dependencies:
 - Numba
 - Kivy
 - Numpy
 - OpenCV (cv2)

# To Do:
 - Add ability to load saved data
 - Add feature to create and render animation using saved data as keyframes
 - Add generalized iteration algorithm so users can input iterative functions without modifying code
 - Add more fractals!
