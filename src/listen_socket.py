import select, time

from utils import *
from walt import adduser_to_image, clone, get_ip, reboot

PATH = "/dev/vport1p1"

def to_bytes(string):
	b = bytearray()
	b.extend(string.encode())
	return b

def to_string(bytes):
	return bytes.decode('ascii')

class ListenSocket:
	def __init__(self, path):
		self.path = path
		self.sock = open(path, "a+b", 0)
	
	def initiate(self):
		# Tell the controller the VM booted
		self.send_confirm()

		# Receive phase
		ready, _, _ = select.select([self.sock], [], [], 15)
		if len(ready) > 0:
			phase = self.recv()
			if phase.strip() == "":
				eprint("Failed to get phase")
			phase = int(phase)
		else:
			eprint("Failed to get phase")

		if phase==1:
			# Receive images
			images = self.recv_elems()
			
			# Start to download images
			for image in images:
				clone(image)
			self.send_confirm()
			
			# Receive usernames and passwords
			usernames = self.recv_elems()
			passwords = self.recv_elems()
			
			# Add users
			for image in images:
				adduser_to_image(image["name"], image["user"], image["pass"])

			# Find IPs
			backends = self.recv_elems()
			ips = []
			for backend in backends:
				ip = get_ip(backend)
				ips += [ ip ]
			# IPs are the only string values sent to the controller
			# They are sent __before__ to expose the VM
			self.send_elems(ips)
		else:
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

	def send(self, string):
		self.sock.write(to_bytes(string+"\n"))

	def recv(self, max_iter=30):
		res = ""
		i = 0
		while True and i<max_iter:
			i+=1
			res = self.sock.readline()
			if not res:
				time.sleep(1)
				continue
			break
		if i >= max_iter:
			eprint("ListenSocket:recv: error: reached max_iter")
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
	lsock = ListenSocket(PATH)
	lsock.initiate()

if __name__ == '__main__':
	main()