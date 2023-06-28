# External
from python_wireguard import Client, Key, ServerConnection
from string import Template
import os

# Internal
from common.utils.logs import *
from common.utils.misc import *
from common.utils.system import *

global WG_PEER_IP, WG_PEER_MASK, CONF_PATH
WG_PEER_IP   = "192.168."
WG_PEER_MASK = "24"
CONF_PATH	 = "/etc/wireguard/"

class WireguardController:

	ENDPOINT_HOST = "10.0.0.1"
	ENDPOINT_PORT = 6000

	def __init__(self, server):
		log(INFO, "WireguardController.__init__: creating the WireguardController")
		self.server = server
		self.name = None

	def __del__(self):
		pass

	def generate_ip(self, dev_id):
		if WG_PEER_MASK == "16":
			return WG_PEER_IP+str(dev_id//255)+"."+str((dev_id%255)+1)
		elif WG_PEER_MASK=="24":
			return WG_PEER_IP+"0."+str((dev_id%255)+1)
		else:
			return None

	def generate_iface(self, dev_id):
		return 'wg-cli-'+str(dev_id)

	def get_name(self):
		return self.__class__.__name__ if self.name is None else self.name

	def set_name(self, name):
		self.name = name

	def keygen(self):
		keys = []

		for honeypot in self.server.config:
			# Generate new keys
			honeypot["privkey"], honeypot["pubkey"] = Key.key_pair()
			honeypot["privkey"] = str(honeypot["privkey"])
			honeypot["pubkey"]  = str(honeypot["pubkey"])
			keys += [ {"id":honeypot["id"], "pubkey":str(honeypot["pubkey"])} ]

		return {"success": True, "answer": keys}

	def door_ip(self):
		return WireguardController.ENDPOINT_HOST

	def door_port(self, ident):
		return WireguardController.ENDPOINT_PORT + int(ident)

	def up(self):
		res = {"success": True, ERROR: [], WARNING: []}

		# Reading Wireguard interface configuration file template
		with open(to_root_path("var/template/wg_client.txt"), "r") as temp_file:
			template = Template(temp_file.read())

		# Removing old configuration files
		for old_conf_file in os.listdir(CONF_PATH):
			os.remove(os.path.join(CONF_PATH, old_conf_file))

		for honeypot in self.server.config:
			iface = self.generate_iface(honeypot["id"])
			vpn_ip = self.generate_ip(honeypot["id"])
			conf_filename = os.path.join(CONF_PATH, iface+".conf")

			# Creating configuration
			config = template.substitute({
				"table": honeypot["door"]["port"], # Table takes the same value as the port
				"ip": vpn_ip,
				"mask": WG_PEER_MASK,
				"vm_privkey": honeypot["privkey"],
				"dev_ip": honeypot["device"]["ip"],
				"server_pubkey": honeypot["door"]["pubkey"],
				"server_ip": honeypot["door"]["ip"],
				"server_port": honeypot["door"]["port"]
			})

			# Writing the configuration file
			with open(conf_filename, "w") as conf_file:
				conf_file.write(config)

			# Run 'wg-quick up'
			cmd = "wg-quick up "+conf_filename
			run(cmd)

		return res

	def down(self):
		res = {"success": True, ERROR: [], WARNING: []}
		
		for honeypot in self.server.config:
			iface = self.generate_iface(honeypot["id"])
			conf_filename = os.path.join(CONF_PATH, iface+".conf")

			if not self.is_up(iface):
				continue
			else:
				# Run 'wg-quick down'
				cmd = "wg-quick down "+conf_filename
				run(cmd)

		return res

	def is_up(self, name):
		# The wireguard library does not allow to check which devices are up
		# (Note: there is a wireguard.list_devices function but it prints the result to stdout instead of returning it)
		res = run("wg show interfaces", output=True)
		return name in res.split()