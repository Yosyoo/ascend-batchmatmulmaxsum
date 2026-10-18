set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
flock -n solo17_data/.npu_serial.lock true
test ! -d variants/s20c/build
test ! -d solo17_data/diagnostic_20c
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s20c/
test "$(sha256sum variants/s20c/kernel.asc | cut -d ' ' -f 1)" = e3b429c07ee8a2d133151a4ee6c09f1621d5d82dc207560da4a1f7152c38ee8d
cmake -S variants/s20c -B variants/s20c/build >variants/s20c/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s20c/build -j2 >>variants/s20c/build.log 2>&1' >solo17_data/compiler20_c.log 2>&1 < /dev/null &
echo "s20c COMPILE ONLY PID $!"
