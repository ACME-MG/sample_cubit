"""
 Title:         EBSD Imager
 Description:   For reading EBSD data and converting orientations from euler-bunge into RGB form for IPF
 Author:        Janzen Choi

"""

# Libraries
import math
from PIL import Image

# Constants
STEP_SIZE = 0.1

# Converts a quaternion into a set of euler-bunge angles (rads)
# https://mooseframework.inl.gov/docs/doxygen/modules/classEulerAngles.html
def quat_to_euler(w, x, y, z):
    phi_1 = math.atan2(x*z+w*y, w*x-y*z)
    Phi   = math.atan2(math.sqrt(1-math.pow(w*w-x*x-y*y+z*z,2)), w*w-x*x-y*y+z*z)
    phi_2 = math.atan2(x*z-w*y,w*x+y*z)
    phi_1 = phi_1 if phi_1 >= 0 else phi_1 + math.pi
    phi_2 = phi_2 if phi_2 >= 0 else phi_2 + math.pi
    return [phi_1, Phi, phi_2]

# Converts radians to degrees
def rad_to_deg(radians):
    if isinstance(radians, list):
        return [rad_to_deg(r) for r in radians]
    return radians * 180 / math.pi

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
        [[0,-1,0], [0,0,1], [-1,0,0]],
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
        [[0,1,0], [-1,0,0], [0,0,1]],
        [[0,1,0], [1,0,0], [0,0,-1]],
        [[0,-1,0], [1,0,0], [0,0,1]],
    ]

# Converts orientation from euler-bunge to RGB (for cubic only)
# https://mooseframework.inl.gov/docs/doxygen/modules/Euler2RGB_8h.html
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
    
    orientation_matrix = euler_to_matrix(phi_1, Phi, phi_2)
    symmetry_matrices = get_cubic_symmetry_matrices()

    # Sort euler angles into SST
    for i in range(len(symmetry_matrices)):\

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

# Reads the EBSD data and produces the plot
# plot_orientations_csv("output_gridify_0030.csv", "plot.png", ipf="z", quat_headers=["orientation_q4", "orientation_q2", "orientation_q3", "orientation_q1"])
def plot_orientations_csv(gridify_path, output_path, ipf="z", coord_headers=["x", "y"], quat_headers=["orientation_q1", "orientation_q2", "orientation_q3", "orientation_q4"]):

    # Load file to RAM
    file = open(gridify_path, "r")
    header = file.readline().replace("\n", "").split(",")
    data = file.readlines()
    file.close()

    # Get column positions
    x_index = header.index(coord_headers[0])
    y_index = header.index(coord_headers[1])
    q1_index = header.index(quat_headers[0])
    q2_index = header.index(quat_headers[1])
    q3_index = header.index(quat_headers[2])
    q4_index = header.index(quat_headers[3])

    # Iterate through data and store it
    pixel_list = []
    for i in range(len(data)):

        # Extract data
        row = data[i].replace("\n", "").split(",")
        q1 = float(row[q1_index])
        q2 = float(row[q2_index])
        q3 = float(row[q3_index])
        q4 = float(row[q4_index])
        x_coord = round(float(row[x_index])/STEP_SIZE)
        y_coord = round(float(row[y_index])/STEP_SIZE)

        # Get euler orientation and IPF colour
        euler = quat_to_euler(q1, q2, q3, q4)
        euler = rad_to_deg(euler)
        colour = euler_to_rgb(*euler, ipf)

        # Store in list of pixels
        pixel_list.append({
            "coord": (x_coord, y_coord),
            "colour": colour
        })

    # Initialise image
    x_min = min([pixel["coord"][0] for pixel in pixel_list])
    x_max = max([pixel["coord"][0] for pixel in pixel_list])
    y_min = min([pixel["coord"][1] for pixel in pixel_list])
    y_max = max([pixel["coord"][1] for pixel in pixel_list])
    img = Image.new("RGBA", size=(x_max-x_min+1,y_max-y_min+1), color=(255,255,255,0))

    # Place pixels on the image and save
    for pixel in pixel_list:
        coord = (pixel["coord"][0]-x_min, pixel["coord"][1]-y_min)
        img.putpixel(coord, pixel["colour"])
    img.save(output_path, "PNG")

# plot_orientations_csv("output_gridify_0030.csv", "plot_z.png", ipf="z", quat_headers=["orientation_q4", "orientation_q2", "orientation_q3", "orientation_q1"])