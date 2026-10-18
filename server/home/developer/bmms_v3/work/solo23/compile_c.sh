set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23c/build
test ! -d solo17_data/diagnostic_23c
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23c/
test "$(sha256sum variants/s23c/kernel.asc | cut -d ' ' -f 1)" = 44b93c8f5d864c1a2caab02d71d4696ae73be7c3ebc52414ab65d0ea3f789e2f
cmake -S variants/s23c -B variants/s23c/build >variants/s23c/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23c/build -j2 >>variants/s23c/build.log 2>&1' >solo17_data/compiler23_c.log 2>&1 < /dev/null &
echo "s23c COMPILE ONLY PID $!"
