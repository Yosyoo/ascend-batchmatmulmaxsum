set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d solo17_data/diagnostic_23l
test -f solo17_data/tiny_stress23/fixture_hashes.json
for attempt in $(seq 1 240); do
    if ! kill -0 386939 2>/dev/null && ! kill -0 402980 2>/dev/null; then
        test -x variants/s23l/build/bench
        test -x variants/s23l/build/bench_cases
        exec python3 -u work/solo23/run_l_pilot.py
    fi
    sleep 5
done
echo "Entire K runner or L compiler still alive; L not executed" >&2
exit 1
