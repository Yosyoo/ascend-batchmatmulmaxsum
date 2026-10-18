set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e solo17_data/baseline_bf16_22
nohup python3 work/solo22/baseline_bf16.py >solo17_data/baseline_bf16_22.log 2>&1 < /dev/null &
echo "BF16 audit PID $!"
