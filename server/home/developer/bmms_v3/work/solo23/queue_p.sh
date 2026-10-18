set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d solo17_data/diagnostic_23p
for attempt in $(seq 1 240); do
    if ! kill -0 461154 2>/dev/null && ! kill -0 469155 2>/dev/null; then
        test -x variants/s23p/build/bench
        test -x variants/s23p/build/bench_cases
        test "$(sha256sum variants/s23p/kernel.asc | cut -d ' ' -f 1)" = 46d3e48b265ba4cd87aa5cedf49a9c31c56200b7f12bc8004ab10922ceb63b30
        exec python3 -u work/solo23/run_p_pilot.py
    fi
    sleep 5
done
echo "Entire O runner or P compiler still alive; P not executed" >&2
exit 1
