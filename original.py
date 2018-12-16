# This code was written to be run in Linux, and will not work properly in Windows due to lack of multiprocessing support.
import numpy as np
from numba import jit
from scipy.misc import imsave
import multiprocessing
import colorsys

# Returns the number of iterations before divergence at a given coordinate using the Mandelbrot algorithm
@jit # These "@jit" tags tell the Numba module to compile this function
def mandelbrot(zReal, zImag, maxIter):
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
    return -1 # Return -1 if the pixel converges

# Returns the number of iterations before divergence at a given coordinate using the Julia algorithm
@jit
def julia(zReal, zImag, cReal, cImag, maxIter):
    for n in range(maxIter):
        # Square the real and imaginary components BEFORE checking for divergence
        real2 = zReal*zReal
        imag2 = zImag*zImag
        if real2 + imag2 > 4.0: # Check for divergence against 4 instead of 2 because of squared coordinates
            return n # Return the number of iterations if this pixel diverges
        zImag = 2 * zImag * zReal + cImag # Finish the required math for this iteration if the pixel has not diverged yet
        zReal = real2 - imag2 + cReal
    return -1 # Return -1 if the pixel converges

# Renders an image based on the center coordinate of the “camera”, and a zoom value.
@jit
def fractalPos(xPos, yPos, zoom, width, height, maxIter, xJulia, yJulia, imgName, mode):
    print(imgName) # Print the name of the current frame
    
    # Determine where the corners of the image are using the center and zoom values
    xmin = xPos - zoom
    xmax = xPos + zoom
    ymin = yPos - (zoom * height / width)
    ymax = yPos + (zoom * height / width)
    
    # Set up arrays of interpolated values for screen space
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    
    n4 = np.empty((height, width, 3)) # Make an empty Numpy array of 3 values (RGB) for each pixel
    
    # Init vars to track inner pixels for skipping algorithm
    innerPix = 0
    totalInner = 0
    
    # Perform the iterative functions for all pixels
    for x in range(width):
        for y in range(height):
            
            # Skip this pixel if there have been more than 2 inner pixels in a row (used to be 5, changed to 2 for faster rendering)
            if innerPix >= 2:
                n4[x, y, 0], n4[x, y, 1], n4[x, y, 2] = colorsys.hsv_to_rgb(0.1, 0.5, 0.0)
                innerPix -= 1
                totalInner += 1
                
            # Call the iterative function    
            else:
                if mode == 0: # Mandelbrot mode
                    scalar = mandelbrot(r1[y], r2[x], maxIter)
                    if scalar == -1: # Make the pixel black if the function returns -1, meaning the pixel converges
                        n4[x, y, 0], n4[x, y, 1], n4[x, y, 2] = colorsys.hsv_to_rgb(0.0, 0.0, 0.0)
                        innerPix += 1
                    else: # If the pixel diverges, color it according to the number of iterations till divergence
                        n4[x, y, 0], n4[x, y, 1], n4[x, y, 2] = colorsys.hsv_to_rgb((scalar%(maxIter/4))/maxIter, 0.5, 0.4)
                        if innerPix == 1: # If the last pixel was skipped, we need to go back and render it in case it actually diverges
                            redo = mandelbrot(r1[y-1], r2[x], maxIter)
                            n4[x, y-1, 0], n4[x, y-1, 1], n4[x, y-1, 2] = colorsys.hsv_to_rgb((redo%(maxIter/4))/maxIter, 0.5, 0.4)
                        innerPix = 0 # This pixel diverges, so we make sure not to skip the next one
                    
                elif mode == 1: # Julia mode
                    scalar = julia(r1[y], r2[x], xJulia, yJulia, maxIter)
                    if scalar == -1: # Make the pixel black if the function returns -1, meaning the pixel converges
                        n4[x, y, 0], n4[x, y, 1], n4[x, y, 2] = colorsys.hsv_to_rgb(0.0, 0.0, 0.0)
                        innerPix += 1
                    else: # If the pixel diverges, color it according to the number of iterations till divergence
                        n4[x, y, 0], n4[x, y, 1], n4[x, y, 2] = colorsys.hsv_to_rgb((scalar%(maxIter/4))/maxIter, 0.5, 0.4)
                        if innerPix == 1: # If the last pixel was skipped, we need to go back and render it in case it actually diverges
                            redo = julia(r1[y-1], r2[x], maxIter)
                            n4[x, y-1, 0], n4[x, y-1, 1], n4[x, y-1, 2] = colorsys.hsv_to_rgb((redo%(maxIter/4))/maxIter, 0.5, 0.4)
                        innerPix = 0 # This pixel diverges, so we make sure not to skip the next one
                    
    print("Total inner pixels skipped is: " + str(totalInner))
    
    imsave(imgName, n4) # Save this frame to a file

