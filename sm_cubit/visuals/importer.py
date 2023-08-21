"""
 Title:         Importer
 Description:   For importing an image of the sample into the program
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from PIL import Image
from sm_cubit.maths.pixel_maths import get_void_pixel_grid
from sm_cubit.visuals.imager import MASK_COLOUR, UNORIENTED_COLOUR, TRANSPARENT
from sm_cubit.visuals.ipf_cubic import euler_to_rgb

def convert_image(grain_map:dict, path:str, ipf:str) -> list:
    """
    Converts an image into a pixel grid and grain map
    
    Parameters:
    * `grain_map`: The mapping of the grain IDs to the grain orientations
    * `path`:      The path to the image
    * `ipf`:       The IPF scheme used by the image
    
    Returns the pixel grid
    """

    # Create map of RGB to grain id
    rgb_2_id = {}
    for id in grain_map.keys():
        euler = grain_map[id].get_orientations()
        rgb = euler_to_rgb(*euler, ipf)
        rgb_string = ",".join([str(c) for c in rgb])
        if rgb_string in rgb_2_id.keys():
            continue
        rgb_2_id[rgb_string] = id

    # Read the image and convert to grid
    img = Image.open(path)
    img = img.convert("RGB")
    colour_grid = np.asarray(img)

    # Create pixel grid
    pixel_grid = get_void_pixel_grid(len(colour_grid[0]), len(colour_grid))
    for row in range(len(colour_grid)):
        for col in range(len(colour_grid[0])):
            
            # Ignore if void, transparent, or homogenous
            colour = colour_grid[row][col]
            for excluded in [MASK_COLOUR, UNORIENTED_COLOUR, TRANSPARENT]:
                if colour[0] == excluded[0] and colour[1] == excluded[1] and colour[2] == excluded[2]:
                    continue

            # Identify pixel
            rgb_string = ",".join([str(c) for c in colour_grid[row][col]])
            pixel_grid[row][col] = rgb_2_id[rgb_string]

    # Return pixel grid
    return pixel_grid
