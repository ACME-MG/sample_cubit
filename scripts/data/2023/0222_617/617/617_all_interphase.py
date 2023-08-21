from modules.api import API

# Initialise and read pixels
api = API(fancy=True, verbose=True)
api.read_pixels("617_ebsd.csv", 6.5)

# Define domain and shape
x_offset, y_offset = 750, 100 # i2_middle
# x_offset, y_offset = 1575, 100 # i23_sides
# x_offset, y_offset = 2350, 100 # i3_middle
# x_offset, y_offset = 1900, 100 # i3_right
api.redefine_domain(x_offset, 2200+x_offset, y_offset, 1700+y_offset)
api.decrease_resolution(3)
api.visualise(ipf="z")

# # Improve quality
api.clean_pixels(5)
api.smoothen_edges(5)
# api.assimilate(10)
api.smoothen_edges(2)
api.visualise(ipf="z")

# Mesh and export
api.mesh("~/cubit/psculpt.exe", 100) # 15*6.5