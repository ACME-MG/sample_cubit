"""
 Title:         Pixel Maths
 Description:   Contains pixel-related functions
 Author:        Janzen Choi

"""

# Libraries
import numpy as np

# Constants
VOID_PIXEL_ID       = 100000 # large number
UNORIENTED_PIXEL_ID = 100001 # large number + 1
NO_ORIENTATION      = [0, 0, 0] # for both void and unoriented

def get_void_pixel_grid(x_cells:list, y_cells:list) -> list:
    """
    Creates a grid of void pixels
    
    Parameters:
    * `x_cells`:    The number of pixels on the horizontal axis
    * `y_cells`:    The number of pixels on the vertical axis
    * `init_value`: The initial value of the cell in the piel grid
    
    Returns a grid of void pixels
    """
    pixel_grid = []
    for _ in range(y_cells):
        pixel_list = []
        for _ in range(x_cells):
            pixel_list.append(VOID_PIXEL_ID)
        pixel_grid.append(pixel_list)
    return pixel_grid

def replace_pixels(pixel_grid:list, coordinates_list:list, replacement:str="void") -> list:
    """
    Replaces a grid of pixels with void pixels based on coordinates
    
    Parameters:
    * `pixel_grid`:       The 2D list of pixels
    * `coordinates_list`: A list of (x,y) coordinates
    * `new_id`:           The new ID that the material will use to replace
    
    Returns the new pixel grid
    """
    
    # Initialise
    replacement_id = VOID_PIXEL_ID if replacement == "void" else UNORIENTED_PIXEL_ID
    x_size = len(pixel_grid[0])
    y_size = len(pixel_grid)
    
    # Iterate through coordinates and replace
    for coordinates in coordinates_list:
        if coordinates[0] >= 0 and coordinates[1] >= 0 and coordinates[0] < x_size and coordinates[1] < y_size:
            coordinates = [int(coordinate) for coordinate in coordinates] # coordinates can unround themselves
            pixel_grid[coordinates[1]][coordinates[0]] = replacement_id
    return pixel_grid

def mult_round(to_round:float, mult_number:float, decimal_place:int=5) -> float:
    """
    Rounds a number to the nearest multiple of another number
    
    Parameters:
    * `to_round`:      The number to be rounded
    * `mult_number`:   The nearest multiple
    * `decimal_place`: The number of decimal places to round to
    
    Returns the rounded multiple 
    """
    result =  mult_number*(round(to_round/mult_number))
    return round(result, decimal_place)

def get_coordinates_within_circle(x_centre:float, y_centre:float, radius:float) -> list:
    """
    Calculates a list of coordinates within a defined circle
    
    Parameters:
    * `x_centre`: The x coordinate of the circle's centre
    * `y_centre`: The y coordinate of the circle's centre
    * `radius`:   The radius of the circle
    
    Returns the coordinates list
    """

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

def get_coordinates_within_rectangle(x_min:float, x_max:float, y_min:float, y_max:float) -> list:
    """
    Returns a list of coordinates within a defined rectangle
    
    Parameters:
    * `x_min`: The minimum x value of the rectangle
    * `x_max`: The maximum x value of the rectangle
    * `y_min`: The minimum y value of the rectangle
    * `y_max`: The maximum y value of the rectangle
    
    Returns the coordinates list
    """
    coordinates_list = []
    for x in np.arange(x_min, x_max, 0.5):
        for y in np.arange(y_min, y_max, 0.5):
            if x >= x_min and x <= x_max and y >= y_min and y <= y_max:
                coordinates_list.append((round(x), round(y)))
    return coordinates_list

def get_sign(x_1:float, y_1:float, x_2:float, y_2:float, x_p:float, y_p:float) -> float:
    """
    Returns the sign of a point relative to a line
    
    Parameters:
    * `x_1`: The x coordinate of the first point on the line
    * `y_1`: The y coordinate of the first point on the line
    * `x_2`: The x coordinate of the second point on the line
    * `y_2`: The y coordinate of the second point on the line
    * `x_p`: The x coordinate of the point on the left / right of the line
    * `y_p`: The y coordinate of the point on the left / right of the line
    
    Returns the sign as some float that is either positive or negative
    """
    return (x_p-x_2) * (y_1-y_2) - (x_1-x_2) * (y_p-y_2)

def is_point_in_triangle(x_1:float, y_1:float, x_2:float, y_2:float,
                         x_3:float, y_3:float, x_p:float, y_p:float) -> bool:
    """
    Returns the sign of a point relative to a line
    
    Parameters:
    * `x_1`: The x coordinate of the first point on the triangle
    * `y_1`: The y coordinate of the first point on the triangle
    * `x_2`: The x coordinate of the second point on the triangle
    * `y_2`: The y coordinate of the second point on the triangle
    * `x_2`: The x coordinate of the third point on the triangle
    * `y_3`: The y coordinate of the third point on the triangle
    * `x_p`: The x coordinate of the point on the left / right of the line
    * `y_p`: The y coordinate of the point on the left / right of the line
    
    Returns whether the point if in the triangle or not
    """

    # Get signs
    sign_12 = get_sign(x_1, y_1, x_2, y_2, x_p, y_p)
    sign_23 = get_sign(x_2, y_2, x_3, y_3, x_p, y_p)
    sign_31 = get_sign(x_3, y_3, x_1, y_1, x_p, y_p)

    # Determine if in triangle
    has_negative = sign_12 < 0 or sign_23 < 0 or sign_31 < 0
    has_positive = sign_12 > 0 or sign_23 > 0 or sign_31 > 0
    return not has_negative or not has_positive

def get_coordinates_within_triangle(x_1:float, y_1:float, x_2:float, y_2:float, x_3:float, y_3:float) -> bool:
    """
    Returns a list of coordinates within a defined triangle
    
    Parameters:
    * `x_1`: The x coordinate of the first point on the triangle
    * `y_1`: The y coordinate of the first point on the triangle
    * `x_2`: The x coordinate of the second point on the triangle
    * `y_2`: The y coordinate of the second point on the triangle
    * `x_2`: The x coordinate of the third point on the triangle
    * `y_3`: The y coordinate of the third point on the triangle
    
    Returns the coordinates list
    """
    
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

def get_neighbours(x:float, y:float, x_size:int, y_size:int) -> list:
    """
    Gets the neighbouring indices of a pixel
    
    Parameters:
    * `x`:      The x coordinate
    * `y`:      The y coordinate
    * `x_size`: The maximum x value 
    * `y_size`: The maximum y value
    
    Returns a list of the neighbouring coordinates 
    """
    neighbours = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
    neighbours = [
        neighbour for neighbour in neighbours
        if neighbour[0] >= 0 and neighbour[0] < x_size
        and neighbour[1] >= 0 and neighbour[1] < y_size
    ]
    return neighbours

def get_all_neighbours(x_list:list, y_list:list, x_size:int, y_size:int):
    """
    Gets the neighbouring indices of a group of pixels
    
    Parameters:
    * `x_list`: The list of x coordinates
    * `y_list`: The list of y coordinates
    * `x_size`: The maximum x value 
    * `y_size`: The maximum y value
    
    Returns a list of all the neighbouring coordinates 
    """
    
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
