set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d work/solo22/probe_fulla/build
cmake -S work/solo22/probe_fulla -B work/solo22/probe_fulla/build >work/solo22/probe_fulla/build.log 2>&1
cmake --build work/solo22/probe_fulla/build -j2 >>work/solo22/probe_fulla/build.log 2>&1
work/solo22/probe_fulla/build/tiling_pair_probe >work/solo22/probe_fulla/results.jsonl
wc -l work/solo22/probe_fulla/results.jsonl
