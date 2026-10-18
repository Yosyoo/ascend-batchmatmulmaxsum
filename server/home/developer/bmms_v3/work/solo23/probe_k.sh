set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d work/solo23/probe_k/build
cmake -S work/solo23/probe_k -B work/solo23/probe_k/build >work/solo23/probe_k/build.log 2>&1
cmake --build work/solo23/probe_k/build -j2 >>work/solo23/probe_k/build.log 2>&1
work/solo23/probe_k/build/tiling_pair_probe >work/solo23/probe_k/results.jsonl
wc -l work/solo23/probe_k/results.jsonl
