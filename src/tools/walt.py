# External
import json, shutil
from string import Template
from walt.client import api

# Internal
from common.utils.files import *
from common.utils.logs import *
from common.utils.misc import *

class Walt:
	def __init__(self, server):
		self.server = server
		self.name = None

	def __del__(self):
		del self.server.config

	def get_name(self):
		return self.__class__.__name__ if self.name is None else self.name

	def set_name(self, name):
		self.name = name

	def find_device(self, mac):
		walt_nodes = api.nodes.get_nodes()
		if len(walt_nodes.filter(mac=mac)) <= 0:
			return None
		return list(walt_nodes.filter(mac=mac))[0]

	def configure_device(self, dev, name):
		if not dev.name == name:
			dev.rename(name)
		dev.config.mount_persist = False
		dev.config.netsetup = 'NAT'

	def find_image(self, name, short_name):
		walt_images = api.images.get_images()
		if len(walt_images.filter(name=short_name)) <= 0:
			if not api.images.clone(name):
				return None
		return list(walt_images.filter(name=short_name))[0]

	def create_honeypot_image(self, dev_name, img, username, password):
		# Generate the Dockerfile content
		with open(to_root_path("var/template/Dockerfile.template"), "r") as template_file:
			template = Template(template_file.read())
		params = {
			'image': img.fullname,
			'user': username,
			'pass': password
		}
		content = template.substitute(params)
		
		# Create the Docker directory and add its content
		try:
			os.makedirs(to_root_path("run/walt/docker/"+dev_name), exist_ok=True)
			shutil.copy(to_root_path("var/useradd.sh"), to_root_path("run/walt/docker/"+dev_name+"/"))
			with open(to_root_path("run/walt/docker/"+dev_name+"/Dockerfile"), "w+") as docker_file:
				docker_file.write(content)
			api.images.build(dev_name, to_root_path("run/walt/docker/"+dev_name+"/"))
		except Exception as e:
			return None

		return True

	def device_ip(self, device):
		return device.ip

	def get_ips(self):
		ips = []
		for honeypot in self.server.config:
			ips += [{"ip":honeypot["device"]["ip"], "id":honeypot["id"]}]
		return {"success": True, "answer": ips}

	def boot_devices(self):
		res = {"success": True, WARNING: [], ERROR: []}
		nodes = api.nodes.get_nodes()

		for honeypot in self.server.config:
			subset = nodes.filter(mac=honeypot["device"]["mac"])
			if len(subset) > 0:
				node = list(subset)[0]
				node.boot(honeypot["device"]["name"]) # The image with the valid user has the node name
			else:
				res[WARNING] += ["failed to boot "+honeypot["device"]["name"]]

	def reboot(self, dev_name):
		nodes = api.nodes.get_nodes()

		subset = nodes.filter(name=dev_name)
		if len(subset) > 0:
			node = list(subset)[0]
			node.reboot(hard_only=True)
			return {"success": True}
		else:
			return {"success": False, ERROR: ["failed to reboot "+dev_name]}

	def remove_images(self):
		log(INFO, "removing images")
		nodes = api.nodes.get_nodes()
		images = api.images.get_images()
		for honeypot in self.server.config:
			if honeypot["device"]["name"] in images:
				# Free the node, so that the image can be removed
				nodes[honeypot["device"]["name"]].boot("default")
				# Remove the image
				images[honeypot["device"]["name"]].remove()
				log(DEBUG, "image "+str(honeypot["device"]["name"])+" removed")
			else:
				log(DEBUG, "image "+str(honeypot["device"]["name"])+" not found")