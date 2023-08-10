"""
 Title:         Exporter
 Description:   Exports stuff
 Author:        Janzen Choi

"""

# Libraries
import math
import pyvista as pv
import numpy as np

# Gets the grain IDs of exodus grains from the SPN file
def get_spn_to_exo(exo_path, spn_path, spn_size):

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
    
# Rewrites an orientation file based on grain id mappings
def get_stastistics(exodus_path, spn_path, spn_size, grain_map, has_void, statistics_list):
    
    # Get grain ids
    spn_id_list = list(grain_map.keys())
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
    print(f"SPN (Num. of Grains):   {len(spn_id_list)}")
    print(f"EXO (Num. of Grains):   {len(spn_to_exo)}")
    print(f"SPN > EXO (Confidence): {avg_confidence}%")
    
    # Get statistics
    void_stats = [0] * len(statistics_list)
    stat_value_list = []
    for spn_id in spn_id_list:
        if spn_id in spn_to_exo.keys():
            stat_value_list.append([grain_map[spn_id][i] for i in statistics_list])
        else:
            stat_value_list.append(void_stats)

    # Pad if the mesh has a void and return
    if has_void:
        stat_value_list = [void_stats] + stat_value_list
    return stat_value_list
