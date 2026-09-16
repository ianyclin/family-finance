"""G11 研究：美股（S&P 500，Shiller 月資料）在歷史新高買進之後的報酬分布。
口徑：名目、月資料（Shiller 的 SP500 欄是月平均價，不是月底價）、沒扣費用稅。
含息月指數照 tools/calc_core.py shiller_tr()：月報酬＝(P_t＋D_t/12)÷P_{t−1}，股利欄第一次為 0 就截止。
價格指數版用同一段月份的 P_t（不含息），新高也用價格指數自己判定。
四捨五入一律 half-up（Decimal）。分位數用線性內插（等同 numpy 預設 / Excel QUARTILE.INC）。
"""
import csv, json, os
from decimal import Decimal, ROUND_HALF_UP

ROOT = '/Users/linyenchu/Cladue Code/family-finance'
CSV = os.path.join(ROOT, 'research/data/shiller_sp_monthly.csv')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g11_us.json')
HORIZONS = (1, 3, 5, 10)

def rh(x, q='0.1'):
    return float(Decimal(repr(x)).quantize(Decimal(q), rounding=ROUND_HALF_UP))

def load():
    rows = list(csv.DictReader(open(CSV, encoding='utf-8')))
    end = next(i for i, r in enumerate(rows) if float(r['Dividend'] or 0) == 0)
    rows = rows[:end]
    dates = [r['Date'][:7] for r in rows]
    price = [float(r['SP500']) for r in rows]
    tr = [1.0]
    for k in range(1, len(rows)):
        p0, p1, d = price[k - 1], price[k], float(rows[k]['Dividend'])
        tr.append(tr[-1] * ((p1 + d / 12) / p0))
    return dates, price, tr

def quantile(sorted_xs, p):
    n = len(sorted_xs)
    h = (n - 1) * p
    lo = int(h); hi = min(lo + 1, n - 1)
    return sorted_xs[lo] + (h - lo) * (sorted_xs[hi] - sorted_xs[lo])

def stats(xs):
    if not xs:
        return {'n': 0}
    s = sorted(xs)
    return {
        'n': len(s),
        'median_pct': rh(quantile(s, 0.5) * 100),
        'q1_pct': rh(quantile(s, 0.25) * 100),
        'q3_pct': rh(quantile(s, 0.75) * 100),
        'min_pct': rh(s[0] * 100),
        'max_pct': rh(s[-1] * 100),
        'positive_share_pct': rh(sum(1 for x in s if x > 0) / len(s) * 100),
        'mean_pct': rh(sum(s) / len(s) * 100),
    }

def flags(v, near=0.05):
    ath, nearf, gap = [], [], []
    m = 0.0
    for x in v:
        m = max(m, x)
        g = 1 - x / m
        gap.append(g)
        ath.append(x >= m)
        nearf.append(g <= near)
    return ath, nearf, gap

def runs(flag):
    n, prev = 0, False
    for f in flag:
        if f and not prev:
            n += 1
        prev = f
    return n

def analyze(dates, v, skip_first=True):
    ath, nearf, gap = flags(v)
    N = len(v)
    start = 1 if skip_first else 0  # 第一個月「創新高」是定義上的必然，排除
    groups = {
        'all': lambda i: True,
        'ath': lambda i: ath[i],
        'within5_of_ath': lambda i: nearf[i],
        'not_ath': lambda i: not ath[i],
        'more_than5_below_ath': lambda i: not nearf[i],
        'more_than20_below_ath': lambda i: gap[i] > 0.20,
    }
    out = {'month_counts': {}, 'ath_runs': runs(ath[start:]), 'within5_runs': runs(nearf[start:]), 'horizons': {}}
    for g, f in groups.items():
        out['month_counts'][g] = sum(1 for i in range(start, N) if f(i))
    for y in HORIZONS:
        k = 12 * y
        idx = range(start, N - k)
        ann = {i: (v[i + k] / v[i]) ** (1 / y) - 1 for i in idx}
        h = {'last_start_month': dates[N - k - 1], 'end_month': dates[N - 1]}
        for g, f in groups.items():
            h[g] = stats([ann[i] for i in idx if f(i)])
        # 非重疊版：從第一個符合的月份起，每取一個就跳過 k 個月
        for g in ('all', 'ath', 'within5_of_ath'):
            picks, nxt = [], -1
            for i in idx:
                if i >= nxt and groups[g](i):
                    picks.append(ann[i]); nxt = i + k
            h[g + '_nonoverlap'] = stats(picks)
        h['ath_worst3_starts'] = [{'start': dates[i], 'annualized_pct': rh(ann[i] * 100)} for i in sorted((i for i in idx if ath[i]), key=lambda i: ann[i])[:3]]
        out['horizons'][str(y) + 'y'] = h
    return out

