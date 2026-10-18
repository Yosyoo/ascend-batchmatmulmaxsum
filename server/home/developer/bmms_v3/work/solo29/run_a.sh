set -eu
cd /home/developer/bmms_v3
bash work/solo28/compile_variant.sh s29a 470b540c3764e4d8d595a0f4a326757c7cc8033d47df6887512672c61fe17958
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
python3 work/solo28/diagnostic.py s29a 470b540c3764e4d8d595a0f4a326757c7cc8033d47df6887512672c61fe17958
python3 work/solo28/quick_compare.py s29a s28d quick29_a /home/developer/bmms_v3/work/solo29/quick_shapes.txt
echo ROUND29_A_SCREEN_COMPLETE
