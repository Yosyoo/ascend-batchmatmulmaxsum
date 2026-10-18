set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s39b ceb0de95c8969524db9d3546465d3ca63c936370efc9810ff9970ea87d337d2e
python3 work/solo39/screen_b.py ceb0de95c8969524db9d3546465d3ca63c936370efc9810ff9970ea87d337d2e
