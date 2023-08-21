"""
 Title:         Shaper
 Description:   For creating non-large geometries for samples 
 Author:        Janzen Choi

"""

# Library
from modules.api import API

# Initialise and read pixels
api = API("", 0)
api.read_pixels("617.csv", 6.5)

# Define domain and shape
x_offset, y_offset = 750, 100
api.redefine_domain(x_offset, 2200+x_offset, y_offset, 1700+y_offset)
api.decrease_resolution(3)
api.visualise(ipf="z")

# # Improve quality
api.clean_pixels(5)
api.smoothen_edges(5)
api.smoothen_edges(2)
api.visualise(ipf="z")

# Mesh and export
api.mesh("~/cubit/psculpt.exe", 6.5*3*1) # 15*6.5
api.export_statistics(orientation=True, area=True)