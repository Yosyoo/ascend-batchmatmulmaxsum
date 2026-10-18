set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23f/build
test ! -d solo17_data/diagnostic_23f
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23f/
test "$(sha256sum variants/s23f/kernel.asc | cut -d ' ' -f 1)" = 550bcc0de7aba9d5d524856a446aa98cc567db62ee39300701ad9c3acffa1abe
cmake -S variants/s23f -B variants/s23f/build >variants/s23f/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23f/build -j2 >>variants/s23f/build.log 2>&1' >solo17_data/compiler23_f.log 2>&1 < /dev/null &
echo "s23f COMPILE ONLY PID $!"
