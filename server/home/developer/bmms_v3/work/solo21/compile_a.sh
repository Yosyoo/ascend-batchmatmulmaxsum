set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s21a/build
test ! -d solo17_data/diagnostic_21a
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s21a/
test "$(sha256sum variants/s21a/kernel.asc | cut -d ' ' -f 1)" = 0bced8bd0556b8d2bde4055a94e981f9dd95e7f1bffb3f101b2b94f501cc6dc4
cmake -S variants/s21a -B variants/s21a/build >variants/s21a/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s21a/build -j2 >>variants/s21a/build.log 2>&1' >solo17_data/compiler21_a.log 2>&1 < /dev/null &
echo "s21a COMPILE ONLY PID $!"
