#!/bin/bash
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID=0
: > /home/developer/bmms_v3/ns_res.txt
runspec(){
  v=$1; name=$2; d=$3; ta=$4; tb=$5
  timeout 300 python3 harness/multi.py $v /tmp/ns_$name.txt 20 $d $ta $tb 2>/dev/null \
   | python3 -c "import sys,json;print('%.4f'%json.load(sys.stdin)['shapes'][0]['warm_median'])" 2>/dev/null || echo FAIL
}
for spec in "p10 1 4096 1280 1152 2 0 0" "p11 1 1536 2048 2048 1 1 1" "p12 1 1280 4096 1536 2 1 0"; do
  name=$(echo $spec | cut -d' ' -f1)
  b=$(echo $spec | cut -d' ' -f2); m=$(echo $spec | cut -d' ' -f3)
  n=$(echo $spec | cut -d' ' -f4); k=$(echo $spec | cut -d' ' -f5)
  d=$(echo $spec | cut -d' ' -f6); ta=$(echo $spec | cut -d' ' -f7); tb=$(echo $spec | cut -d' ' -f8)
  printf "%d %d %d %d\n" $b $m $n $k > /tmp/ns_$name.txt
  for r in 1 2 3 4 5 6; do
    for v in clean118 n1 n3; do
      t=$(runspec $v $name $d $ta $tb)
      echo "$name $r $v $t" >> /home/developer/bmms_v3/ns_res.txt
    done
  done
done
echo DONE > /tmp/ns_done
