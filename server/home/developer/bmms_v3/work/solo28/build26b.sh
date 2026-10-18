set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s26b/build
test "$(sha256sum variants/s26b/kernel.asc | cut -d ' ' -f 1)" = 4b214cd4e162bd2c18340e14bffe70376d93d7df3bfb99ceb9e5968bff1060d4
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s26b/
cmake -S variants/s26b -B variants/s26b/build
cmake --build variants/s26b/build -j2
sha256sum variants/s26b/kernel.asc variants/s26b/build/bench variants/s26b/build/bench_cases variants/s26b/build/bench_multi
echo COMPILE26B_COMPLETE
