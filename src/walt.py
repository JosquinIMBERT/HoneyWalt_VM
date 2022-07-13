from utils import *

def adduser_to_image(image, username, password):
	copy_cmd = "walt image cp "+to_root_path("var/manage_users.sh")+" "+image+":/"
	run(copy_cmd, "walt adduser_to_image: error: failed to copy script to image")
	add_cmd = "chmod u+x /manage_users.sh; \
		/manage_users.sh "+username+" "+password+"; \
		rm /manage_users.sh; exit;"
	run("echo -e \""+add_cmd+"\ny\" | walt image shell "+image, "walt adduser_to_image: error: failed to run command on image")

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