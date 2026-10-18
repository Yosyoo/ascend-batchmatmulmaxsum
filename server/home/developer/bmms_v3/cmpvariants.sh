#!/bin/bash
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID=0
echo "SHAPES:"
cat shapes_sm.txt | tr '\n' '|'; echo
for v in "$@"; do
  echo "== $v"
  python3 harness/multi.py $v shapes_sm.txt 40 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('   '+'  '.join('%6.2f'%s['warm_median'] for s in d['shapes']))
"
done
