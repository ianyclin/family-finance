#!/usr/bin/env python3
"""G11 研究：在「歷史新高（含息指數）」那天／那個月／那一年底買進，之後的報酬和其他時點比起來如何。

2026-09-17（g11）起由 calc_core.py 呼叫 compute()，結果寫進 lite/calc-results.json 的 ath_returns；指南第 6 節「現在是歷史新高」那段的數字從那裡來。

資料（三份，都已在 repo 或本機）
  A. 台股：research/data/taiex_tr_monthly_raw.csv（檔名寫 monthly，內容是逐日收盤）——
     證交所發行量加權股價報酬指數（含息），2003-01-02 起。讀法照 calc_core.taiex_series()。
  B. 美股月資料：research/data/shiller_sp_monthly.csv（Robert Shiller 公開資料）。
     含息月指數照 calc_core.shiller_tr()：月報酬 ＝(P_t ＋ D_t/12) ÷ P_{t−1}，股利欄只到 2023-06。
     注意：Shiller 的 P 是「月內平均價」，不是月底收盤（G12 就是因為這點不做美股事件圖），
     所以「創新高的月份」是月平均值創新高，只能拿來看大方向。
  C. 美股年資料：research/data/damodaran_histret.xls（Damodaran，NYU Stern），S&P 500 含息當年報酬，1928–2025。
     年底值，沒有月平均的問題，但一年只有一個點，年內高點看不到。讀法照 v61_g8_recovery_by_mix.read_annual()。

定義
  「在新高」：當期含息指數 ≥ 從資料起點到當期為止的最高值（含平手）。資料起點本身不算（沒有前史），但仍當一個起點算進「不在新高」與「全部」。
  「不在新高」：其他所有起點。「全部」：兩者合計。
  「離新高 5% 內」（只算台股與美股月資料，當補充）：當期值 ≥ 到當期為止最高值 × 0.95。
  視窗：台股用日曆視窗（從某交易日到滿 N 年同一天，沒開盤取前一個交易日，同 calc_core.taiex_windows）；
        美股月資料用 N×12 個月後；年資料用 N 年後的年底。
  每個起點算年化報酬 (終值÷起值)^(1/N) − 1；各組報「年化報酬的平均數、中位數、最低、最高」與「N 年後賺錢（終值>起值）的比例」。
  視窗互相重疊，不是獨立樣本。

口徑：名目、含息（股利再投入）、沒扣費用、稅、交易成本；台股台幣、美股美元，沒有換匯。
四捨五入一律 half-up（Decimal）。
用法：python3 tools/v61_g11_ath_returns.py [--out 路徑]   （預設只印到螢幕，不寫檔）
"""
import os, sys, csv, json, bisect, statistics
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TAIEX_CSV = os.path.join(ROOT, 'research', 'data', 'taiex_tr_monthly_raw.csv')
SHILLER_CSV = os.path.join(ROOT, 'research', 'data', 'shiller_sp_monthly.csv')
XLS = os.path.join(ROOT, 'research', 'data', 'damodaran_histret.xls')


def hu(x, places=1):
    q = Decimal('1') if places == 0 else Decimal('1').scaleb(-places)
    v = Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP)
    return int(v) if places == 0 else float(v)


# ---------- 讀資料 ----------
def taiex_series():
    rows = list(csv.reader(open(TAIEX_CSV, encoding='utf-8')))[1:]
    return [date.fromisoformat(r[0]) for r in rows], [float(r[1]) for r in rows]


def shiller_tr():
    rows = list(csv.DictReader(open(SHILLER_CSV, encoding='utf-8')))
    end = next(i for i, r in enumerate(rows) if float(r['Dividend'] or 0) == 0)
    rows = rows[:end]
    tr = [1.0]
    for k in range(1, len(rows)):
        p0 = float(rows[k - 1]['SP500']); p1 = float(rows[k]['SP500']); d = float(rows[k]['Dividend'])
        tr.append(tr[-1] * ((p1 + d / 12) / p0))
    return [r['Date'][:7] for r in rows], tr


