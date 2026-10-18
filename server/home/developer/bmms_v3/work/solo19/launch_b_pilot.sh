set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
grep -q 'Built target bench$' variants/s19b/build.log
grep -q 'Built target bench_cases$' variants/s19b/build.log
grep -q 'Built target bench_multi$' variants/s19b/build.log
grep -q 'PASS s19a pilot only' solo17_data/run19_a_pilot.log
test ! -f solo17_data/run19_b_pilot.log
nohup python3 work/solo19/run_b_pilot.py >solo17_data/run19_b_pilot.log 2>&1 < /dev/null &
echo "s19b pilot PID $!"
