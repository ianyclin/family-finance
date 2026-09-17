#!/usr/bin/env python3
"""G11 裁判：獨立重算第 6 節「現在是歷史新高」的數字。

不 import calc_core 或 v61_g11_ath_returns；只照 calc_core.taiex_series 的讀法讀台股 CSV。
實作刻意和原程式不同：
  - 台股視窗終點用「指標往前走」（不用 bisect），目標日自己算（同月同日，2/29 退到 2/28）。
  - 美股含息序列用對數報酬累加再取 exp（不用連乘）。
  - 新高判定用「嚴格大於前史最高」與「大於等於前史最高」各算一次。
  - 四捨五入用 Decimal half-up，自己寫。
只讀資料，輸出印到螢幕。
"""
import csv, math, json, sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

ROOT = '/Users/linyenchu/Cladue Code/family-finance'
TW = ROOT + '/research/data/taiex_tr_monthly_raw.csv'
US = ROOT + '/research/data/shiller_sp_monthly.csv'


def hu(x, p=0):
    q = Decimal(1) if p == 0 else Decimal(1).scaleb(-p)
    v = Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP)
    return int(v) if p == 0 else float(v)


# ---------------- 台股（逐日） ----------------
rows = list(csv.reader(open(TW, encoding='utf-8')))[1:]
td = [date.fromisoformat(r[0]) for r in rows]
tv = [float(r[1]) for r in rows]
assert all(td[k] < td[k + 1] for k in range(len(td) - 1)), '日期沒有嚴格遞增'


def plus_years(d, n):
    try:
        return date(d.year + n, d.month, d.day)
    except ValueError:  # 2/29
        return date(d.year + n, d.month, 28)


def tw_pairs(n_years):
    out = []
    j = 0
    for i, d in enumerate(td):
        tgt = plus_years(d, n_years)
        if tgt > td[-1]:
            break
        if j < i:
            j = i
        while j + 1 < len(td) and td[j + 1] <= tgt:
            j += 1
        if j > i:
            out.append((i, j))
    return out


def ath_flags(vals, strict):
    flags = [False]
    prior_max = vals[0]
    for v in vals[1:]:
        flags.append(v > prior_max if strict else v >= prior_max)
        prior_max = max(prior_max, v)
    return flags


def share(pairs, vals, keep=lambda i: True):
    sel = [(i, j) for i, j in pairs if keep(i)]
    pos = sum(1 for i, j in sel if vals[j] > vals[i])
    return len(sel), pos, (100 * pos / len(sel) if sel else float('nan'))


def ann_mean(pairs, vals, years, keep=lambda i: True):
    xs = [((vals[j] / vals[i]) ** (1 / years) - 1) * 100 for i, j in pairs if keep(i)]
    return sum(xs) / len(xs), len(xs)


out = {'taiex': {}, 'us': {}}
tw_at_ge = ath_flags(tv, strict=False)
tw_at_gt = ath_flags(tv, strict=True)
out['taiex']['from_to'] = (td[0].isoformat(), td[-1].isoformat(), len(td))
out['taiex']['days_at_high_ge'] = sum(tw_at_ge)
out['taiex']['days_at_high_gt'] = sum(tw_at_gt)
out['taiex']['share_at_high_pct_1dp'] = hu(100 * sum(tw_at_ge) / (len(tv) - 1), 1)
TWP = {}
for y in (1, 3, 5, 10):
    P = TWP[y] = tw_pairs(y)
    n_all, p_all, s_all = share(P, tv)
    n_h, p_h, s_h = share(P, tv, lambda i: tw_at_ge[i])
    n_h2, p_h2, s_h2 = share(P, tv, lambda i: tw_at_gt[i])
    m_h, _ = ann_mean(P, tv, y, lambda i: tw_at_ge[i])
    m_nh, _ = ann_mean(P, tv, y, lambda i: not tw_at_ge[i])
    zero = sum(1 for i, j in P if tv[j] == tv[i])
    out['taiex']['%dy' % y] = {
        'any_day': {'n': n_all, 'pos': p_all, 'pct': round(s_all, 3), 'int': hu(s_all)},
        'at_high_ge': {'n': n_h, 'pos': p_h, 'pct': round(s_h, 3), 'int': hu(s_h)},
        'at_high_gt': {'n': n_h2, 'pos': p_h2, 'pct': round(s_h2, 3), 'int': hu(s_h2)},
        'mean_ann_at_high': round(m_h, 2), 'mean_ann_not_at_high': round(m_nh, 2),
        'exact_zero_return_windows': zero,
    }

