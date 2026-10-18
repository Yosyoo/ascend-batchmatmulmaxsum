set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
grep -q 'PASS s19h pilot only' solo17_data/run19_h_pilot.log
if kill -0 190255 2>/dev/null; then echo 'Previous complete experiment runner remains active'; exit 1; fi
test ! -d solo17_data/validation_s19f
test ! -d solo17_data/pool18_s19f
flock -n solo17_data/.npu_serial.lock true
nohup python3 work/solo19/run_f_final.py >solo17_data/run19_f_final.log 2>&1 < /dev/null &
echo "s19f FINAL PID $!"