def subperiod(dates, v, first_month):
    i0 = dates.index(first_month)
    # 新高以全期歷史判定（到當月為止），但只統計 first_month 之後的起點
    ath, nearf, gap = flags(v)
    N = len(v); res = {}
    for y in HORIZONS:
        k = 12 * y; idx = range(max(i0, 1), N - k)
        ann = {i: (v[i + k] / v[i]) ** (1 / y) - 1 for i in idx}
        res[str(y) + 'y'] = {
            'all': stats([ann[i] for i in idx]),
            'ath': stats([ann[i] for i in idx if ath[i]]),
            'within5_of_ath': stats([ann[i] for i in idx if nearf[i]]),
        }
    return res

def main():
    dates, price, tr = load()
    R = {
        'source': 'Robert Shiller 公開月資料（research/data/shiller_sp_monthly.csv），S&P 500（1957 前為 Cowles 等回溯序列）',
        'basis': '名目、月資料（月平均價）、沒扣費用與稅；含息版股利以年化股利/12 當月再投入',
        'from': dates[0], 'to': dates[-1], 'months': len(dates),
        'end_note': '股利欄只到 %s，含息與價格兩版都在這裡截止（同一段月份）' % dates[-1],
        'definitions': {
            'ath': '該月指數 ≥ 到當月為止（含當月）所有月份的最高值；第一個月（%s）排除' % dates[0],
            'within5_of_ath': '該月指數 ≥ 到當月為止最高值的 95%（含創新高那些月）',
            'annualized': '(V[t+12N]/V[t])^(1/N) − 1，起點月到 N 年後同月',
            'quantile': '線性內插（numpy 預設）',
            'overlap': '月起點視窗大量重疊（例如 10 年視窗相鄰起點共用 119 個月），且創新高月份成群出現，樣本不是獨立的；另附非重疊抽樣（從第一個符合月起每取一個跳過 N 年）',
            'rounding': 'half-up 到 0.1 個百分點',
        },
        'total_return': analyze(dates, tr),
        'price_only': analyze(dates, price),
        'subperiod_from_1950_total_return': subperiod(dates, tr, '1950-01'),
    }
    json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for ver in ('total_return', 'price_only'):
        a = R[ver]
        print(ver, a['month_counts'], 'runs', a['ath_runs'], a['within5_runs'])
        for y, h in a['horizons'].items():
            for g in ('all', 'ath', 'within5_of_ath', 'not_ath', 'more_than5_below_ath', 'more_than20_below_ath', 'all_nonoverlap', 'ath_nonoverlap', 'within5_of_ath_nonoverlap'):
                s = h[g]; print(' ', y, g.ljust(26), s.get('n'), s.get('q1_pct'), s.get('median_pct'), s.get('q3_pct'), 'pos', s.get('positive_share_pct'), 'min', s.get('min_pct'))
    print('from1950')
    for y, h in R['subperiod_from_1950_total_return'].items():
        for g, s in h.items():
            print(' ', y, g.ljust(16), s['n'], s['q1_pct'], s['median_pct'], s['q3_pct'], 'pos', s['positive_share_pct'])

main()
