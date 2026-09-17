"""找一個不怕邊界的替代說法：各判定方式下，幾個起點在 N 年內就跑出門檻；以及 T-bill 報酬捨入誤差（±0.005%）對 1964 起點 1974 年底的影響。"""
from fractions import Fraction as F
import math
exec(open('recompute_v2.py').read().split("out = {}")[0])
def hu(x): return F(math.floor(x * 1000 + F(1, 2)), 10)
rules = {'strict_gt': lambda w: abs(w - T) > F(1, 20), 'rounded_1dp_ge': lambda w: abs(hu(w) - 80) >= 5}
for name, fn in rules.items():
    ns = []
    for s in range(1928, 2022):
        ns.append(next(y - s + 1 for y, w in path_A(s, 'bill') if fn(w)))
    print(name, {k: sum(1 for n in ns if n <= k) for k in (2, 3, 4, 5, 10)}, 'of', len(ns))
# 捨入誤差：國庫券欄位只給到 0.01%，每年 ±0.005% 全部同向
for sign in (-1, 1):
    s_, b_ = T, 1 - T
    for y in range(1964, 1975):
        s_ *= 1 + F(ret[y]['sp']); b_ *= 1 + F(ret[y]['bill']) + sign * F(5, 100000)
    print('bill shift %+.3f%%/yr -> 1974 share %.4f%%' % (sign * 0.005, float(s_ / (s_ + b_) * 100)))
print('bill returns 1964-1974:', [ret[y]['bill'] for y in range(1964, 1975)])
