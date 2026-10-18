set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23e/build
test ! -d solo17_data/diagnostic_23e
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23e/
test "$(sha256sum variants/s23e/kernel.asc | cut -d ' ' -f 1)" = 7ab2dc950f023f321d1e2e4cdd5bf37b50e6696e652348b3d61dec070da38337
cmake -S variants/s23e -B variants/s23e/build >variants/s23e/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23e/build -j2 >>variants/s23e/build.log 2>&1' >solo17_data/compiler23_e.log 2>&1 < /dev/null &
echo "s23e COMPILE ONLY PID $!"
