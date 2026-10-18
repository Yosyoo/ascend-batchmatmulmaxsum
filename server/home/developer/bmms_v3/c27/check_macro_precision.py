from pathlib import Path
import subprocess,os,json
root=Path('/home/developer/bmms_v3');os.chdir(root)
lines=[]
for s in (root/'c26/fast_cases/ares128.txt').read_text().splitlines():
 b,m,n,k,dt,ta,tb=map(int,s.split()[:7]);nt=(n+127)//128;cores=(20//nt)*nt
 if not ta and not tb and m>=512 and n>=512 and k*256+131072<=524032 and cores>=16 and b*((m+255)//256)>=2*(cores//nt):lines.append(s)
p=root/'c26/fast_cases/macro_precision.txt';p.write_text('\n'.join(lines)+'\n')
with (root/'c26/clean73_macro_precision.log').open('w') as f:
 rc=subprocess.run(['timeout','180','c26/fast_suite/build_clean73/bench_cases',str(p)],stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'BMMS_DEVICE_ID':'0'}).returncode
print(json.dumps({'cases':len(lines),'rc':rc,'tail':(root/'c26/clean73_macro_precision.log').read_text().splitlines()[-2:]}))
