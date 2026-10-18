set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
python3 work/solo41/gen_stress.py > solo17_data/gen41.log 2>&1 &
gen_pid=$!
bash work/solo32/compile_screen.sh s41a 50378733e7de4d1001d89aecaa9425134f0beae38fd418b0ca9abde21eeb7163
wait "$gen_pid"
python3 work/solo41/screen_a.py 50378733e7de4d1001d89aecaa9425134f0beae38fd418b0ca9abde21eeb7163
