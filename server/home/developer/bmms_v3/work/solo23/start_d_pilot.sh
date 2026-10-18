set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e /proc/318239
test ! -e /proc/327584
test ! -d solo17_data/diagnostic_23d
test ! -d solo17_data/pilot23_d_parent_base
test ! -d solo17_data/pilot23_base_parent_d
grep -q '"passed": true, "observed": 96' solo17_data/run23_c_batch.log
nohup bash -c 'while test -e /proc/327767; do sleep 2; done; cd /home/developer/bmms_v3; test -x variants/s23d/build/bench_cases && test -x variants/s23d/build/bench && test -x variants/s23d/build/bench_multi && python3 work/solo23/run_d_pilot.py' >solo17_data/run23_d_pilot.log 2>&1 < /dev/null &
echo "s23d pilot wrapper PID $!"
