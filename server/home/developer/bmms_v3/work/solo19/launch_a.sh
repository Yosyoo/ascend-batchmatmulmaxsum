set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s19a/build
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s19a/
sha256sum variants/s19a/kernel.asc
cmake -S variants/s19a -B variants/s19a/build >variants/s19a/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s19a/build -j2 >>variants/s19a/build.log 2>&1 && python3 work/solo19/run_a_pilot.py >solo17_data/run19_a_pilot.log 2>&1' >solo17_data/launcher19_a.log 2>&1 < /dev/null &
echo "s19a PID $!"
