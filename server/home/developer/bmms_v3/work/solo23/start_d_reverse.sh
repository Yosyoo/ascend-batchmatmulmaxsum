set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e /proc/328006
test ! -d solo17_data/pilot23_base_parent_d
nohup python3 work/solo23/run_d_reverse.py >solo17_data/run23_d_reverse.log 2>&1 < /dev/null &
echo "s23d remaining reverse runner PID $!"
