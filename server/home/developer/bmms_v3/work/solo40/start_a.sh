set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s40a f8c5cc3906544dd89189438dd41a28db72fc1c149899ad6dc2d81021aecf75d2
python3 work/solo40/screen_a.py f8c5cc3906544dd89189438dd41a28db72fc1c149899ad6dc2d81021aecf75d2
