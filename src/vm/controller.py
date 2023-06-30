# External
import socket, time

# Common
from common.utils.controller import Controller
from common.utils.logs import *
from common.utils.sockets import ClientSocket
from common.utils.system import *
from common.vm.proto import *

class VMController(Controller):
	def __init__(self, server):
		Controller.__init__(self)

		self.server = server

		self.socket = ClientSocket(socktype=socket.AF_VSOCK)
		self.socket.set_name("Socket(VM-Controller)")
		self.keep_running = False
		self.phase = None

	def __del__(self):
		del self.socket

	def connect(self):
		#log(DEBUG, self.get_name()+".connect: connecting to the HoneyWalt_controller")
		return self.socket.connect(socket.VMADDR_CID_HOST, CONTROL_PORT)

	def reconnect(self):
		return self.socket.connect(socket.VMADDR_CID_HOST, CONTROL_PORT)

	def stop(self):
		self.keep_running = False


	#################
	#  CONTROL LOOP #
	#################

	def run(self, sleep=3):
		self.keep_running = True
		while self.keep_running:
			if self.connect():
				disconnected = False
				while self.keep_running and not disconnected:
					cmd = self.socket.recv_cmd()
					if not cmd:
						disconnected = True
					else:
						self.execute(cmd)
				if disconnected:
					log(INFO, self.get_name()+".run: disconnected")
			else:
				time.sleep(sleep)


	#################
	#	 SWITCH  	#
	#################

	def execute(self, cmd):
		if cmd == CMD_VM_PHASE:
			log(INFO, self.get_name()+".execute: CMD_VM_PHASE")
			phase = self.socket.recv_obj()
			self.exec(self.exposed_set_phase, phase)
		elif cmd == CMD_VM_HONEYPOTS and self.phase == COMMIT_PHASE:
			log(INFO, self.get_name()+".execute: CMD_VM_HONEYPOTS")
			honeypots = self.socket.recv_obj()
			self.exec(self.exposed_set_honeypots, honeypots)
		elif cmd == CMD_VM_IPS and self.phase == RUN_PHASE:
			log(INFO, self.get_name()+".execute: CMD_VM_IPS")
			self.exec(self.exposed_get_ips)
		elif cmd == CMD_VM_WG_KEYGEN and self.phase == COMMIT_PHASE:
			log(INFO, self.get_name()+".execute: CMD_VM_WG_KEYGEN")
			self.exec(self.exposed_wg_keygen)
		elif cmd == CMD_VM_WG_UP and self.phase == RUN_PHASE:
			log(INFO, self.get_name()+".execute: CMD_VM_WG_UP")
			self.exec(self.exposed_wg_up)
		elif cmd == CMD_VM_WG_DOWN and self.phase == RUN_PHASE:
			log(INFO, self.get_name()+".execute: CMD_VM_WG_DOWN")
			self.exec(self.exposed_wg_down)
		elif cmd == CMD_VM_FW_UP and self.phase == RUN_PHASE:
			log(INFO, self.get_name()+".execute: CMD_VM_FW_UP")
			self.exec(self.exposed_firewall_up)
		elif cmd == CMD_VM_FW_DOWN and self.phase == RUN_PHASE:
			log(INFO, self.get_name()+".execute: CMD_VM_FW_DOWN")
			self.exec(self.exposed_firewall_down)
		elif cmd == CMD_VM_COMMIT and self.phase == COMMIT_PHASE:
			log(INFO, self.get_name()+".execute: CMD_VM_COMMIT")
			self.exec(self.exposed_commit)
		elif cmd == CMD_VM_SHUTDOWN:
			log(INFO, self.get_name()+".execute: CMD_VM_SHUTDOWN")
			self.socket.send_obj({"success": True})
			self.exposed_shutdown()
		elif cmd == CMD_VM_LIVE:
			self.socket.send_obj({"success": True})
		else:
			log(ERROR, self.get_name()+".execute: Received invalid command")
			self.socket.send_obj({"success": False, ERROR: ["unsupported operation"]})


	#################
	#	COMMANDS	#
	#################

	def exposed_set_phase(self, phase):
		self.phase = phase
		if not isinstance(self.phase, int) or self.phase not in [COMMIT_PHASE, RUN_PHASE, DEBUG_PHASE]:
			log(ERROR, self.get_name()+".exposed_set_phase: invalid phase")
			return {"success": False, ERROR: ["invalid phase type"]}
		if self.phase == RUN_PHASE:
			self.server.walt.boot_devices()
		elif self.phase == DEBUG_PHASE:
			log(INFO, self.get_name()+".exposed_set_phase: the VM was started in DEBUG phase. The daemon will stop")
			self.keep_running = False
		elif self.phase == COMMIT_PHASE:
			log(DEBUG, self.get_name()+".exposed_set_phase: clearing images")
			self.server.reinit()
		log(INFO, self.get_name()+".exposed_set_phase: Running in phase "+str(self.phase))
		return {"success": True}

	def exposed_set_honeypots(self, honeypots):
		return self.server.receive_honeypots(honeypots)

	def exposed_get_ips(self):
		return self.server.walt.get_ips()

	def exposed_wg_keygen(self):
		return self.server.wireguard.keygen()

	def exposed_wg_up(self):
		return self.server.wireguard.up()

	def exposed_wg_down(self):
		return self.server.wireguard.down()

	def exposed_firewall_up(self):
		return self.server.firewall.start()

	def exposed_firewall_down(self):
		return self.server.firewall.stop()

	def exposed_commit(self):
		self.server.dump_config()
		return {"success": True}

	def exposed_shutdown(self):
		if not run("shutdown now"):
			log(WARNING, self.get_name()+".exposed_shutdown: Failed to shutdown the VM")
