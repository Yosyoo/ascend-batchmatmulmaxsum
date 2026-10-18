set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s38a d8d28523b7b2f60dc80d9e77fc16f8de640d12d4d4c4cc997577c6e8a1a3442e
python3 work/solo38/screen_a.py d8d28523b7b2f60dc80d9e77fc16f8de640d12d4d4c4cc997577c6e8a1a3442e
