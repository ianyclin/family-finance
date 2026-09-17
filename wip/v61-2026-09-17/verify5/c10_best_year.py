# 示意例子「一年漲七成」有多罕見：Damodaran 美股含息 1928–2025、台股含息報酬指數 2004–2025 的最好年份
import sys, csv
from datetime import date
ROOT = '/Users/linyenchu/Cladue Code/family-finance'
sys.path.insert(0, ROOT + '/tools')
import v61_g11_ath_returns as g
labels, vals = g.damodaran_tr()
us = sorted(((labels[i], vals[i] / vals[i - 1] - 1) for i in range(1, len(vals))), key=lambda x: -x[1])
print('美股最好三年', [(y, round(r * 100, 1)) for y, r in us[:3]], '年數', len(us), '超過 +50%：', sum(r > .5 for _, r in us), '超過 +70%：', sum(r > .7 for _, r in us))
rows = list(csv.reader(open(ROOT + '/research/data/taiex_tr_monthly_raw.csv', encoding='utf-8')))[1:]
ye = {}
for r in rows: ye[date.fromisoformat(r[0]).year] = float(r[1])
ys = sorted(ye); tw = sorted(((y, ye[y] / ye[y - 1] - 1) for y in ys[1:]), key=lambda x: -x[1])
print('台股最好三年', [(y, round(r * 100, 1)) for y, r in tw[:3]], '年數', len(tw), '超過 +50%：', sum(r > .5 for _, r in tw), '超過 +70%：', sum(r > .7 for _, r in tw))
