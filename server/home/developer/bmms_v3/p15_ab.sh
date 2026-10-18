#!/bin/bash
# 点15 交替重复对照：A=c101 B=c102，各 10 轮交替
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID=0
printf "1 64 64 8192\n" > /tmp/p15.txt
: > /home/developer/bmms_v3/p15_res.txt
for i in $(seq 1 10); do
  for v in c101 c102; do
    t=$(timeout 200 python3 harness/multi.py $v /tmp/p15.txt 20 1 1 1 2>/dev/null \
        | python3 -c "import sys,json;print('%.4f'%json.load(sys.stdin)['shapes'][0]['warm_median'])" 2>/dev/null)
    echo "$i $v $t" >> /home/developer/bmms_v3/p15_res.txt
  done
done
echo DONE > /tmp/p15_done
