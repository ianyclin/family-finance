"""裁判第二輪：G10 rebalance-drift 從原始 xls 獨立重算（不 import tools/ 任何模組，也不用第一輪 recompute.py）。

方法 A：讀『Returns by year』的年報酬欄，全部轉成 Fraction 精確有理數連乘，精確 half-up。
方法 B：讀同一工作表右側『Value of $100 invested at start of 1928』累積值欄，用 起點前一年/當年 的比值算占比（1928 起點用 100）。
兩法對照；另檢查每個印出數字離 half-up 進位邊界多遠、離 75/85 門檻多遠。
"""
import json, math, statistics
from fractions import Fraction as F
import xlrd

XLS = '/Users/linyenchu/Cladue Code/family-finance/research/data/damodaran_histret.xls'
sh = xlrd.open_workbook(XLS).sheet_by_name('Returns by year')
HDR = 19
hdr = [str(sh.cell_value(HDR, c)) for c in range(sh.ncols)]
assert hdr[0] == 'Year' and hdr[1] == 'S&P 500 (includes dividends)' and hdr[3] == '3-month T.Bill' \
    and hdr[4] == 'US T. Bond (10-year)', hdr[:5]
assert hdr[8].startswith('S&P 500 (includes dividends)') and hdr[10].startswith('3-month T.Bill') and hdr[11].startswith('US T. Bond')
ret, cum = {}, {}
for r in range(HDR + 1, sh.nrows):
    y = sh.cell_value(r, 0)
    if isinstance(y, float) and 1900 < y < 2100:
        y = int(y)
        ret[y] = {'sp': sh.cell_value(r, 1), 'bill': sh.cell_value(r, 3), 'bond': sh.cell_value(r, 4)}
        cum[y] = {'sp': sh.cell_value(r, 8), 'bill': sh.cell_value(r, 10), 'bond': sh.cell_value(r, 11)}
years = sorted(ret)
assert years == list(range(1928, 2026)), (years[0], years[-1], len(years))
LAST = years[-1]
T = F(4, 5)


