#!/usr/bin/env python3
"""裁判獨立重算 recovery-by-mix（不 import 起草者模組）。
讀 research/data/damodaran_histret.xls 的 Returns by year，自己組股債比、自己切段落。
"""
import json
import os
from decimal import Decimal, ROUND_HALF_UP

import xlrd

ROOT = '/Users/linyenchu/Cladue Code/family-finance'
XLS = os.path.join(ROOT, 'research/data/damodaran_histret.xls')


def hu(x, nd=0):
    q = Decimal(1).scaleb(-nd)
    return Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP)


wb = xlrd.open_workbook(XLS)
sh = wb.sheet_by_name('Returns by year')
# 表頭在第 19 列（0-based），欄 1 = S&P 500 (includes dividends)，欄 4 = US T. Bond (10-year)
hdr = 19
assert sh.cell_value(hdr, 0) == 'Year'
assert sh.cell_value(hdr, 1).startswith('S&P 500 (includes dividends)')
assert sh.cell_value(hdr, 4).startswith('US T. Bond')
st, bd = {}, {}
r = hdr + 1
while isinstance(sh.cell_value(r, 0), float):
    y = int(sh.cell_value(r, 0))
    st[y] = sh.cell_value(r, 1)
    bd[y] = sh.cell_value(r, 4)
    r += 1
years = sorted(st)
print('years', years[0], years[-1], len(years))


def path(w, rebalance=True):
    vals = [(years[0] - 1, 1.0)]
    v = 1.0
    if rebalance:
        for y in years:
            v *= 1 + w * st[y] + (1 - w) * bd[y]
            vals.append((y, v))
    else:
        s, b = w, 1 - w
        for y in years:
            s *= 1 + st[y]
            b *= 1 + bd[y]
            vals.append((y, s + b))
    return vals


def drawdowns(vals):
    """獨立寫法：先算每個年底的 running max，再掃出『低於前高』的連續區間。"""
    out = []
    pk_y, pk_v = vals[0]
    i = 1
    n = len(vals)
    while i < n:
        y, v = vals[i]
        if v >= pk_v:
            pk_y, pk_v = y, v
            i += 1
            continue
        # 進入水下
        j = i
        tr_y, tr_v = y, v
        while j < n and vals[j][1] < pk_v:
            if vals[j][1] < tr_v:
                tr_y, tr_v = vals[j]
            j += 1
        rec = vals[j][0] if j < n else None
        out.append(dict(peak=pk_y, trough=tr_y, rec=rec, dd=tr_v / pk_v - 1,
                        yrs=(rec - pk_y) if rec else None,
                        under=(j - i)))
        i = j
    return out


res = {}
for w in [1.0, 0.8, 0.6, 0.4, 0.0]:
    vals = path(w)
    eps = drawdowns(vals)
    worst = min(eps, key=lambda e: e['dd'])
    recd = [e for e in eps if e['rec']]
    L = max(e['yrs'] for e in recd)
    longest = [(e['peak'], e['rec']) for e in recd if e['yrs'] == L]
    below = sum(e['under'] for e in eps)
    key = str(int(w * 100))
    print('\n== 股票 %s%% ==' % key)
    print(' worst: %s->%s->%s dd=%.4f%% int=%s' % (worst['peak'], worst['trough'], worst['rec'], worst['dd'] * 100, hu(-worst['dd'] * 100)))
    print(' longest %s yrs %s' % (L, longest))
    print(' year-ends below prior peak:', below, 'of', len(years))
    print(' unrecovered:', [(e['peak'], e['trough'], round(e['dd'] * 100, 2)) for e in eps if not e['rec']])
    print(' all episodes (dd<=-5%):')
    for e in eps:
        if e['dd'] <= -0.05:
            print('   %s->%s->%s dd=%.2f%% yrs=%s under=%s' % (e['peak'], e['trough'], e['rec'], e['dd'] * 100, e['yrs'], e['under']))
    res[key] = dict(eps=eps, worst=worst, L=L, longest=longest, below=below, vals=vals)

