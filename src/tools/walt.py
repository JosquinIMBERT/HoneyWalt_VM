# External
import json, shutil
from string import Template
from walt.client import api

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

		walt_nodes = api.nodes.get_nodes()
		walt_images = api.images.get_images()

		for dev in devices:
			if len(walt_nodes.filter(mac=dev["mac"])) <= 0:
				log(WARNING, self.get_name()+".receive_devices: unknown device ("+dev["mac"]+")")
				res[WARNING] += ["unknown device ("+dev["mac"]+")"]
				fails += 1
				continue
			node = list(walt_nodes.filter(mac=dev["mac"]))[0]

			# Get the image if we don't already have it
			if len(walt_images.filter(name=dev["image"])) <= 0:
				if not api.images.clone(dev["image"]):
					log(WARNING, self.get_name()+".receive_devices: image "+dev["image"]+" not found")
					res[WARNING] += ["image "+dev["image"]+" not found"]
					fails += 1
					continue
			img = list(walt_images.filter(name=dev["image"]))[0]

			#--------------------------------------------------------------------#
			# Create an image with the name of the device and the expected users #
			#--------------------------------------------------------------------#
			
			# Generate the Dockerfile content
			with open(to_root_path("var/template/Dockerfile.template"), "r") as template_file:
				template = Template(template_file.read())
			params = {
				'image': img.fullname,
				'user': dev["username"],
				'pass': dev["password"]
			}
			content = template.substitute(params)
			
			# Create the Docker directory and add its content
			try:
				os.makedirs(to_root_path("run/walt/docker/"+dev["name"]), exist_ok=True)
				shutil.copy(to_root_path("var/useradd.sh"), to_root_path("run/walt/docker/"+dev["name"]+"/"))
				with open(to_root_path("run/walt/docker/"+dev["name"]+"/Dockerfile"), "w+") as docker_file:
					docker_file.write(content)
				api.images.build(dev["name"], to_root_path("run/walt/docker/"+dev["name"]+"/"))
			except Exception as e:
				log(WARNING, self.get_name()+".receive_devices: failed to add the user for dev "+dev["name"])
				log(ERROR, e)
				res[WARNING] += ["failed to add the user for dev "+dev["name"]]
				fails += 1
				continue

			# Rename the device if necessary
			if not node.name == dev["name"]:
				node.rename(dev["name"])
			node.config.mount_persist = False
			node.config.netsetup = 'NAT'

			dev["ip"] = node.ip

			glob.DEVS += [dev]

		res["fails"] = fails
		return res

	def get_ips(self):
		ips = []
		for dev in glob.DEVS:
			ips += [{"name":dev["name"], "ip":dev["ip"]}]
		return {"success": True, "answer": ips}

	def boot_devices(self):
		res = {"success": True, WARNING: [], ERROR: []}
		nodes = api.nodes.get_nodes()

		for dev in glob.DEVS:
			subset = nodes.filter(mac=dev["mac"])
			if len(subset) > 0:
				node = list(subset)[0]
				node.boot(dev["name"]) # The image with the valid user has the node name
			else:
				res[WARNING] += ["failed to boot "+dev["name"]]

	def reboot(self, dev_name):
		nodes = api.nodes.get_nodes()

		subset = nodes.filter(name=dev)
		if len(subset) > 0:
			node = list(subset)[0]
			node.reboot(hard_only=True)
			return {"success": True}
		else:
			return {"success": False, ERROR: ["failed to reboot "+dev_name]}

	def remove_image(self, name):
		images = api.images.get_images()
		if name in images:
			images[name].remove()