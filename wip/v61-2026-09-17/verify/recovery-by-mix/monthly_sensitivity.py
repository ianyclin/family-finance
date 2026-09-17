#!/usr/bin/env python3
"""敏感度（非圖上數字）：年度資料會把跌幅與回到前高的時間低估多少？
用 Shiller 月資料（月平均價、年化股利/12）估股票含息月報酬；
公債用同檔的長期利率（10 年期殖利率，月平均）以 10 年期平價債券重新定價估月報酬。
每年 12 月底調回比例（和圖一致）。這只是量級檢查，不是正式數字。
"""
import csv

ROOT = '/Users/linyenchu/Cladue Code/family-finance'
rows = []
with open(ROOT + '/research/data/shiller_sp_monthly.csv') as f:
    for r in csv.DictReader(f):
        y, m = int(r['Date'][:4]), int(r['Date'][5:7])
        if 1926 <= y and (y, m) <= (2023, 6):  # 2023-07 起股利為 0、2023-10 起殖利率為 0，不能用
            rows.append((y, m, float(r['SP500']), float(r['Dividend']), float(r['Long Interest Rate'])))


def bond_price(coupon, yld, years):
    n = int(round(years * 2))
    c = coupon / 2
    yy = yld / 2
    if yy == 0:
        return c * n + 1
    return c * (1 - (1 + yy) ** -n) / yy + (1 + yy) ** -n


st_r, bd_r, dates = [], [], []
for i in range(1, len(rows)):
    y, m, p, d, ly = rows[i]
    _, _, p0, _, ly0 = rows[i - 1]
    st_r.append((p + d / 12) / p0 - 1)
    y0, y1 = ly0 / 100, ly / 100
    # 近似：9.9 年剩餘期限用 10 年半年付息公式（期限差一個月可忽略）
    bd_r.append(bond_price(y0, y1, 10) - 1 + y0 / 12)
    dates.append((y, m))


def run(w, start=(1927, 12)):
    idx0 = dates.index(start) + 1 if start in dates else 0
    s, b = w, 1 - w
    vals = [(start, 1.0)]
    for i in range(idx0, len(dates)):
        s *= 1 + st_r[i]
        b *= 1 + bd_r[i]
        v = s + b
        vals.append((dates[i], v))
        if dates[i][1] == 12:
            s, b = w * v, (1 - w) * v
    return vals


def eps_of(vals):
    out = []
    pk_d, pk_v = vals[0]
    cur = None
    for d, v in vals[1:]:
        if v >= pk_v:
            if cur:
                cur['rec'] = d
                out.append(cur)
                cur = None
            pk_d, pk_v = d, v
        elif cur is None:
            cur = dict(peak=pk_d, pv=pk_v, trough=d, tv=v)
        elif v < cur['tv']:
            cur['trough'], cur['tv'] = d, v
    if cur:
        cur['rec'] = None
        out.append(cur)
    for e in out:
        e['dd'] = e['tv'] / e['pv'] - 1
        e['months'] = ((e['rec'][0] - e['peak'][0]) * 12 + e['rec'][1] - e['peak'][1]) if e['rec'] else None
    return out


# 起點 1927-12 才能和年度圖同期；月資料的前高會出在 1929
for w in [1.0, 0.8, 0.6, 0.4]:
    eps = eps_of(run(w))
    worst = min(eps, key=lambda e: e['dd'])
    rec = [e for e in eps if e['rec']]
    lng = max(rec, key=lambda e: e['months'])
    print('股票 %d%%: 最深 %.1f%% %s->%s->%s (%.1f 年)；最久 %s->%s %.1f 年' % (
        w * 100, worst['dd'] * 100, worst['peak'], worst['trough'], worst['rec'],
        (worst['months'] or 0) / 12, lng['peak'], lng['rec'], lng['months'] / 12))
    for e in eps:
        if e['dd'] < -0.15:
            print('    %s->%s->%s %.1f%% %.1f 年' % (e['peak'], e['trough'], e['rec'], e['dd'] * 100, (e['months'] or 0) / 12))
