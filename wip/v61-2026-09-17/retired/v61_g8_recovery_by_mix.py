#!/usr/bin/env python3
"""G8：不同股債比，從前高跌下去、再回到前高各要多久（美國 1928–2025，年度資料）。

資料來源
  research/data/damodaran_histret.xls，工作表「Returns by year」（Aswath Damodaran，紐約大學 Stern，
  Historical Returns on Stocks, Bonds and Bills；https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html）。
  讀法照 tools/calc_core.py 的 damodaran_annual()：找「Year」表頭列，取欄名開頭為
  「S&P 500 (includes dividends)」與「US T. Bond」的第一欄，列值為 1900–2100 的年份。
  - 股票：S&P 500 含息，當年年報酬。
  - 防守：美國 10 年期公債當年報酬。這不是債券基金的實際報酬：資料集用 FRED 的 10 年期固定期限殖利率，
    假設年初用前一年底殖利率平價買進、年底用新殖利率重新定價（票息＋價格變動），期限每年維持 10 年。

口徑
  美國一個市場；美元；名目（不扣物價）；沒有扣費用、稅、交易成本；股利與票息全部再投入。
  年度資料：每一年只看年底一個值，年內更深的跌幅看不到，回到前高的時間也只精確到「哪一年底」。

演算法
  1. 組合：股票 w（100%、80%、60%、40%），其餘放 10 年期公債；每年年底調回原比例，
     所以每年報酬 r = w × 股票報酬 +（1 − w）× 公債報酬。另算 0%（全公債）當裁判對照，不畫。
  2. 淨值：1927 年底 = 1，逐年乘 (1 + r)，得到 1928–2025 每年年底的淨值。
  3. 段落：從 1927 年底起，逐年更新「到這一年底為止的最高淨值（前高）」。
     某年底淨值低於前高就開一段（前高那一年＝peak_year）；之後淨值更低就更新谷底年；
     第一次回到「≥ 前高」的那一年底，這一段結束（recover_year）。到 2025 年底還沒回到的，recover_year = None。
     跌幅 = 谷底淨值 ÷ 前高淨值 − 1；回到前高年數 = recover_year − peak_year（年底到年底）。
  4. 每種比例：最深跌幅那一段、最久回到前高那一段（同年數並列時全部列出）。
  5. 叫得出名字的段落：每種比例在一個年份窗內，挑「下跌年（peak_year+1 到 trough_year）和窗有交集」的段落，
     有多段時取最深那段；沒有任何交集就回傳 None（表示那幾年年底都沒有低於前高）。
     窗：1929 起＝1929–1932、1973–74、2000–02、2008、2022。
  6. 印在圖上的數字：跌幅取整數百分比、年數是整數；四捨五入一律 half-up（Decimal），不用 Python round。
"""
import os
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
XLS = os.path.join(ROOT, 'research', 'data', 'damodaran_histret.xls')
SRC_URL = 'https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html'

Y_FROM, Y_TO = 1928, 2025
MIXES = [100, 80, 60, 40]
REFERENCE_MIXES = [0]          # 只給裁判對照，不畫
NAMED = [                      # (key, 圖上標籤, 窗起, 窗迄)
    ('1929', '1929 起', 1929, 1932),
    ('1973-74', '1973–74', 1973, 1974),
    ('2000-02', '2000–02', 2000, 2002),
    ('2008', '2008', 2008, 2008),
    ('2022', '2022', 2022, 2022),
]


def hu(x, places=0):
    q = Decimal('1') if places == 0 else Decimal('1').scaleb(-places)
    v = Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP)
    return int(v) if places == 0 else float(v)


def read_annual():
    import xlrd
    sh = xlrd.open_workbook(XLS).sheet_by_name('Returns by year')
    hdr = next(r for r in range(sh.nrows) if str(sh.cell_value(r, 0)).strip() == 'Year')
    names = [str(sh.cell_value(hdr, c)).strip() for c in range(sh.ncols)]
    col = lambda key: next(c for c, n in enumerate(names) if n.startswith(key))
    c_st, c_bd = col('S&P 500 (includes dividends)'), col('US T. Bond')
    out = {}
    for r in range(hdr + 1, sh.nrows):
        y = sh.cell_value(r, 0)
        if isinstance(y, float) and 1900 < y < 2100:
            out[int(y)] = {'stock': sh.cell_value(r, c_st), 'bond10': sh.cell_value(r, c_bd)}
    return out, {'stock': names[c_st], 'bond10': names[c_bd]}