def hu1(x):
    """精確 half-up 到 0.1（x 是 Fraction、正數）。回傳 (字串, 離進位邊界的距離[百分點])。"""
    q = math.floor(x * 10 + F(1, 2))
    lo_edge = (F(q) - F(1, 2)) / 10
    return '%d.%d' % (q // 10, q % 10), float(min(x - lo_edge, lo_edge + F(1, 10) - x))


def path_A(start, key):
    s, b = T, 1 - T
    out = []
    for y in range(start, LAST + 1):
        s *= 1 + F(ret[y]['sp'])
        b *= 1 + F(ret[y][key])
        out.append((y, s / (s + b)))
    return out


def path_B(start, key):
    base_s = F(100) if start == 1928 else F(cum[start - 1]['sp'])
    base_b = F(100) if start == 1928 else F(cum[start - 1][key])
    out = []
    for y in range(start, LAST + 1):
        s = T * F(cum[y]['sp']) / base_s
        b = (1 - T) * F(cum[y][key]) / base_b
        out.append((y, s / (s + b)))
    return out


def outside(w):
    return abs(w - T) > F(1, 20)


def summ(p):
    first = next(((y, w) for y, w in p if outside(w)), None)
    after = [(y, w) for y, w in p if first and y > first[0]]
    return {
        'first': None if not first else {'year': first[0], 'n': first[0] - p[0][0] + 1, 'pct': hu1(first[1] * 100)[0],
                                          'dir': 'up' if first[1] > T else 'down'},
        'back_inside': [y for y, w in after if not outside(w)],
        'min_after': None if not after else (lambda m: (m[0], hu1(m[1] * 100)[0]))(min(after, key=lambda t: t[1])),
        'min': (lambda m: (m[0], hu1(m[1] * 100)[0]))(min(p, key=lambda t: t[1])),
        'end': hu1(p[-1][1] * 100)[0], 'end_def': hu1((1 - p[-1][1]) * 100)[0],
        'n_out': sum(1 for _, w in p if outside(w)), 'n': len(p),
        'closest_to_band_edge_pp': min(float(abs(abs(w - T) - F(1, 20)) * 100) for _, w in p),
    }


out = {}
# 兩法一致
maxdiff = 0.0
for key in ('bill', 'bond'):
    for s in range(1928, 2022):
        a, b = path_A(s, key), path_B(s, key)
        maxdiff = max(maxdiff, max(abs(float(x[1] - y[1])) for x, y in zip(a, b)))
out['methodA_vs_B_max_abs_diff_share'] = maxdiff

for key in ('bill', 'bond'):
    o = {}
    for s in (1990, 2000, 2009):
        o[str(s)] = summ(path_A(s, key))
    p = path_A(1990, key)
    o['1990_2008'] = hu1(dict(p)[2008] * 100)
    o['1990_2025'] = hu1(dict(p)[2025] * 100)
    o['1990_1995'] = hu1(dict(p)[1995] * 100)
    o['2000_2001'] = hu1(dict(path_A(2000, key))[2001] * 100)
    o['1990_series'] = [(y, hu1(w * 100)[0]) for y, w in p]
    rows = []
    for s in range(1928, 2022):
        sm = summ(path_A(s, key))
        rows.append((s, sm['first']['n'] if sm['first'] else None, sm['first']['dir'] if sm['first'] else None))
    ns = [n for _, n, _ in rows if n]
    n1990 = summ(p)['first']['n']
    o['scan'] = {'count': len(rows), 'never': sum(1 for r in rows if r[1] is None), 'min': min(ns),
                 'median': statistics.median(ns), 'max': max(ns),
                 'max_start_years': [s for s, n, _ in rows if n == max(ns)],
                 'up': sum(1 for r in rows if r[2] == 'up'), 'down': sum(1 for r in rows if r[2] == 'down'),
                 'faster_than_1990': sum(1 for n in ns if n < n1990), 'slower_than_1990': sum(1 for n in ns if n > n1990),
                 'last_start_years_left': LAST - 2021 + 1}
    out[key] = o

# 每年再平衡、調回前
def reb_pre(start, key):
    res = []
    for y in range(start, LAST + 1):
        s, b = T * (1 + F(ret[y]['sp'])), (1 - T) * (1 + F(ret[y][key]))
        res.append((y, s / (s + b)))
    return res
rp = reb_pre(1990, 'bill')
out['bill']['annual_reb_pre'] = {'breach_years': [y for y, w in rp if outside(w)],
                                 'min': hu1(min(w for _, w in rp) * 100)[0], 'max': hu1(max(w for _, w in rp) * 100)[0]}

# 年報酬與國庫券最小值
out['returns_pct'] = {y: {k: hu1(F(ret[y][k]) * 100)[0] if ret[y][k] >= 0 else '-' + hu1(-F(ret[y][k]) * 100)[0]
                          for k in ('sp', 'bill', 'bond')} for y in (1990, 2000, 2001, 2002, 2008, 2022)}
bmin = min(years, key=lambda y: ret[y]['bill'])
out['bill_min'] = (bmin, ret[bmin]['bill'])
out['bill_negative_years'] = [y for y in years if ret[y]['bill'] < 0]
out['bill_avg_1990_2025_arith_pct'] = float(sum(F(ret[y]['bill']) for y in range(1990, 2026)) / 36 * 100)
out['bill_1990_1999'] = {y: ret[y]['bill'] for y in range(1990, 2000)}

# 印出數字：離 half-up 邊界與門檻
p = dict(path_A(1990, 'bill'))
pb = dict(path_A(1990, 'bond'))
p2 = dict(path_A(2000, 'bill'))
printed = {'1995 86.1': p[1995], '2008 87.7': p[2008], '2025 98.3': p[2025], 'bond 2008 78.3': pb[2008], '2000->2001 74.5': p2[2001]}
out['printed_boundary_check'] = {k: {'value': hu1(v * 100)[0], 'dist_to_halfup_edge_pp': hu1(v * 100)[1],
                                     'dist_to_band_edge_pp': float(abs(abs(v - T) - F(1, 20)) * 100)} for k, v in printed.items()}
# 5/25
out['band'] = {'stock': str(min(F(5), F(80, 4))), 'defense': str(min(F(5), F(20, 4)))}
# 圖的 y 軸 70–100 是否裝得下主線
out['main_min_max'] = (hu1(min(p.values()) * 100)[0], hu1(max(p.values()) * 100)[0])

print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