# 3 年虧錢（終值 < 起值）與沒賺（≤）的新高起點，依年份
lose3 = {}
lose3_dates = []
for i, j in TWP[3]:
    if tw_at_ge[i] and tv[j] < tv[i]:
        lose3[td[i].year] = lose3.get(td[i].year, 0) + 1
        lose3_dates.append((td[i].isoformat(), td[j].isoformat(), round((tv[j] / tv[i] - 1) * 100, 1)))
out['taiex']['3y_losing_at_high_by_year'] = lose3
out['taiex']['3y_losing_at_high_first_last'] = (lose3_dates[0], lose3_dates[-1]) if lose3_dates else None
# 5 年虧錢的新高起點（書上沒寫，但確認「一次 2008」敘述不外溢）
lose5 = {}
for i, j in TWP[5]:
    if tw_at_ge[i] and tv[j] < tv[i]:
        lose5[td[i].year] = lose5.get(td[i].year, 0) + 1
out['taiex']['5y_losing_at_high_by_year'] = lose5

# 2007-10 前後：新高旗標與 1 年報酬
near = []
idx = {d: k for k, d in enumerate(td)}
p1 = dict(TWP[1])
for k, d in enumerate(td):
    if date(2007, 10, 15) <= d <= date(2007, 11, 30):
        j = p1.get(k)
        near.append((d.isoformat(), tw_at_ge[k], round((tv[j] / tv[k] - 1) * 100, 1) if j is not None else None))
out['taiex']['2007_oct_nov'] = near
worst = sorted((((tv[j] / tv[i]) - 1) * 100, td[i].isoformat(), tw_at_ge[i]) for i, j in TWP[1])[:6]
out['taiex']['worst6_1y'] = [(d, round(r, 1), h) for r, d, h in worst]

# ---------------- 美股（Shiller 月資料） ----------------
urows = list(csv.DictReader(open(US, encoding='utf-8')))
# 有股利資料的月份：從頭連續到第一個空白或 0
keep = []
for r in urows:
    dv = r['Dividend'].strip()
    if dv == '' or float(dv) == 0:
        break
    keep.append(r)
later_nonzero = sum(1 for r in urows[len(keep):] if r['Dividend'].strip() not in ('', '0', '0.0') and float(r['Dividend']) != 0)
um = [r['Date'][:7] for r in keep]
logs = [0.0]
for k in range(1, len(keep)):
    p0 = float(keep[k - 1]['SP500']); p1_ = float(keep[k]['SP500']); dv = float(keep[k]['Dividend'])
    logs.append(logs[-1] + math.log((p1_ + dv / 12.0) / p0))
uv = [math.exp(x) for x in logs]
us_at_ge = ath_flags(uv, strict=False)
us_at_gt = ath_flags(uv, strict=True)
out['us']['from_to'] = (um[0], um[-1], len(um), 'nonzero dividends after cut: %d' % later_nonzero)
out['us']['months_at_high_ge'] = sum(us_at_ge)
out['us']['months_at_high_gt'] = sum(us_at_gt)
out['us']['share_at_high_pct_of_all'] = round(100 * sum(us_at_ge) / len(uv), 2)
out['us']['share_at_high_pct_excl_first'] = round(100 * sum(us_at_ge) / (len(uv) - 1), 2)


