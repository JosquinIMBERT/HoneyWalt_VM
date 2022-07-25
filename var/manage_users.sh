#!/bin/bash

if [[ $# -ne 2 ]]; then
	echo "usage: $0 <username> <password>"
	exit 1
fi

user=$1
pass=$2

# Add user and his password
if [ "$user" = "root" ]; then
	echo -e "$pass\n$pass" | passwd root
else
	exists=$(cat /etc/passwd | cut -d":" -f1 | grep $user | tr "\n" " ")
	if [ "$exists" = "" ]; then
		echo -e "$pass\n$pass\n\n\n\n\n\nY\n" | adduser $user >/dev/null 2>&1
	else
		echo -e "$pass\n$pass" | passwd $user
	fi
fi

# Allow ssh password authentication for root
sed 's/.*PermitRootLogin.*/PermitRootLogin yes/g' /etc/ssh/sshd_config >/tmp/tmp_sshd_config
mv /tmp/tmp_sshd_config /etc/ssh/sshd_config