from modules.api import API

# Initialise and read pixels
api = API("", 0)
api.read_pixels("tensile/inl_617_40x_4m.csv", 4)
api.decrease_resolution(5)
api.visualise(ipf="z")

# Clean microstructure mesh
api.pad_edges(10)
api.clean_pixels(3)
api.smoothen_edges(3)
api.assimilate(5)
api.redefine_domain(0, 2000, 0, 1700)

# Add grips
api.redefine_domain(2000/2-9500/2, 2000/2+9500/2, 1700/2-5000/2, 1700/2+5000/2)
api.add_homogenised()

# Cut grips
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