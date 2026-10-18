set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test "$(sha256sum variants/s30p/kernel.asc | cut -d ' ' -f 1)" = 27bdef5b733320408f9179c8de1b74ee9b36df9801214d47c10bb2310fc1941c
cmake --build variants/s30p/build --target bench -j2
echo BUILD30_P_BENCH_COMPLETE
