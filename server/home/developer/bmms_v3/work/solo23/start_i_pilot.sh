set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test -x variants/s23i/build/bench
test -x variants/s23i/build/bench_cases
test ! -d solo17_data/diagnostic_23i
nohup python3 -u work/solo23/run_h_pilot.py >solo17_data/run23_i_pilot.log 2>&1 < /dev/null &
echo "s23i PILOT PID $!"
