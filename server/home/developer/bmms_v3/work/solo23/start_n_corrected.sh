set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d solo17_data/diagnostic_23n
test -x variants/s23n/build/bench_cases
test "$(sha256sum variants/s23n/kernel.asc | cut -d ' ' -f 1)" = 14e796a1ea878af21b96933f73a2b79186770e6a406f8b495be0e4af8f67c97f
if kill -0 425808 2>/dev/null; then exit 1; fi
nohup python3 -u work/solo23/run_n_pilot.py >solo17_data/run23_n_pilot.log 2>&1 < /dev/null &
echo "s23n runner $!"