def episodes_of(values):
    """values: [(year, 年底淨值)]，第一筆是 1927 年底 = 1。"""
    eps, cur = [], None
    peak_y, peak_v = values[0]
    for y, v in values[1:]:
        if v >= peak_v:
            if cur:
                cur['recover_year'] = y
                eps.append(cur)
                cur = None
            peak_y, peak_v = y, v
        elif cur is None:
            cur = {'peak_year': peak_y, 'peak_value': peak_v, 'trough_year': y, 'trough_value': v}
        elif v < cur['trough_value']:
            cur['trough_year'], cur['trough_value'] = y, v
    if cur:
        cur['recover_year'] = None
        eps.append(cur)
    out = []
    for e in eps:
        dd = (e['trough_value'] / e['peak_value'] - 1) * 100
        rec = e['recover_year']
        out.append({
            'peak_year': e['peak_year'], 'trough_year': e['trough_year'], 'recover_year': rec,
            'peak_value': hu(e['peak_value'], 6), 'trough_value': hu(e['trough_value'], 6),
            'drawdown_pct_exact': dd, 'drawdown_pct_1dp': hu(dd, 1),
            'drop_label_pct': hu(abs(dd)),              # 圖上印的整數跌幅（正數，前面加負號）
            'years_peak_to_trough': e['trough_year'] - e['peak_year'],
            'years_peak_to_recover': (rec - e['peak_year']) if rec else None,
            'years_since_peak_at_end_if_unrecovered': (Y_TO - e['peak_year']) if rec is None else None,
            'recovered': rec is not None,
        })
    return out


