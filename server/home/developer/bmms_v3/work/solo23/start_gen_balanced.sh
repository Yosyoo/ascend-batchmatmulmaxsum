set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d solo17_data/balanced_stress23
nohup python3 work/solo23/gen_balanced_stress.py >solo17_data/gen_balanced23.log 2>&1 < /dev/null &
echo "CPU REFERENCE ONLY balanced stress PID $!"
