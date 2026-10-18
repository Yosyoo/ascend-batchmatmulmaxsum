import sys, json
d = json.load(sys.stdin)
for s in d['shapes']:
    u = s['units']
    print('%-22s warm=%8.2f aicS=%7.2f aicMac=%6.2f aicMte2=%6.2f fix=%6.2f | aivS=%6.2f aivVec=%6.2f aivMte2=%6.2f' % (
        str(s['shape']), s['warm_median'], u.get('aic_scalar_time(us)',0), u.get('aic_mac_time(us)',0),
        u.get('aic_mte2_time(us)',0), u.get('aic_fixpipe_time(us)',0),
        u.get('aiv_scalar_time(us)',0), u.get('aiv_vec_time(us)',0), u.get('aiv_mte2_time(us)',0)))
