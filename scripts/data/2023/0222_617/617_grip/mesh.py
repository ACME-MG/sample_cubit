from modules.api import API

# Initialise and read pixels
api = API("", 0)
api.read_pixels("617.csv", 6.5)
api.add_homogenised()
api.read_image("617_grip.png", "z")

# Mesh and export
api.mesh("~/cubit/psculpt.exe", 200) # 5*3*6.5
api.export_statistics("input_orientations.csv", orientation=True)