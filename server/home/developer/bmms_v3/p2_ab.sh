#!/bin/bash
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID=0
printf "1 3 5 40\n" > /tmp/p2.txt
: > /home/developer/bmms_v3/p2_res.txt
for i in $(seq 1 12); do
  for v in c102 c106; do
    t=$(timeout 200 python3 harness/multi.py $v /tmp/p2.txt 20 2 1 0 2>/dev/null \
        | python3 -c "import sys,json;print('%.4f'%json.load(sys.stdin)['shapes'][0]['warm_median'])" 2>/dev/null)
    echo "$i $v $t" >> /home/developer/bmms_v3/p2_res.txt
  done
done
echo DONE > /tmp/p2_done
