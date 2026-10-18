set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23a/build
test ! -d solo17_data/diagnostic_23a
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23a/
test "$(sha256sum variants/s23a/kernel.asc | cut -d ' ' -f 1)" = 191da66c6b2b0c375f64fc986494a353eb4db65b31c7cfa9c0e6dcb67861d73e
cmake -S variants/s23a -B variants/s23a/build >variants/s23a/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23a/build -j2 >>variants/s23a/build.log 2>&1' >solo17_data/compiler23_a.log 2>&1 < /dev/null &
echo "s23a COMPILE ONLY PID $!"
