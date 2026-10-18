#!/bin/bash
# hangscan2.sh <variant> <shapefile> <dtype> <ta> <tb>
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID=0
V=$1; F=$2; DT=$3; TA=$4; TB=$5
n=0
while read b m n k; do
  n=$((n+1))
  out=$(timeout 45 python3 harness/one.py $V ${b}_${m}_${n}_${k}_${DT}_${TA}_${TB} 2>&1 | tail -1)
  case "$out" in
    *"median= None"*|"") echo "HANG: $V ${b}_${m}_${n}_${k} dt=$DT ta=$TA tb=$TB" ;;
  esac
done < $F
echo "SCAN DONE $V dt=$DT ta=$TA tb=$TB  ($n shapes)"
