set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
flock -n solo17_data/.npu_serial.lock true
test ! -d variants/s20d/build
test ! -d solo17_data/diagnostic_20d
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s20d/
test "$(sha256sum variants/s20d/kernel.asc | cut -d ' ' -f 1)" = b046e86c17b13a7b7af86cf865afe3e3f71bf269615f6dce33c21fa0e4ee020a
cmake -S variants/s20d -B variants/s20d/build >variants/s20d/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s20d/build -j2 >>variants/s20d/build.log 2>&1' >solo17_data/compiler20_d.log 2>&1 < /dev/null &
echo "s20d COMPILE ONLY PID $!"
