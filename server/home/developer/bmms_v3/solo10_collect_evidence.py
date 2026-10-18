from pathlib import Path
import tarfile

root=Path('/home/developer/bmms_v3')
paths=[root/'solo10_data/validation_s10g',root/'solo10_data/final_s10g',
       root/'solo10_data/metrics_final/summary.json']
paths+=sorted((root/'solo8_data').glob('solo10_*.jsonl'))
for name in ['metrics','metrics_final']:
    paths+=sorted((root/'solo10_data'/name).glob('**/mindstudio_profiler_output/op_summary_*.csv'))
with tarfile.open('/tmp/solo10-final-evidence.tar.gz','w:gz') as archive:
    for p in paths:
        assert p.exists(),p
        archive.add(p,arcname=str(p.relative_to(root)))
print('evidence bytes',Path('/tmp/solo10-final-evidence.tar.gz').stat().st_size)
