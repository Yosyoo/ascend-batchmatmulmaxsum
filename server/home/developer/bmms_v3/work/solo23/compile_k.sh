set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23k/build
test ! -d solo17_data/diagnostic_23k
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23k/
test "$(sha256sum variants/s23k/kernel.asc | cut -d ' ' -f 1)" = 91d3fe0fb7b557433619e7af0cbf6c7bacf1a49d4cdb619441b25e2eb2759e83
cmake -S variants/s23k -B variants/s23k/build >variants/s23k/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23k/build -j2 >>variants/s23k/build.log 2>&1' >solo17_data/compiler23_k.log 2>&1 < /dev/null &
echo "s23k COMPILE ONLY PID $!"
