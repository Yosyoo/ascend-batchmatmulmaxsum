from pathlib import Path
import fcntl,hashlib,json,subprocess
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s23j'
sha='d1ef4d7627fa77b8bf9edcc50558a6a0dcace5d32462321320d392bb152f5437'
out=d/'diagnostic_23j';out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
exe=r/'variants'/v/'build/bench_cases';src=r/'variants'/v/'kernel.asc'
assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]};items=[]
for manifest in [r/'work/solo18/fail_8.txt',d/'resident_cases18.txt',d/'manual_cases18.txt',d/'medium_cases.txt',r/'solo14_data/split16_cases.txt']:
    p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,timeout=600)
    (out/(manifest.stem+'.log')).write_text(p.stdout+p.stderr)
    rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    good=p.returncode==0 and len(rows)==len(manifest.read_text().splitlines()) and all(x['passed'] and x['consistent'] for x in rows)
    item=dict(suite=manifest.stem,passed=good,observed=len(rows),expected=len(manifest.read_text().splitlines()),hashes=hashes);items.append(item)
    (out/'summary.json').write_text(json.dumps(items,indent=2));print(json.dumps(item),flush=True)
    if not good:print((p.stdout+p.stderr)[-3000:]);raise SystemExit(1)
assert sum(x['observed'] for x in items)==648
fixture_hashes=json.loads((d/'dot_once_input_sha256.json').read_text())
def check_dot():
    for name,expected in fixture_hashes.items():
        assert hashlib.sha256((d/name).read_bytes()).hexdigest()==expected
check_dot()
p=subprocess.run([str(exe),str(d/'dot_once_cases.txt')],capture_output=True,text=True,timeout=600)
(out/'dot_once_576.log').write_text(p.stdout+p.stderr)
rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
assert p.returncode==0 and len(rows)==576 and all(x['passed'] and x['consistent'] for x in rows)
check_dot()
(out/'dot_summary.json').write_text(json.dumps(dict(passed=True,cases=576,fixture_hashes_unchanged=True,hashes=hashes),indent=2)+'\n')
print('PASS dot576,648diagnostics',flush=True)
public=d/'public_case1_23';public_meta=json.loads((public/'metadata.json').read_text())
for name,x in public_meta['files'].items():assert hashlib.sha256((public/name).read_bytes()).hexdigest()==x['sha256']
p=subprocess.run([str(exe),str(d/'public_case1_23.txt')],capture_output=True,text=True,timeout=60)
(out/'public_case1.log').write_text(p.stdout+p.stderr)
public_rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
assert p.returncode==0 and len(public_rows)==1 and public_rows[0]['passed'] and public_rows[0]['consistent']
for name,x in public_meta['files'].items():assert hashlib.sha256((public/name).read_bytes()).hexdigest()==x['sha256']
print('PASS exact official public case1 seed42',flush=True)
fcntl.flock(lock,fcntl.LOCK_UN)
specs=['1_8_8_32_1_0_0','1_8_8_32_2_0_0','1_8_8_32_1_1_0','1_8_8_32_2_1_1','1_8_8_64_1_0_0','1_8_8_64_2_1_1','8_8_8_32_1_0_0','40_8_8_64_2_0_0']
for label,variants in [('pilot23_j_parent_base','s23j,s23d,s15i'),('pilot23_base_parent_j','s15i,s23d,s23j')]:
    p=subprocess.run(['python3',str(r/'work/solo17/scan.py'),label,variants,*specs])
    if p.returncode:raise SystemExit(p.returncode)
print('PASS s23j diagnostics648,dot576,pilots48; not submission ready.',flush=True)