def damodaran_tr():
    import xlrd
    sh = xlrd.open_workbook(XLS).sheet_by_name('Returns by year')
    hdr = next(r for r in range(sh.nrows) if str(sh.cell_value(r, 0)).strip() == 'Year')
    names = [str(sh.cell_value(hdr, c)).strip() for c in range(sh.ncols)]
    c_st = next(c for c, n in enumerate(names) if n.startswith('S&P 500 (includes dividends)'))
    ret = {}
    for r in range(hdr + 1, sh.nrows):
        y = sh.cell_value(r, 0)
        if isinstance(y, float) and 1900 < y < 2100:
            ret[int(y)] = sh.cell_value(r, c_st)
    years = sorted(ret)
    labels, vals = [str(years[0] - 1)], [1.0]          # 1927 年底 = 1
    for y in years:
        labels.append(str(y)); vals.append(vals[-1] * (1 + ret[y]))
    return labels, vals


# ---------- 共用 ----------
def add_months(d, months):
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    dd = d.day
    while True:
        try:
            return date(y, m, dd)
        except ValueError:
            dd -= 1


def flags(vals):
    at, near, runmax = [False], [False], vals[0]
    for v in vals[1:]:
        runmax = max(runmax, v)
        at.append(v >= runmax)
        near.append(v >= runmax * 0.95)
    return at, near


def summarize(pairs, years):
    """pairs: [(起值, 終值)]"""
    if not pairs:
        return {'n': 0}
    ann = [((b / a) ** (1 / years) - 1) * 100 for a, b in pairs]
    pos = sum(1 for a, b in pairs if b > a)
    return {'n': len(pairs), 'mean_ann_pct': hu(statistics.fmean(ann)), 'median_ann_pct': hu(statistics.median(ann)),
            'min_ann_pct': hu(min(ann)), 'max_ann_pct': hu(max(ann)),
            'positive_share_pct': hu(100 * pos / len(pairs)), 'positive_share_int': hu(100 * pos / len(pairs), 0)}


def grouped(V, starts_end, at, near, years):
    """V：序列；starts_end: [(i, j)] 起點索引與終點索引；回傳各組摘要。
    （2026-09-17 整合進 calc_core 時把全域變數 V 改成參數。）"""
    return {
        'at_high': summarize([(V[i], V[j]) for i, j in starts_end if at[i]], years),
        'not_at_high': summarize([(V[i], V[j]) for i, j in starts_end if not at[i]], years),
        'within_5pct': summarize([(V[i], V[j]) for i, j in starts_end if near[i]], years) if near else None,
        'all': summarize([(V[i], V[j]) for i, j in starts_end], years),
    }


def taiex_starts_ends(dates, years):
    """台股日曆視窗，起點從索引 0 開始（和 calc_core.taiex_windows 同一套，n 才會和 rolling 一致）。
    資料第一天 at=False，所以它落在「不在新高」與「全部」，不影響「在新高」那組。"""
    se = []
    for i in range(len(dates)):
        tgt = add_months(dates[i], 12 * years)
        if tgt > dates[-1]:
            break
        j = bisect.bisect_right(dates, tgt) - 1
        if j > i:
            se.append((i, j))
    return se


