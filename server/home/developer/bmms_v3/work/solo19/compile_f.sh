set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s19f/build
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s19f/
test "$(sha256sum variants/s19f/kernel.asc | cut -d ' ' -f 1)" = da69df97529ad80885a26c428b04146576bfd63a1cc43354a782fb611e13d9a1
cmake -S variants/s19f -B variants/s19f/build >variants/s19f/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s19f/build -j2 >>variants/s19f/build.log 2>&1' >solo17_data/compiler19_f.log 2>&1 < /dev/null &
echo "s19f COMPILE ONLY PID $!"
