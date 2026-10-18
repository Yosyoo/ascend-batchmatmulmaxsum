set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s20e/build
test ! -d solo17_data/diagnostic_20e
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s20e/
test "$(sha256sum variants/s20e/kernel.asc | cut -d ' ' -f 1)" = 2458dd18843d9de805968ffd61ccaa56c7d3687768374bc18424131901aae5f1
cmake -S variants/s20e -B variants/s20e/build >variants/s20e/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s20e/build -j2 >>variants/s20e/build.log 2>&1' >solo17_data/compiler20_e.log 2>&1 < /dev/null &
echo "s20e COMPILE ONLY PID $!"
