set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s20f/build
test ! -d solo17_data/diagnostic_20f
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s20f/
test "$(sha256sum variants/s20f/kernel.asc | cut -d ' ' -f 1)" = 198ee0bb6eca5a4503e734438da20f05a4ad962e5c7d53976b84552190b09f3c
cmake -S variants/s20f -B variants/s20f/build >variants/s20f/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s20f/build -j2 >>variants/s20f/build.log 2>&1' >solo17_data/compiler20_f.log 2>&1 < /dev/null &
echo "s20f COMPILE ONLY PID $!"
