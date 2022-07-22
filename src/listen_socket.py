import time

from utils import run
from walt import adduser_to_image, clone, get_ip, reboot

PATH = "/dev/vport1p1"

class ListenSocket:
	def __init__(self, path):
		self.path = path
		self.sock = open(path, "a+b", 0)
	
	def initiate(self):
		# Tell the controller the VM booted
		self.send_confirm()

		# Receive phase
		phase = int(self.recv())

		if phase==1:
			# Receive images
			images = self.recv_elems()
			
			# Start to download images
			for image in images:
				clone(image)
			self.send("done")
			
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
		self.sock.write(b"1")

	def send_fail(self):
		self.sock.write(b"0")

	def send(self, string):
		self.sock.write(to_bytes(string+"\n"))

	def recv(self):
		return to_string(self.sock.readline())

	def send_elems(self, elems):
		str_elems = ""
		for elem in elems:
			str_elems += str(elem)
		self.sock.write(str_elems)

	def recv_elems(self):
		elems = self.sock.readline()
		return elems.split(" ")
    
	def to_bytes(string):
		b = bytearray()
		b.extend(string.encode())
		return b

	def to_string(bytes):
		return bytes.decode('ascii')

def main():
	lsock = ListenSocket(PATH)
	lsock.initiate()

if __name__ == '__main__':
	main()