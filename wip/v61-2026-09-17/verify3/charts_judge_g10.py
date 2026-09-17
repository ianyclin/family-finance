#!/usr/bin/env python3
"""圖表裡判：G10 rebalance-drift 獨立重算（不 import 專案模組）。

直接讀 research/data/damodaran_histret.xls 'Returns by year'，
自己找欄位（S&P 500 含息、3-month T.Bill、US T. Bond 10-year），
自己算 80/20 不再平衡路徑，half-up 用 Decimal(float) 精確值，並標出落在 .x5 邊界附近的值。
"""
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import xlrd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
XLS = os.path.join(ROOT, 'research', 'data', 'damodaran_histret.xls')


def hu1(x):
    """half-up 到小數一位；用 float 的精確十進位值。"""
    return Decimal(x).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)


def near_tie(x_pct):
    d = Decimal(x_pct) * 100
    frac = d - d.to_integral_value(rounding='ROUND_FLOOR')
    return abs(frac - Decimal(50)) < Decimal('0.01')  # 小數第二位是 5 附近（±0.0001pp）


wb = xlrd.open_workbook(XLS)
sh = wb.sheet_by_name('Returns by year')
hdr = None
for r in range(sh.nrows):
    if str(sh.cell_value(r, 0)).strip() == 'Year':
        hdr = r
        break
names = [str(sh.cell_value(hdr, c)) for c in range(sh.ncols)]
# 只取年度報酬區塊（第一組），欄位完全相等比對
c_st = names.index('S&P 500 (includes dividends)')
c_bill = names.index('3-month T.Bill')
c_bond = names.index('US T. Bond (10-year)')
data = {}
for r in range(hdr + 1, sh.nrows):
    v = sh.cell_value(r, 0)
    if isinstance(v, float) and 1900 < v < 2100:
        data[int(v)] = dict(st=sh.cell_value(r, c_st), bill=sh.cell_value(r, c_bill), bond=sh.cell_value(r, c_bond))
years = sorted(data)
assert years == list(range(years[0], years[-1] + 1)), '年份不連續'
LAST = years[-1]
out = {'cols': [names[c_st], names[c_bill], names[c_bond]], 'first_year': years[0], 'last_year': LAST}


def path(start, defense='bill', end=LAST):
    s, b = 0.8, 0.2
    rows = []
    for y in range(start, end + 1):
        s *= 1 + data[y]['st']
        b *= 1 + data[y][defense]
        rows.append((y, s / (s + b)))
    return rows


def outside_strict(w):
    return abs(w - 0.8) > 0.05


def outside_shown(w):
    return abs(hu1(w * 100) - 80) >= 5


main = path(1990)
out['main_series'] = [(y, str(hu1(w * 100)), w) for y, w in main]
out['main_near_ties'] = [(y, w * 100) for y, w in main if near_tie(w * 100)]
fb = next((y, w) for y, w in main if outside_strict(w))
out['main_first_breach'] = {'year': fb[0], 'nth_year': fb[0] - 1990 + 1, 'pct': str(hu1(fb[1] * 100)),
                            'direction': 'above' if fb[1] > 0.8 else 'below'}
after = [(y, w) for y, w in main if y > fb[0]]
out['main_back_inside_after_breach'] = [y for y, w in after if not outside_strict(w)]
out['main_back_inside_after_breach_shown_rule'] = [y for y, w in after if not outside_shown(w)]
out['main_min_after_breach'] = min(((y, str(hu1(w * 100)), w) for y, w in after), key=lambda t: t[2])
out['main_2008'] = str(hu1(dict(main)[2008] * 100))
out['main_2025'] = str(hu1(dict(main)[2025] * 100))
out['main_years_before_breach'] = [(y, str(hu1(w * 100))) for y, w in main if y <= fb[0]]

# 公債敏感度
bond = path(1990, 'bond')
bd = dict(bond)
out['bond_series'] = [(y, str(hu1(w * 100)), round(w * 100, 4), 'OUT' if outside_strict(w) else 'in') for y, w in bond]
out['bond_2002'] = (str(hu1(bd[2002] * 100)), 'inside' if not outside_strict(bd[2002]) else 'outside')
out['bond_2001'] = (str(hu1(bd[2001] * 100)), 'inside' if not outside_strict(bd[2001]) else 'outside')
out['bond_2007'] = (str(hu1(bd[2007] * 100)), 'inside' if not outside_strict(bd[2007]) else 'outside')
out['bond_2008'] = (str(hu1(bd[2008] * 100)), 'inside' if not outside_strict(bd[2008]) else 'outside')
out['bond_returns_pct'] = {y: str(hu1(data[y]['bond'] * 100)) for y in (2000, 2001, 2002, 2007, 2008)}
out['stock_returns_pct'] = {y: str(hu1(data[y]['st'] * 100)) for y in (2000, 2001, 2002, 2007, 2008)}
out['bill_returns_pct'] = {y: str(hu1(data[y]['bill'] * 100)) for y in (2000, 2001, 2002, 2007, 2008)}
out['bill_negative_years'] = [y for y in years if data[y]['bill'] < 0]
out['bill_min'] = min((data[y]['bill'], y) for y in years)

# 2000 起點
p2000 = path(2000)
fb2000 = next((y, w) for y, w in p2000 if outside_strict(w))
out['start2000'] = {'series_first5': [(y, str(hu1(w * 100))) for y, w in p2000[:5]],
                    'first_breach': (fb2000[0], str(hu1(fb2000[1] * 100)), 'above' if fb2000[1] > 0.8 else 'below')}

# 全部起點
scan = {}
for rule_name, rule in (('strict', outside_strict), ('shown', outside_shown)):
    res = {}
    for s in range(1928, 2022):
        p = path(s)
        hit = next((y for y, w in p if rule(w)), None)
        res[s] = (hit - s + 1) if hit else None
    v = [x for x in res.values() if x is not None]
    scan[rule_name] = {
        'n_starts': len(res), 'never': sum(1 for x in res.values() if x is None),
        'min': min(v), 'max': max(v), 'within4': sum(1 for x in v if x <= 4), 'within10': sum(1 for x in v if x <= 10),
        'within3': sum(1 for x in v if x <= 3), 'within5': sum(1 for x in v if x <= 5),
        'median': sorted(v)[len(v) // 2] if len(v) % 2 else (sorted(v)[len(v) // 2 - 1] + sorted(v)[len(v) // 2]) / 2,
        'slowest_starts': sorted(res.items(), key=lambda t: -(t[1] or 999))[:5],
        'min_count': sum(1 for x in v if x == min(v)),
        'main_rank_faster': sum(1 for x in v if x < out['main_first_breach']['nth_year']),
        'main_rank_slower': sum(1 for x in v if x > out['main_first_breach']['nth_year']),
    }
# 起點延伸到 2024（資料允許）時說法是否仍成立
ext = {}
for s in range(1928, LAST + 1):
    p = path(s)
    hit = next((y for y, w in p if outside_strict(w)), None)
    ext[s] = (hit - s + 1) if hit else None
out['scan'] = scan
out['scan_extended_to_last'] = {s: ext[s] for s in range(2018, LAST + 1)}
# 起點的方向
dirs = {'above': 0, 'below': 0}
for s in range(1928, 2022):
    p = path(s)
    hit = next(((y, w) for y, w in p if outside_strict(w)), None)
    dirs['above' if hit[1] > 0.8 else 'below'] += 1
out['scan_direction'] = dirs

json.dump(out, sys.stdout, ensure_ascii=False, indent=1, default=str)
