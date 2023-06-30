from common.utils.files import *
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
			ips += [honeypot["device"]["ip"]]
		str_ips = ",".joint(ips)
		run(to_root_path("src/script/firewall-up.sh")+" "+str_ips)

	def stop(self):
		if len(self.str_ips) > 0:
			run(to_root_path("src/script/firewall-down.sh")+" "+str_ips)