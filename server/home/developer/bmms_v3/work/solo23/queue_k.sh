set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d solo17_data/diagnostic_23k
for attempt in $(seq 1 240); do
    if ! kill -0 385528 2>/dev/null && ! kill -0 383794 2>/dev/null; then
        test -x variants/s23k/build/bench
        test -x variants/s23k/build/bench_cases
        exec python3 -u work/solo23/run_k_pilot.py
    fi
    sleep 5
done
echo "Entire J runner or K compiler still alive; K not executed" >&2
exit 1
