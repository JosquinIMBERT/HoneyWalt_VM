def init(vm_server):
	global PORT, IP_OUT, WIREGUARD_PORTS
	global SERVER

	IP_OUT = "10.0.0.1"
	WIREGUARD_PORTS=6000

	SERVER = vm_server