#!/usr/bin/env python3
"""圖表裡判：G9 country-recovery 獨立重算（不 import 專案模組）＋ G10 印出值的原始小數（看有沒有落在 half-up 邊界）。

一手出處（2026-09-17 裡判自己查）：
  美國：Federal Reserve History「The index peaked on September 3, 1929, closing at 381.17.」
        「The index did not reach the 1929 high again until November 23, 1954.」
  日本：日本經濟新聞 2024-02-22「終値は前日比836円52銭（2.19%）高の3万9098円68銭」
        「1989年12月29日に付けた史上最高値（3万8915円）」「34年2カ月ぶりに更新」
        含息版：Nikkei Inc.「the dividend-included index reached its highest price ever in February 2021」
  台灣：證交所 FMTQIK 逐日：79/02/10 收 12,495.34（1990-01～03 最高收盤）；
        109/07/22 收 12,473.27、109/07/24 收 12,304.04、109/07/27 收 12,588.30（第一次收盤超過）。
兩種算法：(a) 日數 ÷ 365.2425；(b) 曆法年月日差。
"""
import json
import os
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

ROWS = {'美國': (date(1929, 9, 3), date(1954, 11, 23)),
        '日本': (date(1989, 12, 29), date(2024, 2, 22)),
        '台灣': (date(1990, 2, 10), date(2020, 7, 27))}


def ymd(a, b):
    y, m, d = b.year - a.year, b.month - a.month, b.day - a.day
    if d < 0:
        m -= 1
        pm = (b.month - 2) % 12 + 1
        py = b.year if b.month > 1 else b.year - 1
        import calendar
        d += calendar.monthrange(py, pm)[1]
    if m < 0:
        y -= 1
        m += 12
    return y, m, d


out = {}
for k, (a, b) in ROWS.items():
    days = (b - a).days
    yrs = days / 365.2425
    out[k] = {'days': days, 'years_by_days': round(yrs, 3),
              'half_up_years': int(Decimal(repr(yrs)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)),
              'months_by_days_half_up': int(Decimal(repr(yrs * 12)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)),
              'calendar_ymd': ymd(a, b)}
out['日本_年月'] = divmod(out['日本']['months_by_days_half_up'], 12)

# G10 印出值的原始小數
try:
    here = os.path.dirname(os.path.abspath(__file__))
    g10 = json.load(open(os.path.join(here, 'charts_judge_g10.out.json'), encoding='utf-8'))
    raw = {y: w * 100 for y, _, w in g10['main_series']}
    out['G10_raw_pct'] = {'1995': raw[1995], '2008': raw[2008], '2025': raw[2025]}
except Exception as e:  # noqa
    out['G10_raw_pct'] = 'run charts_judge_g10.py first: %s' % e
print(json.dumps(out, ensure_ascii=False, indent=1))
