set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23n/build
test ! -d solo17_data/diagnostic_23n
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23n/
test "$(sha256sum variants/s23n/kernel.asc | cut -d ' ' -f 1)" = 14e796a1ea878af21b96933f73a2b79186770e6a406f8b495be0e4af8f67c97f
cmake -S variants/s23n -B variants/s23n/build >variants/s23n/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23n/build -j2 >>variants/s23n/build.log 2>&1' >solo17_data/compiler23_n.log 2>&1 < /dev/null &
echo "s23n COMPILE ONLY PID $!"
