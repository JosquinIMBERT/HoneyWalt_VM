# External
import argparse, json, os, signal, sys

# Internal
from tools.walt import WaltController
from tools.wireguard import WireguardController
from vm.controller import VMController

# Common
from common.utils.files import *
from common.utils.logs import *

server = None

def handle(signum, frame):
	global server
	server.stop()

class VMServer:
	"""VMServer"""
	def __init__(self):
		log(DEBUG, "VMServer.__init__: initializing global variables")

		self.vm = VMController(self)
		self.walt = WaltController(self)
		self.wireguard = WireguardController(self)

		self.user_conf_file = to_root_path("etc/honeywalt_vm.cfg")
		self.dist_conf_file = to_root_path("etc/honeywalt_vm.cfg.dist")
		self.config = {}

		signal.signal(signal.SIGINT, handle) # handle ctrl-C

	def load_config(self):
		conf_filename = self.user_conf_file if isfile(self.user_conf_file) else self.dist_conf_file
		with open(conf_filename, "r") as conf_file:
			self.config = json.loads(conf_file.read())

	def dump_config(self):
		# Write the configuration file
		with open(self.user_conf_file, "w") as conf_file:
			conf_file.write(json.dumps(self.config, indent=4))
			# We ensure the data is written to the file because the next operation will likely be a shutdown
			conf_file.flush()
			os.fsync(conf_file)

	def reinit(self):
		self.walt.remove_images()
		self.config = []
		self.dump_config()

	def receive_honeypots(self, honeypots):
		res = {"success": True, WARNING: [], ERROR: []}

		honeypots = json.loads(honeypots)

		for h in honeypots:
			# Device
			dev = self.walt.find_device(h["device"]["mac"])
			if not dev:
				log(ERROR, "failed to find device", h["device"]["name"])
				continue
			self.walt.configure_device(dev, h["device"]["name"])

			# Base Image
			img = self.walt.find_image(h["image"]["name"], h["image"]["short_name"])
			if not img:
				log(ERROR, "failed to find image", h["image"]["name"])
				continue

			# Honeypot Image
			res = self.walt.create_honeypot_image(h["device"]["mac"], img, h["credentials"]["user"], h["credentials"]["pass"])
			if not res:
				log(ERROR, "failed to build the image for honeypot", str(h["id"]))
				continue

			h["device"]["ip"] = self.walt.device_ip(dev)
			h["door"]["ip"]   = self.wireguard.door_ip()
			h["door"]["port"] = self.wireguard.door_port(h["id"])

			self.config += [h]

		return res

	def stop(self):
		log(DEBUG, "VMServer.stop: stopping VM controller")
		self.vm.stop()

	def start(self):
		log(DEBUG, "VMServer.start: loading devices")
		self.load_config()
		log(DEBUG, "VMServer.start: running VM controller")
		self.vm.run()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='HoneyWalt VM Daemon')
	parser.add_argument("-l", "--log-level", nargs=1, help="Set log level (COMMAND, DEBUG, INFO, WARNING, ERROR, FATAL)")

	options = parser.parse_args()
	if options.log_level is not None:
		log_level = options.log_level[0]
		set_log_level(log_level)

	server = VMServer()
	server.start()