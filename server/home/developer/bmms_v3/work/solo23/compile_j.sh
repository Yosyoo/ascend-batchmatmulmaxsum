set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23j/build
test ! -d solo17_data/diagnostic_23j
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23j/
test "$(sha256sum variants/s23j/kernel.asc | cut -d ' ' -f 1)" = d1ef4d7627fa77b8bf9edcc50558a6a0dcace5d32462321320d392bb152f5437
cmake -S variants/s23j -B variants/s23j/build >variants/s23j/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23j/build -j2 >>variants/s23j/build.log 2>&1' >solo17_data/compiler23_j.log 2>&1 < /dev/null &
echo "s23j COMPILE ONLY PID $!"
