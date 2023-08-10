"""
 Title:         IPF Cubic
 Description:   For converting orientations from euler-bunge into RGB form for IPF
 Resource:      Adapted from https://mooseframework.inl.gov/docs/doxygen/modules/Euler2RGB_8h.html
                which is generalised for all/most structures
 Author:        Janzen Choi

"""

# Libraries
import math
from scipy.optimize import minimize

# Converts degrees to radians
def deg_to_rad(degrees):
    if isinstance(degrees, list):
        return [deg_to_rad(d) for d in degrees]
    return degrees * math.pi / 180

# Determines the orientation matrix of a set of euler-bunge angles (rads)
def euler_to_matrix(phi_1, Phi, phi_2):
    om_11 = math.cos(phi_1)*math.cos(phi_2) - math.sin(phi_1)*math.sin(phi_2)*math.cos(Phi)
    om_12 = math.sin(phi_1)*math.cos(phi_2) + math.cos(phi_1)*math.sin(phi_2)*math.cos(Phi)
    om_13 = math.sin(phi_2)*math.sin(Phi)
    om_21 = -math.cos(phi_1)*math.sin(phi_2) - math.sin(phi_1)*math.cos(phi_2)*math.cos(Phi)
    om_22 = -math.sin(phi_1)*math.sin(phi_2) + math.cos(phi_1)*math.cos(phi_2)*math.cos(Phi)
    om_23 = math.cos(phi_2)*math.sin(Phi)
    om_31 = math.sin(phi_1)*math.sin(Phi)
    om_32 = -math.cos(phi_1)*math.sin(Phi)
    om_33 = math.cos(Phi)
    om = [[om_11, om_12, om_13],
          [om_21, om_22, om_23],
          [om_31, om_32, om_33]]
    return om

# Returns the cubic symmetry matrices
def get_cubic_symmetry_matrices():
    return [
        [[1,0,0], [0,1,0], [0,0,1]],
        [[0,0,1], [1,0,0], [0,1,0]],
        [[0,1,0], [0,0,1], [1,0,0]],
        [[0,-1,0], [0,0,-1], [1,0,0]],
        [[0,-1,0], [0,0,-1], [1,0,0]],
        [[0,1,0], [0,0,-1], [-1,0,0]],
        [[0,0,-1], [1,0,0], [0,-1,0]],
        [[0,0,-1], [-1,0,0], [0,1,0]],
        [[0,0,1], [-1,0,0], [0,-1,0]],
        [[-1,0,0], [0,1,0], [0,0,-1]],
        [[-1,0,0], [0,-1,0], [0,0,1]],
        [[1,0,0], [0,-1,0], [0,0,-1]],
        [[0,0,-1], [0,-1,0], [-1,0,0]],
        [[0,0,1], [0,-1,0], [1,0,0]],
        [[0,0,1], [0,1,0], [-1,0,0]],
        [[0,0,-1], [0,1,0], [1,0,0]],
        [[-1,0,0], [0,0,-1], [0,-1,0]],
        [[1,0,0], [0,0,-1], [0,1,0]],
        [[1,0,0], [0,0,1], [0,-1,0]],
        [[-1,0,0], [0,0,1], [0,1,0]],
        [[0,-1,0], [-1,0,0], [0,0,-1]],
        [[0,1,0], [-1,0,0], [0,0,-1]], # [[0,1,0], [-1,0,0], [0,0,1]]
        [[0,1,0], [1,0,0], [0,0,-1]],
        [[0,-1,0], [1,0,0], [0,0,1]],
    ]

# Converts orientation from euler-bunge to RGB (for cubic only)
def euler_to_rgb(phi_1, Phi, phi_2, ipf="x"):
    
    # Get IPF direction list
    if ipf == "x":
        ipf_list = [1,0,0]
    elif ipf == "y":
        ipf_list = [0,1,0]
    elif ipf == "z":
        ipf_list = [0,0,1]

    # Convert orientation
    phi_1 = deg_to_rad(phi_1)
    Phi   = deg_to_rad(Phi)
    phi_2 = deg_to_rad(phi_2)

    # Define auxiliary variables
    eta_min = deg_to_rad(0)
    eta_max = deg_to_rad(45)
    chi_min = deg_to_rad(0)
    chi_max = math.acos(1/math.sqrt(2+math.pow(math.tan(eta_max), 2)))

    # Assign black for out of RGB domain
    if phi_1 > 2*math.pi or Phi > math.pi or phi_2 > 2*math.pi:
        return 255, 255, 255
    
    # Get matrices
    orientation_matrix = euler_to_matrix(phi_1, Phi, phi_2)
    symmetry_matrices = get_cubic_symmetry_matrices()

    # Sort euler angles into SST
    for i in range(len(symmetry_matrices)):

        # Calculate temporary matrix
        temp_matrix = [[0,0,0],[0,0,0],[0,0,0]]
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    temp_matrix[j][k] += symmetry_matrices[i][j][l] * orientation_matrix[l][k]
        
        # Get multiple orientation matrix
        hkl = [0,0,0]
        for j in range(3):
            for k in range(3):
                hkl[j] += temp_matrix[j][k] * ipf_list[k]
        
        # Convert to spherical coordinates
        eta = abs(math.atan2(hkl[1], hkl[0]))
        chi = math.acos(abs(hkl[2]))

        # Check if eta and chi values are within SST, and keep searching otherwise
        if eta >= eta_min and eta < eta_max and chi >= chi_min and chi < chi_max:
            break

    # Calculate auxiliary variables
    chi_max_2 = math.acos(1/math.sqrt(2+math.pow(math.tan(eta),2)))
    eta_diff  = abs((eta-eta_min)/(eta_max-eta_min))

    # Calculate RGB colours
    red   = math.sqrt(abs(1-chi/chi_max_2))
    green = math.sqrt((1-eta_diff)*(chi/chi_max_2))
    blue  = math.sqrt(eta_diff*(chi/chi_max_2))

    # Normalise, round, and return
    max_rgb = max(red, green, blue)
    red     = round(red/max_rgb*255)
    green   = round(green/max_rgb*255)
    blue    = round(blue/max_rgb*255)
    return red, green, blue

# Converts RGB to euler-bunge orientation (through optimisation)
def rgb_to_euler(red, green, blue, ipf="x"):

    # Define the objective function
    def obj_func(x):
        phi_1, Phi, phi_2 = x
        red_, green_, blue_ = euler_to_rgb(phi_1, Phi, phi_2, ipf)
        return math.pow(red-red_, 2) + math.pow(green-green_, 2) + math.pow(blue-blue_, 2)
    
    # Get the euler angle
    euler = minimize(
        fun=obj_func,
        x0=(100,100,100),
        method="Powell",
    ).x

    # Wrap and return
    euler = [e % 360 for e in euler]
    return euler[0], euler[1], euler[2]
