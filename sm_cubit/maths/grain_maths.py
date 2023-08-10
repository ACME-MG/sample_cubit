"""
 Title:         Grain
 Description:   Contains grain-related functions
 Author:        Janzen Choi

"""

# Returns a grain dictionary
def get_grain_dict(phase_id, phi_1, Phi, phi_2, size):
    return {
        "phase_id": phase_id,
        "phi_1":    phi_1,
        "Phi":      Phi,
        "phi_2":    phi_2,
        "size":     size,
    }

# Updates an existing grain dictionary
def update_grain_dict(grain_dict, phi_1, Phi, phi_2):
    size = grain_dict["size"]
    grain_dict["phi_1"] = (size * grain_dict["phi_1"] + phi_1) / (size + 1)
    grain_dict["Phi"]   = (size * grain_dict["Phi"] + Phi) / (size + 1)
    grain_dict["phi_2"] = (size * grain_dict["phi_2"] + phi_2) / (size + 1)
    grain_dict["size"] += 1
    return grain_dict

# Gets the average orientation weighted by area
def get_average_orientation(grain_map):
    total_pixels = sum([grain_map[id]["size"] for id in grain_map.keys()])
    avg_phi_1 = sum([grain_map[id]["phi_1"]*grain_map[id]["size"] for id in grain_map.keys()]) / total_pixels
    avg_Phi   = sum([grain_map[id]["Phi"]*grain_map[id]["size"] for id in grain_map.keys()]) / total_pixels
    avg_phi_2 = sum([grain_map[id]["phi_2"]*grain_map[id]["size"] for id in grain_map.keys()]) / total_pixels
    return (avg_phi_1, avg_Phi, avg_phi_2)