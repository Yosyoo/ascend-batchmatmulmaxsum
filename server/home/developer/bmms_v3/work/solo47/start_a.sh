set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s47a 93432404a2c1676eb8f572237fb11f3f65dc9e07da6c8079402f8556a9c014f6
cmake -S work/solo47/guard -B work/solo47/guard/build
cmake --build work/solo47/guard/build --target guard -j1 >solo17_data/compile47_guard.log 2>&1
python3 work/solo47/screen_a.py 93432404a2c1676eb8f572237fb11f3f65dc9e07da6c8079402f8556a9c014f6
python3 work/solo47/final_a.py
