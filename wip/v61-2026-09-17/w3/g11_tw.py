"""G11 台股：在歷史新高收盤日買進，之後 1/3/5/10 年的年化報酬分布，與所有交易日比較。
資料：research/data/taiex_tr_monthly_raw.csv（證交所發行量加權股價報酬指數，含息、逐日，2003-01-02–2025-12-31）。
讀法照 calc_core.taiex_series()；視窗規則照 calc_core.taiex_windows()；不 import calc_core（它 import 時會重算並寫檔）。
四捨五入一律 half-up（Decimal）。"""
import csv, json, bisect, os
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

CSV = '/Users/linyenchu/Cladue Code/family-finance/research/data/taiex_tr_monthly_raw.csv'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g11_tw.json')

def r1(x): return float(Decimal(str(x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
def r0(x): return int(Decimal(str(x)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

def taiex_series():
    rows = list(csv.reader(open(CSV, encoding='utf-8')))[1:]
    return [date.fromisoformat(r[0]) for r in rows], [float(r[1]) for r in rows]

def add_months(d, months):
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    dd = d.day
    while True:
        try: return date(y, m, dd)
        except ValueError: dd -= 1

def window_end(dates, i, months):
    tgt = add_months(dates[i], months)
    if tgt > dates[-1]: return None
    j = bisect.bisect_right(dates, tgt) - 1
    return j if j > i else None

def pct_rank(xs, q):  # 線性內插分位數（xs 已排序）
    k = (len(xs) - 1) * q; f = int(k); c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)

def summarize(anns):
    xs = sorted(anns); n = len(xs)
    if n == 0: return {'n': 0}
    pos = sum(1 for x in xs if x > 0)
    return {'n': n, 'positive': pos, 'pos_pct': r1(100 * pos / n), 'pos_pct_int': r0(100 * pos / n),
            'min_pct': r1(xs[0]), 'p10_pct': r1(pct_rank(xs, .10)), 'p25_pct': r1(pct_rank(xs, .25)),
            'median_pct': r1(pct_rank(xs, .5)), 'p75_pct': r1(pct_rank(xs, .75)), 'p90_pct': r1(pct_rank(xs, .90)),
            'max_pct': r1(xs[-1]), 'mean_pct': r1(sum(xs) / n)}

dates, vals = taiex_series()
# 歷史新高：收盤嚴格高於此前所有收盤（資料起點 2003-01-02 本身不算）
ath = [False] * len(vals); run = vals[0]
for i in range(1, len(vals)):
    if vals[i] > run: ath[i] = True
    if vals[i] > run: run = vals[i]
# 近高點：收盤距離到當天為止最高收盤不到 5%（含新高日），僅作敏感度
near5 = []; run = vals[0]
for i, v in enumerate(vals):
    run = max(run, v); near5.append(i > 0 and v >= 0.95 * run)

BURN = date(2006, 1, 1)  # 敏感度：排除前三年（「歷史」只回看不到三年時的新高）
R = {'source': 'research/data/taiex_tr_monthly_raw.csv（TWSE 發行量加權股價報酬指數，含息、名目、逐日、未扣費用稅）',
     'data_from': dates[0].isoformat(), 'data_to': dates[-1].isoformat(), 'trading_days': len(dates),
     'definition': '新高日＝收盤嚴格高於資料起點以來此前所有收盤；視窗＝滿 N 年同一天，當天沒開盤取之前最後一個交易日；年化＝(終/起)^(1/N)−1',
     'ath_days_total': sum(ath),
     'ath_days_by_year': {}, 'windows': {}, 'windows_from_2006': {}, 'near_high_5pct': {}}
for i, a in enumerate(ath):
    if a: R['ath_days_by_year'][str(dates[i].year)] = R['ath_days_by_year'].get(str(dates[i].year), 0) + 1

for yrs in (1, 3, 5, 10):
    groups = {'all': [], 'ath': [], 'non_ath': [], 'all_2006': [], 'ath_2006': [], 'near5': [], 'not_near5': []}
    starts = {'ath': [], 'all': []}
    for i in range(len(dates)):
        j = window_end(dates, i, yrs * 12)
        if j is None: continue
        a = ((vals[j] / vals[i]) ** (1 / yrs) - 1) * 100
        groups['all'].append(a); starts['all'].append(dates[i])
        (groups['ath'] if ath[i] else groups['non_ath']).append(a)
        if ath[i]: starts['ath'].append(dates[i])
        (groups['near5'] if near5[i] else groups['not_near5']).append(a)
        if dates[i] >= BURN:
            groups['all_2006'].append(a)
            if ath[i]: groups['ath_2006'].append(a)
    k = f'{yrs}年'
    R['windows'][k] = {g: summarize(groups[g]) for g in ('all', 'ath', 'non_ath')}
    R['windows'][k]['start_range_all'] = [starts['all'][0].isoformat(), starts['all'][-1].isoformat()]
    if starts['ath']:
        R['windows'][k]['start_range_ath'] = [starts['ath'][0].isoformat(), starts['ath'][-1].isoformat()]
        R['windows'][k]['ath_start_years'] = sorted({d.year for d in starts['ath']})
    R['windows_from_2006'][k] = {'all': summarize(groups['all_2006']), 'ath': summarize(groups['ath_2006'])}
    R['near_high_5pct'][k] = {'near': summarize(groups['near5']), 'not_near': summarize(groups['not_near5'])}

# 新高起點中之後為負報酬的，依起點年份計數
for yrs in (1, 3, 5, 10):
    cnt = {}
    for i in range(len(dates)):
        if not ath[i]: continue
        j = window_end(dates, i, yrs * 12)
        if j is None: continue
        if vals[j] <= vals[i]: cnt[str(dates[i].year)] = cnt.get(str(dates[i].year), 0) + 1
    R['windows'][f'{yrs}年']['ath_nonpositive_by_start_year'] = cnt

# 最差新高買點：之後最深跌幅與再創新高所需時間
worst = None
for i in range(len(dates)):
    if not ath[i]: continue
    mn = min(vals[i:]); k = vals.index(mn, i)
    dd = (mn / vals[i] - 1) * 100
    if worst is None or dd < worst[1]:
        rec = next((m for m in range(k, len(vals)) if vals[m] >= vals[i]), None)
        worst = (i, dd, k, rec)
i, dd, k, rec = worst
R['worst_ath_entry'] = {'date': dates[i].isoformat(), 'max_drawdown_after_pct': r1(dd), 'trough_date': dates[k].isoformat(),
                        'back_to_entry_date': dates[rec].isoformat() if rec is not None else None,
                        'days_to_recover_calendar': (dates[rec] - dates[i]).days if rec is not None else None}
json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: R[k] for k in ('ath_days_total', 'ath_days_by_year', 'worst_ath_entry')}, ensure_ascii=False))
for k, v in R['windows'].items():
    for g in ('all', 'ath', 'non_ath'): print(k, g, v[g])
    print(k, 'ath years', v.get('ath_start_years'), 'nonpos', v['ath_nonpositive_by_start_year'])
for k, v in R['windows_from_2006'].items(): print('2006+', k, v)
for k, v in R['near_high_5pct'].items(): print('near5', k, v)
