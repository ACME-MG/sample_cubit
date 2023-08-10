"""
 Title:         Imager
 Description:   Reads and writes images (of size smaller than 10000 x 10000)
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from PIL import Image
from sm_cubit.visuals.ipf_cubic import euler_to_rgb
from sm_cubit.maths.pixel_maths import VOID_PIXEL_ID

# Colours
MASK_COLOUR = (0,0,0) # black
TRANSPARENT = (255,255,255,0)

# Generates a random colour
def get_random_colour():
    random_colour = tuple(np.random.choice(range(256), size=3))
    if random_colour == MASK_COLOUR:
        return get_random_colour() # never black
    return random_colour

# Generates an image based on a grid of pixels
def generate_image(pixel_grid, grain_map, path, ipf=None):

    # Gets bounds of image
    y_size = len(pixel_grid)
    x_size = len(pixel_grid[0])

    # Get unique ids
    id_list = [pixel for pixel_list in pixel_grid for pixel in pixel_list]
    id_list = list(dict.fromkeys(id_list))
    
    # Allocate colours to unique ids
    id_colour_map = {}
    for id in id_list:
        if id == VOID_PIXEL_ID:
            id_colour_map[str(id)] = TRANSPARENT
        elif ipf == None:
            id_colour_map[str(id)] = get_random_colour()
        else:
            phi_1 = grain_map[id]["phi_1"]
            Phi   = grain_map[id]["Phi"]
            phi_2 = grain_map[id]["phi_2"]
            id_colour_map[str(id)] = euler_to_rgb(phi_1, Phi, phi_2, ipf)
        if id != VOID_PIXEL_ID and id_colour_map[str(id)] == (108, 255, 75):
            print(id, grain_map[id])

    # Create image and save
    img = Image.new("RGBA", size=(x_size,y_size), color=TRANSPARENT)
    for row in range(y_size):
        for col in range(x_size):
            img.putpixel((col,row), id_colour_map[str(pixel_grid[row][col])])
    img.save(f"{path}.png", "PNG")

# Gets a list of coordinates of void pixels
def get_void_pixels(path):
    
    # Read image and convert to pixel grid
    img = Image.open(path)
    img = img.convert("RGBA")
    pixel_grid = np.asarray(img)

    # Return coordinates of void pixels
    coordinates_list = []
    for row in range(len(pixel_grid)):
        for col in range(len(pixel_grid[0])):
            pixel = pixel_grid[row][col]
            if pixel[0] == MASK_COLOUR[0] and pixel[1] == MASK_COLOUR[1] and pixel[2] == MASK_COLOUR[2]:
                coordinates_list.append((col, row))
    return coordinates_list
