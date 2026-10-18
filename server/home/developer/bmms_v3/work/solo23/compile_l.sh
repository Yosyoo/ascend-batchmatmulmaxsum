set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23l/build
test ! -d solo17_data/diagnostic_23l
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23l/
test "$(sha256sum variants/s23l/kernel.asc | cut -d ' ' -f 1)" = 8580a0d276ed97d1dcc8d30bb18b0b13413b659256d25c49a1cda10ae7da49e9
cmake -S variants/s23l -B variants/s23l/build >variants/s23l/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23l/build -j2 >>variants/s23l/build.log 2>&1' >solo17_data/compiler23_l.log 2>&1 < /dev/null &
echo "s23l COMPILE ONLY PID $!"
