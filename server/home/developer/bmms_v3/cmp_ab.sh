#!/bin/bash
# 换序重复对照: cmp_ab.sh <va> <vb>   (SHAPEFILE, ITERS 可覆盖)
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID=0
A=$1; B=$2; F=${SHAPEFILE:-shapes_pool2.txt}; N=${ITERS:-20}
mkdir -p /home/developer/bmms_v3/o_cmp
echo "== order A: $A then $B"
python3 harness/multi.py $A $F $N 2>/dev/null > o_cmp/A_$A.json
python3 harness/multi.py $B $F $N 2>/dev/null > o_cmp/A_$B.json
echo "== order B: $B then $A"
python3 harness/multi.py $B $F $N 2>/dev/null > o_cmp/B_$B.json
python3 harness/multi.py $A $F $N 2>/dev/null > o_cmp/B_$A.json
echo DONE
