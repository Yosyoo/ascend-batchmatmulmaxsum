from pathlib import Path
import hashlib,json,fcntl,subprocess,time
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
deadline=time.monotonic()+2400
while 'FINAL32_I_COMPLETE' not in (d/'final32_i.log').read_text(errors='replace'):
 assert time.monotonic()<deadline;time.sleep(5)
subprocess.run(['python3','work/solo32/gen_pad_legal.py'],cwd=r,check=True)
fixture=d/'pad_legal32';meta=json.loads((fixture/'fixture_hashes.json').read_text())
out=d/'legal32_s32i';out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
def check():
 for item in meta:
  for name,z in item['files'].items():
   p=fixture/f"c{item['case']:03d}"/name
   assert hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256']
check();exe=r/'variants/s32i/build/bench_cases';src=r/'variants/s32i/kernel.asc'
p=subprocess.run([str(exe),str(d/'pad_legal32.txt')],cwd=r,capture_output=True,text=True,timeout=900)
(out/'precision.log').write_text(p.stdout+p.stderr);check()
rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
good=p.returncode==0 and len(rows)==96 and all(z['passed'] and z['consistent'] for z in rows)
(out/'summary.json').write_text(json.dumps(dict(passed=good,expected=96,observed=len(rows),inputs_unchanged=True,fixture_metadata_sha256=hashlib.sha256((fixture/'fixture_hashes.json').read_bytes()).hexdigest(),hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (src,exe)},failures=[z for z in rows if not z['passed']]),indent=2)+'\n')
fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
print('LEGAL32_I',good,len(rows),flush=True);assert good
subprocess.run(['python3','work/solo31/quick_layout_compare.py','s32i','s32d','quick32_i_pair','work/solo32/pair_pad_shapes.txt','1','0','0'],cwd=r,check=True)
print('LEGAL32_I_COMPLETE',flush=True)
