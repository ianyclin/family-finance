"""G10：不再平衡的話，股票和防守的比例會漂成什麼樣（支撐指南第 11 節「再平衡」與 5/25 門檻）。

資料來源
    research/data/damodaran_histret.xls，工作表 'Returns by year'
    Damodaran（紐約大學 Stern）Historical Returns on Stocks, Bonds and Bills
    https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html
    欄位：'S&P 500 (includes dividends)'（股票）、'3-month T.Bill'（防守，主線）、
    'US T. Bond (10-year)'（防守換成公債的敏感度，只寫進 note，不畫線）。
    讀法與 tools/calc_core.py 的 damodaran_annual() 相同（找 'Year' 表頭列、欄名 startswith 比對）。

口徑
    美國一個市場；年度資料；名目、美元、含息；沒有扣物價、費用、稅；不投入新錢、不提領。
    指南「本指南的做法」的防守是台幣定存或活存，插圖前一段也寫「股票八成、定存兩成」。
    資料集裡 1928–2025 都有 3 個月國庫券，這裡拿它代表定存（年報酬沒有一年是負的、利息低），
    和第 4 節輪換圖的「現金」用同一欄。10 年期公債股票大跌時常常上漲，會把比例拉回門檻裡，
    放定存的人不會有這一段，所以公債只當敏感度。

演算法
    1. 起點年 S 的年初（＝S−1 年底）放股票 0.8、防守 0.2。
    2. 不再平衡：每年股票 × (1＋股票報酬)、防守 × (1＋防守報酬)，年底股票占比＝股 ÷ (股＋防守)。
       一路算到資料最後一年（2025）。
    3. 每年再平衡：每年年初回到 0.8／0.2，年底調回前的占比記下來（給裁判看，不印），
       調回後就是設定的 80%，圖上畫成虛線。
    4. 5/25 門檻：門檻寬度＝min(5 個百分點, 原比例 ÷ 4)。股票 80% → min(5, 20)＝5；
       防守 20% → min(5, 5)＝5。兩邊都是股票占比 75%–85%。
       「超出」＝年底占比與 80% 的差「嚴格大於」5 個百分點（剛好 85.0% 不算）；
       另記錄有沒有落在邊界 ±0.05 個百分點內的年份（edge_cases），方便裁判確認沒有被四捨五入影響。
       年底看一次只是這張圖的取樣點（資料是年度），不是指南規定的檢查時間：指南計畫表 F 區第 22 格
       「多久看」由讀者自己填（範例小安是每月扣款後看）；年底檢查是作者規則卡（第 11 節黃框）的做法。
    5. 主圖起點選 1990：到 2025 年共 36 年，中間包含 2000–2002 與 2008 兩次大跌；
       第一次超出門檻的年數和全部起點（1928–2021）的中位數比較，記在 main.why_this_start，
       確認不是挑「跑得最快」的那一個。
       另外算 1990、2000、2009 三個起點的完整路徑，以及 1928–2021 每一個起點第一次超出門檻的年數分布。
    6. 全部起點的說法不用「最慢幾年」：最慢那個起點（1964）靠 1974 年底 75.0017% 擦邊留在門檻裡，
       差距遠小於資料精度。印出的是「最快 1 年；一半以上 N 年內、超過九成 M 年內」這種計數說法，
       並用兩種判定（嚴格 >5pp；先 half-up 到一位再 >=5pp）都算一次，兩種都成立才印（assert）。
       每一個起點「到第一次超出為止」的年份裡，離邊界 0.05pp 以內的都記進 all_starts_scan.edge_cases。
    7. 所有印在圖上的百分比一律 Decimal half-up 到小數一位（不用 Python round）。

compute() 只用標準庫＋xlrd；chart(res) 才 lazy import essay_charts。
"""
import os
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
XLS = os.path.join(ROOT, 'research', 'data', 'damodaran_histret.xls')
URL = 'https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html'

TARGET = 0.80
MAIN_START = 1990
ALT_STARTS = [1990, 2000, 2009]
SCAN_FROM, SCAN_TO = 1928, 2021   # 每個起點至少有 5 年資料可看
DEFENSE = 'bill'                  # 主線防守：3 個月國庫券；'bond' 只做敏感度
DEF_IDX = {'bill': 1, 'bond': 2}
MARK_YEAR = 2008                  # 圖中間標的那一年（股票大跌）


