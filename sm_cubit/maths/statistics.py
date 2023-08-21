"""
 Title:         Exporter
 Description:   Exports stuff
 Author:        Janzen Choi

"""

# Libraries
import math, numpy as np, pyvista as pv
from copy import deepcopy
from sm_cubit.maths.pixel_maths import VOID_PIXEL_ID, UNORIENTED_PIXEL_ID, NO_ORIENTATION
from sm_cubit.interface.format import HEADER_X, HEADER_Y, HEADER_PHI_1, HEADER_PHI, HEADER_PHI_2

def get_spn_to_exo(exo_path:str, spn_path:str, spn_size:tuple) -> dict:
    """
    Gets the grain IDs of exodus grains from the SPN file
    
    Parameters:
    * `exo_path`: The path to the exodus file
    * `spn_path`: The path to the SPN file
    * `spn_size`: The size of the SPN file as a tuple, (x_size, y_size, z_size)
    
    Returns a mapping of the SPN to exodus IDs and the confidence of the mapping;
    the mapping is in the form of a dictionary with keys "exo_id", "confidence"
    """

    # Reads the contents of the exodus file
    exo_grains = pv.read(exo_path)[0]
    bounds = exo_grains.bounds
    exo_bounds = [{"min": bounds[2*i], "max": bounds[2*i+1], "range": bounds[2*i+1] - bounds[2*i]} for i in range(3)]

    # Read the contents of the SPN file
    with open(spn_path, "r") as spn_file:
        voxel_string = " ".join(spn_file.readlines())
        voxel_list = [int(voxel) for voxel in voxel_string.split(" ") if voxel != ""]

    # Iterate through the exodus grains
    spn_to_exo = {}
    for i in range(exo_grains.n_blocks):
        
        # Get grain elements
        exo_grain = exo_grains[i]
        elements = exo_grain.cell_centers().points
        elements = [list(element) for element in elements]

        # Get the grain ids based on element coordinates
        id_list = []
        for element in elements:
            if math.nan in element:
                continue
            pos = [math.floor((element[j] - exo_bounds[j]["min"]) / exo_bounds[j]["range"] * spn_size[j]) for j in range(3)]
            grain_id_index = pos[0] * spn_size[1] * spn_size[2] + pos[1] * spn_size[2] + pos[2]
            grain_id = voxel_list[grain_id_index]
            id_list.append(grain_id)
        
        # Add exodus grain id
        mode = max(set(id_list), key=id_list.count)
        freq = id_list.count(mode)
        total = len(id_list)
        spn_to_exo[mode] = {"exo_id": i+1, "confidence": round(freq / total * 100, 2)}

    # Return
    return spn_to_exo
    
def get_grain_stats(exodus_path:str, spn_path:str, spn_size:tuple, grain_map:dict, has_void:bool) -> list:
    """
    Generates statistics of the grains
    
    Parameters:
    * `exo_path`:  The path to the exodus file
    * `spn_path`:  The path to the SPN file
    * `spn_size`:  The size of the SPN file as a tuple, (x_size, y_size, z_size)
    * `grain_map`: The mapping of grain IDs to their orientations
    * `has_void`:  Whether the pixel grid has voids
    
    Returns a list of the orientations, area, and phase id for each grain
    """
    
    # Get grain ids
    spn_id_list = list(grain_map.keys())
    num_spn_grains = len(spn_id_list) + (1 if UNORIENTED_PIXEL_ID in spn_id_list else 0)
    spn_id_list.sort()

    # If the mesh has voids, then increment id list
    if has_void:
        spn_id_list = [spn_id+1 for spn_id in spn_id_list]
        new_grain_map = {}
        for key in grain_map.keys():
            new_grain_map[key+1] = grain_map[key]
        grain_map = new_grain_map

    # Get spn to exo mapping and print
    spn_to_exo = get_spn_to_exo(exodus_path, spn_path, spn_size)
    avg_confidence = round(np.average([spn_to_exo[spn_id]["confidence"] for spn_id in spn_to_exo.keys()]), 2)
    print(f"SPN (Num. of Grains):   {num_spn_grains}")
    print(f"EXO (Num. of Grains):   {len(spn_to_exo)}")
    print(f"SPN > EXO (Confidence): {avg_confidence}%")
    
    # Get statistics
    void_stats = [0] * len(next(iter(grain_map.values())).get_all_stats())
    stat_value_list = []
    for spn_id in spn_id_list:
        if spn_id in spn_to_exo.keys():
            stat_list = grain_map[spn_id].get_all_stats()
            stat_value_list.append(stat_list)
        else:
            stat_value_list.append(void_stats)

    # Pad if the mesh has a void and return
    if has_void:
        stat_value_list = [void_stats] + stat_value_list
    return stat_value_list

