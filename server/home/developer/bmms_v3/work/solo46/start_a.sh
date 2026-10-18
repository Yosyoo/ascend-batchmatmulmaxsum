set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s46a edd7b57ca02c049b77017a21c3cfcdaa113f22e10739ebe133a6d1df3a069262
python3 work/solo46/final_a.py
