import sys; sys.path += [".."]
from sm_cubit.api import API

# Initialise and read pixels
api = API("inl_40x_40m")
api.read_pixels("20230628_617/inl_40x_10m.csv", 10)
api.decrease_resolution(4)

# Cut microstructure
api.redefine_domain(245, 2417, 123-100, 1753-130)
api.redefine_domain(-2172/4, 2172+2172/4, 0, 1600)
# api.redefine_domain(245, 2417, 123-100, 1753-100)
# api.redefine_domain(-2172/4, 2172+2172/4, 0, 1630)

# Add grips
api.clean_pixels(3)
api.smoothen_edges(3)
api.add_homogenised()
api.visualise(ipf="z")

# Mesh
api.mesh("~/cubit/psculpt.exe", thickness=40*3, adaptive=False)
api.export_statistics("input_stats", orientation=True, area=True)
