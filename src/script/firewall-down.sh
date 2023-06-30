#!/bin/bash

# We only add/remove one rule because we don't want to interfere with wireguard/walt rules

#######################
###    FIREWALL     ###
#######################

# Removing reference
iptables -t mangle -D PREROUTING 1 -i walt-net -j NOSPOOF
# Removing NOSPOOF rules
iptables -t mangle -F NOSPOOF
# Removing NOSPOOF tables
iptables -t mangle -X NOSPOOF