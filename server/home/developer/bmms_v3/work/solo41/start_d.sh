set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s41d f55d154c15c72cfc9bb9e877e928bd5fa250c7b399a39a4adf2ca40172e5110a
python3 work/solo41/screen_d.py f55d154c15c72cfc9bb9e877e928bd5fa250c7b399a39a4adf2ca40172e5110a
