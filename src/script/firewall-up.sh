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
iptables -I PREROUTING 1 -t mangle -i walt-net ! -s ${ips} -j DROP