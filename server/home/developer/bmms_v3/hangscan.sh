#!/bin/bash
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID=0
V=$1; F=$2
while read b m n k; do
  out=$(timeout 45 python3 harness/one.py $V ${b}_${m}_${n}_${k} 2>&1 | tail -1)
  case "$out" in
    *"median= None"*|"") echo "HANG/FAIL: $V $b $m $n $k  ->  ${out:0:60}" ;;
  esac
done < $F
echo "SCAN DONE $V"
