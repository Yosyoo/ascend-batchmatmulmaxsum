#!/bin/bash
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID=0
printf "1 16 32 128 256\n" > /tmp/p7.txt
: > /home/developer/bmms_v3/p7_res.txt
for r in $(seq 1 8); do
  for v in c106 clean118; do
    t=$(python3 harness/multi.py $v /tmp/p7.txt 20 1 1 0 2>/dev/null \
      | python3 -c "import sys,json;print('%.4f'%json.load(sys.stdin)['shapes'][0]['warm_median'])" 2>/dev/null)
    echo "$r $v $t" >> /home/developer/bmms_v3/p7_res.txt
  done
done
echo DONE > /tmp/p7_done
