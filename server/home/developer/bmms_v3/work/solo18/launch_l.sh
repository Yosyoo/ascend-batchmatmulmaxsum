set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s17l/build
cp variants/s17j/bench.asc variants/s17j/bench_cases.asc variants/s17j/bench_multi.asc variants/s17j/CMakeLists.txt variants/s17j/data_utils.h variants/s17l/
sha256sum variants/s17l/kernel.asc
cmake -S variants/s17l -B variants/s17l/build >variants/s17l/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s17l/build -j2 >>variants/s17l/build.log 2>&1 && python3 work/solo18/run_l_pilot.py >solo17_data/run_l_pilot.log 2>&1' >solo17_data/l_launcher.log 2>&1 < /dev/null &
echo "s17l PID $!"
