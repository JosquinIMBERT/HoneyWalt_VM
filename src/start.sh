#!/bin/bash

# This script should be called at boot by the VM

git -C /root/HoneyWalt_VM/ reset -q --hard
git -C /root/HoneyWalt_VM/ pull -q --recurse-submodules
/root/HoneyWalt_VM/requirements.sh
python3 /root/HoneyWalt_VM/src/honeywalt_vm.py -l CMD