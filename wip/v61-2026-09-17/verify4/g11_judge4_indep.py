#!/usr/bin/env python3
"""G11 裁判第 4 輪：獨立重算第 6 節 fix2 改稿後的數字。

不 import calc_core、v61_g11_ath_returns，也不讀 calc-results.json 來算（最後只拿來對照）。
刻意和模組不同的寫法：
  - 美股含息序列：log 報酬加總再 exp；股利欄第一個 0 之前截斷（同 calc_core 口徑），用 csv 逐行 split 讀。
  - 新高：「嚴格大於前史最高」與「大於等於前史最高」各算一次。
  - 台股視窗：自己算目標日（同月同日，2/29 退 2/28），指標往前走找「≤ 目標日的最後一個交易日」。
  - 四捨五入：Decimal half-up，自己寫。
只讀資料，結果印到螢幕並寫 g11_judge4_indep.out.json（在本資料夾）。
"""
import csv, math, json, os
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

ROOT = '/Users/linyenchu/Cladue Code/family-finance'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g11_judge4_indep.out.json')


def hu(x, p=0):
    q = Decimal(1) if p == 0 else Decimal(1).scaleb(-p)
    v = Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP)
    return int(v) if p == 0 else float(v)


def ath(vals, strict):
    f = [False]; m = vals[0]
    for v in vals[1:]:
        f.append(v > m if strict else v >= m)
        m = max(m, v)
    return f


O = {}

# ---------------- 美股 Shiller 月資料 ----------------
lines = open(ROOT + '/research/data/shiller_sp_monthly.csv', encoding='utf-8').read().strip().split('\n')
hdr = lines[0].split(',')
iD, iP, iDiv = hdr.index('Date'), hdr.index('SP500'), hdr.index('Dividend')
ym, P, Dv = [], [], []
for ln in lines[1:]:
    c = ln.split(',')
    if float(c[iDiv] or 0) == 0:
        break
    ym.append((int(c[iD][:4]), int(c[iD][5:7]))); P.append(float(c[iP])); Dv.append(float(c[iDiv]))
logs = [0.0]
for k in range(1, len(P)):
    logs.append(logs[-1] + math.log((P[k] + Dv[k] / 12) / P[k - 1]))
TR = [math.exp(x) for x in logs]
O['us_span'] = [ym[0], ym[-1], len(TR)]

for strict in (False, True):
    at = ath(TR, strict)
    tag = 'strict' if strict else 'ge'
    d = O.setdefault('us_' + tag, {})
    d['months_at_high'] = sum(at[1:]); d['share_pct'] = 100 * sum(at[1:]) / (len(TR) - 1)
    for yrs in (1, 5, 10):
        k = 12 * yrs
        starts = range(0, len(TR) - k)
        def grp(sel):
            xs = [i for i in starts if sel(i)]
            pos = sum(1 for i in xs if TR[i + k] > TR[i])
            ann = [((TR[i + k] / TR[i]) ** (1 / yrs) - 1) * 100 for i in xs]
            return {'n': len(xs), 'pos_pct': 100 * pos / len(xs), 'pos_int': hu(100 * pos / len(xs)),
                    'mean_ann': sum(ann) / len(ann), 'mean_ann_1': hu(sum(ann) / len(ann), 1)}
        d[f'{yrs}y'] = {'at': grp(lambda i: at[i]), 'not': grp(lambda i: not at[i]), 'all': grp(lambda i: True)}
        if yrs in (5,):
            d['split_1950_5y'] = {
                'before': {'at': grp(lambda i: at[i] and ym[i][0] < 1950), 'not': grp(lambda i: (not at[i]) and ym[i][0] < 1950)},
                'after': {'at': grp(lambda i: at[i] and ym[i][0] >= 1950), 'not': grp(lambda i: (not at[i]) and ym[i][0] >= 1950)},
            }
    # 1929、2000 年所有新高月份放 10 年；也看前一年（1928、1999）的新高月份，檢查「新高時買進」的範圍
    d['record_months_10y'] = {}
    for yr in (1928, 1929, 1999, 2000, 2007):
        rows = [(f'{ym[i][0]}-{ym[i][1]:02d}', ((TR[i + 120] / TR[i]) ** 0.1 - 1) * 100)
                for i in range(1, len(TR) - 120) if at[i] and ym[i][0] == yr]
        d['record_months_10y'][yr] = rows
    d['record_months_5y_1929_2000'] = {yr: [(f'{ym[i][0]}-{ym[i][1]:02d}', ((TR[i + 60] / TR[i]) ** 0.2 - 1) * 100)
                                           for i in range(1, len(TR) - 60) if at[i] and ym[i][0] == yr] for yr in (1929, 2000)}

# ---------------- 台股逐日 ----------------
rows = list(csv.reader(open(ROOT + '/research/data/taiex_tr_monthly_raw.csv', encoding='utf-8')))[1:]
td = [date.fromisoformat(r[0]) for r in rows]; tv = [float(r[1]) for r in rows]


def plus_years(d, n):
    try:
        return date(d.year + n, d.month, d.day)
    except ValueError:
        return date(d.year + n, d.month, 28)


def windows(n):
    out = []; j = 0
    for i, d in enumerate(td):
        tgt = plus_years(d, n)
        if tgt > td[-1]:
            break
        j = max(j, i)
        while j + 1 < len(td) and td[j + 1] <= tgt:
            j += 1
        if j > i:
            out.append((i, j))
    return out


