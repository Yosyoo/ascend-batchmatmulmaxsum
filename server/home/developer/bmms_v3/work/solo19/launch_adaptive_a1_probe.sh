set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
cmake -S work/solo19/adaptive_a1_probe -B work/solo19/adaptive_a1_probe/build >work/solo19/adaptive_a1_probe/build.log 2>&1
cmake --build work/solo19/adaptive_a1_probe/build -j2 >>work/solo19/adaptive_a1_probe/build.log 2>&1
work/solo19/adaptive_a1_probe/build/tiling_pair_probe >work/solo19/adaptive_a1_probe/results.jsonl
sha256sum work/solo19/adaptive_a1_probe/results.jsonl
