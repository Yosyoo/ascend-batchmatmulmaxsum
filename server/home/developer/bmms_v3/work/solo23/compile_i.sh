set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23i/build
test ! -d solo17_data/diagnostic_23i
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23i/
test "$(sha256sum variants/s23i/kernel.asc | cut -d ' ' -f 1)" = be327461b89963ee31f33989983c41522b40e0d4e056f9d470fae0f45931b8df
cmake -S variants/s23i -B variants/s23i/build >variants/s23i/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23i/build -j2 >>variants/s23i/build.log 2>&1' >solo17_data/compiler23_i.log 2>&1 < /dev/null &
echo "s23i COMPILE ONLY PID $!"
