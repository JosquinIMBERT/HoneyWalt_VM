# External
import json, socket

from common.utils.controller import *
from common.utils.logs import *
from common.utils.sockets import ClientSocket
from common.vm.proto import *

class VMController(Controller):
	def __init__(self):
		self.socket = ClientSocket(socktype=socket.AF_VSOCK)
		self.keep_running = False
		self.phase = None

	def __del__(self):
		del self.socket

	def connect(self):
		return self.socket.connect(socket.VMADDR_CID_HOST, CONTROL_PORT)

	def stop(self):
		self.keep_running = False


	#################
	#  CONTROL LOOP #
	#################

	def run(self):
		self.keep_running = True
		while self.keep_running:
			if self.connect()
				disconnected = False
				while self.keep_running and not disconnected:
					cmd = self.socket.recv_cmd()
					if not cmd:
						disconnected = True
					else:
						self.execute(cmd)
				if disconnected:
					log(INFO, self.name()+".run: disconnected")


	#################
	#	 SWITCH  	#
	#################

	def execute(self):
		if cmd == CMD_VM_PHASE:
			log(INFO, self.name()+".execute: CMD_VM_PHASE")
			self.exec(self.cmd_vm_phase)
		elif cmd == CMD_VM_WALT_DEVS and self.phase is not None:
			log(INFO, self.name()+".execute: CMD_VM_WALT_ADD_DEV")
			self.exec(self.cmd_vm_walt_devs)
		elif cmd == CMD_VM_WALT_IPS and self.phase is not None:
			log(INFO, self.name()+".execute: CMD_VM_WALT_DEV_IP")
			self.exec(self.cmd_vm_walt_ips)
		elif cmd == CMD_VM_WG_KEYGEN and self.phase is not None:
			log(INFO, self.name()+".execute: CMD_VM_WG_KEYGEN")
			self.exec(self.cmd_vm_wg_keygen)
		elif cmd == CMD_VM_WG_DOORS and self.phase is not None:
			log(INFO, self.name()+".execute: CMD_VM_WG_DOORS")
			self.exec(self.cmd_vm_wg_doors)
		elif cmd == CMD_VM_WG_UP and self.phase is not None:
			log(INFO, self.name()+".execute: CMD_VM_WG_UP")
			self.exec(self.cmd_vm_wg_up)
		elif cmd == CMD_VM_WG_DOWN and self.phase is not None:
			log(INFO, self.name()+".execute: CMD_VM_WG_DOWN")
			self.exec(self.cmd_vm_wg_down)
		elif cmd == CMD_VM_COMMIT and self.phase is not None:
			log(INFO, self.name()+".execute: CMD_VM_COMMIT")
			self.exec(self.cmd_vm_commit)
		elif cmd == CMD_VM_SHUTDOWN:
			log(INFO, self.name()+".execute: CMD_VM_SHUTDOWN")
			self.exec(self.cmd_vm_shutdown)
		elif cmd == CMD_VM_LIVE:
			self.socket.send_obj({"success": True})
		else:
			log(ERROR, self.name()+".execute: Received invalid command")
			self.socket.send_obj({"success": True, "error": ["unsupported operation"]})


	#################
	#	COMMANDS	#
	#################

	def cmd_vm_phase(self):
		self.phase = self.socket.recv_obj()
		if not isinstance(self.phase, int) or self.phase not in [COMMIT_PHASE, RUN_PHASE, DEBUG_PHASE]:
			log(ERROR, self.name()+".cmd_vm_phase: invalid phase")
			return {"success": False, "error": ["invalid phase type"]}
		if self.phase == RUN_PHASE:
			glob.SERVER.WALT_CONTROLLER.load_devices()
		elif self.phase == DEBUG_PHASE:
			log(INFO, self.name()+".cmd_vm_phase: the VM was started in DEBUG phase. The daemon will stop")
			self.keep_running = False
		else:
			log(INFO, self.name()+".cmd_vm_phase: Running in phase "+str(self.phase))
		return {"success": True}

	def cmd_vm_walt_devs(self):
		if self.phase != COMMIT_PHASE:
			log(ERROR, self.name()+".cmd_vm_walt_devs: Received devices during run phase")
			return {"success": False, "error": ["cannot add devices during run phase"]}
		else:
			devs = self.socket.recv_obj()
			return glob.SERVER.WALT_CONTROLLER.receive_devices(devs)

	def cmd_vm_walt_ips(self):
		return glob.SERVER.WALT_CONTROLLER.get_ips()

	def cmd_vm_wg_keygen(self):
		if self.phase != COMMIT_PHASE:
			log(WARNING, self.name()+".cmd_wg_keygen: keys can only be generated during commit phase")
			return {"success": False, "error": ["keys can only be generated during commit phase"]}
		else:
			return glob.SERVER.WIREGUARD_CONTROLLER.keygen()

	def cmd_vm_wg_doors(self):
		if self.phase != COMMIT_PHASE:
			log(WARNING, self.name()+".cmd_wg_doors: doors can only be received during commit phase")
			return {"success": False, "error": ["doors can only be received during commit phase"]}
		else:
			# Receive public keys
			doors = self.socket.recv_obj()
			return glob.SERVER.WIREGUARD_CONTROLLER.receive_doors(doors)

	def cmd_vm_wg_up(self):
		if self.phase != RUN_PHASE:
			log(ERROR, self.name()+".cmd_vm_wg_up: cannot setup wireguard during run phase")
			return {"success": False, "error": ["cannot setup wireguard during run phase"]}
		return glob.SERVER.WIREGUARD_CONTROLLER.up()

	def cmd_vm_wg_down(self):
		return glob.SERVER.WIREGUARD_CONTROLLER.down()

	def cmd_vm_commit(self):
		if self.phase != COMMIT_PHASE:
			log(ERROR, self.name()+".cmd_vm_commit: cannot commit in run phase")
			return {"success": False, "error": ["cannot commit in run phase"]}
		else:
			# Write the configuration file
			with open(to_root_path("etc/honeywalt_vm.cfg"), "w") as conf_file:
				conf_file.write(json.dumps(glob.DEVS, indent=4))
			return {"success": True}

	def cmd_vm_shutdown(self):
		run("init 0", self.name()+".cmd_vm_shutdown: Failed to shutdown the VM")