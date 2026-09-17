"""裁判敏感度：防守換成 3 個月國庫券（最接近定存、活存）時，G10 的敘事是否成立。"""
import sys, json, statistics
sys.path.insert(0, '.')
from recompute import load, buyhold, annual_reb, first_out, outside, hu
d, _, _ = load()
last = max(d)
out = {}
for key in ('tb', 'bill'):
    p = buyhold(d, 1990, last, key)
    f = first_out(p)
    out[key] = dict(
        first=(f[0], f[0]-1989, hu(f[1]*100)[0]),
        back_inside=[y for y, sw, _ in p if y > f[0] and not outside(sw)],
        min_after=min(((hu(sw*100)[0], y) for y, sw, _ in p if y > f[0])),
        y2007_2012=[(y, hu(sw*100)[0]) for y, sw, _ in p if 2007 <= y <= 2012],
        end=hu(p[-1][1]*100)[0],
        outside=sum(1 for _, sw, _ in p if outside(sw)),
        reb_pre=[(y, hu(sw*100)[0]) for y, sw, _ in annual_reb(d, 1990, last, key) if outside(sw)],
    )
    s2000 = buyhold(d, 2000, last, key); f2 = first_out(s2000)
    out[key]['start2000'] = dict(first=(f2[0], hu(f2[1]*100)[0]), min=min((hu(sw*100)[0], y) for y, sw, _ in s2000), end=hu(s2000[-1][1]*100)[0])
    rows = []
    for s in range(1928, 2022):
        q = buyhold(d, s, last, key); g = first_out(q)
        rows.append(((g[0]-s+1) if g else None, ('above' if g and g[1] > .8 else 'below') if g else None))
    ys = [r[0] for r in rows if r[0]]
    out[key]['scan'] = dict(min=min(ys), median=statistics.median(ys), max=max(ys), never=sum(1 for r in rows if r[0] is None),
                            above=sum(1 for r in rows if r[1]=='above'), below=sum(1 for r in rows if r[1]=='below'))
out['returns_2008'] = {k: hu(d[2008][k]*100)[0] for k in ('sp', 'tb', 'bill')}
out['returns_2002'] = {k: hu(d[2002][k]*100)[0] for k in ('sp', 'tb', 'bill')}
print(json.dumps(out, ensure_ascii=False, indent=1))
