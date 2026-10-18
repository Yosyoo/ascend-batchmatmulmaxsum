set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test "$(sha256sum variants/s19f/kernel.asc | cut -d ' ' -f 1)" = da69df97529ad80885a26c428b04146576bfd63a1cc43354a782fb611e13d9a1
grep -q 'PASS s19e pilot only' solo17_data/run19_e_pilot.log
if kill -0 147731 2>/dev/null; then echo 'Previous complete experiment runner remains active'; exit 1; fi
test ! -d solo17_data/diagnostic_19f
grep -q 'Built target bench_multi' variants/s19f/build.log
grep -q 'Built target bench_cases' variants/s19f/build.log
grep -q 'Built target bench$' variants/s19f/build.log
flock -n solo17_data/.npu_serial.lock true
nohup python3 work/solo19/run_f_pilot.py >solo17_data/run19_f_pilot.log 2>&1 < /dev/null &
echo "s19f PILOT PID $!"
