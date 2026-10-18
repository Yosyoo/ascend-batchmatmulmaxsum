set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s45c fd992a17f3754984f806d3da14ac0afbc08ca5989c8510152279ef8cf8c98182
python3 work/solo45/final_c.py
