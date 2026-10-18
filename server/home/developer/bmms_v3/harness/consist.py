import json,sys
for l in sys.stdin:
    if not l.startswith('{'): continue
    d=json.loads(l)
    print(d['shape'], 'consistent=',d.get('consistent'), 'passed=',d.get('passed'), 'rounds=',d.get('rounds'))
