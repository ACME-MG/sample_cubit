from modules.api import API

api = API("", 0)
api.read_pixels("p91b.csv", 0.15)

api.pad_edges(15)
api.clean_pixels(5)
api.smoothen_edges(5)
api.redefine_domain(2,27,0,39)

# api.cut_rectangle(0,6.75,6,24)
# api.cut_rectangle(18.3,25,6,24)
# api.cut_rectangle(0,9.75,9,21)
# api.cut_rectangle(15.3,25,9,21)
# api.cut_circle(6.75,9,3)
# api.cut_circle(6.75,21,3)
# api.cut_circle(18.3,9,3)
# api.cut_circle(18.3,21,3)

api.decrease_resolution(3)
api.smoothen_edges(3)
api.clean_pixels(3)

api.visualise(ipf="z")
api.mesh("~/cubit/psculpt.exe", 5.55)
api.export_statistics(orientation=True)