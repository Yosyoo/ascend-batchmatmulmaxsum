set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s42b b405e207e962cf691ca813a76604c4811ed6628a90e104f683aa23df0b2f196d
python3 work/solo42/screen_b.py b405e207e962cf691ca813a76604c4811ed6628a90e104f683aa23df0b2f196d
