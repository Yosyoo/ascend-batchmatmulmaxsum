set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e /proc/317502
test ! -e /proc/317573
test ! -e /proc/307628
test ! -d solo17_data/diagnostic_23c
test ! -d solo17_data/pilot23_c_parent_base
test ! -d solo17_data/pilot23_base_parent_c
grep -q 'PASS generated96 immutable validation fixtures' solo17_data/gen_kparallel23.log
test -x variants/s23c/build/bench_cases
test -x variants/s23c/build/bench
test -x variants/s23c/build/bench_multi
nohup python3 work/solo23/run_c_pilot.py >solo17_data/run23_c_pilot.log 2>&1 < /dev/null &
echo "s23c pilot wrapper PID $!"
