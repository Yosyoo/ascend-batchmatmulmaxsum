set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d variants/s23b/build
test ! -d solo17_data/diagnostic_23b
cp variants/s17l/bench.asc variants/s17l/bench_cases.asc variants/s17l/bench_multi.asc variants/s17l/CMakeLists.txt variants/s17l/data_utils.h variants/s23b/
test "$(sha256sum variants/s23b/kernel.asc | cut -d ' ' -f 1)" = dd4fe9fcded5e0ee78cf9912690c7bf5dfc7fb78c7777a1c8a2fb920a49214db
cmake -S variants/s23b -B variants/s23b/build >variants/s23b/build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23b/build -j2 >>variants/s23b/build.log 2>&1' >solo17_data/compiler23_b.log 2>&1 < /dev/null &
echo "s23b COMPILE ONLY PID $!"
