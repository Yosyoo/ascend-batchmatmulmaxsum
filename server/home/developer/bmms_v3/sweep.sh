#!/bin/bash
# sweep.sh <variant> <mode> <shape...>
cd /home/developer/bmms_v3/harness
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID="${DEV:-0}"
python3 measure.py "$@"
