#!/bin/bash

# We only add/remove one rule because we don't want to interfere with wireguard/walt rules 

#######################
###      INPUT      ###
#######################

if [[ $# != 1 ]]; then
	echo "Usage: $0 <ips>"
	echo -e "\tips: (coma separated) list of device ips"
	exit 1
fi



#######################
###    VARIABLES    ###
#######################

ips=$1



#######################
###    FIREWALL     ###
#######################

# We drop all packets from devices that are not used by honeywalt
# This way we can avoid IP spoofing
iptables -t mangle -N NOSPOOF
iptables -t mangle -F NOSPOOF
iptables -t mangle -A NOSPOOF -s ${ips} -j RETURN
iptables -t mangle -A NOSPOOF -d ${ips} -j RETURN
iptables -t mangle -A NOSPOOF -d 224.0.1.129 -j RETURN # Allow PTP
iptables -t mangle -A NOSPOOF -j LOG --log-prefix "[NOSPOOF_DROP] " # Adding log message for spoofed packets
iptables -t mangle -A NOSPOOF -j DROP
iptables -t mangle -I PREROUTING 1 -i walt-net -j NOSPOOF