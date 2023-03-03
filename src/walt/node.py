import time

from utils import *

def get_ip(node):
	# We consider the node doesn't belong to anyone.
	# If it belong to root or to another user, we won't get the ip
	command = "walt node show --all | \
		grep \""+node+"\" | \
		tr -s \"[:blank:]\" | \
		cut -d\" \" -f4"
	return run(command, "walt get_ip: failed to get node ip", output=True).strip()

def get_name(mac_addr):
	command = "walt device show | \
		grep \""+mac_addr+"\" | \
		tr -s \"[:blank:]\" | \
		cut -d\" \" -f1"
	return run(command, "walt get_name: failed", output=True).strip()

def name_exists(name):
	command = "walt node show --all | grep \"^"+name+" \""
	res = run(command, "walt node_exists: failed", output=True, ignore_errors=[1])
	return res != ""

def mac_exists(mac):
	command = "walt device show | tr -s \"[:blank:]\" | cut -d\" \" -f 2 | grep \""+mac+"\""
	res = run(command, "walt.node.mac_exists: failed", output=True, ignore_errors=[1])
	return res != ""

def rename(old_name, new_name):
	command = "walt device rename "+old_name+" "+new_name
	run(command, "walt rename: failed")

def reboot(node):
	command = "walt node reboot "+node+" --hard"
	run(command, "walt reboot: failed to reboot a node")

def config(node, netsetup):
	run("walt node config "+node+" netsetup="+netsetup, "walt config: failed")

def boot(node, image):
	run("walt node boot "+node+" "+image, "walt boot: failed to boot a node")

def equal(list1, list2):
        if len(list1) != len(list2):
                return False
        list1.sort()
        list2.sort()
        for i in range(len(list1)):
                if list1[i] != list2[i]:
                        return False
        return True

def get_booted():
        booted_nodes = run("walt node show --all | \
                grep \"yes\" | \
                cut -d\" \" -f1", "walt get_booted_nodes: failed", output=True)
        return booted_nodes.strip().split("\n")

def wait_boots(nodes):
	i=0
	while i<24:
		i+=1
		booted_nodes = get_booted_nodes()
		if equal(booted_nodes, nodes):
			return True
		else:
			time.sleep(5)
	return False