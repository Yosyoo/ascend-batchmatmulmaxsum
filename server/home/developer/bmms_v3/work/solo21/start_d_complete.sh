set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e solo17_data/run21_d_final.log
test ! -e solo17_data/long_accuracy21d
test ! -e solo17_data/long_stress21
test ! -e solo17_data/run21_gen_long.log
test ! -e solo17_data/validation_s21d
test ! -e solo17_data/pool18_s21d
grep -q 'PASS pilot only' solo17_data/run21_d_pilot.log
state=$(ps -p 258608 -o stat= || true)
case "$state" in ""|Z*) ;; *) echo 'pilot runner still alive; not launching';exit 2;; esac
nohup bash -c '
set -eu
cd /home/developer/bmms_v3
python3 work/solo21/gen_long_stress.py >solo17_data/run21_gen_long.log 2>&1
grep -q "PASS generated96" solo17_data/run21_gen_long.log
python3 work/solo21/run_d_complete.py
' >solo17_data/run21_d_final.log 2>&1 < /dev/null &
echo "s21d complete validation wrapper PID $!"
