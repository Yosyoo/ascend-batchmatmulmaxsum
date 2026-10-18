set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
flock -n solo17_data/.npu_serial.lock true
test ! -d variants/s20b/build
test ! -d solo17_data/diagnostic_20b
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s20b/
test "$(sha256sum variants/s20b/kernel.asc | cut -d ' ' -f 1)" = d0c2321563e205a69262209ed75fc54d8037f59a39e858acc17f8e675fdb8160
cmake -S variants/s20b -B variants/s20b/build >variants/s20b/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s20b/build -j2 >>variants/s20b/build.log 2>&1 && python3 work/solo20/run_b_final.py >solo17_data/run20_b_final.log 2>&1' >solo17_data/compiler20_b.log 2>&1 < /dev/null &
echo "s20b COMPILE AND FINAL PID $!"
