set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d work/solo23/probe_c/build
cmake -S work/solo23/probe_c -B work/solo23/probe_c/build >work/solo23/probe_c/build.log 2>&1
cmake --build work/solo23/probe_c/build -j2 >>work/solo23/probe_c/build.log 2>&1
work/solo23/probe_c/build/tiling_pair_probe >work/solo23/probe_c/results.jsonl
wc -l work/solo23/probe_c/results.jsonl
