from modules.api import API

# Initialise and read pixels
api = API("", 0)
api.read_pixels(f"tensile/inl_617_40x_4m.csv", 4)
api.decrease_resolution(5)
api.add_homogenised()
api.read_image(f"tensile/inl_617_40x_20m.png", "z")
api.visualise(ipf="z")

# Mesh and export
api.mesh("~/cubit/psculpt.exe", thickness=100, adaptive=False)
api.export_statistics("input_orientations.csv", orientation=True)