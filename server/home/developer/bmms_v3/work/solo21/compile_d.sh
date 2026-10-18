set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s21d/build
test ! -d solo17_data/diagnostic_21d
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s21d/
test "$(sha256sum variants/s21d/kernel.asc | cut -d ' ' -f 1)" = 00601d4b917ad487200cc7907e6a6adfdbf76d9a820bb8a8e6c47df56f2c272d
cmake -S variants/s21d -B variants/s21d/build >variants/s21d/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s21d/build -j2 >>variants/s21d/build.log 2>&1' >solo17_data/compiler21_d.log 2>&1 < /dev/null &
echo "s21d COMPILE ONLY PID $!"
