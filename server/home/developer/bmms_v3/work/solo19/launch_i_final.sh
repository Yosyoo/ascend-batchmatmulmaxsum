set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test "$(sha256sum variants/s19i/kernel.asc | cut -d ' ' -f 1)" = 314d61425771496515f98d3668d9559af1d6fcdab9df2e04f0a6dcc86e103a7f
grep -q 'PASS s19f final precision,100-pool and six hangs' solo17_data/run19_f_final.log
if kill -0 210168 2>/dev/null; then echo 'Previous complete experiment runner remains active'; exit 1; fi
test ! -d solo17_data/diagnostic_19i
test ! -d solo17_data/validation_s19i
test ! -d solo17_data/pool18_s19i
grep -q 'Built target bench_multi' variants/s19i/build.log
grep -q 'Built target bench_cases' variants/s19i/build.log
grep -q 'Built target bench$' variants/s19i/build.log
flock -n solo17_data/.npu_serial.lock true
nohup python3 work/solo19/run_i_final.py >solo17_data/run19_i_final.log 2>&1 < /dev/null &
echo "s19i FINAL PID $!"
