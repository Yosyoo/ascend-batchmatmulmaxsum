set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d solo17_data/diagnostic_23j
test ! -d solo17_data/unaligned_23i
test -x variants/s23i/build/bench_unaligned
test -x variants/s23j/build/bench
for attempt in $(seq 1 180); do
    if ! kill -0 373244 2>/dev/null; then
        python3 -u work/solo23/run_i_unaligned.py
        exec python3 -u work/solo23/run_j_pilot.py
    fi
    sleep 5
done
echo "Previous entire I runner still alive; J not executed" >&2
exit 1
