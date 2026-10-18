#!/bin/bash
# 对真实 15 点做换序 A/B：每个形状用各自的 dtype/ta/tb 单独测
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID=0
VA=$1; VB=$2; TAG=$3
FLAGS=( "1 0 0" "2 1 0" "1 0 1" "2 1 1" "1 0 0" "2 0 1" "1 1 0" "2 1 1" "1 0 1" "2 0 0" "1 1 1" "2 1 0" "1 0 0" "2 0 1" "1 1 1" )
i=0
runone(){ V=$1; idx=$2; spec=$3; set -- ${FLAGS[$idx]}
  printf "%d %d %d %d\n" $spec > /tmp/ab15.txt
  timeout 200 python3 harness/multi.py $V /tmp/ab15.txt 20 $1 $2 $3 2>/dev/null \
    | python3 -c "import sys,json;print('%.4f'%json.load(sys.stdin)['shapes'][0]['warm_median'])" 2>/dev/null || echo FAIL; }
: > /home/developer/bmms_v3/ab15_$TAG.txt
while read a b c d; do
  ra=$(runone $VA $i "$a $b $c $d")
  rb=$(runone $VB $i "$a $b $c $d")
  echo "$i $ra $rb" >> /home/developer/bmms_v3/ab15_$TAG.txt
  i=$((i+1))
done < exact15_shapes.txt
