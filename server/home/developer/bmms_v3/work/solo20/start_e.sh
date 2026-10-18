set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d solo17_data/diagnostic_20e
test ! -f solo17_data/run20_e_final.log
grep -q 'PASS s20d complete' solo17_data/run20_d_final.log
nohup bash -c 'cd /home/developer/bmms_v3; while kill -0 228313 2>/dev/null; do sleep 2; done; test "$(grep -c "Built target" variants/s20e/build.log)" = 3 && flock -n solo17_data/.npu_serial.lock true && python3 work/solo20/run_e_final.py' >solo17_data/run20_e_final.log 2>&1 < /dev/null &
echo "s20e waiting compile then FULL validation PID $!"
