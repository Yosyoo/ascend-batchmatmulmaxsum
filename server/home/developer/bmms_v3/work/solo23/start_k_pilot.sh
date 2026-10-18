set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e /proc/349999
test ! -e /proc/350372
test ! -d solo17_data/diagnostic_23k
test ! -d solo17_data/pilot23_k_parent_base
test ! -d solo17_data/pilot23_base_parent_k
grep -q 'PASS audit completed18' solo17_data/run23_cancel_m_audit.log
grep -q 'PASS generated96 immutable validation fixtures' solo17_data/gen_balanced23.log
nohup bash -c 'while test -e /proc/350770; do sleep 2; done; cd /home/developer/bmms_v3; test -x variants/s23k/build/bench_cases && test -x variants/s23k/build/bench && test -x variants/s23k/build/bench_multi && python3 work/solo23/run_g_pilot.py' >solo17_data/run23_k_pilot.log 2>&1 < /dev/null &
echo "s23k pilot wrapper PID $!"
