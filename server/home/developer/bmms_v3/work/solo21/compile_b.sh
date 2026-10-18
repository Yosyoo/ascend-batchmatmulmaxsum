set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s21b/build
test ! -d solo17_data/diagnostic_21b
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s21b/
test "$(sha256sum variants/s21b/kernel.asc | cut -d ' ' -f 1)" = d6dcc4e678a83c1b408ae8bd5079181d534a41f2f0f7085e0eabda2c13b5a536
cmake -S variants/s21b -B variants/s21b/build >variants/s21b/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s21b/build -j2 >>variants/s21b/build.log 2>&1' >solo17_data/compiler21_b.log 2>&1 < /dev/null &
echo "s21b COMPILE ONLY PID $!"
