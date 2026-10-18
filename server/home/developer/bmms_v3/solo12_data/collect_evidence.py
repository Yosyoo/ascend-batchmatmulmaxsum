from pathlib import Path
import hashlib,json,tarfile
root=Path('/home/developer/bmms_v3')
out=root/'solo12_data'
files=[p for p in out.rglob('*') if p.is_file() and p.suffix in {'.csv','.json','.jsonl','.log','.txt','.py','.elf'}]
for v in ['s11a','s12a','s12b','s12c']:
 d=root/'variants'/v
 files.extend([d/'kernel.asc'])
 files.extend(d.glob('build*.log'))
for file in ['measure.py','multi.py','bench.asc','bench_multi.asc','data_utils.h','one.py']:
 files.append(root/'harness'/file)
files.extend([root/'variants/s12c/bench_cases.asc',root/'variants/s12c/CMakeLists.txt',root/'shapes_pool2.txt',root/'solo12_scan.py'])
files=sorted(set(p for p in files if p.is_file()))
manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(out/'evidence_sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
files.append(out/'evidence_sha256.json')
with tarfile.open(root/'solo12_evidence.tar.gz','w:gz') as t:
 for p in files:t.add(p,arcname=str(p.relative_to(root)),recursive=False)
print('Evidence:',len(files),'files,', (root/'solo12_evidence.tar.gz').stat().st_size,'bytes')
