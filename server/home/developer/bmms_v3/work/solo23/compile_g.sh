set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23g/build
test ! -d solo17_data/diagnostic_23g
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23g/
test "$(sha256sum variants/s23g/kernel.asc | cut -d ' ' -f 1)" = 6cf472846e3f623a5b0e3acc47f6c2b62f52e0ca0db22065c19f18444dbe0406
cmake -S variants/s23g -B variants/s23g/build >variants/s23g/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23g/build -j2 >>variants/s23g/build.log 2>&1' >solo17_data/compiler23_g.log 2>&1 < /dev/null &
echo "s23g COMPILE ONLY PID $!"
