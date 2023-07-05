#!/bin/bash

# Usage: stop.sh [pidfile]

HOME=$(realpath $(dirname $(dirname "$0")))

if [[ $# -gt 0 ]]; then
	pidfile="$1"
else
	pidfile="${HOME}/var/honeywalt_vm.pid"
fi

if [ -f ${pidfile} ]; then
	pid=$(cat ${pidfile})
	if [[ "$pid" =~ ^[0-9]+$ ]]; then
		kill -2 "$pid"
	else
		echo "The content of the pid file is invalid"
	fi
else
	echo "The pid file was not found"
fi