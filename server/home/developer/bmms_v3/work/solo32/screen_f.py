from pathlib import Path
import fcntl,hashlib,json,subprocess,sys,time
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s32f';sha=sys.argv[1]
deadline=time.monotonic()+1800
log=d/'compile32_f.log'
while not log.exists() or 'COMPILE32_F_COMPLETE' not in log.read_text(errors='replace'):
    assert time.monotonic()<deadline;time.sleep(5)
for name in ('compile32_f_cases.log','compile32_f_multi.log'):
    assert 'error:' not in (d/name).read_text(errors='replace'),(d/name).read_text()[-2000:]
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
manifests=[r/'delivery4/validation/cases.txt',r/'solo13_data/generic_nt_cases.txt',r/'solo13_data/nt_cases.txt',
 r/'solo11_data/copy_cases.txt',d/'medium_cases.txt',r/'solo14_data/balanced_cases.txt',r/'work/solo18/fail_8.txt',
 d/'whole_stress30.txt',d/'short_resident_stress31.txt',r/'solo14_data/split16_cases.txt',
 r/'solo14_data/narrow_legal_cases.txt',r/'solo14_data/pair_edge_cases.txt',d/'dot_once_cases.txt',
 r/'solo14_data/long_sum.txt',r/'solo10_data/vector_cases.txt',r/'solo9_data/micro_cases.txt',
 r/'solo8_data/nz_cases.txt',r/'variants/s5d/split_cases.txt',r/'variants/s5p/direct_cases.txt',
 r/'variants/s5r/tail_cases.txt',r/'solo6_data/large_cases.txt',r/'solo8_data/narrow_cases.txt',
 r/'solo8_data/narrow_extra_cases.txt']
selected=[];origins=[]
def gate(b,m,n,k,ta,tb):
    kp=(k+15)//16*16
    return ta==0 and tb==0 and k%16!=0 and 16<=k<=256 and m<=256 and n<=256 and \
        b*m*n*k<(1<<28) and b*kp*n<=(1<<20) and b*m*n*k>=1024
for p in manifests:
    if not p.exists():continue
    before=hashlib.sha256(p.read_bytes()).hexdigest();cnt=0;aligned=0
    for line in p.read_text().splitlines():
        f=line.split()
        if len(f)<4:continue
        b,m,n,k=map(int,f[:4]);ta=int(f[5]) if len(f)>6 else 0;tb=int(f[6]) if len(f)>6 else 0
        if gate(b,m,n,k,ta,tb):selected.append(line);cnt+=1
        elif k%16==0 and ta==0 and tb==0 and b*m*n*k<=(1<<28) and aligned<3 and (b+m+n+k)%7==0:
            selected.append(line);aligned+=1
    origins.append(dict(path=str(p),sha256=before,nonAligned=cnt,alignedSample=aligned))
    assert before==hashlib.sha256(p.read_bytes()).hexdigest()
extra=d/'probe32_nn/probe32_nn_manifest.txt'
if extra.exists():selected.extend(extra.read_text().splitlines())
out=d/f'diagnostic32_{v}';out.mkdir(exist_ok=False)
manifest=out/'cases.txt';manifest.write_text('\n'.join(selected)+'\n');case_sha=hashlib.sha256(manifest.read_bytes()).hexdigest()
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (r/f'variants/{v}/kernel.asc',r/f'variants/{v}/build/bench_cases')}
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
p=subprocess.run([str(r/f'variants/{v}/build/bench_cases'),str(manifest)],cwd=r,capture_output=True,text=True,timeout=1800)
(out/'precision.log').write_text(p.stdout+p.stderr);rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
good=p.returncode==0 and len(rows)==len(selected) and all(z['passed'] and z['consistent'] for z in rows)
(out/'summary.json').write_text(json.dumps(dict(variant=v,hashes=hashes,origins=origins,manifest_sha256=case_sha,
 expected=len(selected),observed=len(rows),passed=good,returncode=p.returncode,
 failures=[z for z in rows if not z['passed'] or not z['consistent']]),indent=2)+'\n')
print('PRECISION32_F',good,len(rows),flush=True)
fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if not good:
    print(json.dumps([z for z in rows if not z['passed']][:5]),flush=True);raise SystemExit(1)
for ta,tb in ((0,0),):
    subprocess.run(['python3','work/solo31/quick_layout_compare.py',v,'s32d',f'quick32_f_{ta}{tb}',
                    'work/solo32/probe_shapes.txt','1',str(ta),str(tb)],cwd=r,check=True)
print('SCREEN32_F_COMPLETE',flush=True)
