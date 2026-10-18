set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d solo17_data/diagnostic_23a
test ! -d solo17_data/pilot23_a_parent_base
test ! -d solo17_data/pilot23_base_parent_a
nohup bash -c 'while test -e /proc/296799 || test -e /proc/297179; do sleep 2; done; cd /home/developer/bmms_v3; test -x variants/s23a/build/bench_cases && test -x variants/s23a/build/bench && test -x variants/s23a/build/bench_multi && grep -q "PASS generated96" solo17_data/gen_pair23.log && python3 work/solo23/run_a_pilot.py' >solo17_data/run23_a_pilot.log 2>&1 < /dev/null &
echo "s23a pilot wrapper PID $!"
