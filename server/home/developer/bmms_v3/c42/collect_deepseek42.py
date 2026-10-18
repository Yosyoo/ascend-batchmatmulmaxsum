from pathlib import Path
import hashlib
import json
import shutil
import tarfile

root = Path('/home/developer/bmms_v3')
expected = {
    'dsh125': 'a2e6ca65d7dfca49bd81af577b2cf17f6c7c8a187deeff0e36d11805bd5c5323',
    'dsh131': '70848eebdabd555fe78085d1678bd06333db7f660267d10c160f26f61154e354',
}
destination = root / 'dsh_verify/codex_collected_after_completion'
destination.mkdir(exist_ok=True)
for name, sha in expected.items():
    source = root / 'variants' / name / 'kernel.asc'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == sha
    shutil.copy2(source, destination / (name + '_kernel.asc'))
rows = json.loads((root / 'c29/dsh131_official15.json').read_text())
assert len(rows) == 15 and all(row['passed'] and row['returncode'] == 0 for row in rows)
shutil.copy2(root / 'c29/dsh131_official15.json', destination / 'dsh131_local15.json')
for row in rows:
    spec = '_'.join(map(str, row['shape'])) + '_' + str(row['dtype']) + '_' + str(int(row['ta'])) + '_' + str(int(row['tb']))
    work = root / 'variants/dsh131/research/PipeUtilization' / spec
    profiles = sorted(work.glob('profile/PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
    assert profiles
    shutil.copy2(profiles[-1], destination / ('P' + str(row['case']) + '.csv'))
    for path, suffix in [(work / 'output/y.bin', '_y.bin'), (work / 'msprof.log', '_msprof.log')]:
        if path.exists():
            shutil.copy2(path, destination / ('P' + str(row['case']) + suffix))
with tarfile.open(root / 'c42/deepseek_evidence.tgz', 'w:gz') as archive:
    for path in sorted((root / 'dsh_verify').rglob('*')):
        if path.is_file() and path.suffix != '.tgz' and '__pycache__' not in path.parts:
            archive.add(path, arcname='dsh_verify/' + str(path.relative_to(root / 'dsh_verify')), recursive=False)
print('archived independent source identities and15/15RC0PASS')
