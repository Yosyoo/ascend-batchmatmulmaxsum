set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test "$(sha256sum variants/s29a/kernel.asc | cut -d ' ' -f 1)" = d857a7ae73547188775409cd483f9fca9c474471d5fe5548a953ed892658fd03
cmake --build variants/s29a/build -j2
python3 work/solo28/diagnostic.py s29a d857a7ae73547188775409cd483f9fca9c474471d5fe5548a953ed892658fd03
python3 work/solo28/quick_compare.py s29a s28d quick29_a /home/developer/bmms_v3/work/solo29/quick_shapes.txt
echo ROUND29_A_SCREEN_COMPLETE
