set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d solo17_data/diagnostic_23o
for attempt in $(seq 1 240); do
    if ! kill -0 456027 2>/dev/null && ! kill -0 456997 2>/dev/null; then
        test -x variants/s23o/build/bench
        test -x variants/s23o/build/bench_cases
        test "$(sha256sum variants/s23o/kernel.asc | cut -d ' ' -f 1)" = c1363aef7224cf29b98e428786040dd746dec302d9f2e832ad8dd62a64f89757
        exec python3 -u work/solo23/run_o_pilot.py
    fi
    sleep 5
done
echo "Entire N runner or O compiler still alive; O not executed" >&2
exit 1
