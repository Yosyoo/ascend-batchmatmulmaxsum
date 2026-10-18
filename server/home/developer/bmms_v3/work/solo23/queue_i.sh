set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d solo17_data/diagnostic_23i
test -x variants/s23i/build/bench
test -x variants/s23i/build/bench_cases
for attempt in $(seq 1 180); do
    if ! kill -0 364963 2>/dev/null; then
        exec python3 -u work/solo23/run_i_pilot.py
    fi
    sleep 5
done
echo "Previous entire NPU runner still alive; I not executed" >&2
exit 1
