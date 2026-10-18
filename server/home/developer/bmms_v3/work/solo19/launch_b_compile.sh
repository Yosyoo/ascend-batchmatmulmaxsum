set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s19b/build
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s19b/
sha256sum variants/s19b/kernel.asc
cmake -S variants/s19b -B variants/s19b/build >variants/s19b/build.log 2>&1
nohup cmake --build variants/s19b/build -j2 >>variants/s19b/build.log 2>&1 < /dev/null &
echo "s19b compile PID $! (no NPU task launched)"
