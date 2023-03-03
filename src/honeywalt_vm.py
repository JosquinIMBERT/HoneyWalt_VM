# External
import signal

# Internal
sys.path[0] = os.path.join(os.environ["HONEYWALT_VM_HOME"],"src/")
import glob
from tools.walt import WaltController
from tools.wireguard import WireguardController
from tools.vm import VMController

def handle(signum, frame):
	glob.SERVER.stop()

class VMServer:
	"""VMServer"""
	def __init__(self):
		glob.init(self)
		self.VM_CONTROLLER = VMController()
		self.WALT_CONTROLLER = WaltController()
		self.WIREGUARD_CONTROLLER = WireguardController()
		signal.signal(signal.SIGINT, handle) # handle ctrl-C

	def stop(self):
		glob.VM_CONTROLLER.stop()

	def start(self):
		glob.VM_CONTROLLER.connect()
		glob.VM_CONTROLLER.run()

if __name__ == '__main__':
	vm_server = VMServer()
	vm_server.start()