#!/usr/bin/env python3
"""敏感度：防守換成 3 個月國庫券（較接近指南預設的台幣定存），同一套年度規則。"""
import xlrd
from decimal import Decimal, ROUND_HALF_UP
sh = xlrd.open_workbook('/Users/linyenchu/Cladue Code/family-finance/research/data/damodaran_histret.xls').sheet_by_name('Returns by year')
assert sh.cell_value(19, 3) == '3-month T.Bill'
st, tb, bd = {}, {}, {}
r = 20
while isinstance(sh.cell_value(r, 0), float):
    y = int(sh.cell_value(r, 0)); st[y] = sh.cell_value(r, 1); tb[y] = sh.cell_value(r, 3); bd[y] = sh.cell_value(r, 4); r += 1
years = sorted(st)
def eps(w, dfn):
    v = 1.0; pk_y, pk_v = 1927, 1.0; cur = None; out = []
    for y in years:
        v *= 1 + w * st[y] + (1 - w) * dfn[y]
        if v >= pk_v:
            if cur: cur['rec'] = y; out.append(cur); cur = None
            pk_y, pk_v = y, v
        elif cur is None: cur = dict(peak=pk_y, pv=pk_v, trough=y, tv=v)
        elif v < cur['tv']: cur['trough'], cur['tv'] = y, v
    if cur: cur['rec'] = None; out.append(cur)
    return out
W = [('1929', 1929, 1932), ('1937', 1937, 1941), ('1973-74', 1973, 1974), ('2000-02', 2000, 2002), ('2008', 2008, 2008), ('2022', 2022, 2022)]
for name, dfn in [('10y bond', bd), ('3m T-bill', tb)]:
    print('==', name)
    for w in [1.0, 0.8, 0.6, 0.4]:
        E = eps(w, dfn)
        worst = min(E, key=lambda e: e['tv'] / e['pv'])
        L = max(e['rec'] - e['peak'] for e in E if e['rec'])
        row = []
        for k, a, b in W:
            h = [e for e in E if max(e['peak'] + 1, a) <= min(e['trough'], b)]
            e = min(h, key=lambda e: e['tv'] / e['pv']) if h else None
            row.append('%s:%s' % (k, e and ('%.1f%%/%s' % ((e['tv'] / e['pv'] - 1) * 100, (e['rec'] - e['peak']) if e['rec'] else 'NA'))))
        print(' %d%% worst %.1f%% (%s->%s) longest %d | %s' % (w * 100, (worst['tv'] / worst['pv'] - 1) * 100, worst['peak'], worst['rec'], L, ' '.join(row)))
print('2023 bond', bd[2023], '2022 bond', bd[2022], '2022 tbill', tb[2022])
