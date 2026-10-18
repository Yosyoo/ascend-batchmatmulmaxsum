set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e /proc/318239
test ! -d solo17_data/kparallel_batch_accuracy23c
grep -q 'PASS generated96 immutable validation fixtures' solo17_data/gen_kparallel_batch23.log
nohup python3 work/solo23/run_c_batch.py >solo17_data/run23_c_batch.log 2>&1 < /dev/null &
echo "s23c batch validation PID $!"
