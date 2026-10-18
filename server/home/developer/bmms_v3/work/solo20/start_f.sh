set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d solo17_data/diagnostic_20f
test ! -f solo17_data/run20_f_final.log
nohup bash -c 'cd /home/developer/bmms_v3; while kill -0 231795 2>/dev/null || kill -0 230318 2>/dev/null; do sleep 2; done; grep -q "PASS s20e complete" solo17_data/run20_e_final.log && test "$(grep -c "Built target" variants/s20f/build.log)" = 3 && flock -n solo17_data/.npu_serial.lock true && python3 work/solo20/run_f_final.py' >solo17_data/run20_f_final.log 2>&1 < /dev/null &
echo "s20f waiting E complete and compile then FULL validation PID $!"
