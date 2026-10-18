set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test "$(sha256sum variants/s19h/kernel.asc | cut -d ' ' -f 1)" = c99dc172435c5f4ee2955b537f4da22e1e3495d9d9843c0c5827b99a57e9409f
grep -q 'PASS s19f pilot only' solo17_data/run19_f_pilot.log
if kill -0 168947 2>/dev/null; then echo 'Previous complete experiment runner remains active'; exit 1; fi
test ! -d solo17_data/diagnostic_19h
grep -q 'Built target bench_multi' variants/s19h/build.log
grep -q 'Built target bench_cases' variants/s19h/build.log
grep -q 'Built target bench$' variants/s19h/build.log
flock -n solo17_data/.npu_serial.lock true
nohup python3 work/solo19/run_h_pilot.py >solo17_data/run19_h_pilot.log 2>&1 < /dev/null &
echo "s19h PILOT PID $!"
