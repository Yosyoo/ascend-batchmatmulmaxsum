set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
if kill -0 466574 2>/dev/null; then exit 1; fi
test ! -d solo17_data/diagnostic_23p
test ! -f variants/s23p/build_compile1.log
test "$(sha256sum variants/s23p/kernel.asc | cut -d ' ' -f 1)" = 85442c9f4b20afc32df5d857926330379ddb049203047706e9a5e61660032c33
cp variants/s23p/kernel.asc variants/s23p/kernel_compile1.asc
cp variants/s23p/build.log variants/s23p/build_compile1.log
test "$(sha256sum variants/s23p/kernel_corrected.asc | cut -d ' ' -f 1)" = 46d3e48b265ba4cd87aa5cedf49a9c31c56200b7f12bc8004ab10922ceb63b30
cp variants/s23p/kernel_corrected.asc variants/s23p/kernel.asc
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23p/build -j2 >variants/s23p/build.log 2>&1' >solo17_data/compiler23_p_retry.log 2>&1 < /dev/null &
echo "P retry compiler $!"
