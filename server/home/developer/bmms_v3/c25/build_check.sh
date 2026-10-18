#!/bin/bash
set -e
bmms_variant="$1"
bmms_dir="/home/developer/bmms_v3/variants/$bmms_variant"
mkdir -p "$bmms_dir"
cp /home/developer/bmms_v3/harness/{bench.asc,bench_multi.asc,CMakeLists.txt,data_utils.h} "$bmms_dir/"
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
cmake -S "$bmms_dir" -B "$bmms_dir/build" > "$bmms_dir/build.log" 2>&1
cmake --build "$bmms_dir/build" --target bench -j8 >> "$bmms_dir/build.log" 2>&1
echo "BUILT_CHECK $bmms_variant"
