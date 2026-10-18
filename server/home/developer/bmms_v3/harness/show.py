import sys, json
d = json.load(sys.stdin)
print(' ' + ' '.join('%7.2f' % s['warm_median'] for s in d['shapes']))
