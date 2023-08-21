"""
 Title:         CTF File Reader
 Description:   Reads CTF Files
 Author:        Janzen Choi

"""

# Libraries
import sm_cubit.maths.pixel_maths as pixel_maths
from sm_cubit.maths.grain import Grain
from sm_cubit.interface.format import HEADER_X, HEADER_Y, HEADER_PHASE_ID, HEADER_GRAIN_ID
from sm_cubit.interface.format import HEADER_AVG_PHI_1, HEADER_AVG_PHI, HEADER_AVG_PHI_2

def get_info(value_list:list, step_size:float) -> tuple:
    """
    Gets the range and step size from a list of values
    
    Parameters:
    * `value_list`: List of values
    * `step_size`:  The step size of each pixel
    
    Returns the number of values and minimum values
    """
    max_value = max(value_list)
    min_value = min(value_list)
    num_values = round((max_value - min_value) / step_size) + 1
    return num_values, min_value

def read_pixels(path:str, step_size:float) -> tuple:
    """
    Converts a CSV file into a grid of pixels
    
    Parameters:
    * `path`:      The path to the CSV file
    * `step_siez`: The step size of each pixel
    
    Returns the pixel grid and grain map
    """

    # Open file and read headers
    file = open(path, "r")
    headers = file.readline().replace("\n", "").split(",")
    rows = file.readlines()
    
    # Get column indexes
    index_x         = headers.index(HEADER_X)
    index_y         = headers.index(HEADER_Y)
    index_phase_id  = headers.index(HEADER_PHASE_ID)
    index_grain_id  = headers.index(HEADER_GRAIN_ID)
    index_avg_phi_1 = headers.index(HEADER_AVG_PHI_1)
    index_avg_Phi   = headers.index(HEADER_AVG_PHI)
    index_avg_phi_2 = headers.index(HEADER_AVG_PHI_2)

    # Get dimensions
    x_cells, x_min = get_info([float(row.split(",")[index_x]) for row in rows], step_size)
    y_cells, y_min = get_info([float(row.split(",")[index_y]) for row in rows], step_size)
    
    # Initialise pixel grid and grain map
    pixel_grid = pixel_maths.get_void_pixel_grid(x_cells, y_cells)
    grain_map = {}

    # Read CSV and fill grid
    for row in rows:

        # Process data
        row_list = row.replace("\n", "").split(",")
        if "NaN" in row_list or "nan" in row_list:
            continue
        row_list = [float(val) for val in row_list]
        grain_id = round(row_list[index_grain_id])

        # Add to pixel grid
        x = round(float(row_list[index_x] - x_min) / step_size)
        y = round(float(row_list[index_y] - y_min) / step_size)
        pixel_grid[y][x] = grain_id

        # Add to grain map if not yet added
        if not grain_id in grain_map:
            new_grain = Grain(
                phase_id = row_list[index_phase_id],
                phi_1    = row_list[index_avg_phi_1],
                Phi      = row_list[index_avg_Phi],
                phi_2    = row_list[index_avg_phi_2],
                size     = 1,
            )
            grain_map[grain_id] = new_grain
        
        # Update grain map if already added
        else:
            grain_map[grain_id].increment_size()
    
    # Close file and return grid and map
    file.close()
    return pixel_grid, grain_map

def remap_grains(pixel_grid:list, grain_map:dict) -> tuple:
    """
    Renumbers the grain IDs
    
    Parameters:
    * `pixel_grid`: A grid of pixels
    * `grain_map`:  A mapping of the grains to the average orientations
    
    Returns the new pixel grid and grain map
    """

    # Get list of old IDs
    flattened = [pixel for pixel_list in pixel_grid for pixel in pixel_list]
    old_ids = list(set(flattened))
    for excluded_id in [pixel_maths.VOID_PIXEL_ID, pixel_maths.UNORIENTED_PIXEL_ID]:
        if excluded_id in old_ids:
            old_ids.remove(excluded_id)
    old_ids.sort()

    # Map old IDs to new IDs
    id_map = {}
    for i in range(len(old_ids)):
        id_map[old_ids[i]] = i + 1
    
    # Create new pixel grid
    new_pixel_grid = pixel_maths.get_void_pixel_grid(len(pixel_grid[0]), len(pixel_grid))
    for row in range(len(pixel_grid)):
        for col in range(len(pixel_grid[0])):
            if pixel_grid[row][col] in [pixel_maths.VOID_PIXEL_ID, pixel_maths.UNORIENTED_PIXEL_ID]:
                new_pixel_grid[row][col] = pixel_grid[row][col]
            else:
                new_id = id_map[pixel_grid[row][col]]
                new_pixel_grid[row][col] = new_id
    
    # Create new grain map
    new_grain_map = {}
    for old_id in old_ids:
        new_id = id_map[old_id]
        new_grain_map[new_id] = grain_map[old_id]

    # Return new pixel grid and grain map
    return new_pixel_grid, new_grain_map
