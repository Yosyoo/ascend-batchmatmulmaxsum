set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e /proc/297435
test ! -d solo17_data/diagnostic_23b
test ! -d solo17_data/pilot23_b_parent_base
test ! -d solo17_data/pilot23_base_parent_b
nohup bash -c 'while test -e /proc/307014; do sleep 2; done; cd /home/developer/bmms_v3; test -x variants/s23b/build/bench_cases && test -x variants/s23b/build/bench && test -x variants/s23b/build/bench_multi && python3 work/solo23/run_b_pilot.py' >solo17_data/run23_b_pilot.log 2>&1 < /dev/null &
echo "s23b pilot wrapper PID $!"
