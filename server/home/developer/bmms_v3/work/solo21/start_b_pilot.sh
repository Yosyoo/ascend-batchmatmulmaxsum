set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e solo17_data/run21_b_pilot.log
nohup bash -c '
set -eu
cd /home/developer/bmms_v3
for i in $(seq 1 90); do
    state=$(ps -p 250008 -o stat= || true)
    case "$state" in ""|Z*) break;; esac
    sleep 10
done
state=$(ps -p 250008 -o stat= || true)
case "$state" in ""|Z*) ;; *) echo "compiler still running; not launching NPU"; exit 2;; esac
test -x variants/s21b/build/bench
test -x variants/s21b/build/bench_cases
test -x variants/s21b/build/bench_multi
if pgrep -f "^python3 /home/developer/bmms_v3/work/solo[0-9]+/run_"; then
    echo "another runner exists; not launching NPU"; exit 3
fi
python3 work/solo21/run_b_pilot.py
' >solo17_data/run21_b_pilot.log 2>&1 < /dev/null &
echo "s21b diagnostic/pilot wrapper PID $!"
