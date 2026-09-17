"""『最慢 22 年』對門檻判定方式的敏感度：嚴格 > 5pp（模組）、>= 5pp（指南例子寫「以上／以下」）、先四捨五入到 0.1 再用 >=。"""
import statistics
from fractions import Fraction as F
exec(open('recompute_v2.py').read().split("out = {}")[0])
def hu(x):  # 精確 half-up 到 0.1 個百分點，回傳 Fraction（百分比）
    import math
    return F(math.floor(x * 1000 + F(1, 2)), 10)
rules = {
    'strict_gt': lambda w: abs(w - T) > F(1, 20),
    'inclusive_ge': lambda w: abs(w - T) >= F(1, 20),
    'rounded_1dp_ge': lambda w: abs(hu(w) - 80) >= 5,
}
for name, fn in rules.items():
    rows = []
    for s in range(1928, 2022):
        p = path_A(s, 'bill')
        n = next((y - s + 1 for y, w in p if fn(w)), None)
        rows.append((s, n))
    ns = [n for _, n in rows if n]
    mx = max(ns)
    p90 = path_A(1990, 'bill'); n90 = next(y - 1990 + 1 for y, w in p90 if fn(w))
    print(name, 'never', sum(1 for _, n in rows if n is None), 'min', min(ns), 'median', statistics.median(ns), 'max', mx,
          'max_starts', [s for s, n in rows if n == mx], 'top5', sorted(ns)[-5:], '1990:', n90)
# 1964 起點 1974 年底的原值
p = dict(path_A(1964, 'bill'))
print('1964 start, 1974 year-end stock share % =', float(p[1974] * 100))
