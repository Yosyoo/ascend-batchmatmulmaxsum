set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -f solo17_data/run_l_final.log
nohup python3 work/solo18/run_l_final.py >solo17_data/run_l_final.log 2>&1 < /dev/null &
echo "s17l final PID $!"
