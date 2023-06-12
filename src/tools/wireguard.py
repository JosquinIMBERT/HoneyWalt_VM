# This Wireguard library does not work, since we need to set the
# wireguard interface's table number but the python_wireguard library
# does ot implement this functionnality 

# External
from python_wireguard import Client, Key, ServerConnection

# Internal
from common.utils.logs import *
from common.utils.misc import *
from common.utils.system import *
import glob

global WG_PEER_IP
WG_PEER_IP = "192.168."

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
			log(ERROR, self.get_name()+".cmd_wg_doors: the number of doors did not match the number of devices")
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
		for dev in glob.DEVS:
			iface = self.generate_iface(dev["id"])
			cli_key = Key(dev["wg_privkey"])
			cli_ip = self.generate_ip(dev["id"])
			client = Client(iface, cli_key, cli_ip)

			srv_key = Key(dev["door_wg_pubkey"])
			endpoint = dev["door_ip"]
			port = dev["door_port"]
			server_conn = ServerConnection(srv_key, endpoint, port)

			client.set_server(server_conn)
			client.connect()

			post_res = self.post_up(dev["ip"], dev["door_port"])
			if not post_res["success"]:
				if hasattr(post_res, WARNING): res[WARNING] += post_res[WARNING]
				if hasattr(post_res, ERROR): res[ERROR] += post_res[ERROR]

		return res

	def post_up(self, ip, table):
		# TODO: find how to replace table or to give the wg interface a table id
		if not run("ip -4 rule add from "+str(ip)+" table "+str(table)):
			log(ERROR, "WireguardController.post_up: failed to start redirection of packets to wireguard")
			return {"success": False, ERROR: ["failed to start redirection of packets to wireguard"]}
		return {"success": True}

	def pre_down(self, ip, table):
		# TODO: find how to replace table or to give the wg interface a table id
		if not run("ip -4 rule del from "+str(ip)+" table "+str(table)):
			log(ERROR, "WireguardController.pre_down: failed to start redirection of packets to wireguard")
			return {"success": False, ERROR: ["failed to start redirection of packets to wireguard"]}
		return {"success": True}

	def down(self):
		res = {"success": True, ERROR: [], WARNING: []}
		for dev in glob.DEVS:
			if not self.is_up(dev["id"]):
				continue
			else:
				pre_res = self.pre_down()
				if not pre_res["success"]:
					if hasattr(post_res, WARNING): res[WARNING] += post_res[WARNING]
					if hasattr(post_res, ERROR): res[ERROR] += post_res[ERROR]

				iface = self.generate_iface(dev["id"])
				cli_key = Key(dev["wg_privkey"])
				cli_ip = self.generate_ip(dev["id"])
				Client(iface, cli_key, cli_ip).delete_interface()
		return res