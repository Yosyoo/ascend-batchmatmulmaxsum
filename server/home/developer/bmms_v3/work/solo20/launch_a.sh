set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
flock -n solo17_data/.npu_serial.lock true
test ! -d variants/s20a/build
test ! -d solo17_data/diagnostic_20a
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s20a/
test "$(sha256sum variants/s20a/kernel.asc | cut -d ' ' -f 1)" = b4141a3e0bd792a6f953454924af68bcb4e49e7b195c4f74892b98de8d162f6c
cmake -S variants/s20a -B variants/s20a/build >variants/s20a/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s20a/build -j2 >>variants/s20a/build.log 2>&1 && python3 work/solo20/run_a_final.py >solo17_data/run20_a_final.log 2>&1' >solo17_data/compiler20_a.log 2>&1 < /dev/null &
echo "s20a COMPILE AND FINAL PID $!"
