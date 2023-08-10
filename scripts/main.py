import sys; sys.path += [".."]
from sm_cubit.api import API

# Initialise and read pixels
api = API("inl_40x_10m")
api.read_pixels("20230628_617/inl_40x_10m.csv", 10)
api.visualise(ipf="z")

# Cut microstructure and add grips
api.redefine_domain(245, 2417, 123-100, 1753-100)
api.redefine_domain(-2172/4, 2172+2172/4, 0, 1630)
# api.decrease_resolution(2)
api.add_homogenised()
api.visualise(ipf="z")

# Mesh
api.mesh("~/cubit/psculpt.exe", thickness=10*3, adaptive=False)
api.export_statistics("input_stats", orientation=True, area=True)
