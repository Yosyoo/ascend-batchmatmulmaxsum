set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d solo17_data/diagnostic_22a
test ! -d solo17_data/pilot22_a_d_base
test ! -d solo17_data/pilot22_base_d_a
test ! -e /proc/271551
nohup bash -c 'while test -e /proc/281294; do sleep 2; done; cd /home/developer/bmms_v3; test -x variants/s22a/build/bench_cases && test -x variants/s22a/build/bench && test -x variants/s22a/build/bench_multi && python3 work/solo22/run_a_pilot.py' >solo17_data/run22_a_pilot.log 2>&1 < /dev/null &
echo "s22a pilot wrapper PID $!"
