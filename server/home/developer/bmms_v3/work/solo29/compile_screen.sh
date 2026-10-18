set -eu
cd /home/developer/bmms_v3
v="$1"
expected="$2"
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d "variants/$v/build"
test "$(sha256sum "variants/$v/kernel.asc" | cut -d ' ' -f 1)" = "$expected"
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h "variants/$v/"
cmake -S "variants/$v" -B "variants/$v/build"
cmake --build "variants/$v/build" --target bench_cases bench_multi -j2
echo "COMPILE29_SCREEN_COMPLETE $v"
