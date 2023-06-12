# External
from python_wireguard import Client, Key, ServerConnection
from string import Template
import os

# Internal
from common.utils.logs import *
from common.utils.misc import *
from common.utils.system import *
import glob

global WG_PEER_IP, WG_PEER_MASK, CONF_PATH
WG_PEER_IP   = "192.168."
WG_PEER_MASK = "16"
CONF_PATH	 = "/etc/wireguard/"

class WireguardController:
	def __init__(self):
		self.name = None

	def __del__(self):
		pass

	def generate_ip(self, dev_id):
		return WG_PEER_IP+str(dev_id//255)+"."+str((dev_id%255)+1)

	def generate_iface(self, dev_id):
		return 'wg-cli-'+str(dev_id)

	def get_name(self):
		return self.__class__.__name__ if self.name is None else self.name

	def set_name(self, name):
		self.name = name

	def keygen(self):
		keys = []

		for dev in glob.DEVS:
			# Generate new keys
			dev["wg_privkey"], dev["wg_pubkey"] = Key.key_pair()
			dev["wg_privkey"] = str(dev["wg_privkey"])
			dev["wg_pubkey"]  = str(dev["wg_pubkey"])
			keys += [ {"dev_id":dev["id"], "pubkey":str(dev["wg_pubkey"])} ]

		return {"success": True, "answer": keys}

	def receive_doors(self, doors):
		if len(doors) != len(glob.DEVS):
			log(ERROR, self.get_name()+".receive_doors: the number of doors did not match the number of devices")
			return {"success": False, ERROR: ["the number of doors did not match the number of devices"]}
		else:
			for door in doors:
				dev = find(glob.DEVS, door["dev_id"], "id")
				dev["door_ip"] = door["ip"]
				dev["door_port"] = door["port"]
				dev["door_wg_pubkey"] = door["wg_pubkey"]
			return {"success": True}

	def up(self):
		res = {"success": True, ERROR: [], WARNING: []}

		# Reading Wireguard interface configuration file template
		with open(to_root_path("var/template/wg_client.txt"), "r") as temp_file:
			template = Template(temp_file.read())

		# Removing old configuration files
		for old_conf_file in os.listdir(CONF_PATH):
			os.remove(os.path.join(CONF_PATH, old_conf_file))

		for dev in glob.DEVS:
			iface = self.generate_iface(dev["id"])
			vpn_ip = self.generate_ip(dev["id"])
			conf_filename = os.path.join(CONF_PATH, iface+".conf")

			# Creating configuration
			config = template.substitute({
				"table": dev["door_port"], # Table takes the same value as the port
				"ip": vpn_ip,
				"mask": WG_PEER_MASK,
				"vm_privkey": dev["wg_privkey"],
				"dev_ip": dev["ip"],
				"server_pubkey": dev["door_wg_pubkey"],
				"server_ip": dev["door_ip"],
				"server_port": dev["door_port"]
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
		
		for dev in glob.DEVS:
			iface = self.generate_iface(dev["id"])
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