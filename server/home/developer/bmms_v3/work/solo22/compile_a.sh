set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s22a/build
test ! -d solo17_data/diagnostic_22a
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s22a/
test "$(sha256sum variants/s22a/kernel.asc | cut -d ' ' -f 1)" = ac2be87e7efdf9e50aa7d923b8d14bada8ebd2dc461945203746ed62b006e0ca
cmake -S variants/s22a -B variants/s22a/build >variants/s22a/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s22a/build -j2 >>variants/s22a/build.log 2>&1' >solo17_data/compiler22_a.log 2>&1 < /dev/null &
echo "s22a COMPILE ONLY PID $!"
