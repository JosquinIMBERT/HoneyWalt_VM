#!/bin/bash

HOME=$(realpath $(dirname $(dirname "$0")))

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <log-level> [pidfile]"
	exit 1
else
	loglevel="$1"
fi

if [[ $# -gt 1 ]]; then
	pidfile="$1"
else
	pidfile="${HOME}/var/honeywalt_vm.pid"
fi

git -C ${HOME} reset -q --hard
git -C ${HOME} pull -q --recurse-submodules
${HOME}/requirements.sh

python3 ${HOME}/src/honeywalt_vm.py \
	--log-level ${loglevel} \
	--pid-file ${pidfile}