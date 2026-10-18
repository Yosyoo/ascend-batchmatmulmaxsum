set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e /proc/349999
test ! -d solo17_data/cancel_m_audit23
nohup python3 work/solo23/audit_cancel_m.py >solo17_data/run23_cancel_m_audit.log 2>&1 < /dev/null &
echo "cancel_m actual NPU audit PID $!"
