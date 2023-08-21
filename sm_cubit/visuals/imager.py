"""
 Title:         Imager
 Description:   Reads and writes images (of size smaller than 10000 x 10000)
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from PIL import Image
from sm_cubit.visuals.ipf_cubic import euler_to_rgb
from sm_cubit.maths.pixel_maths import VOID_PIXEL_ID, UNORIENTED_PIXEL_ID, NO_ORIENTATION

# Colours
MASK_COLOUR       = (0,0,0) # black
UNORIENTED_COLOUR = (0,255,0)
TRANSPARENT       = (255,255,255,0)

def get_random_colour() -> tuple:
    """
    Returns a random colour
    """
    random_colour = tuple(np.random.choice(range(256), size=3))
    if random_colour == MASK_COLOUR:
        return get_random_colour() # never black
    return random_colour

def visualise_by_grain(output_path:str, pixel_grid:list, grain_map:dict, ipf:str=None) -> None:
    """
    Generates an image based on the orientations of each grain
    
    Parameters:
    * `output_path`: The path to the output path
    * `pixel_grid`:  A grid of pixels
    * `grain_map`:   A mapping of the grain IDs to orientations
    * `ipf`:         The specific IPF scheme to use for visualising the EBSD map
    """

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
        elif id == UNORIENTED_PIXEL_ID:
            id_colour_map[str(id)] = UNORIENTED_COLOUR
        elif ipf == None:
            id_colour_map[str(id)] = get_random_colour()
        else:
            orientations = grain_map[id].get_orientation()
            id_colour_map[str(id)] = euler_to_rgb(*orientations, ipf)

    # Create image and save
    img = Image.new("RGBA", size=(x_size,y_size), color=TRANSPARENT)
    for row in range(y_size):
        for col in range(x_size):
            img.putpixel((col,row), id_colour_map[str(pixel_grid[row][col])])
    img.save(f"{output_path}.png", "PNG")

def visualise_by_element(output_path:str, pixel_grid:list, orientation_grid:list, ipf:str) -> None:
    """
    Generates an image based on the orientations of each pixel; assumes that the
    first line of the CSV file contains the pixel with the minimum x and y values
    
    Parameters:
    * `output_path`:      The path to the output path
    * `pixel_grid`:       A grid of pixels
    * `orientation_grid`: A grid of the orientations
    * `ipf`:              The specific IPF scheme to use for visualising the EBSD map
    """
    
    # Initialise image
    y_size = len(orientation_grid)
    x_size = len(orientation_grid[0])
    img = Image.new("RGBA", size=(x_size,y_size), color=TRANSPARENT)
        
    # Generate the image    
    for y in range(y_size):
        for x in range(x_size):
            
            # Add unoriented colour if pixel is unoriented
            if pixel_grid[y][x] == UNORIENTED_PIXEL_ID:
                img.putpixel((x, y), UNORIENTED_COLOUR)
                continue
            
            # Skip if orientation is void
            orientation = orientation_grid[y][x]
            if orientation == NO_ORIENTATION:
                continue
            
            # Colour if pixel is oriented
            colour = euler_to_rgb(*orientation, ipf)
            img.putpixel((x, y), colour)

    # Save the image
    img.save(f"{output_path}.png", "PNG")

def get_void_pixels(png_path:str) -> list:
    """
    Gets a list of coordinates of void pixels from a PNG file
    
    Parameters:
    * `png_path`: The path to the PNG file
    
    Returns the coordinate list
    """
    
    # Read image and convert to pixel grid
    img = Image.open(png_path)
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
