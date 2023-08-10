import sys; sys.path += [".."]
from sm_cubit.api import API

# Initialise and read pixels
api = API("inl_40x_10m")
api.read_pixels("20230628_617/inl_40x_10m.csv", 10)
api.visualise(ipf="z")

# Cut microstructure and add grips
api.redefine_domain(0, 300, 0, 100)
api.visualise(ipf="z")

# Mesh
api.mesh("~/cubit/psculpt.exe", thickness=10*3, adaptive=False)
api.export_statistics("input_stats", orientation=True, area=True)
