set -eu
cd /home/developer/bmms_v3
v="$1"
expected="$2"
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d "variants/$v/build"
test "$(sha256sum "variants/$v/kernel.asc" | cut -d ' ' -f 1)" = "$expected"
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h "variants/$v/"
cmake -S "variants/$v" -B "variants/$v/build"
cmake --build "variants/$v/build" --target bench_cases -j1 >"solo17_data/compile31_${v}_cases.log" 2>&1 &
case_pid=$!
cmake --build "variants/$v/build" --target bench_multi -j1 >"solo17_data/compile31_${v}_multi.log" 2>&1 &
multi_pid=$!
wait "$case_pid"
wait "$multi_pid"
echo "COMPILE31_SCREEN_COMPLETE $v"
