set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d work/solo21/probe_d/build
cmake -S work/solo21/probe_d -B work/solo21/probe_d/build >work/solo21/probe_d/build.log 2>&1
cmake --build work/solo21/probe_d/build -j2 >>work/solo21/probe_d/build.log 2>&1
work/solo21/probe_d/build/tiling_pair_probe >work/solo21/probe_d/results.jsonl
wc -l work/solo21/probe_d/results.jsonl
