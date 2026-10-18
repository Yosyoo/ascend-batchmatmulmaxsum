set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s19c/build
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s19c/
test "$(sha256sum variants/s19c/kernel.asc | cut -d ' ' -f 1)" = 7266fd43e903656a57539a0a5d0753c482b48b302a41e2bef844ec912a4690c2
cmake -S variants/s19c -B variants/s19c/build >variants/s19c/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s19c/build -j2 >>variants/s19c/build.log 2>&1 && python3 work/solo19/run_c_pilot.py >solo17_data/run19_c_pilot.log 2>&1' >solo17_data/launcher19_c.log 2>&1 < /dev/null &
echo "s19c PID $!"
