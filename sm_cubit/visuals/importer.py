"""
 Title:         Importer
 Description:   For importing an image of the sample into the program
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from PIL import Image
from sm_cubit.maths.pixel_maths import get_void_pixel_grid
from sm_cubit.visuals.imager import MASK_COLOUR
from sm_cubit.visuals.ipf_cubic import euler_to_rgb

# Converts an image into a pixel grid and grain map
def convert_image(grain_map, path, ipf):

    # Create map of RGB to grain id
    rgb_2_id = {}
    for id in grain_map.keys():
        
        # Get RGB of each grain
        euler = [grain_map[id][p] for p in ["phi_1", "Phi", "phi_2"]]
        rgb = euler_to_rgb(*euler, ipf)

        # Check if already in map (seldom)
        rgb_string = ",".join([str(c) for c in rgb])
        if rgb_string in rgb_2_id.keys():
            continue

        # Add to map
        rgb_2_id[rgb_string] = {
            "id":       id,
            "phase_id": grain_map[id]["phase_id"],
            "phi_1":    grain_map[id]["phi_1"],
            "Phi":      grain_map[id]["Phi"],
            "phi_2":    grain_map[id]["phi_2"],
            "size":     0,
        }

    # Read the image and convert to grid
    img = Image.open(path)
    img = img.convert("RGB")
    colour_grid = np.asarray(img)

    # Create pixel grid
    pixel_grid = get_void_pixel_grid(len(colour_grid[0]), len(colour_grid))
    for row in range(len(colour_grid)):
        for col in range(len(colour_grid[0])):
            
            # Ignore if black (i.e., void)
            colour = colour_grid[row][col]
            if colour[0] == MASK_COLOUR[0] and colour[1] == MASK_COLOUR[1] and colour[2] == MASK_COLOUR[2]:
                continue

            # Identify pixel
            rgb_string = ",".join([str(c) for c in colour_grid[row][col]])
            pixel_grid[row][col] = rgb_2_id[rgb_string]["id"]
            rgb_2_id[rgb_string]["size"] += 1

    # Return pixel grid
    return pixel_grid
