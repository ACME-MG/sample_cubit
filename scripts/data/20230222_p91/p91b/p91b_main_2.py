from modules.api import API

api = API("", 0)
api.read_pixels("p91b.csv", 0.15)
api.read_image("p91b.png", "z")
api.visualise(ipf="z")
api.mesh("~/cubit/psculpt.exe", 5.55)
api.export_statistics(orientation=True)