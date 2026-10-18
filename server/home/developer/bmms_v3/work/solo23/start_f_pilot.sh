set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e /proc/328006
test ! -e /proc/336954
test ! -e /proc/334317
test ! -e /proc/336683
test ! -d solo17_data/diagnostic_23f
test ! -d solo17_data/pilot23_f_parent_base
test ! -d solo17_data/pilot23_base_parent_f
grep -q 'PASS s23d reverse30 completed' solo17_data/run23_d_reverse.log
grep -q 'PASS generated96 immutable validation fixtures' solo17_data/gen_balanced23.log
nohup bash -c 'while test -e /proc/341175; do sleep 2; done; cd /home/developer/bmms_v3; test -x variants/s23f/build/bench_cases && test -x variants/s23f/build/bench && test -x variants/s23f/build/bench_multi && python3 work/solo23/run_f_pilot.py' >solo17_data/run23_f_pilot.log 2>&1 < /dev/null &
echo "s23f pilot wrapper PID $!"
