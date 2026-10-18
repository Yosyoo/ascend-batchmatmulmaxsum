set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
grep -q 'EXTRA42_COMPLETE s41c' solo17_data/extra42_c.log
bash work/solo32/compile_screen.sh s42a dc7c037c671d8c921cbf093d322adfa53dde32b4d57513c7698e93c06e5bf3aa
python3 work/solo42/screen_a.py dc7c037c671d8c921cbf093d322adfa53dde32b4d57513c7698e93c06e5bf3aa
