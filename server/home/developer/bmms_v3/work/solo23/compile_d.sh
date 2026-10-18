set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23d/build
test ! -d solo17_data/diagnostic_23d
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23d/
test "$(sha256sum variants/s23d/kernel.asc | cut -d ' ' -f 1)" = f0aab8ebf32d2f71314baadc98359ed18e0ab42177e99aaf2a153de9ba886a5b
cmake -S variants/s23d -B variants/s23d/build >variants/s23d/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23d/build -j2 >>variants/s23d/build.log 2>&1' >solo17_data/compiler23_d.log 2>&1 < /dev/null &
echo "s23d COMPILE ONLY PID $!"
