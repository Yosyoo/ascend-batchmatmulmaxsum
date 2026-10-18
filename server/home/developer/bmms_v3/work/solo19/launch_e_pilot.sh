set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s19e/build
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s19e/
test "$(sha256sum variants/s19e/kernel.asc | cut -d ' ' -f 1)" = 61e8175ca89e442e66361848125e7ef26bee1f76b3de9e2ab0a9441a42549c84
cmake -S variants/s19e -B variants/s19e/build >variants/s19e/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s19e/build -j2 >>variants/s19e/build.log 2>&1 && python3 work/solo19/run_e_pilot.py >solo17_data/run19_e_pilot.log 2>&1' >solo17_data/launcher19_e.log 2>&1 < /dev/null &
echo "s19e PID $!"
