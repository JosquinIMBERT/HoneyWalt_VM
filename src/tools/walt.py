# External
import json
import walt.common.api as waltapi

# Internal
from common.utils.files import *
from common.utils.logs import *
from common.utils.misc import *
import glob

class WaltController:
	def __init__(self):
		glob.DEVS = []
		self.name = None

	def __del__(self):
		del glob.DEVS

	def get_name(self):
		return self.__class__.__name__ if self.name is None else self.name

	def set_name(self, name):
		self.name = name

	def load_devices(self):
		with open(to_root_path("etc/honeywalt_vm.cfg"), "r") as conf_file:
			glob.DEVS = json.load(conf_file)

	def dump_devices(self):
		# Write the configuration file
		with open(to_root_path("etc/honeywalt_vm.cfg"), "w") as conf_file:
			conf_file.write(json.dumps(glob.DEVS, indent=4))

	def receive_devices(self, devices):
		res = {"success": True, WARNING: [], ERROR: []}
		fails = 0
		images = {}

		for dev in devices:
			if not find(waltapi.nodes, dev["mac"], "mac"):
				log(WARNING, self.get_name()+".receive_devices: unknown device ("+dev["mac"]+")")
				res[WARNING] += ["unknown device ("+dev["mac"]+")"]
				fails += 1
				continue

			# Get the image if we don't already have it
			if not find(waltapi.images, dev["image"], "name"):
				# TODO
				# try:
				# 	waltapi.images.clone(dev["image"])
				# except:
				# 	log(WARNING, self.get_name()+".receive_devices: image "+dev["image"]+" not found")
				# 	res[WARNING] += ["image "+dev["image"]+" not found"]
				# 	fails += 1
				#	continue
				pass
			
			# Store the users in each image
			if not hasattr(images, dev["image"]):
				images[dev["image"]] = [{"username": dev["username"], "password": dev["password"]}]
			else:
				images[dev["image"]] += [{"username": dev["username"], "password": dev["password"]}]

			if not waltapi.nodes[dev["name"]]:
				curr_name = find(waltapi.nodes, dev["mac"], "mac")["name"]
				waltapi.nodes[curr_name].rename(dev["name"])

			dev["ip"] = waltapi.nodes[dev["name"]].ip

			glob.DEVS += [dev]

		for image,users in images.items():
			# TODO
			#waltapi.images[image].addusers(users)
			pass

		res["fails"] = fails
		return res

	def get_ips(self):
		ips = []
		for dev in glob.DEVS:
			ips += [{"name":dev["name"], "ip":dev["ip"]}]
		return {"success": True, "answer": ips}