set -eu
cd /home/developer/bmms_v3
test ! -d solo17_data/kparallel_stress23
test ! -e solo17_data/gen_kparallel23.log
nohup python3 work/solo23/gen_kparallel_stress.py >solo17_data/gen_kparallel23.log 2>&1 < /dev/null &
echo "Reference generation only PID $!"
