set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s19h/build
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s19h/
test "$(sha256sum variants/s19h/kernel.asc | cut -d ' ' -f 1)" = c99dc172435c5f4ee2955b537f4da22e1e3495d9d9843c0c5827b99a57e9409f
cmake -S variants/s19h -B variants/s19h/build >variants/s19h/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s19h/build -j2 >>variants/s19h/build.log 2>&1' >solo17_data/compiler19_h.log 2>&1 < /dev/null &
echo "s19h COMPILE ONLY PID $!"
