import json, shutil
from pathlib import Path
R = Path('/home/developer/bmms_v3'); O = R/'dsh_verify'/'out'
d = json.loads((R/'c29'/'dsh152_official15.json').read_text())
mx = [x.get('maxrel') for x in d if x.get('maxrel') is not None]
print('full15: cases=%d passed=%d tasks_all=%d maxrel_max=%.6e' % (
    len(d), sum(1 for x in d if x.get('passed')), all(x.get('tasks', 0) > 0 for x in d), max(mx)))
print('P14 local=%.2f  P15 local=%.2f' % (
    [x['warm_us'] for x in d if x['case'] == 14][0], [x['warm_us'] for x in d if x['case'] == 15][0]))
shutil.copy2(R/'c29'/'dsh152_official15.json', O/'dsh152_official15.json')
print('csv=%d y_bin=%d json=%d' % (len(list(O.glob('P1*_op_summary.csv'))), len(list(O.glob('P1*_y.bin'))), len(list(O.glob('*.json')))))
