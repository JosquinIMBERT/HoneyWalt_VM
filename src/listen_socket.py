import select, socket, time

from utils import *
from walt import *

def to_bytes(string):
	b = bytearray()
	b.extend(string.encode())
	return b

def to_string(bytes_obj):
	return bytes_obj.decode('ascii')

class ListenSocket:
	def __init__(self, port):
		self.socket = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
		self.socket.connect((socket.VMADDR_CID_HOST, port))
	
	def initiate(self):
		# Receive phase
		phase = int(self.recv())
		self.send_confirm()

		if phase==1:
			# Receive images
			images = self.recv_elems()
			
			# Start to download images
			for image in images:
				clone(image)
			print("Images: ", images)
			self.send_confirm()
			
			# Receive usernames and passwords
			usernames = self.recv_elems()
			print("Usernames: ", usernames)
			self.send_confirm()

			passwords = self.recv_elems()
			print("Passwords: ", passwords)
			self.send_confirm()
			
			# Add users
			i=0
			for i in range(len(images)):
				# TODO: fix this function (for now, the user should be added manually)
				#adduser_to_image(images[i], usernames[i], passwords[i])
				i+=1

			# Receive backends
			backends = self.recv_elems()
			print("Backends: ", backends)
			self.send_confirm()

			# Receive mac addresses
			macs = self.recv_elems()
			print("MACs: ", backends)
			self.send_confirm()

			if len(macs) != len(backends):
				eprint("ListenSocket.initiate: invalid number of MACs/backends")

			# Renaming the backends
			for i in range(len(backends)):
				if not node_exists(backends[i]):
					curr_name = get_name(macs[i])
					rename(curr_name, backends[i])

			# Find IPs
			ips = []
			for backend in backends:
				ip = get_ip(backend)
				ips += [ ip ]
			# IPs is the only information sent to the controller
			# They are sent __before__ to expose the VM
			self.send_elems(ips)
			print("Images: ", ips)
			self.wait_confirm()
		else:
			images = self.recv_elems()
			print("Images: ", images)
			self.send_confirm()
			backends = self.recv_elems()
			print("Backends: ", backends)

			# I had a problem when running manually the config and boot commands successively
			# I try running first the config commands, waiting and then running the boot cmds
			i=0
			for i in range(len(backends)):
				config(backends[i], "NAT")
			time.sleep(5)
			i=0
			for i in range(len(backends)):
				boot(backends[i], images[i])

			self.send_confirm()
			#if wait_boots(backends):
			#	self.send_confirm()
			#else:
			#	self.send_fail()

			self.run()

	def run(self):
		switch = {
			"reboot": reboot
		}

		while True:
			data = self.recv()
			if data:
				split = data.split(":",1)
				op = split[0]
				if len(split) > 1:
					data = split[1]
				else:
					data = ""
				func = switch.get(op)
				if func:
					func(data)
					self.send_confirm()
			else:
				time.sleep(2)
				continue

	def send_confirm(self):
		self.send("1")

	def send_fail(self):
		self.send("0")

	def wait_confirm(self, timeout=30):
		res = self.recv(timeout=timeout)
		return res[0] == "1"

	def send(self, string):
		self.socket.send(to_bytes(string+"\n"))

	def recv(self, timeout=30):
		self.socket.settimeout(timeout)
		try:
			res = self.socket.recv(2048)
		except socket.timeout:
			eprint("ListenSocket.recv: error: reached timeout")
		except:
			eprint("ListenSocket.recv: error: an unknown error occured")
		else:
			if not res:
				eprint("ControlSocket.recv: error: Connection terminated")
			return to_string(res)

	def send_elems(self, elems, sep=" "):
		str_elems = ""
		for elem in elems:
			str_elems += str(elem) + sep
		self.send(str_elems)

	def recv_elems(self, sep=" "):
		elems = self.recv().strip()
		if not elems:
			return []
		return elems.split(sep)

def main():
	lsock = ListenSocket(5555)
	lsock.initiate()

if __name__ == '__main__':
	main()