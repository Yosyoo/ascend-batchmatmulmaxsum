import sys, json
d = json.load(sys.stdin)
for s in d['shapes']:
    u = s['units']
    dur = s.get('dur_median')
    print('%-20s warm=%7.2f dur=%7.2f | aicS=%6.2f mac=%5.2f mte2=%5.2f fix=%5.2f | aivS=%5.2f vec=%5.2f mte2=%5.2f'
          % (str(s['shape']), s['warm_median'], (dur or -1),
             u.get('aic_scalar_time(us)',0), u.get('aic_mac_time(us)',0), u.get('aic_mte2_time(us)',0),
             u.get('aic_fixpipe_time(us)',0), u.get('aiv_scalar_time(us)',0),
             u.get('aiv_vec_time(us)',0), u.get('aiv_mte2_time(us)',0)))
