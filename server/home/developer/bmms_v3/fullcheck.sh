#!/bin/bash
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
export BMMS_DEVICE_ID=0
V=$1
S="1_1_1_32 2_3_7_40 3_17_19_72 1_32_32_32 1_64_64_64 1_16_16_16 1_33_65_72 1_32_48_32 1_100_100_100 1_17_17_32 2_64_32_128 1_65_129_128 1_163_163_163"
for sh in $S; do
  for lay in 1_0_0 1_0_1 1_1_0 1_1_1 2_0_0 2_1_1; do
    python3 harness/dbgtest.py $V ${sh}_${lay} | head -1
  done
done
S2="1_129_257_256 4_256_256_128 1_512_512_512 1_16_8192_64 1_8192_17_32 1_256_4096_1024"
for sh in $S2; do
  for lay in 1_0_0 1_1_1 2_0_0 2_1_1; do
    python3 harness/dbgtest.py $V ${sh}_${lay} | head -1
  done
done
