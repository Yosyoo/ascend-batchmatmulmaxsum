set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23p/build
test ! -d solo17_data/diagnostic_23p
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23p/
test "$(sha256sum variants/s23p/kernel.asc | cut -d ' ' -f 1)" = 85442c9f4b20afc32df5d857926330379ddb049203047706e9a5e61660032c33
cmake -S variants/s23p -B variants/s23p/build >variants/s23p/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23p/build -j2 >>variants/s23p/build.log 2>&1' >solo17_data/compiler23_p.log 2>&1 < /dev/null &
echo "s23p COMPILE ONLY PID $!"
