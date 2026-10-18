set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23h/build
test ! -d solo17_data/diagnostic_23h
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23h/
test "$(sha256sum variants/s23h/kernel.asc | cut -d ' ' -f 1)" = f3bedfba72f19e9d51f0b0ea5035647b2f6d54f350c0f5a27a7c1ee5dcb46f28
cmake -S variants/s23h -B variants/s23h/build >variants/s23h/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23h/build -j2 >>variants/s23h/build.log 2>&1' >solo17_data/compiler23_h.log 2>&1 < /dev/null &
echo "s23h COMPILE ONLY PID $!"
