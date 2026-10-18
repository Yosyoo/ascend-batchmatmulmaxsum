set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -e solo17_data/run19_c_final.log
test ! -d solo17_data/validation_s19c
test ! -d solo17_data/pool18_s19c
test ! -d solo17_data/hangs19_c
grep -q 'PASS s19c pilot only' solo17_data/run19_c_pilot.log
test "$(sha256sum variants/s19c/kernel.asc | cut -d ' ' -f 1)" = 7266fd43e903656a57539a0a5d0753c482b48b302a41e2bef844ec912a4690c2
nohup python3 work/solo19/run_c_final.py >solo17_data/run19_c_final.log 2>&1 < /dev/null &
echo "s19c final PID $!"
