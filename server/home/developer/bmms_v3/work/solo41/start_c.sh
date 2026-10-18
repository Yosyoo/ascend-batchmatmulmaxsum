set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s41c 5fc87dcd3f6e8eff0c036274369af504b2951ae2a1c186a88d107e5e398b3494
while kill -0 205638 2>/dev/null; do sleep 5; done
python3 work/solo41/screen_c.py 5fc87dcd3f6e8eff0c036274369af504b2951ae2a1c186a88d107e5e398b3494
