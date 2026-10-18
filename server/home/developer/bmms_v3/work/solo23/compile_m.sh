set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23m/build
test ! -d solo17_data/diagnostic_23m
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23m/
test "$(sha256sum variants/s23m/kernel.asc | cut -d ' ' -f 1)" = ef5af43ab8fba85dd4dfd2e93c7aa982260597b72c5186165dcb1c434348f695
cmake -S variants/s23m -B variants/s23m/build >variants/s23m/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23m/build -j2 >>variants/s23m/build.log 2>&1' >solo17_data/compiler23_m.log 2>&1 < /dev/null &
echo "s23m COMPILE ONLY PID $!"
