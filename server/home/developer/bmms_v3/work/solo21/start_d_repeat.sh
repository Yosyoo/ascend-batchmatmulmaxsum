set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e solo17_data/run21_d_repeat.log
test ! -e solo17_data/pool21_repeat_s21d
grep -q 'PASS s21d complete' solo17_data/run21_d_final.log
state=$(ps -p 265521 -o stat= || true)
case "$state" in ""|Z*) ;; *) echo 'complete runner still alive; not launching';exit 2;; esac
nohup python3 work/solo21/repeat_d_pool.py s21d >solo17_data/run21_d_repeat.log 2>&1 < /dev/null &
echo "s21d independent100 ABBA repeat PID $!"
