# Convert a candidate pixel art image from a generative model to a 16x16 or 32x32 pixel art image.

# pip install pillow
# pip install numpy

import os
import sys
import argparse
import numpy as np
from PIL import Image

from PIL import Image, ImageOps  


# Convert
def convert(filenameIn, filenameOut, size):
    # Load the file
    print("Loading: " + filenameIn)
    img = Image.open(filenameIn)

    # First, crop the image (remove the border)
    cropTop = 0.25
    cropBottom = 0.25
    cropLeft = 0.25
    cropRight = 0.25
    width, height = img.size
    img = img.crop((cropLeft * width, cropTop * height, (1.0 - cropRight) * width, (1.0 - cropBottom) * height))


    # Posterize to only 16 colors
    levels = 4
    if img.mode == 'RGBA':
        # Separate the alpha channel
        r, g, b, a = img.split()

        # Convert the image to RGB and posterize
        rgb_img = Image.merge('RGB', (r, g, b))
        posterized_img = ImageOps.posterize(rgb_img, levels)

        # Merge the posterized image with the alpha channel
        r, g, b = posterized_img.split()
        img = Image.merge('RGBA', (r, g, b, a))
    else:
        img = ImageOps.posterize(img, levels)


    # Resize to 16x16 or 32x32
    img = img.resize((size, size), Image.NEAREST)

    # Make whatever color is in the top-left corner transparent
    img = img.convert("RGBA")
    data = img.getdata()
    newData = []
    # Get the color of the pixel at the top-left corner
    topLeftColor = data[0]
    print("Top-left color: " + str(topLeftColor))
    # Make every pixel in the rest of the image that has that same color as transparent
    for item in data:
        if item[0] == topLeftColor[0] and item[1] == topLeftColor[1] and item[2] == topLeftColor[2]:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)

   # Display size of the image
    print("Size: " + str(img.size))

    # Show the image, but scale up a factor of 4
    img1 = img.resize((size * 4, size * 4), Image.NEAREST)
    img1.show()

    
    # Save the image
    print("Saving as: " + filenameOut)
    img.save(filenameOut)




# Main 
if __name__ == '__main__':
    size = 32
    filenameIn = "imagetools/generated/flowerpot1.png"
    filenameOut = "assets/generated/flowerpot1_" + str(size) + ".png"
    
    # Parse command line arguments
    # TODO

    # Convert
    convert(filenameIn, filenameOut, size)