def us_pairs(y):
    k = 12 * y
    return [(i, i + k) for i in range(len(uv) - k)]


USP = {}
for y in (1, 3, 5, 10):
    P = USP[y] = us_pairs(y)
    n_all, p_all, s_all = share(P, uv)
    n_h, p_h, s_h = share(P, uv, lambda i: us_at_ge[i])
    n_h2, p_h2, s_h2 = share(P, uv, lambda i: us_at_gt[i])
    out['us']['%dy' % y] = {
        'any_month': {'n': n_all, 'pos': p_all, 'pct': round(s_all, 3), 'int': hu(s_all)},
        'at_high_ge': {'n': n_h, 'pos': p_h, 'pct': round(s_h, 3), 'int': hu(s_h)},
        'at_high_gt': {'n': n_h2, 'pos': p_h2, 'pct': round(s_h2, 3), 'int': hu(s_h2)},
    }
    # 1950 前後
    sp = {}
    for lab, cond in (('before_1950', lambda i: um[i] < '1950-01'), ('1950_on', lambda i: um[i] >= '1950-01')):
        mh, nh = ann_mean(P, uv, y, lambda i: cond(i) and us_at_ge[i])
        mn, nn = ann_mean(P, uv, y, lambda i: cond(i) and not us_at_ge[i])
        _, _, sh = share(P, uv, lambda i: cond(i) and us_at_ge[i])
        _, _, sn = share(P, uv, lambda i: cond(i) and not us_at_ge[i])
        sp[lab] = {'mean_at_high': round(mh, 2), 'mean_other': round(mn, 2), 'n': (nh, nn),
                   'pos_at_high': round(sh, 2), 'pos_other': round(sn, 2)}
    out['us']['%dy' % y]['split_1950'] = sp

# 1929、2000 年的新高月份，放 5 年、10 年
for yr in ('1929', '2000'):
    lst = []
    for i, m in enumerate(um):
        if m.startswith(yr) and us_at_ge[i]:
            row = {'month': m}
            for y in (5, 10):
                if i + 12 * y < len(uv):
                    row['%dy_ann' % y] = round(((uv[i + 12 * y] / uv[i]) ** (1 / y) - 1) * 100, 2)
            lst.append(row)
    out['us']['at_high_months_' + yr] = lst
# 10 年最差的新高月份
w10 = sorted(((((uv[j] / uv[i]) ** 0.1) - 1) * 100, um[i]) for i, j in USP[10] if us_at_ge[i])[:8]
out['us']['worst8_10y_at_high'] = [(m, round(r, 2)) for r, m in w10]
neg10_years = sorted({um[i][:4] for i, j in USP[10] if us_at_ge[i] and uv[j] < uv[i]})
out['us']['years_with_negative_10y_at_high_start'] = neg10_years

json.dump(out, sys.stdout, ensure_ascii=False, indent=1, default=str)
print()

# 追加：1950 年以後、5 年、非新高月份平均的精確值（確認 10.6 還是 10.7）
if __name__ == '__main__':
    P = USP[5]
    xs = [((uv[j] / uv[i]) ** 0.2 - 1) * 100 for i, j in P if um[i] >= '1950-01' and not us_at_ge[i]]
    ys = [((uv[j] / uv[i]) ** 0.2 - 1) * 100 for i, j in P if um[i] >= '1950-01' and us_at_ge[i]]
    zs = [((uv[j] / uv[i]) ** 0.2 - 1) * 100 for i, j in P if um[i] < '1950-01' and us_at_ge[i]]
    ws = [((uv[j] / uv[i]) ** 0.2 - 1) * 100 for i, j in P if um[i] < '1950-01' and not us_at_ge[i]]
    for lab, s in (('5y 1950_on other', xs), ('5y 1950_on at_high', ys), ('5y pre1950 at_high', zs), ('5y pre1950 other', ws)):
        m = sum(s) / len(s)
        print(lab, len(s), repr(m), hu(m, 1), file=sys.stderr)
