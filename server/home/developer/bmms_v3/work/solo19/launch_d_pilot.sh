set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s19d/build
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s19d/
test "$(sha256sum variants/s19d/kernel.asc | cut -d ' ' -f 1)" = f9c1276648cf0307ca7ca105a05edfcff36e2a8c2a4e63d92e050746708da54c
cmake -S variants/s19d -B variants/s19d/build >variants/s19d/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s19d/build -j2 >>variants/s19d/build.log 2>&1 && python3 work/solo19/run_d_pilot.py >solo17_data/run19_d_pilot.log 2>&1' >solo17_data/launcher19_d.log 2>&1 < /dev/null &
echo "s19d PID $!"
