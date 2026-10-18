set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s19i/build
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s19i/
test "$(sha256sum variants/s19i/kernel.asc | cut -d ' ' -f 1)" = 314d61425771496515f98d3668d9559af1d6fcdab9df2e04f0a6dcc86e103a7f
cmake -S variants/s19i -B variants/s19i/build >variants/s19i/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s19i/build -j2 >>variants/s19i/build.log 2>&1' >solo17_data/compiler19_i.log 2>&1 < /dev/null &
echo "s19i COMPILE ONLY PID $!"
