#!/bin/bash
# cmpc.sh <variant...>   -- compare variants on $SHAPEFILE (default shapes_pool2.txt), 20 iters
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID=0
F=${SHAPEFILE:-shapes_pool2.txt}; N=${ITERS:-20}
for v in "$@"; do
  printf "%-8s" "$v"
  python3 harness/multi.py $v $F $N 2>/dev/null | python3 -c "
import sys, json
d=json.load(sys.stdin)
print(' ' + ' '.join('%8.2f'%s['warm_median'] for s in d['shapes']))
" 
done
