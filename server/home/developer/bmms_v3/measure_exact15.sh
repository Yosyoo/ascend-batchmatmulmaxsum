#!/bin/bash
# 逐个用各自的 dtype/ta/tb 测量 15 个真实评测形状
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID=0
V="$1"; F=/home/developer/bmms_v3/exact15.txt
i=0
while read b m n k dt ta tb; do
  i=$((i+1))
  printf "P%-2d (%d,%d,%d,%d) d%d t%d%d  " $i $b $m $n $k $dt $ta $tb
  printf "%d %d %d %d\n" $b $m $n $k > /tmp/one15.txt
  timeout 200 python3 harness/multi.py $V /tmp/one15.txt 20 $dt $ta $tb 2>/dev/null \
    | python3 -c "import sys,json
d=json.load(sys.stdin)['shapes']
s=d[0]
print('%9.2f us  passed=%s' % (s['warm_median'], s.get('passed')))" 2>/dev/null || echo "FAIL"
done < $F
