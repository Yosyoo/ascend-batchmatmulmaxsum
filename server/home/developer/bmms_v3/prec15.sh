#!/bin/bash
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID=0
V=$1
i=0
while read b m n k dt ta tb; do
  i=$((i+1))
  printf "P%-2d " $i
  timeout 200 python3 harness/dbgtest.py $V ${b}_${m}_${n}_${k}_${dt}_${ta}_${tb} 2>&1 | tail -1
done < /home/developer/bmms_v3/exact15.txt
