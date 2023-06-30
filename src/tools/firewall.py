from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *

class Firewall:
	def __init__(self, server):
		self.server = server
		self.ips = []
		self.str_ips = ""

	def __del__(self):
		pass

	def start(self):
		self.ips = []
		for honeypot in self.server.config:
			self.ips += [honeypot["device"]["ip"]]
		if len(self.ips) > 0:
			self.str_ips = ",".join(self.ips)
			run(to_root_path("src/script/firewall-up.sh")+" "+self.str_ips)
		else:
			log(WARNING, "Firewall.up: tried to start the firewall while no IP is known")

	def stop(self):
		if len(self.str_ips) > 0:
			run(to_root_path("src/script/firewall-down.sh")+" "+self.str_ips)