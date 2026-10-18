set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s38b f47223beab7bee0df0f729d8f325a575cbde1679757f5caa4c6289006a34d8e1
python3 work/solo38/screen_b.py f47223beab7bee0df0f729d8f325a575cbde1679757f5caa4c6289006a34d8e1
