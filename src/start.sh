#!/bin/bash

# This script should be called at boot by the VM

git -C /root/HoneyWalt_VM/ reset --hard
git -C /root/HoneyWalt_VM/ pull
python3 /root/HoneyWalt_VM/src/honeywalt_vm.py