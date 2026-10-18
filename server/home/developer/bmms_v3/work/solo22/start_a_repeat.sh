set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e /proc/288225
test ! -e solo17_data/pool22_repeat_s22a
flock -n solo17_data/.npu_serial.lock -c 'echo NPU_SERIAL_LOCK_FREE'
nohup python3 work/solo22/repeat_a_pool.py >solo17_data/run22_a_repeat.log 2>&1 < /dev/null &
echo "s22a independent repeat PID $!"
