set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
test ! -d solo17_data/validation_s22a
test ! -d solo17_data/pool18_s22a
test ! -d solo17_data/hangs22_a
nohup bash -c 'while test -e /proc/281419; do sleep 2; done; cd /home/developer/bmms_v3; python3 work/solo22/run_a_final.py' >solo17_data/run22_a_final.log 2>&1 < /dev/null &
echo "s22a full wrapper PID $!"
