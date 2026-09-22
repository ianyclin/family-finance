"""v7 批 S2／S6：兩個市場的長期月序列，一份實作、三個地方共用。

為什麼獨立成一支
    calc_core.py 是一支「跑起來就把全書的數字算完並寫檔」的腳本，import 它等於重跑一次；
    畫圖的模組（tools/v7_g08_long_run.py、v7_g10_holding_box.py、v7_g11_rolling_30y.py）
    只需要序列本身。所以序列的實作放這裡，calc_core.py 匯入後只負責 assert 與寫進
    lite/calc-results.json，圖的模組也匯入同一份，三邊不會各算各的。
    本檔只用標準庫。

兩條序列
    us  ：S&P 500 含息、名目。1871-01 到 2023-06 用 Robert Shiller 公開月資料，
          月報酬＝(P_t＋D_t/12)÷P_{t−1}（和 calc_core.shiller_tr() 同一個口徑）；
          Shiller 的股利欄從 2023-07 起是 0，序列在 2023-06 截止，所以 2023-07 以後
          改用 S&P 500 總報酬指數（^SP500TR）各月最後一個交易日收盤的月報酬串接，
          延長到 2026-08。串接點兩邊的口徑不完全一樣（Shiller 的價格是當月每日收盤
          平均、股利是年率÷12；SP500TR 是月底收盤、股利實際再投入），差異寫在
          research/data/README.md。
    taiex：證交所發行量加權股價指數（價格，不含息）各月最後一個交易日收盤，
          1990-01 到 2025-12。含息的報酬指數官方只從 2003 年起提供，所以要看到
          1990 年那一段就只能用價格指數；書上另一張含息的圖（2003 起）是另一份資料。
"""
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'research', 'data')
SHILLER = os.path.join(DATA, 'shiller_sp_monthly.csv')
SP500TR = os.path.join(DATA, 'sp500tr_monthend_2023_2026.csv')
TAIEX_PRICE = os.path.join(DATA, 'taiex_price_monthend_1990_2025.csv')

# 串接點：Shiller 股利欄最後一個有值的月份
SPLICE_MONTH = '2023-06'


def shiller_tr():
    """Shiller 原序列（止於股利欄最後一個有值的月份）。回傳 (months, tr)，tr[0]＝1.0。"""
    rows = list(csv.DictReader(open(SHILLER, encoding='utf-8')))
    end = next(i for i, r in enumerate(rows) if float(r['Dividend'] or 0) == 0)
    rows = rows[:end]
    tr = [1.0]
    for k in range(1, len(rows)):
        p0 = float(rows[k - 1]['SP500']); p1 = float(rows[k]['SP500']); d = float(rows[k]['Dividend'])
        tr.append(tr[-1] * ((p1 + d / 12) / p0))
    return [r['Date'][:7] for r in rows], tr


def shiller_tr_extended():
    """Shiller 序列在 2023-06 接上 ^SP500TR 的月報酬，延長到 2026-08。回傳 (months, tr)。"""
    months, tr = shiller_tr()
    assert months[-1] == SPLICE_MONTH, months[-1]
    ext = [(r['month'], float(r['sp500tr_close']))
           for r in csv.DictReader(open(SP500TR, encoding='utf-8'))]
    i0 = [m for m, _ in ext].index(SPLICE_MONTH)
    for k in range(i0 + 1, len(ext)):
        tr.append(tr[-1] * (ext[k][1] / ext[k - 1][1]))
        months.append(ext[k][0])
    return months, tr


def taiex_price_monthly():
    """台股價格指數月底收盤。回傳 (months, values, rows)；rows 保留月內最高／最低收盤那兩欄。"""
    rows = list(csv.DictReader(open(TAIEX_PRICE, encoding='utf-8')))
    return ([r['month'] for r in rows], [float(r['taiex_close']) for r in rows], rows)


def rolling_annualised(months, tr, years):
    """滾動年化報酬（%）。每一個月都當一次買進日，抱滿 years 年。

    回傳 list of (結束月, 年化%, 起始月)；視窗彼此重疊，不是互相獨立的樣本。
    """
    k = years * 12
    out = []
    for i in range(len(tr) - k):
        g = tr[i + k] / tr[i]
        out.append((months[i + k], (g ** (1.0 / years) - 1) * 100, months[i]))
    return out


def quantile(sorted_vals, p):
    """線性內插分位數（和 statistics.quantiles 的 'inclusive' 同一種）。"""
    idx = (len(sorted_vals) - 1) * p
    lo = int(idx)
    hi = min(lo + 1, len(sorted_vals) - 1)
    f = idx - lo
    return sorted_vals[lo] * (1 - f) + sorted_vals[hi] * f


def rolling_summary(months, tr, years):
    """一個持有期間的五個數字：最差、第 15 百分位、中位、第 85 百分位、最好。"""
    r = rolling_annualised(months, tr, years)
    vals = sorted(x[1] for x in r)
    worst = min(r, key=lambda x: x[1])
    best = max(r, key=lambda x: x[1])
    return {
        'years': years, 'n': len(r),
        'min': worst[1], 'min_end': worst[0], 'min_start': worst[2],
        'max': best[1], 'max_end': best[0], 'max_start': best[2],
        'p15': quantile(vals, 0.15), 'median': quantile(vals, 0.5), 'p85': quantile(vals, 0.85),
    }


def max_drawdown(months, values):
    """最大回撤：回傳 (跌幅%, 高點月, 谷底月)。用月資料算，比逐日淺。"""
    peak = None; peak_m = None; worst = (0.0, None, None)
    for m, v in zip(months, values):
        if peak is None or v > peak:
            peak, peak_m = v, m
        dd = (v / peak - 1) * 100
        if dd < worst[0]:
            worst = (dd, peak_m, m)
    return worst


def months_back_to(months, values, from_month):
    """從 from_month 那個月的收盤起算，之後第一個回到（含）那個水準的月份；沒回到就回 None。"""
    i = months.index(from_month)
    level = values[i]
    for k in range(i + 1, len(values)):
        if values[k] >= level:
            return months[k]
    return None
