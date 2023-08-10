"""
 Title:         Pixel Maths
 Description:   Contains pixel-related functions
 Author:        Janzen Choi

"""

# Libraries
import numpy as np

# Constants
VOID_PIXEL_ID = 100000 # large number
HOMOGENOUS_PIXEL_ID = 100001 # large number + 1

# Returns a grid of void pixels
def get_void_pixel_grid(x_cells, y_cells):
    pixel_grid = []
    for _ in range(y_cells):
        pixel_list = []
        for _ in range(x_cells):
            void_pixel = VOID_PIXEL_ID
            pixel_list.append(void_pixel)
        pixel_grid.append(pixel_list)
    return pixel_grid

# Replaces a grid of pixels with void pixels based on coordinates
def remove_pixels(pixel_grid, coordinates_list):
    x_size = len(pixel_grid[0])
    y_size = len(pixel_grid)
    for coordinates in coordinates_list:
        if coordinates[0] >= 0 and coordinates[1] >= 0 and coordinates[0] < x_size and coordinates[1] < y_size:
            coordinates = [int(coordinate) for coordinate in coordinates] # coordinates can unround themselves
            pixel_grid[coordinates[1]][coordinates[0]] = VOID_PIXEL_ID
    return pixel_grid

# Rounds a number to the nearest multiple of another number
def mult_round(to_round, mult_number, decimal_place=5):
    result =  mult_number*(round(to_round/mult_number))
    return round(result, decimal_place)

# Returns a list of coordinates within a defined circle
def get_coordinates_within_circle(x_centre, y_centre, radius):

    # Define bounds
    x_min = max(x_centre-radius, 0)
    x_max = x_centre + radius
    y_min = max(y_centre-radius, 0)
    y_max = y_centre + radius

    # Get list of coordinates within bounds
    coordinates_list = []
    for x in np.arange(x_min, x_max, 0.5):
        for y in np.arange(y_min, y_max, 0.5):
            if (x-x_centre)**2 + (y-y_centre)**2 < radius**2:
                coordinates_list.append((round(x), round(y)))
    
    # Return list of pixels
    return coordinates_list

# Returns a list of coordinates within a defined rectangle
def get_coordinates_within_rectangle(x_min, x_max, y_min, y_max):
    coordinates_list = []
    for x in np.arange(x_min, x_max, 0.5):
        for y in np.arange(y_min, y_max, 0.5):
            if x >= x_min and x <= x_max and y >= y_min and y <= y_max:
                coordinates_list.append((round(x), round(y)))
    return coordinates_list

# Returns the sign of a point relative to a line
#   (x_p, y_p) is a point on the left/right of the line
def get_sign(x_1, y_1, x_2, y_2, x_p, y_p):
    return (x_p-x_2) * (y_1-y_2) - (x_1-x_2) * (y_p-y_2)

def is_point_in_triangle(x_1, y_1, x_2, y_2, x_3, y_3, x_p, y_p):

    # Get signs
    sign_12 = get_sign(x_1, y_1, x_2, y_2, x_p, y_p)
    sign_23 = get_sign(x_2, y_2, x_3, y_3, x_p, y_p)
    sign_31 = get_sign(x_3, y_3, x_1, y_1, x_p, y_p)

    # Determine if in triangle
    has_negative = sign_12 < 0 or sign_23 < 0 or sign_31 < 0
    has_positive = sign_12 > 0 or sign_23 > 0 or sign_31 > 0
    return not has_negative or not has_positive

# Returns a list of coordinates within a defined triangle
def get_coordinates_within_triangle(x_1, y_1, x_2, y_2, x_3, y_3):
    
    # Get boundaries
    x_min = min([x_1, x_2, x_3])
    y_min = min([y_1, y_2, y_3])
    x_max = max([x_1, x_2, x_3])
    y_max = max([y_1, y_2, y_3])

    # Get points in triangle
    coordinates_list = []
    for x in np.arange(x_min, x_max, 0.5):
        for y in np.arange(y_min, y_max, 0.5):
            if is_point_in_triangle(x_1, y_1, x_2, y_2, x_3, y_3, x, y):
                coordinates_list.append((round(x), round(y)))
    return coordinates_list

# Gets the neighbouring indices of a pixel
def get_neighbours(x, y, x_size, y_size):
    neighbours = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
    neighbours = [
        neighbour for neighbour in neighbours
        if neighbour[0] >= 0 and neighbour[0] < x_size
        and neighbour[1] >= 0 and neighbour[1] < y_size
    ]
    return neighbours

# Gets the neighbouring indices of a group of pixels
def get_all_neighbours(x_list, y_list, x_size, y_size):
    
    # Gets all the neighbours
    all_neighbours = []
    for i in range(len(x_list)):
        neighbours = get_neighbours(x_list[i], y_list[i], x_size, y_size)
        all_neighbours += neighbours
    
    # Remove duplicates and neighbours in the group
    all_neighbours = list(set(all_neighbours))
    group = [(x_list[i],y_list[i]) for i in range(len(x_list))]
    all_neighbours = [neighbour for neighbour in all_neighbours if not neighbour in group]

    # Return
    return all_neighbours