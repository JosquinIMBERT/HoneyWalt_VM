from utils import run

def clone(image):
	run("walt image clone "+image, "walt clone: error: failed to clone image")

def get_ip(node):
	command = "walt node show | \
		grep \""+node+"\" | \
		tr -s \"[:blank:]\" | \
		cut -d\" \" -f5"
	return run(command, "walt get_ip: error: failed to get node ip", output=True)

def reboot(node):
	command = "walt node reboot "+node+" --hard"
	run(command, "walt reboot: error: failed to reboot a node")