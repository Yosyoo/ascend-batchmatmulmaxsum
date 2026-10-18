set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23q/build
test ! -d solo17_data/diagnostic_23q
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23q/
test "$(sha256sum variants/s23q/kernel.asc | cut -d ' ' -f 1)" = 5424920e2603672cb9a00b611499a00fb41f37ee70d987c1224e6482f29a6888
cmake -S variants/s23q -B variants/s23q/build >variants/s23q/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23q/build -j2 >>variants/s23q/build.log 2>&1' >solo17_data/compiler23_q.log 2>&1 < /dev/null &
echo "s23q COMPILE ONLY PID $!"
