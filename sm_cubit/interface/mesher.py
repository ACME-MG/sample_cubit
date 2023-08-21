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

def coarse_mesh(psculpt_path:str, step_size:float, i_path:str, spn_path:str, exodus_path:str,
                pixel_grid:list, thickness:int, has_void:bool, adaptive:bool) -> None:
    """
    Generates a mesh based on an SPN file
    
    Parameters:
    * `psculpt_path`: The path to PSculpt 
    * `step_size`:    The size that each pixel represents
    * `i_path`:       The path to the input file 
    * `spn_path`:     The path to the SPN file 
    * `exodus_path`:  The path to the exodus mesh file 
    * `pixel_grid`:   The grid of pixels 
    * `thickness`:    The thickness of each the mesh (in pixels) 
    * `has_void`:     Whether the mesh has void pixels or not 
    * `adaptive`:     Whether to use adaptive meshing; if activated, the script will
                      try to use the maximum adaptive meshing level possible
    """

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

    # Write SPN file (x = gauge, y = height, z = thickness)
    #   Mesh will be flipped but this is intentional because MTEX indexes the origin ...
    #   ... of the EBSD map from bottom left, but Cubit/Paraview does it from top left.
    #   Original line: file.write(f"{pixel_grid[y_size - i - 1][j]} ")
    file = open(spn_path, "w+")
    for j in range(x_size):            # x
        for i in range(y_size):        # y
            for _ in range(thickness): # z
                file.write(f"{pixel_grid[i][j]} ")
    file.close()

    # Adaptive meshing
    levels = math.floor(math.log(thickness, 2)) # (2^levels <= thickness)
    adaptive_list = ["adapt_type = 5", f"adapt_levels = {levels}", "adapt_threshold = 0.01"]
    adaptive_string = "\n    ".join(adaptive_list)
    adaptive_string = adaptive_string if adaptive else ""

    # Create input file
    file = open(i_path, "w+", newline = "")
    file.write(INPUT_FILE_CONTENT.format(
        x_cells     = x_size,
        y_cells     = y_size,
        z_cells     = thickness,
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
