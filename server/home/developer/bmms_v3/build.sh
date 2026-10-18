#!/bin/bash
# build.sh <variant>  -- build a variant dir under variants/
set -e
V="$1"
D=/home/developer/bmms_v3/variants/$V
mkdir -p "$D"
cp -f /home/developer/bmms_v3/harness/{bench.asc,bench_multi.asc,CMakeLists.txt,data_utils.h} "$D/"
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
cmake -S "$D" -B "$D/build" > "$D/build.log" 2>&1
cmake --build "$D/build" -j8 >> "$D/build.log" 2>&1
echo "BUILT $V"
