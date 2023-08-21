from modules.api import API

# Initialise and read pixels
api = API("", 0)
api.read_pixels("617.csv", 6.5)

# Define domain and shape
x_offset, y_offset = 850, 100 # i2_middle
api.redefine_domain(x_offset, 2000+x_offset, y_offset, 1700+y_offset)
api.redefine_domain(2000/2-9500/2, 2000/2+9500/2, 1700/2-5000/2, 1700/2+5000/2)
api.visualise(ipf="z")
api.add_homogenised()

# Cut
api.cut_rectangle(3650, 5670, 0, 1650)
api.cut_rectangle(3650, 5670, 3350, 5000)
api.cut_circle(3660, 650, 1000)
api.cut_circle(5840, 650, 1000)
api.cut_circle(3660, 4350, 1000)
api.cut_circle(5840, 4350, 1000)
api.cut_triangle(1600, 0, 3120, 0, 3120, 1500)
api.cut_triangle(6380, 0, 7900, 0, 6380, 1500)
api.cut_triangle(1600, 5000, 3120, 5000, 3120, 3500)
api.cut_triangle(6380, 5000, 7900, 5000, 6380, 3500)
api.visualise(ipf="z")

# Improve quality
api.decrease_resolution(3)
api.clean_pixels(5)
api.smoothen_edges(5)
api.visualise(ipf="z")

# # Mesh and export
# api.mesh("~/cubit/psculpt.exe", 40) # 23*6.5
# api.export_statistics("input_orientations.csv", orientation=True)