import sys; sys.path += [".."]
from sm_cubit.api import API

# Initialise and read pixels
api = API("inl_40x_10m")
api.read_pixels("20230817_617/inl_10m_r25.csv", 10)
# api.decrease_resolution(4)

# Cut microstructure
api.redefine_domain(245, 2417, 123-100, 1753-130)
api.redefine_domain(-2172/4, 2172+2172/4, 0, 1600)
# api.redefine_domain(245, 2417, 123-100, 1753-100)
# api.redefine_domain(-2172/4, 2172+2172/4, 0, 1630)

# Add grips
# api.clean_pixels(3)
# api.smoothen_edges(3)
api.fill_void()
api.visualise_by_grain(ipf="z")
api.visualise_by_element(ipf="z")

# Mesh
api.mesh("~/cubit/psculpt.exe", thickness=10*3, adaptive=False)
api.export_grain_stats()
api.export_element_stats()