def r1(x):
    return float(Decimal(repr(x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))


def band_width_pp(weight_pct):
    """5/25：5 個百分點與原比例四分之一取小。"""
    return min(Decimal('5'), Decimal(str(weight_pct)) / 4)


def outside(w):
    return abs(w - TARGET) > 0.05


def outside_rounded(w):
    """敏感度判定：先 half-up 到小數一位（像讀者看到的 75.0%），再用「以上／以下」。"""
    return abs(Decimal(repr(w * 100)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP) - 80) >= 5


ROBUST_FAST, ROBUST_MOST = 4, 10   # 「一半以上 4 年內、超過九成 10 年內」


def load():
    """回傳 {年: (股票報酬, 3 個月國庫券報酬, 10 年期公債報酬)} 與三個欄名。"""
    import xlrd
    sh = xlrd.open_workbook(XLS).sheet_by_name('Returns by year')
    hdr = next(r for r in range(sh.nrows) if str(sh.cell_value(r, 0)).strip() == 'Year')
    names = [str(sh.cell_value(hdr, c)).strip() for c in range(sh.ncols)]
    col = lambda key: next(c for c, n in enumerate(names) if n.startswith(key))
    c_st, c_bl, c_bd = col('S&P 500 (includes dividends)'), col('3-month T.Bill'), col('US T. Bond')
    out = {}
    for r in range(hdr + 1, sh.nrows):
        y = sh.cell_value(r, 0)
        if isinstance(y, float) and 1900 < y < 2100:
            out[int(y)] = (float(sh.cell_value(r, c_st)), float(sh.cell_value(r, c_bl)), float(sh.cell_value(r, c_bd)))
    return out, names[c_st], names[c_bl], names[c_bd]


def drift_path(data, start, end, defense=DEFENSE):
    i = DEF_IDX[defense]
    s, b = TARGET, 1 - TARGET
    rows = []
    for y in range(start, end + 1):
        s *= 1 + data[y][0]
        b *= 1 + data[y][i]
        rows.append({'year': y, 'stock_w': s / (s + b), 'value': s + b})
    return rows


def rebalanced_path(data, start, end, defense=DEFENSE):
    i = DEF_IDX[defense]
    v = 1.0
    rows = []
    for y in range(start, end + 1):
        s, b = v * TARGET * (1 + data[y][0]), v * (1 - TARGET) * (1 + data[y][i])
        v = s + b
        rows.append({'year': y, 'pre_rebalance_stock_w': s / v, 'value': v})
    return rows


def first_breach(rows, key='stock_w'):
    for r in rows:
        if outside(r[key]):
            return r
    return None


def summarize(data, start, end, defense=DEFENSE):
    p = drift_path(data, start, end, defense)
    br = first_breach(p)
    lo = min(p, key=lambda r: r['stock_w'])
    hi = max(p, key=lambda r: r['stock_w'])
    after = [r for r in p if br and r['year'] > br['year']]
    return {
        'defense': defense, 'start': start, 'end': end,
        'first_breach_year': br['year'] if br else None,
        'first_breach_years_after_start': (br['year'] - start + 1) if br else None,
        'first_breach_direction': (('above_85' if br['stock_w'] > TARGET else 'below_75') if br else None),
        'first_breach_stock_pct': r1(br['stock_w'] * 100) if br else None,
        'years_back_inside_after_breach': [r['year'] for r in after if not outside(r['stock_w'])],
        'min_stock_pct': r1(lo['stock_w'] * 100), 'min_year': lo['year'],
        'max_stock_pct': r1(hi['stock_w'] * 100), 'max_year': hi['year'],
        'end_stock_pct': r1(p[-1]['stock_w'] * 100),
        'years_outside_band': sum(1 for r in p if outside(r['stock_w'])),
        'years_total': len(p),
    }


def edges(rows, key='stock_w'):
    """離邊界 0.05 個百分點以內：四捨五入到一位會看起來像剛好 75.0／85.0。"""
    return [{'year': r['year'], 'stock_w_raw': r[key]} for r in rows if abs(abs(r[key] - TARGET) - 0.05) < 0.0005]


def scan_starts(data, last, defense=DEFENSE):
    scan = []
    for s in range(SCAN_FROM, SCAN_TO + 1):
        sm = summarize(data, s, last, defense)
        p = drift_path(data, s, last, defense)
        br_r = next((r for r in p if outside_rounded(r['stock_w'])), None)
        upto = [r for r in p if sm['first_breach_year'] is None or r['year'] <= sm['first_breach_year']]
        scan.append({'start': s, 'years_to_breach': sm['first_breach_years_after_start'],
                     'years_to_breach_rounded_rule': (br_r['year'] - s + 1) if br_r else None,
                     'direction': sm['first_breach_direction'], 'end_stock_pct': sm['end_stock_pct'],
                     'edge_years_up_to_breach': edges(upto)})
    yrs = sorted(x['years_to_breach'] for x in scan if x['years_to_breach'] is not None)
    n = len(yrs)
    median = yrs[n // 2] if n % 2 else (yrs[n // 2 - 1] + yrs[n // 2]) / 2
    return scan, yrs, median


def compute():
    data, st_name, bl_name, bd_name = load()
    last = max(data)
    main = drift_path(data, MAIN_START, last)
    reb = rebalanced_path(data, MAIN_START, last)
    br = first_breach(main)
    br_n = br['year'] - MAIN_START + 1

    stock_band = band_width_pp(80)
    def_band = band_width_pp(20)
    assert stock_band == def_band == Decimal('5')

    # 「代表定存」的前提：國庫券年報酬沒有一年是負的
    bill_min_year = min(data, key=lambda y: data[y][1])
    assert data[bill_min_year][1] >= 0

    after = [r for r in main if r['year'] > br['year']]
    back_inside = [r['year'] for r in after if not outside(r['stock_w'])]
    lo_after = min(after, key=lambda r: r['stock_w'])
    mark = next(r for r in main if r['year'] == MARK_YEAR)

    scan, yrs, median = scan_starts(data, last)
    reb_single_year_breaches = [r['year'] for r in reb if outside(r['pre_rebalance_stock_w'])]

    # 敏感度：防守換成 10 年期公債（只進 note）
    bond_main = drift_path(data, MAIN_START, last, 'bond')
    bond_sum = summarize(data, MAIN_START, last, 'bond')
    bond_mark = next(r for r in bond_main if r['year'] == MARK_YEAR)
    _, bond_yrs, bond_median = scan_starts(data, last, 'bond')

    n_scan = len(scan)
    robust = {}
    for key in ('years_to_breach', 'years_to_breach_rounded_rule'):
        v = [x[key] for x in scan if x[key] is not None]
        robust[key] = {'min': min(v), 'within_%d' % ROBUST_FAST: sum(1 for y in v if y <= ROBUST_FAST),
                       'within_%d' % ROBUST_MOST: sum(1 for y in v if y <= ROBUST_MOST),
                       'min_count': sum(1 for y in v if y == min(v)), 'never': n_scan - len(v)}
    # 印出的三個說法，兩種判定都要成立
    for rb in robust.values():
        assert rb['min'] == 1 and rb['never'] == 0
        assert rb['within_%d' % ROBUST_FAST] * 2 > n_scan          # 一半以上
        assert rb['within_%d' % ROBUST_MOST] * 10 > n_scan * 9     # 超過九成
    scan_edges = [{'start': x['start'], 'years': x['edge_years_up_to_breach']} for x in scan if x['edge_years_up_to_breach']]

    edge_other = {'annual_rebalance_pre_rebalance_%d' % MAIN_START: edges(reb, 'pre_rebalance_stock_w'),
                  **{'no_rebalance_start_%d' % s: edges(drift_path(data, s, last)) for s in ALT_STARTS}}

    return {
        'id': 'rebalance-drift',
        'basis': {
            'market': '美國',
            'stock': 'S&P 500 含息（美元）',
            'defense': '美國 3 個月國庫券（美元），代表定存：年報酬沒有一年是負的、利息低',
            'defense_sensitivity': '美國 10 年期公債（美元，資料集用 10 年期殖利率換算的報酬，不是債券基金實績），只寫進 note',
            'frequency': '年度（只看得到每年年底）',
            'nominal': True,
            'fees_taxes_inflation': '沒有扣物價、費用、稅',
            'cashflows': '不投入新錢、不提領',
            'start_weights': {'stock': 80, 'defense': 20},
            'start_timing': '起點年的年初（＝前一年年底）',
            'check_timing': '每年年底看一次（年度資料的取樣點，不是指南規定的檢查時間；指南計畫表 F 區第 22 格由讀者自己填，年底檢查是作者規則卡、第 11 節黃框的做法）',
            'data_last_year': last,
            'bill_min_annual_return': {'year': bill_min_year, 'return': data[bill_min_year][1]},
        },
        'source': {
            'name': 'Damodaran（紐約大學 Stern）Historical Returns on Stocks, Bonds and Bills',
            'file': os.path.relpath(XLS, ROOT), 'sheet': 'Returns by year',
            'columns': [st_name, bl_name, bd_name], 'url': URL,
        },
        'returns_pct': {str(y): {'stock': r1(data[y][0] * 100), 'bill': r1(data[y][1] * 100), 'bond': r1(data[y][2] * 100)}
                        for y in (2002, MARK_YEAR)},
        'rule_5_25': {
            'stock_band_pp': float(stock_band), 'defense_band_pp': float(def_band),
            'stock_band_pct': [75.0, 85.0],
            'breach_definition': '年底股票占比與 80% 的差嚴格大於 5 個百分點',
            'edge_case_years_within_0.05pp': edges(main),
            'edge_cases_other_paths': edge_other,
        },
        'main': {
            'start': MAIN_START, 'end': last,
            'why_this_start': '到資料最後一年共 %d 年，包含 2000–2002 與 2008 兩次大跌；第一次超出門檻花 %d 年，'
                              '1928–2021 全部起點的中位數是 %s 年，比它更快的起點有 %d 個、更慢的有 %d 個'
                              % (len(main), br_n, median, sum(1 for y in yrs if y < br_n), sum(1 for y in yrs if y > br_n)),
            'series': [{'year': r['year'], 'stock_pct': r1(r['stock_w'] * 100),
                        'stock_w_raw': r['stock_w']} for r in main],
            'first_breach_year': br['year'],
            'first_breach_years_after_start': br_n,
            'first_breach_stock_pct': r1(br['stock_w'] * 100),
            'years_back_inside_band_after_breach': back_inside,
            'lowest_after_breach': {'year': lo_after['year'], 'stock_pct': r1(lo_after['stock_w'] * 100)},
            'mark_year': {'year': MARK_YEAR, 'stock_pct': r1(mark['stock_w'] * 100), 'outside_band': outside(mark['stock_w'])},
            'years_outside_band': sum(1 for r in main if outside(r['stock_w'])),
            'years_total': len(main),
            'end_stock_pct': r1(main[-1]['stock_w'] * 100),
            'end_defense_pct': r1((1 - main[-1]['stock_w']) * 100),
            'summary': summarize(data, MAIN_START, last),
        },
        'bond_sensitivity': {
            'note': '防守換成 10 年期公債：2002、2008 年公債上漲，股票占比落回門檻裡',
            'summary': bond_sum,
            'mark_year': {'year': MARK_YEAR, 'stock_pct': r1(bond_mark['stock_w'] * 100), 'outside_band': outside(bond_mark['stock_w'])},
            'scan_years_to_breach': {'min': bond_yrs[0], 'median': bond_median, 'max': bond_yrs[-1]},
        },
        'rebalanced_annually': {
            'stock_pct_after_rebalance': 80.0,
            'single_year_breach_years_before_rebalance': reb_single_year_breaches,
            'single_year_breach_count': len(reb_single_year_breaches),
            'max_single_year_pre_rebalance_pct': r1(max(r['pre_rebalance_stock_w'] for r in reb) * 100),
            'min_single_year_pre_rebalance_pct': r1(min(r['pre_rebalance_stock_w'] for r in reb) * 100),
            '_not_printed_growth_multiple': {'no_rebalance': main[-1]['value'], 'annual_rebalance': reb[-1]['value']},
        },
        'alt_starts': {str(s): {**summarize(data, s, last),
                                'series': [{'year': r['year'], 'stock_pct': r1(r['stock_w'] * 100)}
                                           for r in drift_path(data, s, last)]}
                       for s in ALT_STARTS},
        'all_starts_scan': {
            'from': SCAN_FROM, 'to': SCAN_TO, 'count': len(scan), 'never_breached': len(scan) - len(yrs),
            'years_to_breach_min': yrs[0], 'years_to_breach_median': median, 'years_to_breach_max': yrs[-1],
            'first_breach_above_85': sum(1 for x in scan if x['direction'] == 'above_85'),
            'first_breach_below_75': sum(1 for x in scan if x['direction'] == 'below_75'),
            'robust_counts': robust,
            'robust_thresholds_years': [ROBUST_FAST, ROBUST_MOST],
            'edge_cases': scan_edges,
            'faster_than_main': sum(1 for y in yrs if y < br_n),
            'slower_than_main': sum(1 for y in yrs if y > br_n),
            'rows': scan,
        },
        'printed': {},   # chart() 會用到的字串數字，下方填
    }


def chart(res):
    import essay_charts as E
    m = res['main']
    ser = [{'year': m['start'] - 1, 'stock_pct': 80.0}] + m['series']   # 起點年初＝80%
    y0, y1 = m['start'] - 1, m['end']
    vmin, vmax = 70, 100
    br_year, br_pct = m['first_breach_year'], m['first_breach_stock_pct']
    mk = m['mark_year']
    end_pct = m['end_stock_pct']
    a2000 = res['alt_starts']['2000']
    sc = res['all_starts_scan']
    bs = res['bond_sensitivity']
    rf, rm = sc['robust_thresholds_years']
    assert all(rb['min'] == sc['years_to_breach_min'] for rb in sc['robust_counts'].values())
    assert not m['years_back_inside_band_after_breach']   # 圖說寫「沒有一年回到門檻裡」的前提
    assert mk['outside_band']

    def pct(v):
        return '%.1f%%' % v

    def draw(lay):
        mob = lay.mobile
        h = 230 if mob else 290
        left, right = lay.left, lay.right - (34 if mob else 44)
        top, bottom = lay.top + 4, h - 28

        def px(y): return left + (right - left) * (y - y0) / (y1 - y0)

        def py(v): return bottom - (bottom - top) * (v - vmin) / (vmax - vmin)

        out = [E.svg_open(lay, h, '美國股票八成、現金兩成（3 個月國庫券），%d 年初放好後不再平衡，每年年底股票占比的變化' % m['start'])]
        # 門檻帶 75–85
        out.append(E.rect(left, py(85), right - left, py(75) - py(85), E.AMBER, 0, opacity='0.14'))
        out += E.grid(lay, py, [70, 75, 80, 85, 90, 95, 100], lambda v: '%d%%' % v)
        out.append(E.hline(left, right, py(80), E.INK, 1.6, '6 5'))
        # x 軸：刻度是年底
        ticks = [1990, 2000, 2010, 2020, 2025] if not mob else [1990, 2000, 2010, 2025]
        for t in ticks:
            out.append(E.text(px(t), bottom + 17, str(t), lay.fs, 'middle', E.MUTED))
        # 不再平衡那條線
        out.append(E.poly([(px(r['year']), py(r['stock_pct'])) for r in ser], E.ACCENT, lay.line))
        # 起點：年初
        sx, sy = px(y0), py(80)
        out.append(E.dot(sx, sy, E.ACCENT, 3.5))
        out.append(E.text(sx + 2, py(72.6), '%d 年初 80%%' % m['start'], lay.fs, 'start', E.MUTED, '700'))
        # 第一次超出：標籤放在 97% 高度（桌面標籤橫跨約 1995–2002，那幾年線都低於 93%），拉一條引線
        bx, by = px(br_year), py(br_pct)
        out.append(E.dot(bx, by, E.ACCENT))
        blab = ('%d 年 %s' % (br_year, pct(br_pct))) if mob else ('%d 年第一次超過 85%%：%s' % (br_year, pct(br_pct)))
        ty = py(97)
        out.append(E.text(bx if mob else bx - 4, ty, blab, lay.fl, 'middle' if mob else 'start', E.INK, '800'))
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
                   % (bx, by - 6, bx, ty + 5, E.MUTED))
        # 2008：放在點的下方（門檻帶上緣附近）
        mx, my = px(mk['year']), py(mk['stock_pct'])
        out.append(E.dot(mx, my, E.ACCENT))
        mlab = ('%d 年 %s' % (mk['year'], pct(mk['stock_pct']))) if mob else \
               ('%d 年底 %s：股市大跌那年也沒回到門檻裡' % (mk['year'], pct(mk['stock_pct'])))
        out.append(E.text(mx, my + (16 if mob else 18), mlab, lay.fs if mob else lay.fl, 'middle', E.INK, '700'))
        # 終點
        ex, ey = px(y1), py(end_pct)
        out.append(E.dot(ex, ey, E.ACCENT))
        out.append(E.text(ex + 6, ey + 4, pct(end_pct), lay.fl, 'start', E.INK, '800'))
        # 目標線右側標籤
        out.append(E.text(right + 6, py(80) + 4, '80%', lay.fs, 'start', E.INK, '700'))
        out.append('</svg>')
        return '\n'.join(out)

    lg = E.legend([(E.ACCENT, '%d 年初放股票八成、現金兩成，之後都不動：每年年底的股票占比（防守用美國 3 個月國庫券代表定存，不跌價、利息低）' % m['start']),
                   (E.INK, '虛線：設定的 80%（再平衡就是調回這裡）'),
                   (E.AMBER, '淡色帶：5/25 門檻 75% 到 85%')])
    # S49（v6.3 批 3）：圖下說明壓成三句；防守換公債的敏感度與 94 個起點的統計刪掉（數字仍在 compute() 的回傳值裡）。
    nt = E.note('%d 年初放股票 80%%、現金 20%%（防守用美國 3 個月國庫券代表定存，不跌價、利息低），之後不買不賣，每年年底看一次股票占多少；'
                '圖只看得到每年年底，兩個年底之間可能早就跑出門檻，或跑得更遠，這裡看不出來。'
                '門檻照 5/25 算：股票 80%% 的四分之一是 20 個百分點，比 5 大，取 5；現金 20%% 的四分之一剛好是 5，所以兩邊都是股票 75%% 到 85%%。'
                '這只是示意——只用美國一個市場、一個起點，換個起點跑的方向和快慢都不一樣（%d 年初開始的話先往下跑，%d 年底掉到 %s）；'
                '資料是美國 S&P 500（含息）與美國 3 個月國庫券的年度報酬，出自 Damodaran（紐約大學 Stern）公開資料集，名目、以美元計，'
                '沒有扣物價、費用和稅，也沒有投入新錢或提領，過去的走法不代表以後會一樣。'
                % (m['start'], 2000, a2000['first_breach_year'], pct(a2000['first_breach_stock_pct'])))
    caption = ('%d 年初放股票八成、現金兩成，之後都不動：第 %d 年（%d 年底）股票占比第一次超過 85%%，'
               '之後到 %d 年底沒有一年回到門檻裡，%d 年底是 %s，%d 年底變成 %s；'
               '往哪邊跑、多快跑出去，換個起點就不一樣（圖下說明有 2000 年起點先往下跑的例子）。'
               '中間虛線是設定的八成；線跑出淡色帶，就是 5/25 說該動手的時候。'
               % (m['start'], m['first_breach_years_after_start'], br_year,
                  m['end'], mk['year'], pct(mk['stock_pct']), m['end'], pct(end_pct)))
    lead = ('比例不去管它，會跑多遠？下面這張圖用美國的歷史資料，從 %d 年初放股票八成、現金兩成'
            '（美國 3 個月國庫券，接近定存）開始，之後都不買不賣，看每年年底股票占多少，'
            '淡色帶就是這個比例的 5/25 門檻。' % m['start'])
    res['printed'] = {'first_breach': [br_year, m['first_breach_years_after_start'], br_pct],
                      'mark_year': [mk['year'], mk['stock_pct']],
                      'end': [m['end'], end_pct],
                      'bond_mark_year': [bs['mark_year']['year'], bs['mark_year']['stock_pct']],
                      'alt_2000_breach': [a2000['first_breach_year'], a2000['first_breach_stock_pct']],
                      'scan_years_to_breach': [sc['from'], sc['to'], sc['count'], sc['years_to_breach_min'], rf, rm],
                      'lead_sentence': lead}
    return dict(title='不管它，比例會自己跑掉',
                sub='美國股票八成、現金兩成，每年年底股票占多少（%d 年初起算，到 %d 年底）' % (m['start'], m['end']),
                svgs=[draw(E.L('d')), draw(E.L('m'))], extras=lg + nt, caption=caption)


if __name__ == '__main__':
    import json
    r = compute()
    print(json.dumps({k: v for k, v in r.items() if k not in ('alt_starts',)}, ensure_ascii=False, indent=1)[:4000])