def get_orientation_grid(csv_path:str, pixel_grid:list, step_size:float,
                         x_start_index:int, y_start_index:int) -> list:
    """
    Generates a grid of the orientations corresponding to the pixel grid
    
    Parameters:
    * `csv_path`:      The path to the CSV path
    * `pixel_grid`:    The grid of pixels
    * `step_size`:     The amount that each pixel represents
    * `x_start_index`: The x index for when the microstructure starts in the pixel grid
    * `y_start_index`: The y index for when the microstructure starts in the pixel grid

    Returns a grid of the orientations
    """
    
    # Read headers from CSV and get column positions
    csv_fh      = open(csv_path, "r")
    headers     = csv_fh.readline().replace("\n", "").split(",")
    index_x     = headers.index(HEADER_X)
    index_y     = headers.index(HEADER_Y)
    index_phi_1 = headers.index(HEADER_PHI_1)
    index_Phi   = headers.index(HEADER_PHI)
    index_phi_2 = headers.index(HEADER_PHI_2)
    
    # Initialise orientation frid
    y_size = len(pixel_grid)
    x_size = len(pixel_grid[0])
    orientation_grid = []
    for _ in range(y_size):
        orientation_list = []
        for _ in range(x_size):
            empty_orientation = deepcopy(NO_ORIENTATION)
            orientation_list.append(empty_orientation)
        orientation_grid.append(orientation_list)
    
    # Read through each row of the CSV file, and don't load too much to RAM
    first_line = True
    for line in csv_fh:
        line_list = line.replace("\n", "").split(",")
        
        # Calculate the minimum bounds if first line
        if first_line:
            x_min = round(float(line_list[index_x]))
            y_min = round(float(line_list[index_y]))
            first_line = False
        
        # Get the indexes in the pixel grid
        x_coord = round((float(line_list[index_x]) - x_min) / step_size) + x_start_index
        y_coord = round((float(line_list[index_y]) - y_min) / step_size) + y_start_index
    
        # Skip if not within bounds
        if x_coord < 0 or x_coord >= x_size or y_coord < 0 or y_coord >= y_size:
            continue
        
        # Gets the euler-bunge orientations
        phi_1 = float(line_list[index_phi_1])
        Phi   = float(line_list[index_Phi])
        phi_2 = float(line_list[index_phi_2])
        
        # Apply the orientation
        orientation_grid[y_coord][x_coord] = [phi_1, Phi, phi_2]
    
    # Close the file and return the grid
    csv_fh.close()
    return orientation_grid

def get_element_stats(exodus_path:str, orientation_grid:list, pixel_grid:list,
                           grain_map:dict, step_size:float) -> list:
    """
    Generates statistics of the grain elements; the order of the statistics are
    grain first, then elements within the grains
    
    Parameters:
    * `exodus_path`:      The path to the exodus file
    * `orientation_grid`: A grid of the orientations
    * `pixel_grid`:       The grid of pixels
    * `grain_map`:        The mapping of grain IDs to their orientations
    * `step_size`:        The amount that each pixel represents

    Returns a list of the orientations, grain_id, and phase id for each element
    """
    
    # Read all the grains
    mesh = pv.read(exodus_path)[0]
    grain_list = [mesh[i] for i in range(mesh.n_blocks)]

    # Read all the centroids of the elements for each grain
    centroid_list = []
    for grain in grain_list:
        elements = grain.cell_centers().points
        elements = [list(element) for element in elements]
        centroid_list += list(elements)
    
    # Iterate through centroids and gather statistics
    stats_list = []
    for centroid in centroid_list:
        
        # Get the index of the centroid in the pixel grid
        x_index = math.floor(centroid[0] / step_size)
        y_index = math.floor(centroid[1] / step_size)
        
        # Get grain ID and check
        grain_id = pixel_grid[y_index][x_index]
        if grain_id in [VOID_PIXEL_ID, UNORIENTED_PIXEL_ID]:
            stats = NO_ORIENTATION + [grain_id, -1]
            stats_list.append(stats)
            continue
        
        # Get phase ID and orientation
        phase_id = grain_map[grain_id].get_phase_id()
        orientation = orientation_grid[y_index][x_index]
        
        # Compile and append to list
        stats = orientation + [grain_id, phase_id]
        stats_list.append(stats)
    
    # Return the list of statistics
    return stats_list