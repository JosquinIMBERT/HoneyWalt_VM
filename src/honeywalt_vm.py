# External
import argparse, os, signal, sys

# Internal
#sys.path[0] = os.path.join(os.environ["HONEYWALT_VM_HOME"],"src/")
from common.utils.logs import *
import glob
from tools.walt import WaltController
from tools.wireguard import WireguardController
from vm.controller import VMController

def handle(signum, frame):
	glob.SERVER.stop()

class VMServer:
	"""VMServer"""
	def __init__(self):
		log(DEBUG, "VMServer.__init__: initializing global variables")
		glob.init(self)
		log(DEBUG, "VMServer.__init__: initializing VM controller")
		self.VM_CONTROLLER = VMController()
		log(DEBUG, "VMServer.__init__: initializing WalT controller")
		self.WALT_CONTROLLER = WaltController()
		log(DEBUG, "VMServer.__init__: initializing Wireguard controller")
		self.WIREGUARD_CONTROLLER = WireguardController()
		signal.signal(signal.SIGINT, handle) # handle ctrl-C

	def stop(self):
		log(DEBUG, "VMServer.stop: stopping VM controller")
		self.VM_CONTROLLER.stop()

	def start(self):
		log(DEBUG, "VMServer.start: running VM controller")
		self.VM_CONTROLLER.run()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='HoneyWalt VM Daemon')
	parser.add_argument("-l", "--log-level", nargs=1, help="Set log level (COMMAND, DEBUG, INFO, WARNING, ERROR, FATAL)")

	options = parser.parse_args()
	if options.log_level is not None:
		log_level = options.log_level[0]
		set_log_level(log_level)

	vm_server = VMServer()
	vm_server.start()