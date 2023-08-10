"""
 Title:         Mesher
 Description:   For converting the pixels into a mesh
 Author:        Janzen Choi

"""

# Libraries
import subprocess, os, math
from sm_cubit.maths.pixel_maths import VOID_PIXEL_ID

# Input file
INPUT_FILE_CONTENT = """
BEGIN SCULPT
    
    # Dimensions
    nelx = {x_cells}
    nely = {y_cells}
    nelz = {z_cells}
    scale = {step_size}

    # Remove cuts if any
    void_mat = {void_id}
    
    # Fixed mesh improvement
    smooth = 3
    defeature = 1
    pillow_curves = true
    pillow_boundaries = true
    micro_shave = true
    
    # Variable mesh improvement
    opt_threshold = 0.7
    pillow_curve_layers = 4
    pillow_curve_thresh = 0.3

    # Solver
    laplacian_iters = 5
    max_opt_iters = 50
    {adapt_options}
    
    # Output
    input_spn = {spn_file}
    exodus_file = {exodus_file}

END SCULPT
"""

# Mesh Parameters
NUM_PROCESSORS = 1

# Add void thickness
def add_void_thickness(file, pixel_grid, num_pixels):
    for _ in range(num_pixels):
        for pixel_list in pixel_grid:
            for _ in pixel_list:
                file.write(f"{VOID_PIXEL_ID} ")
    return num_pixels

# Generates the mesh
def coarse_mesh(psculpt_path, step_size, i_path, spn_path, exodus_path, pixel_grid, thickness, has_void, adaptive):

    # Get dimensions
    y_size = round(len(pixel_grid))
    x_size = round(len(pixel_grid[0]))

    # If void exists, allocate void id to 1 and shift
    if has_void:
        for row in range(y_size):
            for col in range(x_size):
                if pixel_grid[row][col] == VOID_PIXEL_ID:
                    pixel_grid[row][col] = 1
                else: 
                    pixel_grid[row][col] += 1
    new_void_id = 1 if has_void else VOID_PIXEL_ID

    # Write SPN file
    file = open(spn_path, "w+")
    for _ in range(thickness):
        for pixel_list in pixel_grid:
            for pixel in pixel_list:
                file.write(f"{pixel} ")
    file.close()

    # Adaptive meshing
    levels = math.floor(math.log(thickness, 2)) # (2^levels <= thickness)
    adaptive_list = ["adapt_type = 5", f"adapt_levels = {levels}", "adapt_threshold = 0.01"]
    adaptive_string = "\n    ".join(adaptive_list)
    adaptive_string = adaptive_string if adaptive else ""

    # Create input file
    file = open(i_path, "w+", newline = "")
    file.write(INPUT_FILE_CONTENT.format(
        x_cells     = thickness,
        y_cells     = y_size,
        z_cells     = x_size,
        step_size   = step_size,
        void_id     = new_void_id,
        adapt_options = adaptive_string,
        spn_file    = spn_path,
        exodus_file = exodus_path,
    ))
    file.close()

    # Run mesh command
    command = f"mpiexec -n {NUM_PROCESSORS} {psculpt_path} -j {NUM_PROCESSORS} -i {i_path}"
    subprocess.run([command], shell = True, check = True)
    os.rename(f"{exodus_path}.e.1.0", f"{exodus_path}")