set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
while kill -0 207235 2>/dev/null; do sleep 3; done
bash work/solo32/compile_screen.sh s41e fec1ba0c694283fc3d55b5f357c45d2b31957dab1b6ef64ae6a7d2af08f60de5
while kill -0 207200 2>/dev/null; do sleep 3; done
python3 work/solo41/screen_e.py fec1ba0c694283fc3d55b5f357c45d2b31957dab1b6ef64ae6a7d2af08f60de5
