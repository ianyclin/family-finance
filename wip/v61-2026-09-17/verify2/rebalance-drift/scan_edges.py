"""掃 1928–2021 每個起點：第一次超出門檻那年、以及之前的年份，離 75/85 邊界是否在 0.05 個百分點內（會不會因為 >/>= 或四捨五入改變「最快 1 年、最慢 22 年」）。"""
from fractions import Fraction as F
exec(open('recompute_v2.py').read().split("out = {}")[0])
hits = []
for s in range(1928, 2022):
    p = path_A(s, 'bill')
    for y, w in p:
        d = abs(abs(w - T) - F(1, 20)) * 100
        if d < F(1, 20):
            hits.append((s, y, float(d), outside(w)))
        if outside(w):
            break
print('edge hits up to first breach (start, year, dist_pp, outside):', hits)
p = path_A(1964, 'bill')
print('1964 start first breach:', [(y, round(float(w*100), 3)) for y, w in p if outside(w)][:1])
mins = [s for s in range(1928, 2022) if outside(path_A(s, 'bill')[0][1])]
print('1-year breach starts:', mins)
