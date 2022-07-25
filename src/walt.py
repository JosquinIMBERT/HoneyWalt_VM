from string import Template

from utils import *

# TODO: fix this function (it doesn't work)
def adduser_to_image(image, username, password):
	copy_cmd = "walt image cp "+to_root_path("var/manage_users.sh")+" "+image+":manage_users.sh"
	run(copy_cmd, "walt adduser_to_image: error: failed to copy script to image")
	with open(to_root_path("var/image_commands.txt"), "r") as file:
		add_cmd_temp = Template(file.read())
	add_cmd = add_cmd_temp.substitute({"username": str(username), "password": str(password), "image": image})
	run(
		"echo -e \""+add_cmd+"\" | walt image shell "+image,
		"walt adduser_to_image: error: failed to run command on image"
	)

def clone(image):
	run("walt image clone "+image, "walt clone: error: failed to clone image")

def get_ip(node):
	# We consider the node doesn't belong to anyone.
	# If it belong to root or to another user, we won't get the ip
	command = "walt node show --all | \
		grep \""+node+"\" | \
		tr -s \"[:blank:]\" | \
		cut -d\" \" -f4"
	return run(command, "walt get_ip: error: failed to get node ip", output=True).strip()

def reboot(node):
	command = "walt node reboot "+node+" --hard"
	run(command, "walt reboot: error: failed to reboot a node")