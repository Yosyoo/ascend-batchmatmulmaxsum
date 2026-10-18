set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
cp variants/s17j/bench.asc variants/s17j/bench_cases.asc variants/s17j/bench_multi.asc variants/s17j/CMakeLists.txt variants/s17j/data_utils.h variants/s17k/
sha256sum variants/s17k/kernel.asc
cmake -S variants/s17k -B variants/s17k/build >variants/s17k/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s17k/build -j2 >>variants/s17k/build.log 2>&1 && python3 work/solo18/gen_k_cases.py >solo17_data/gen_k_cases.log 2>&1 && python3 work/solo18/run_k_final.py >solo17_data/run_k_final.log 2>&1' >solo17_data/k_launcher.log 2>&1 < /dev/null &
echo "s17k PID $!"