def compute():
    data, colnames = read_annual()
    years = list(range(Y_FROM, Y_TO + 1))
    missing = [y for y in years if y not in data]
    if missing:
        raise ValueError('資料缺年份：%s' % missing)
    mixes = {}
    for w in MIXES + REFERENCE_MIXES:
        f = w / 100.0
        v, series, rets = 1.0, [(Y_FROM - 1, 1.0)], []
        for y in years:
            r = f * data[y]['stock'] + (1 - f) * data[y]['bond10']
            v *= 1 + r
            series.append((y, v))
            rets.append({'year': y, 'return_pct_1dp': hu(r * 100, 1)})
        eps = episodes_of(series)
        worst = min(eps, key=lambda e: e['drawdown_pct_exact'])
        rec_eps = [e for e in eps if e['recovered']]
        longest_n = max(e['years_peak_to_recover'] for e in rec_eps)
        longest = [e for e in rec_eps if e['years_peak_to_recover'] == longest_n]
        unrecovered = [e for e in eps if not e['recovered']]
        below = sum(1 for (y, val), (_, pk) in zip(series[1:], _running_peak(series)[1:]) if val < pk)
        named = {}
        for key, label, a, b in NAMED:
            hits = [e for e in eps if max(e['peak_year'] + 1, a) <= min(e['trough_year'], b)]
            named[key] = min(hits, key=lambda e: e['drawdown_pct_exact']) if hits else None
        mixes[str(w)] = {
            'stock_pct': w, 'bond_pct': 100 - w,
            'end_value_2025': hu(v, 2),
            'cagr_pct_1dp': hu((v ** (1 / len(years)) - 1) * 100, 1),
            'worst_down_year_return_pct_1dp': min(rets, key=lambda t: t['return_pct_1dp']),
            'max_drawdown': worst,
            'longest_recovery_years': longest_n,
            'longest_recovery_episodes': longest,
            'unrecovered_at_end': unrecovered,
            'year_ends_below_prior_peak': below,
            'n_episodes': len(eps),
            'n_episodes_10pct_or_more': sum(1 for e in eps if e['drawdown_pct_exact'] <= -10),
            'named': named,
            'episodes': eps,
            'annual_returns': rets,
            'values_year_end': [{'year': y, 'value': hu(val, 6)} for y, val in series],
        }
    # 裁判用：資料是否支持「股票越多，跌越深、爬越久」
    order = [str(w) for w in MIXES]
    depth = [mixes[k]['max_drawdown']['drawdown_pct_exact'] for k in order]
    longest = [mixes[k]['longest_recovery_years'] for k in order]
    checks = {
        'max_drawdown_deeper_with_more_stock': all(depth[i] < depth[i + 1] for i in range(len(depth) - 1)),
        'longest_recovery_non_increasing_as_stock_falls': all(longest[i] >= longest[i + 1] for i in range(len(longest) - 1)),
        'longest_recovery_strictly_longer_with_more_stock': all(longest[i] > longest[i + 1] for i in range(len(longest) - 1)),
        'named': {},
    }
    for key, label, a, b in NAMED:
        row = [mixes[k]['named'][key] for k in order]
        d = [e['drawdown_pct_exact'] if e else 0.0 for e in row]
        yrs = [e['years_peak_to_recover'] if e else 0 for e in row]
        checks['named'][key] = {
            'depth_deeper_with_more_stock': all(d[i] <= d[i + 1] for i in range(len(d) - 1)),
            'recovery_longer_or_equal_with_more_stock': all((yrs[i] or 99) >= (yrs[i + 1] or 99) for i in range(len(yrs) - 1)),
            'depth_spread_pct_points': hu(max(d) - min(d), 1),
        }
    return {
        'id': 'recovery-by-mix',
        'source': 'Damodaran（紐約大學 Stern）Historical Returns on Stocks, Bonds and Bills，工作表 Returns by year',
        'source_file': os.path.relpath(XLS, ROOT),
        'source_url': SRC_URL,
        'columns_used': colnames,
        'from': Y_FROM, 'to': Y_TO, 'n_years': len(years),
        'basis': {
            'market': '美國一個市場', 'currency': '美元', 'nominal': True, 'total_return': True,
            'fees_taxes': '沒有扣', 'frequency': '年度（只看每年年底）',
            'rebalance': '每年年底調回原比例',
            'stock': 'S&P 500 含息', 'defense': '美國 10 年期公債（資料集用固定期限殖利率換算的報酬，不是債券基金實績）',
        },
        'rules': {
            'episode': '年底淨值低於「到那年底為止的最高年底淨值」就開一段；第一次回到 ≥ 前高的那年底結束。',
            'drawdown': '谷底年底淨值 ÷ 前高年底淨值 − 1',
            'years_to_recover': '回到前高那一年 − 前高那一年（年底到年底）',
            'named_window': '下跌年（前高隔年到谷底年）和窗有交集的段落，取最深一段；無交集＝None',
            'rounding': '圖上跌幅取整數、half-up（Decimal）',
        },
        'mixes_charted': MIXES,
        'mixes_reference_only': REFERENCE_MIXES,
        'named_windows': [{'key': k, 'label': l, 'from': a, 'to': b} for k, l, a, b in NAMED],
        'mixes': mixes,
        'checks': checks,
        'caveats': [
            '年度資料只看年底：年內真正的最深跌幅會比圖上更深（這份資料沒有月資料，量不出深多少），回到前高的時間也只精確到哪一年底，可能差到將近一年。',
            '美國一個市場，而且是事後回頭看得到的、最後表現很好的市場。',
            '名目、美元、沒有扣物價、費用和稅：物價上漲吃掉的購買力，這張圖看不出來；扣掉物價，回到前高的年數可能更長。',
            '全公債（股票 0%%）只當對照、不畫：它 2020 年底的高點，到 2025 年底還沒回到。'.replace('%%', '%'),
            '防守是美國 10 年期公債，不是本指南建議先用的台幣定存；公債報酬是資料集用殖利率換算的。',
            '每年年底再平衡；沒有再平衡或在年中調整，結果會不同。',
            '歷史不是保證；過去回到前高，不代表以後一定回得來。',
        ],
    }


def _running_peak(series):
    out, pk = [], float('-inf')
    for y, v in series:
        pk = max(pk, v)
        out.append((y, pk))
    return out


