#!/bin/bash

user=$1
pass=$2

# Check if user exists
if id ${user} &>/dev/null; then
        # Change user password
        echo ${pass} | sudo passwd ${user}
else
        # Add user
        useradd -m ${user} -p $(perl -e 'print crypt($ARGV[0], "password")' '${pass}')
fi