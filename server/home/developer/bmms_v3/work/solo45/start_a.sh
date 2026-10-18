set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s45a f7decda57c1360da6a5415a3ba200aa3b60a434e5993b16997807ce20cd3c5bf
python3 work/solo45/final_a.py
