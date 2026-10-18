set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s39a e9255c8f3cad241f961ee02541322dde62152f485ac1e7f3cb99994224e1aec3
python3 work/solo39/screen_a.py e9255c8f3cad241f961ee02541322dde62152f485ac1e7f3cb99994224e1aec3
