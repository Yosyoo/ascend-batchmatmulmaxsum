set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
cp variants/s17i/bench.asc variants/s17i/bench_cases.asc variants/s17i/bench_multi.asc variants/s17i/CMakeLists.txt variants/s17i/data_utils.h variants/s17j/
sha256sum variants/s17j/kernel.asc
cmake -S variants/s17j -B variants/s17j/build >variants/s17j/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s17j/build -j2 >>variants/s17j/build.log 2>&1 && python3 work/solo18/run_j_final.py >solo17_data/run_j_final.log 2>&1' >solo17_data/j_launcher.log 2>&1 < /dev/null &
echo "s17j PID $!"
nohup python3 work/solo17/scan.py layout_ig s17i,s17g 1_1280_4096_1536_2_0_0 1_1280_4096_1536_2_1_0 1_1024_4096_1536_2_0_0 1_1024_4096_1536_2_1_0 >solo17_data/layout_ig.log 2>&1 < /dev/null &
echo "layout reverse PID $!"
