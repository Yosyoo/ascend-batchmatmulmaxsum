set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test -e solo17_data/baseline_bf16_22/summary.json
test ! -e solo17_data/pilot22_fulla_forward
test ! -e solo17_data/pilot22_fulla_reverse
test ! -e /proc/270681
flock -n solo17_data/.npu_serial.lock -c 'echo NPU_SERIAL_LOCK_FREE'
nohup python3 work/solo22/audit_fulla.py >solo17_data/audit_fulla_22.log 2>&1 < /dev/null &
echo "FullA audit PID $!"
