import json, statistics, math, sys
A, B = sys.argv[1], sys.argv[2]
def load(tag, v):
    d = json.load(open("/home/developer/bmms_v3/o_cmp/%s_%s.json" % (tag, v)))
    return {tuple(s['shape']): s['warm_median'] for s in d['shapes']}
pairs = []
for tag in ("A", "B"):
    a = load(tag, A); b = load(tag, B)
    common = sorted(set(a) & set(b))
    rs = [b[k]/a[k] for k in common if a[k] > 0]
    g = statistics.exp(statistics.mean([math.log(x) for x in rs]))
    print("%s: %s/%s  geo-mean = %.4f   (n=%d, 中位 %.4f, 快于%s 的形状 %d/%d)" % (
        tag, B, A, g, len(rs), statistics.median(rs), A, sum(1 for x in rs if x < 1), len(rs)))
    pairs.append((tag, g, rs))
allr = [x for _, _, rs in pairs for x in rs]
g = statistics.exp(statistics.mean([math.log(x) for x in allr]))
print("合计 geo-mean %s/%s = %.4f  (n=%d)" % (B, A, g, len(allr)))