# Renders an animation based on a starting and ending position, zoom, iteration value, and frame number.
def renderZoomAnimPos(xPosStart, yPosStart, zoomStart, xJuliaStart, yJuliaStart, xPosEnd, yPosEnd, zoomEnd, xJuliaEnd, yJuliaEnd, width, height, maxIterStart, maxIterEnd, frameStart, frameStop, frameEnd, frameRatio, mode):
    fz = []
    fi = []
    newZoom = zoomStart
    
    print("range is " + str(frameStop - frameStart))
    
    # Populate a list of zoom values so that each frame is 1/frameRatio smaller than the last in complex space.  I used a frameRatio of 4, so each frame is 1/4 the size of the last.
    for i in range(frameEnd):
        newZoom = newZoom / frameRatio
        if newZoom < zoomEnd:
            if frameStop > i:
                frameStop = i + 1
            frameEnd = i + 1
            fz.append(zoomEnd)
            print('breaking zoom at ' + str(len(fz)))
            break
        else:
            fz.append(newZoom)
            
    # Create a linear interpolation path for the positional values.
    fx = np.linspace(xPosStart, xPosEnd, frameEnd)
    fy = np.linspace(yPosStart, yPosEnd, frameEnd)
    
    # Create a linear interpolation of Julia values
    jx = np.linspace(xJuliaStart, xJuliaEnd, frameEnd)
    jy = np.linspace(yJuliaStart, yJuliaEnd, frameEnd)

    # Create a linearly spaced scale from 0-1 for use in creating the exponentially scaled array of maximum iteration values for each frame.
    scale = np.linspace(0, 1, frameEnd)
        
    # Create an exponentially scaled array of maximum iteration values for each frame.
    for i in range(frameEnd):
        expon = scale[i] ** 2
        iters = (expon * maxIterEnd) + maxIterStart
        fi.append(int(iters))
        
    # Start a multiprocessing pool.
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    
    # Add a job to the pool for each frame to be rendered.
    for f in range(frameStart, frameStop):
        p.apply_async(fractalPos, (fx[f], fy[f], fz[f], width, height, fi[f], jx[f], jy[f], 'UHD MandelFull' + str(f) + '.png', mode))
        
# Renders an animation that sweeps position or Julia arguments
def renderSweepAnimPos(xPosStart, yPosStart, xJuliaStart, yJuliaStart, xPosEnd, yPosEnd, xJuliaEnd, yJuliaEnd, zoom, width, height, maxIters, frameStart, frameStop, frameEnd, mode):
    # Create a linear interpolation path for the positional values.
    fx = np.linspace(xPosStart, xPosEnd, frameEnd)
    fy = np.linspace(yPosStart, yPosEnd, frameEnd)
    
    # Create a linear interpolation of Julia c values
    jx = np.linspace(xJuliaStart, xJuliaEnd, frameEnd)
    jy = np.linspace(yJuliaStart, yJuliaEnd, frameEnd)
        
    # Start a multiprocessing pool.
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    
    # Add a job to the pool for each frame to be rendered.
    for f in range(frameStart, frameStop):
        p.apply_async(fractalPos, (fx[f], fy[f], zoom, width, height, maxIters, jx[f], jy[f], 'juliaSweep' + str(f) + '.png', mode))
        #fractalPos(fx[f], fy[f], zoom, width, height, maxIters, jx[f], jy[f], 'juliaSweep' + str(f) + '.png', mode)


# Argument keys:
# renderZoomAnimPos(xPosStart, yPosStart, zoomStart, xJuliaStart, yJuliaStart, xPosEnd, yPosEnd, zoomEnd, xJuliaEnd, yJuliaEnd, width, height, maxIterStart, maxIterEnd, frameStart, frameStop, frameEnd, frameRatio, mode)
# renderSweepAnimPos(xPosStart, yPosStart, xJuliaStart, yJuliaStart, xPosEnd, yPosEnd, xJuliaEnd, yJuliaEnd, zoom, width, height, maxIters, frameStart, frameStop, frameEnd, mode)
# fractalPos(xPos, yPos, zoom, width, height, maxIter, xJulia, yJulia, imgName, mode)

# Renders a Julia sweep where c ranges from (-0.7 + 0.056i) to (-0.9 + 0.256i)
renderSweepAnimPos(0, 0, -0.7, 0.056, 0, 0, -0.9, 0.256, 2, 2048, 2048, 2000, 0, 0, 2000, 1)
