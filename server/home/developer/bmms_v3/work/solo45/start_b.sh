set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s45b 446132aacaf16a5603a4c3f0ef0980f326b8698942c8d39cf704158dfc13f048
python3 work/solo45/final_b.py