def compute():
    R = {'definition': '在新高＝當期含息指數 ≥ 資料起點到當期的最高值（含平手；資料起點不算）。'
                       '年化報酬＝(終值÷起值)^(1/N)−1；視窗重疊，不是獨立樣本。名目、含息、沒扣費用稅。'
                       '起點從資料第一期開始（和 calc_core rolling 同一個 n）；資料第一期不算新高。'}

    # A. 台股逐日
    dates, vals = taiex_series()
    at, near = flags(vals)
    R['taiex_daily'] = {'source': '證交所發行量加權股價報酬指數（含息），逐日收盤', 'currency': 'TWD',
                        'from': dates[0].isoformat(), 'to': dates[-1].isoformat(), 'days': len(vals),
                        'days_at_high': sum(at[1:]), 'share_days_at_high_pct': hu(100 * sum(at[1:]) / (len(vals) - 1)),
                        'share_days_within_5pct_pct': hu(100 * sum(near[1:]) / (len(vals) - 1)),
                        'horizons': {}}
    tw_se = {}
    for y in (1, 3, 5, 10):
        se = tw_se[y] = taiex_starts_ends(dates, y)
        R['taiex_daily']['horizons'][str(y) + 'y'] = {'last_start': dates[se[-1][0]].isoformat(), **grouped(vals, se, at, near, y)}

    # 台股敏感度（簡報第 1-4 節發現 2、3、4；第 9 節第 5 條）
    tw_sens = R['taiex_daily']['sensitivity'] = {}
    # (a) 在新高買進、N 年後沒賺（終值 ≤ 起值）的起點，依起點年份計數
    tw_sens['at_high_nonpositive_by_start_year'] = {}
    for y in (1, 3, 5, 10):
        cnt = {}
        for i, j in tw_se[y]:
            if at[i] and vals[j] <= vals[i]:
                cnt[str(dates[i].year)] = cnt.get(str(dates[i].year), 0) + 1
        tw_sens['at_high_nonpositive_by_start_year'][str(y) + 'y'] = cnt
    # (b) 起點只取 2006 年以後（「新高」回看至少三年）
    tw_sens['starts_from_2006'] = {}
    for y in (1, 3, 5, 10):
        se = [(i, j) for i, j in tw_se[y] if dates[i] >= date(2006, 1, 1)]
        g = grouped(vals, se, at, None, y); g.pop('within_5pct')
        tw_sens['starts_from_2006'][str(y) + 'y'] = g
    # (c) 拿掉 2006-07-01 到 2007-12-31 的起點（2008 年那一次）
    tw_sens['excluding_starts_2006H2_2007'] = {}
    for y in (1, 3, 5):
        se = [(i, j) for i, j in tw_se[y] if not (date(2006, 7, 1) <= dates[i] <= date(2007, 12, 31))]
        g = grouped(vals, se, at, None, y); g.pop('within_5pct')
        tw_sens['excluding_starts_2006H2_2007'][str(y) + 'y'] = g
    # (d) 放 1 年最差的五個起點，和它們是不是新高日（「新高」標籤本身不是重點）
    worst = sorted(((((vals[j] / vals[i]) - 1) * 100, i) for i, j in tw_se[1]))[:5]
    tw_sens['worst5_starts_1y'] = [{'date': dates[i].isoformat(), 'ret_1y_pct': hu(r), 'at_high': at[i]} for r, i in worst]
    nh = [r for r, i in worst if not at[i]]
    tw_sens['worst5_starts_1y_not_at_high_range_pct'] = [hu(min(nh)), hu(max(nh))] if nh else None
    # (f) 2026-09-17 fix2：第 6 節「三年、五年的差距，主要就是這一次大跌」的程式擔保。
    #     拿掉「持有期間跨過 2008 年最低點」的視窗（最低點由資料算，不寫死），看新高組和其他日子還差多少。
    #     只拿掉 2006H2–2007 起點（上面 c）對 5 年不夠：2003、2004 年的新高起點也是抱進 2008 年才虧。
    y08 = [t for t in range(len(dates)) if dates[t].year == 2008]
    t08 = min(y08, key=lambda t: vals[t])
    tw_sens['low_2008_date'] = dates[t08].isoformat()
    tw_sens['excluding_windows_spanning_2008_low'] = {}
    for y in (3, 5):
        se = [(i, j) for i, j in tw_se[y] if not (i <= t08 <= j)]
        g = grouped(vals, se, at, None, y); g.pop('within_5pct')
        full = R['taiex_daily']['horizons'][str(y) + 'y']
        gap_full = full['not_at_high']['positive_share_pct'] - full['at_high']['positive_share_pct']
        gap_ex = g['not_at_high']['positive_share_pct'] - g['at_high']['positive_share_pct']
        lose_ends = [dates[j] for i, j in tw_se[y] if at[i] and vals[j] <= vals[i]]
        tw_sens['excluding_windows_spanning_2008_low'][str(y) + 'y'] = {
            **g, 'gap_pp_full': hu(gap_full), 'gap_pp_excluding': hu(gap_ex),
            'at_high_losers_end_range': [min(lose_ends).isoformat(), max(lose_ends).isoformat()]}
        # 「主要」＝拿掉跨 2008 低點的視窗後，差距剩不到原來的三分之一
        assert gap_ex < gap_full / 3, ('2008 大跌解釋不了大部分差距', y, gap_full, gap_ex)
    # 「就算挑不是新高的日子買，一年後一樣跌掉約一半」
    assert nh and all(-55 < r < -45 for r in nh), ('非新高最差起點不是約一半', nh)
    # (e) 2003–2005 的「新高」只和 2003 年以後比；這份含息資料沒有 2000 年以前的值，無法直接比 1990、2000 年高點
    tw_sens['at_high_days_by_year'] = {}
    for i in range(1, len(dates)):
        if at[i]:
            k = str(dates[i].year); tw_sens['at_high_days_by_year'][k] = tw_sens['at_high_days_by_year'].get(k, 0) + 1
    tw_sens['note_2003_2005'] = ('含息指數 2003-01-02 才開始，2003–2005 年的「新高」只是 2003 年以後的新高，'
                                 '價格上還低於 2000 年與 1990 年的高點；5 年最差的起點 2004-03-02 就屬於這種')
    # 台股反例：2007-10 前高那天、2018-01 前高、2021-12 前高 之後 1/3/5 年
    def tw_case(label, d0, d1):
        i0 = bisect.bisect_left(dates, date.fromisoformat(d0)); i1 = bisect.bisect_right(dates, date.fromisoformat(d1))
        k = max(range(i0, i1), key=lambda t: vals[t])
        out = {'label': label, 'peak_date': dates[k].isoformat(), 'is_record': at[k]}
        for y in (1, 3, 5):
            tgt = add_months(dates[k], 12 * y)
            if tgt <= dates[-1]:
                j = bisect.bisect_right(dates, tgt) - 1
                out[str(y) + 'y_ann_pct'] = hu(((vals[j] / vals[k]) ** (1 / y) - 1) * 100)
                out[str(y) + 'y_cum_pct'] = hu((vals[j] / vals[k] - 1) * 100)
        rec = next((t for t in range(k + 1, len(vals)) if vals[t] >= vals[k] and min(vals[k + 1:t + 1]) < vals[k] * 0.999), None)
        out['back_to_this_high'] = dates[rec].isoformat() if rec else None
        return out
    R['taiex_daily']['cases'] = [tw_case('2007 年高點', '2007-01-01', '2008-06-30'),
                                 tw_case('2018 年高點', '2018-01-01', '2018-12-31'),
                                 tw_case('2021–22 年高點', '2021-06-01', '2022-06-30')]

    # B. 美股月（Shiller，月平均價）
    months, tr = shiller_tr()
    at, near = flags(tr)
    R['us_monthly_shiller'] = {'source': 'Robert Shiller 公開資料，S&P 500（1957 年前為前身指數）含息、名目；價格是月內平均', 'currency': 'USD',
                               'from': months[0], 'to': months[-1], 'months': len(tr),
                               'months_at_high': sum(at[1:]), 'share_months_at_high_pct': hu(100 * sum(at[1:]) / (len(tr) - 1)),
                               'share_months_within_5pct_pct': hu(100 * sum(near[1:]) / (len(tr) - 1)),
                               'horizons': {}}
    for y in (1, 3, 5, 10, 20):
        k = 12 * y
        se = [(i, i + k) for i in range(0, len(tr) - k)]
        R['us_monthly_shiller']['horizons'][str(y) + 'y'] = {'last_start': months[se[-1][0]], **grouped(tr, se, at, near, y)}
    # 同一套算法、只取 1926 年以後（對照 Dimensional 的 1926 起點）
    i26 = months.index('1926-01')
    R['us_monthly_shiller']['from_1926'] = {}
    for y in (1, 3, 5, 10):
        k = 12 * y
        se = [(i, i + k) for i in range(i26, len(tr) - k)]
        R['us_monthly_shiller']['from_1926'][str(y) + 'y'] = grouped(tr, se, at, near, y)
    # 分期敏感度（簡報發現 1）：起點在 1950 年以前 vs 1950 年以後
    i50 = months.index('1950-01')
    R['us_monthly_shiller']['split_1950'] = {}
    for y in (1, 5, 10):
        k = 12 * y
        before = [(i, i + k) for i in range(0, min(i50, len(tr) - k))]
        after = [(i, i + k) for i in range(i50, len(tr) - k)]
        gb = grouped(tr, before, at, None, y); gb.pop('within_5pct')
        ga = grouped(tr, after, at, None, y); ga.pop('within_5pct')
        R['us_monthly_shiller']['split_1950'][str(y) + 'y'] = {'starts_before_1950': gb, 'starts_1950_on': ga}
    # 2026-09-17 fix2：「1929 年、2000 年新高時買進美股的人，放十年都還是虧的」——那一年所有新高月份都要算，不只 cases 的高點月
    R['us_monthly_shiller']['record_months_10y_ann_pct_by_year'] = {}
    for yr in (1929, 2000):
        rows = [{'month': months[i], '10y_ann_pct': hu(((tr[i + 120] / tr[i]) ** 0.1 - 1) * 100)}
                for i in range(1, len(tr) - 120) if at[i] and months[i].startswith(str(yr))]
        assert rows and all(r['10y_ann_pct'] < 0 for r in rows), ('新高月份放十年不是全部虧', yr, rows)
        R['us_monthly_shiller']['record_months_10y_ann_pct_by_year'][str(yr)] = rows

    def us_case(label, m0, m1):
        a, b = months.index(m0), months.index(m1)
        p = max(range(a, b + 1), key=lambda t: tr[t])
        out = {'label': label, 'peak_month': months[p], 'is_record': at[p]}
        if not at[p]:
            out['note'] = '這個高點不是歷史新高（前一個含息高點還沒回來），不能當成「在新高買進」的例子'
        for y in (1, 3, 5, 10, 20):
            if p + 12 * y < len(tr):
                out[str(y) + 'y_ann_pct'] = hu(((tr[p + 12 * y] / tr[p]) ** (1 / y) - 1) * 100)
        # 回到這個高點：先要有「下個月比高點低」（真的跌下去），再找之後第一個 ≥ 高點的月份。
        # 下個月就更高的話，沒有「跌下去再回來」這回事，回本欄位留 None 並標出來。
        if p + 1 < len(tr) and tr[p + 1] >= tr[p]:
            out['no_drop_next_month'] = True
            rec = None
        else:
            rec = next((t for t in range(p + 1, len(tr)) if tr[t] >= tr[p]), None)
        out['back_to_this_high'] = months[rec] if rec else None
        out['months_to_back'] = (rec - p) if rec else None
        low = min(range(p, rec if rec else len(tr)), key=lambda t: tr[t])
        out['max_drop_pct'] = hu((tr[low] / tr[p] - 1) * 100)
        out['low_month'] = months[low]
        return out
    R['us_monthly_shiller']['cases'] = [us_case('1929', '1929-01', '1929-12'),
                                        us_case('1937（不是新高：1929 年的含息高點還沒回來）', '1937-01', '1937-12'),
                                        us_case('1973', '1972-06', '1973-06'), us_case('2000', '2000-01', '2000-12'),
                                        us_case('2007', '2007-01', '2007-12')]

    # C. 美股年（Damodaran 年底）
    labels, yv = damodaran_tr()
    at, _ = flags(yv)
    R['us_annual_damodaran'] = {'source': 'Damodaran（NYU Stern）S&P 500 含息當年報酬，年底值；1927 年底=1', 'currency': 'USD',
                                'from': labels[1], 'to': labels[-1], 'years': len(yv) - 1,
                                'years_at_high': sum(at[1:]), 'share_years_at_high_pct': hu(100 * sum(at[1:]) / (len(yv) - 1)),
                                'horizons': {}}
    for y in (1, 3, 5, 10):
        se = [(i, i + y) for i in range(1, len(yv) - y)]
        g = grouped(yv, se, at, None, y); g.pop('within_5pct')
        R['us_annual_damodaran']['horizons'][str(y) + 'y'] = {'last_start': labels[se[-1][0]], **g}
    # 在新高的年底裡，之後 10 年年化最差的五個
    worst = sorted(((((yv[i + 10] / yv[i]) ** 0.1 - 1) * 100, labels[i]) for i in range(1, len(yv) - 10) if at[i]))[:5]
    R['us_annual_damodaran']['worst10y_from_record_yearends'] = [{'yearend': l, 'ann_pct': hu(v)} for v, l in worst]

    R['caveats'] = [
        '視窗重疊，相鄰起點的結果高度相關，不是獨立樣本；新高又常常連在一起出現，「在新高」那組的有效樣本比 n 少很多',
        '台股含息指數只從 2003 年開始，「新高」是相對 2003 年以後，不是相對 1990 年；又剛好從大跌後起算',
        'Shiller 價格是月內平均價，不是月底收盤；股利欄只到 2023-06',
        '平均數把不同年代混在一起；個別起點（1929、2000、2007）可以差很多',
        '名目、含息、沒扣物價、費用、稅；台股台幣、美股美元',
        '只看一國單一指數；日本 1989 年那種例子不在這三份資料裡',
    ]
    return R


if __name__ == '__main__':
    r = compute()
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    s = json.dumps(r, ensure_ascii=False, indent=1)
    if out:
        open(out, 'w', encoding='utf-8').write(s)
    print(s)
