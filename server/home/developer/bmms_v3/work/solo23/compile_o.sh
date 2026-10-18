set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23o/build
test ! -d solo17_data/diagnostic_23o
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23o/
test "$(sha256sum variants/s23o/kernel.asc | cut -d ' ' -f 1)" = c1363aef7224cf29b98e428786040dd746dec302d9f2e832ad8dd62a64f89757
cmake -S variants/s23o -B variants/s23o/build >variants/s23o/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23o/build -j2 >>variants/s23o/build.log 2>&1' >solo17_data/compiler23_o.log 2>&1 < /dev/null &
echo "s23o COMPILE ONLY PID $!"
