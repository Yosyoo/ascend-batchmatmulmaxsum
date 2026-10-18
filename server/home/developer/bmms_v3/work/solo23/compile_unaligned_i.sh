set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e /proc/364882
test ! -e variants/s23i/bench_unaligned.asc
cp work/solo23/bench_unaligned.asc variants/s23i/
cp variants/s23i/CMakeLists.txt work/solo23/CMake_s23i_original.txt
cp work/solo23/CMake_unaligned.txt variants/s23i/CMakeLists.txt
cmake -S variants/s23i -B variants/s23i/build >variants/s23i/unaligned_build.log 2>&1
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23i/build --target bench_unaligned -j1 >>variants/s23i/unaligned_build.log 2>&1' >solo17_data/compiler23_i_unaligned.log 2>&1 < /dev/null &
echo "s23i UNALIGNED HARNESS COMPILE PID $!"