at = ath(tv, False); at_s = ath(tv, True)
O['tw_days_at_high'] = [sum(at[1:]), sum(at_s[1:])]
low08 = min((t for t in range(len(td)) if td[t].year == 2008), key=lambda t: tv[t])
O['tw_2008_low'] = td[low08].isoformat()
for n in (1, 3, 5, 10):
    W = windows(n)
    def g(sel, W=W):
        xs = [(i, j) for i, j in W if sel(i, j)]
        pos = sum(1 for i, j in xs if tv[j] > tv[i])
        return {'n': len(xs), 'pos_pct': 100 * pos / len(xs) if xs else None, 'pos_int': hu(100 * pos / len(xs)) if xs else None}
    e = O.setdefault('tw', {})[f'{n}y'] = {'at': g(lambda i, j: at[i]), 'not': g(lambda i, j: not at[i]), 'all': g(lambda i, j: True)}
    e['gap_all_minus_at'] = e['all']['pos_pct'] - e['at']['pos_pct']
    e['gap_not_minus_at'] = e['not']['pos_pct'] - e['at']['pos_pct']
    losers = [(i, j) for i, j in W if at[i] and tv[j] <= tv[i]]
    by = {}
    for i, j in losers:
        by[td[i].year] = by.get(td[i].year, 0) + 1
    e['at_high_losers_by_start_year'] = by
    e['at_high_losers_all_span_2008_low'] = all(i <= low08 <= j for i, j in losers) if losers else None
    e['at_high_losers_end_range'] = [td[min(j for i, j in losers)].isoformat(), td[max(j for i, j in losers)].isoformat()] if losers else None
    # 非新高的虧損視窗是不是也都跨 2008 低點
    nl = [(i, j) for i, j in W if (not at[i]) and tv[j] <= tv[i]]
    e['not_high_losers'] = len(nl)
    e['not_high_losers_span_2008_low'] = sum(1 for i, j in nl if i <= low08 <= j)
    if n in (3, 5):
        ex = [(i, j) for i, j in W if not (i <= low08 <= j)]
        def gx(sel):
            xs = [(i, j) for i, j in ex if sel(i)]
            pos = sum(1 for i, j in xs if tv[j] > tv[i])
            return {'n': len(xs), 'pos_pct': 100 * pos / len(xs)}
        a_, n_, all_ = gx(lambda i: at[i]), gx(lambda i: not at[i]), gx(lambda i: True)
        e['excl_span_2008_low'] = {'at': a_, 'not': n_, 'all': all_, 'gap_not_minus_at': n_['pos_pct'] - a_['pos_pct'],
                                   'gap_all_minus_at': all_['pos_pct'] - a_['pos_pct']}
        # 另一種定義：只拿掉 2005-01-01 到 2007-12-31 的起點
        ex2 = [(i, j) for i, j in W if not (date(2005, 1, 1) <= td[i] <= date(2007, 12, 31))]
        def gy(sel):
            xs = [(i, j) for i, j in ex2 if sel(i)]
            pos = sum(1 for i, j in xs if tv[j] > tv[i])
            return 100 * pos / len(xs)
        e['excl_starts_2005_2007'] = {'at': gy(lambda i: at[i]), 'not': gy(lambda i: not at[i]), 'all': gy(lambda i: True)}
        ex3 = [(i, j) for i, j in W if not (date(2003, 1, 1) <= td[i] <= date(2007, 12, 31))]
        def gz(sel):
            xs = [(i, j) for i, j in ex3 if sel(i)]
            pos = sum(1 for i, j in xs if tv[j] > tv[i])
            return (100 * pos / len(xs), len(xs))
        e['excl_starts_2003_2007'] = {'at': gz(lambda i: at[i]), 'not': gz(lambda i: not at[i]), 'all': gz(lambda i: True)}
    if n == 1:
        r1 = [((tv[j] / tv[i] - 1) * 100, i) for i, j in W]
        worst = sorted(r1)[:12]
        e['worst12'] = [(td[i].isoformat(), round(r, 2), at[i]) for r, i in worst]
        # 2007 年所有非新高日，一年後的報酬分布
        y07 = [(r, i) for r, i in r1 if td[i].year == 2007 and not at[i]]
        e['y2007_not_high'] = {'n': len(y07), 'le_minus45': sum(1 for r, i in y07 if r <= -45),
                               'le_minus40': sum(1 for r, i in y07 if r <= -40),
                               'le_minus30': sum(1 for r, i in y07 if r <= -30),
                               'gt_0': sum(1 for r, i in y07 if r > 0),
                               'median': sorted(r for r, i in y07)[len(y07) // 2],
                               'le_minus45_dates': [td[i].isoformat() for r, i in sorted(y07, key=lambda t: t[1]) if r <= -45]}
        y07h = [(r, i) for r, i in r1 if td[i].year == 2007 and at[i]]
        e['y2007_high'] = {'n': len(y07h), 'range': [min(r for r, i in y07h), max(r for r, i in y07h)],
                           'le_minus45': sum(1 for r, i in y07h if r <= -45)}
        # 2007-10-01 到 2007-11-30 非新高日
        oct_nov = [(td[i].isoformat(), round(r, 1)) for r, i in sorted(r1, key=lambda t: t[1])
                   if date(2007, 10, 1) <= td[i] <= date(2007, 11, 30) and not at[i]]
        e['oct_nov_2007_not_high'] = oct_nov

print(json.dumps(O, ensure_ascii=False, indent=1, default=str))
json.dump(O, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)

# ---- 補充：新高月份占比分年代（正文拿掉「1871 到 2023 年」後的讀法檢查）----
at_us = ath(TR, False)
for lo, hi in ((1871, 1949), (1950, 2023), (2000, 2023)):
    idx = [i for i in range(1, len(TR)) if lo <= ym[i][0] <= hi]
    print('us share at high', lo, hi, round(100 * sum(at_us[i] for i in idx) / len(idx), 1))
