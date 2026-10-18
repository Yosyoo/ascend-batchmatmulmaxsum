#!/bin/bash
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID=0
echo "SHAPES:"; cat shapes_big.txt | tr '\n' '|'; echo
for v in "$@"; do
  echo "== $v"
  python3 harness/multi.py $v shapes_big.txt 30 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('   '+'  '.join('%8.2f'%s['warm_median'] for s in d['shapes']))
print('   aicS '+'  '.join('%8.2f'%s['units'].get('aic_scalar_time(us)',0) for s in d['shapes']))
"
done
