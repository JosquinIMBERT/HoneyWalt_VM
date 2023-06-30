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

iptables -D PREROUTING -t mangle -i walt-net ! -s ${ips} -j DROP