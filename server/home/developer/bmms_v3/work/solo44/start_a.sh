set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s44a ff550f23e7c3fe1b2e3e5ae7365786edbd72b2e56b288c28274c8f179badda34
python3 work/solo44/final_a.py