# ======================================================================
def chart(res):
    import sys
    sys.path.insert(0, HERE)
    import essay_charts as E
    L, svg_open, text, rect = E.L, E.svg_open, E.text, E.rect
    TEAL, MUTED, ACCENT, INK, LINE = E.TEAL, E.MUTED, E.ACCENT, E.INK, E.LINE

    order = [str(w) for w in res['mixes_charted']]
    M = res['mixes']
    named = res['named_windows']
    max_drop = max(M[k]['max_drawdown']['drop_label_pct'] for k in order)
    drop_scale = 10 * -(-max_drop // 10)                 # 往上取到 10 的倍數（65 → 70）
    max_years = max(M[k]['longest_recovery_years'] for k in order)
    year_scale = max(10, max_years)

    def draw(lay):
        mob = lay.mobile
        out = []
        # ---------- 上半：1928–2025 最深一次、最久一次 ----------
        lw = 66 if mob else 86                      # 列名欄
        gap = 12 if mob else 34
        valw = 32 if mob else 40                    # 長條後面的數字空間
        colw = (lay.W - 4 - lw - gap) / 2
        ax = lw                                     # 跌幅欄起點
        bx = lw + colw + gap                        # 年數欄起點
        abar = colw - valw
        bbar = colw - valw
        y = 14
        out.append(text(ax, y, ('最深跌幅' if mob else '最深跌幅（年底比前高）'), lay.fs, 'start', MUTED, '700'))
        out.append(text(bx, y, ('最久幾年回到前高' if mob else '最久要幾年才回到前高'), lay.fs, 'start', MUTED, '700'))
        rh = 26 if mob else 28
        bh = 13 if mob else 15
        y0 = y + 10
        for i, k in enumerate(order):
            yy = y0 + i * rh
            m = M[k]
            lab = '股票 %s%%' % k
            out.append(text(4, yy + bh - 2, lab, lay.f, 'start', INK, '700'))
            dd = m['max_drawdown']['drop_label_pct']
            w1 = abar * dd / drop_scale
            out.append(rect(ax, yy + 1, w1, bh, ACCENT, 3))
            out.append(text(ax + w1 + 5, yy + bh - 1, '−%d%%' % dd, lay.fl, 'start', INK, '800'))
            n = m['longest_recovery_years']
            w2 = bbar * n / year_scale
            out.append(rect(bx, yy + 1, w2, bh, TEAL, 3))
            out.append(text(bx + w2 + 5, yy + bh - 1, '%d 年' % n, lay.fl, 'start', INK, '800'))
        y = y0 + len(order) * rh + (6 if mob else 8)
        out.append(E.hline(4, lay.W - 4, y, LINE, 1, None))

        # ---------- 下半：五段叫得出名字的 ----------
        y += 18 if mob else 20
        out.append(text(4, y, ('五段大跌，各比例分開看' if mob else '五段大跌，各比例分開看（跌幅／回到前高的年數）'),
                        lay.fs, 'start', MUTED, '700'))
        elw = 60 if mob else 86
        cw = (lay.W - 4 - elw) / len(order)
        y += 16 if mob else 18
        for j, k in enumerate(order):
            out.append(text(elw + j * cw + 4, y, ('股票 %s%%' % k) if not mob else ('%s%%' % k),
                            lay.fs, 'start', MUTED, '700'))
        y += 8 if mob else 8
        rh2 = 40 if mob else 34
        for i, nw in enumerate(named):
            yy = y + i * rh2
            if i:
                out.append(E.hline(4, lay.W - 4, yy - 2, LINE, 0.8, '2 3'))
            out.append(text(4, yy + (15 if mob else 16), nw['label'], lay.fs if mob else lay.f, 'start', INK, '700'))
            for j, k in enumerate(order):
                e = M[k]['named'][nw['key']]
                cx = elw + j * cw + 4
                barmax = cw - 12
                if e is None:
                    out.append(text(cx, yy + 15, '年底沒跌破前高', lay.fs, 'start', MUTED))
                    continue
                dd = e['drop_label_pct']
                yrs = e['years_peak_to_recover']
                ys = ('%d 年' % yrs) if yrs is not None else '未回到'
                if mob:
                    out.append(text(cx, yy + 13, '−%d%%' % dd, lay.fl, 'start', INK, '800'))
                    out.append(text(cx + 38, yy + 13, ys, lay.fs, 'start', TEAL, '700'))
                    out.append(rect(cx, yy + 20, max(1.5, barmax * dd / drop_scale), 6, ACCENT, 2))
                else:
                    out.append(text(cx, yy + 14, '−%d%%' % dd, lay.fl, 'start', INK, '800'))
                    out.append(text(cx + 44, yy + 14, ys, lay.fl, 'start', TEAL, '700'))
                    out.append(rect(cx, yy + 21, max(1.5, barmax * dd / drop_scale), 6, ACCENT, 2))
        h = int(y + len(named) * rh2) + 2
        return '\n'.join([svg_open(lay, h, '美國股債比 100%、80%、60%、40%，1928 到 2025 年最深跌幅與回到前高的年數，以及五段大跌各比例的結果')] + out + ['</svg>'])

    lg = E.legend([(ACCENT, '跌幅：前高那年底到最低那年底'), (TEAL, '年數：前高那年底到回到前高那年底')])
    m100, m40 = M['100'], M['40']
    nm = lambda key: [M[k]['named'][key] for k in order]
    n22, n00, n08 = nm('2022'), nm('2000-02'), nm('2008')
    worst_all_1929 = all(M[k]['max_drawdown']['peak_year'] == 1928 for k in order)
    d22 = sorted(set(e['drop_label_pct'] for e in n22))
    # 圖說裡的文字判斷都要資料撐得住；資料一變就停下來，不讓舊文字配新數字
    assert res['checks']['max_drawdown_deeper_with_more_stock'] and worst_all_1929
    assert len(d22) == 1 and n22[0]['years_peak_to_recover'] == min(e['years_peak_to_recover'] for e in n22) \
        and n22[0]['years_peak_to_recover'] < max(e['years_peak_to_recover'] for e in n22)
    assert all(e and e['recovered'] for e in n00 + n08 + n22)
    assert len(set(e['years_peak_to_recover'] for e in n22[1:])) == 1
    ymin = min(M[k]['longest_recovery_years'] for k in order)
    ymax = max(M[k]['longest_recovery_years'] for k in order)
    nt = E.note(
        '股票是 S&P 500 含息，其餘放美國 10 年期公債（Damodaran 資料集用殖利率換算的報酬，不是債券基金實績），'
        '每年年底調回原比例；%d–%d 年、美元、名目，沒有扣物價、費用和稅。'
        '只用每年年底的值：年內真正的最深跌幅會更深，回到前高也只算到哪一年底。'
        '四種比例最深的那一次都是 1929 年起那一段。防守放台幣定存的人，公債那一塊和自己的情況不同。'
        '只有美國一個市場，是回頭看得到的歷史，不是保證以後也回得來。'
        % (res['from'], res['to']))
    title = '股票放幾成，跌多深、多久回到前高：美國 %d–%d' % (res['from'], res['to'])
    sub = 'S&P 500 含息＋美國 10 年期公債，每年年底再平衡；年度資料、名目、美元'
    caption = ('上半是 %d–%d 年最深的一次：股票從四成放到全部，年底帳面最深跌幅從 %d%% 到 %d%%；'
               '最久回到前高的年數，四種都是 %d 到 %d 年，差得不多。'
               '下半分開看：2000–02 年股票全放的要 %d 年、股票四成 %d 年；2008 年是 %d 年和 %d 年。'
               '2022 年股票和公債一起跌，四種比例年底都跌 %d%%，股票全放的反而最早回到前高（%d 年，其他 %d 年）。'
               % (res['from'], res['to'], m40['max_drawdown']['drop_label_pct'], m100['max_drawdown']['drop_label_pct'],
                  ymin, ymax,
                  n00[0]['years_peak_to_recover'], n00[-1]['years_peak_to_recover'],
                  n08[0]['years_peak_to_recover'], n08[-1]['years_peak_to_recover'],
                  d22[0], n22[0]['years_peak_to_recover'], max(e['years_peak_to_recover'] for e in n22)))
    return dict(title=title, sub=sub, svgs=[draw(L('d')), draw(L('m'))], extras=lg + nt, caption=caption)


if __name__ == '__main__':
    import json
    r = compute()
    for k in [str(w) for w in MIXES + REFERENCE_MIXES]:
        m = r['mixes'][k]
        print('股票 %s%%: 最深 %s%%（%s–%s–%s）最久 %s 年 %s；低於前高年底數 %s' % (
            k, m['max_drawdown']['drawdown_pct_1dp'], m['max_drawdown']['peak_year'], m['max_drawdown']['trough_year'],
            m['max_drawdown']['recover_year'], m['longest_recovery_years'],
            [(e['peak_year'], e['recover_year']) for e in m['longest_recovery_episodes']], m['year_ends_below_prior_peak']))
        for nk, e in m['named'].items():
            print('   ', nk, e and (e['peak_year'], e['trough_year'], e['recover_year'], e['drawdown_pct_1dp'], e['years_peak_to_recover']))
    print(json.dumps(r['checks'], ensure_ascii=False, indent=1))
