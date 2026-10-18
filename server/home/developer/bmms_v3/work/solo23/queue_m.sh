set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d solo17_data/diagnostic_23m
for attempt in $(seq 1 240); do
    if ! kill -0 404558 2>/dev/null && ! kill -0 422343 2>/dev/null; then
        test -x variants/s23m/build/bench
        test -x variants/s23m/build/bench_cases
        exec python3 -u work/solo23/run_m_pilot.py
    fi
    sleep 5
done
echo "Entire L runner or M compiler still alive; M not executed" >&2
exit 1