# 五個窗：用兩種不同定義交叉對照
WINDOWS = [('1929', 1929, 1932), ('1973-74', 1973, 1974), ('2000-02', 2000, 2002), ('2008', 2008, 2008), ('2022', 2022, 2022)]
print('\n== 五段（定義A：下跌年[peak+1..trough]和窗有交集，取最深） ==')
for k, a, b in WINDOWS:
    row = []
    for w in ['100', '80', '60', '40']:
        hits = [e for e in res[w]['eps'] if max(e['peak'] + 1, a) <= min(e['trough'], b)]
        e = min(hits, key=lambda e: e['dd']) if hits else None
        row.append(e and ('%s->%s->%s  -%s%% (%.2f) %s年' % (e['peak'], e['trough'], e['rec'], hu(-e['dd'] * 100), e['dd'] * 100, e['yrs'])))
    print(k, row)
print('\n== 五段（定義B：谷底年落在窗內） ==')
for k, a, b in WINDOWS:
    row = []
    for w in ['100', '80', '60', '40']:
        hits = [e for e in res[w]['eps'] if a <= e['trough'] <= b]
        e = min(hits, key=lambda e: e['dd']) if hits else None
        row.append(e and ('%s->%s->%s -%s%% %s年' % (e['peak'], e['trough'], e['rec'], hu(-e['dd'] * 100), e['yrs'])))
    print(k, row)

# 2022 細節
print('\n2022 各比例精確跌幅：')
for w in ['100', '80', '60', '40']:
    hits = [e for e in res[w]['eps'] if e['peak'] == 2021]
    e = hits[0]
    print(w, '%.3f%%' % (e['dd'] * 100), hu(-e['dd'] * 100, 1), hu(-e['dd'] * 100), e['rec'], e['yrs'])

# 0% 對照
e0 = [e for e in res['0']['eps'] if not e['rec']]
print('\n0% unrecovered', [(e['peak'], e['trough'], '%.3f' % (e['dd'] * 100), hu(e['dd'] * 100, 1)) for e in e0])
v0 = dict(res['0']['vals'])
print('0%% 2020->2025 change %.3f%%' % ((v0[2025] / v0[2020] - 1) * 100))

# 不再平衡對照（只看敏感度）
print('\n== 不再平衡（買入後不動）對照 ==')
for w in [0.8, 0.6, 0.4]:
    eps = drawdowns(path(w, rebalance=False))
    worst = min(eps, key=lambda e: e['dd'])
    recd = [e for e in eps if e['rec']]
    L = max(e['yrs'] for e in recd)
    print(w, 'worst %.2f%% %s->%s' % (worst['dd'] * 100, worst['peak'], worst['rec']), 'longest', L)

# 1928 年底 → 1944：100% 在 1928–1944 期間多少個年底 >= 1928 年底值
v100 = dict(res['100']['vals'])
print('\n100%: 年底值 / 1928 年底值，1928–1945')
for y in range(1928, 1946):
    print(y, '%.3f' % (v100[y] / v100[1928]), '  /1936: %.3f' % (v100[y] / v100[1936]) if y >= 1936 else '')

# 起點敏感度：換不同起點年，最久回到前高年數
print('\n== 起點敏感度：從 1946、1950、1970 起算 ==')
for start in [1946, 1950, 1970]:
    row = []
    for w in [1.0, 0.8, 0.6, 0.4]:
        vals = [(start - 1, 1.0)]
        v = 1.0
        for y in years:
            if y < start:
                continue
            v *= 1 + w * st[y] + (1 - w) * bd[y]
            vals.append((y, v))
        eps = drawdowns(vals)
        worst = min(eps, key=lambda e: e['dd'])
        L = max(e['yrs'] for e in eps if e['rec'])
        row.append('%d%%: %.0f%% / %d年' % (w * 100, worst['dd'] * 100, L))
    print(start, row)

json.dump({k: dict(worst=v['worst'], L=v['L'], longest=v['longest'], below=v['below']) for k, v in res.items()},
          open(os.path.join(os.path.dirname(__file__), 'recompute.json'), 'w'), ensure_ascii=False, indent=1, default=str)
