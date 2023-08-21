"""
 Title:         Orientations
 Description:   For orientation related functions
 Author:        Janzen Choi

"""

# Libraries
import math

def deg_to_rad(degrees:float) -> float:
    """
    Converts degrees to radians
    
    Parameters:
    * `degrees`: The angle in degrees
    
    Returns the angle in radians
    """
    if isinstance(degrees, list):
        return [deg_to_rad(d) for d in degrees]
    return degrees * math.pi / 180

def rad_to_deg(radians) -> float:
    """
    Converts radians to degrees
    
    Parameters:
    * `radians`: The angle in radians
    
    Returns the angle in degrees
    """
    if isinstance(radians, list):
        return [rad_to_deg(r) for r in radians]
    return radians * 180 / math.pi

def euler_to_matrix(phi_1:float, Phi:float, phi_2:float) -> list:
    """
    Determines the orientation matrix of a set of euler-bunge angles (rads)
    
    Parameters:
    * `phi_1`: The first component of the euler-bunge orientation
    * `Phi`:   The second component of the euler-bunge orientation
    * `phi_2`: The third component of the euler-bunge orientation
    
    Returns the orientation matrix
    """
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

def euler_to_quat(phi_1:float, Phi:float, phi_2:float) -> tuple:
    """
    Converts a set of euler-bunge angles into a quaternion (rads)
    
    Parameters:
    * `phi_1`: The first component of the euler-bunge orientation
    * `Phi`:   The second component of the euler-bunge orientation
    * `phi_2`: The third component of the euler-bunge orientation
    
    Returns the orientation as a quarternion
    """
    cy = math.cos(phi_2 * 0.5)
    sy = math.sin(phi_2 * 0.5)
    cp = math.cos(Phi * 0.5)
    sp = math.sin(Phi * 0.5)
    cr = math.cos(phi_1 * 0.5)
    sr = math.sin(phi_1 * 0.5)
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    w = cr * cp * cy + sr * sp * sy
    return x, y, z, w

def quat_to_euler(x:float, y:float, z:float, w:float) -> tuple:
    """
    Converts a quaternion into a set of euler-bunge angles (rads)
    
    Parameters:
    * `x`: The first component of the quaternion orientation
    * `y`: The second component of the quaternion orientation
    * `z`: The third component of the quaternion orientation
    * `w`: The fourth component of the quaternion orientation
    
    Returns the orientation in euler-bunge form
    """
    phi_1 = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    Phi   = math.asin(max([min([2 * (w * y - z * x), 1]), -1]))
    phi_2 = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return phi_1, Phi, phi_2
