"""G08／G09（v7 批 S2）：兩張長線圖——台股 1990 起、美股 1950 起（另做 1929 起的樣張）。

為什麼有這兩張圖
    第 8 節「跌的時候、很久沒漲的時候，記得這幾句」之後，讀者需要看見「每一件在當時
    都像世界末日，拉長看是線上的一個凹陷」。表和比例講得到「多少年是賺的」，講不到
    「那幾年長什麼樣子」。

口徑
    台股：證交所發行量加權股價指數（價格，不含息）各月最後一個交易日收盤，1990-01 到
          2025-12。含息的報酬指數官方只從 2003 年起提供，所以 1990 那一段只能用價格指數；
          含息會比這條線更陡。
    美股：S&P 500 含息、名目。1871-01 到 2023-06 用 Shiller 月資料，2023-07 起用
          S&P 500 總報酬指數串接（見 tools/v7_series.py）。指南放 1950 起那一版，
          1929 起那一版產成樣張 wip/v63-review/samples/sp500-long-run-1929.html。

版式
    縱軸對數刻度（同樣高度＝同樣的百分比，早期的跌幅才看得到）。
    事件標在圖上方的標籤帶，細虛線引到線上的圓點；手機版標籤帶只放編號，圖下（同一個
    SVG 裡）列出編號對應的年月與名稱。標籤帶用貪心排列，同一列不重疊，每一版都會
    assert 不重疊、不超出 viewBox。
    圖上只寫事件名稱與年月，不寫跌幅；跌幅與每個事件的出處寫在第 8 節的來源卡。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v7_series as S


# ---------------------------------------------------------------- 事件表
# label：圖上的短標籤（年月＋名稱）。month：標在線上的那個月。
# 每一筆的日期與名稱都有來源，寫在第 8 節來源卡（見 spec-v7-content-s.md S2）。
TAIEX_EVENTS = [
    ('1990-02', '1990/2 歷史高點'),
    ('1995-08', '1995/8 台海飛彈危機'),
    ('1997-10', '1997/10 亞洲金融風暴'),
    ('1999-09', '1999/9 九二一地震'),
    ('2000-03', '2000/3 網路泡沫'),
    ('2001-09', '2001/9 九一一'),
    ('2003-04', '2003/4 SARS'),
    ('2004-03', '2004/3 三一九槍擊'),
    ('2008-09', '2008/9 金融海嘯'),
    ('2011-08', '2011/8 歐債危機'),
    ('2015-08', '2015/8 中國股災'),
    ('2018-10', '2018/10 貿易戰'),
    ('2020-03', '2020/3 疫情'),
    ('2022-03', '2022/3 升息'),
    ('2024-08', '2024/8 單日大跌'),
    ('2025-04', '2025/4 關稅'),
]

US_EVENTS_1929 = [('1929-10', '1929/10 大蕭條')]
US_EVENTS = [
    ('1962-10', '1962/10 古巴飛彈危機'),
    ('1973-10', '1973/10 石油危機'),
    ('1987-10', '1987/10 黑色星期一'),
    ('2000-03', '2000/3 網路泡沫'),
    ('2001-09', '2001/9 九一一'),
    ('2008-09', '2008/9 金融海嘯'),
    ('2020-03', '2020/3 疫情'),
    ('2022-03', '2022/3 升息'),
]

def _tnum(m):
    y, mm = m.split('-')
    return int(y) + (int(mm) - 1) / 12.0


# ---------------------------------------------------------------- compute
def compute_taiex():
    months, values, rows = S.taiex_price_monthly()
    # 1990 年那一段：當年收盤最高的那一天、當年收盤最低的那一天，以及收盤再站回那個高點的月份。
    # 只有收盤價可查：證交所線上的開高低收（MI_5MINS_HIST）只到 1999-01-05，
    # 1990 年 2 月 12 日盤中 12,682 點那個常被引用的數字，官方 API 查不到，所以本文用收盤高點。
    y1990 = [r for r in rows if r['month'] < '1991-01']
    hi = max(y1990, key=lambda r: float(r['month_high_close']))
    lo_after = min((r for r in y1990 if r['month'] >= hi['month']),
                   key=lambda r: float(r['month_low_close']))
    lvl = float(hi['month_high_close'])
    # 只到月：本檔存的是月底收盤與月內最高／最低收盤，查不到「第一天」是哪一天。
    # 第 7 節那張三個例子的圖有逐日的日期（台灣 1990-02-10 → 2020-07-27，約 30 年），兩邊一致。
    back = next((r['month'] for r in rows
                 if r['month'] > hi['month'] and float(r['month_high_close']) >= lvl), None)
    return {
        'id': 'taiex-long-run',
        'market': 'taiex',
        'months': months, 'values': values,
        'events': [(m, lab) for m, lab in TAIEX_EVENTS if m >= months[0] and m <= months[-1]],
        'y_ticks': [2000, 3000, 5000, 10000, 20000, 30000],
        'y_fmt': lambda v: ('%d,000' % (v // 1000)),
        'x_ticks': [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025],
        'basis': {
            'source': '證交所發行量加權股價指數（價格，不含息）',
            'file': 'research/data/taiex_price_monthend_1990_2025.csv',
            'from': months[0], 'to': months[-1], 'n_months': len(months),
            'high_close': float(hi['month_high_close']), 'high_date': hi['month_high_date'],
            'low_close': float(lo_after['month_low_close']), 'low_date': lo_after['month_low_date'],
            'back_to_high_month': back,
            'max_drawdown': S.max_drawdown(months, values),
        },
    }


def compute_us(start='1950-01'):
    months, tr = S.shiller_tr_extended()
    i = months.index(start)
    m2 = months[i:]
    v2 = [v / tr[i] for v in tr[i:]]
    evs = [(m, lab) for m, lab in (US_EVENTS_1929 + US_EVENTS) if m >= start]
    y0 = int(start[:4])
    decade = 20 if (int(m2[-1][:4]) - y0) > 60 else 10
    ticks = list(range(y0 - y0 % decade + (decade if y0 % decade else 0), int(m2[-1][:4]) + 1, decade))
    hi = max(v2)
    tk = [1]
    while tk[-1] * 10 < hi * 1.2:
        tk.append(tk[-1] * 10)
    return {
        'id': 'sp500-long-run' if start == '1950-01' else 'sp500-long-run-1929',
        'market': 'us',
        'months': m2, 'values': v2,
        'events': evs,
        'y_ticks': tk,
        'y_fmt': lambda v: ('%s 倍' % ('{:,}'.format(int(v)))),
        'x_ticks': ticks,
        'basis': {
            'source': 'Shiller 月資料（S&P 500 含息、名目）1871-01～2023-06，2023-07 起用 S&P 500 總報酬指數串接',
            'file': 'research/data/shiller_sp_monthly.csv＋research/data/sp500tr_monthend_2023_2026.csv',
            'from': m2[0], 'to': m2[-1], 'n_months': len(m2),
            'end_multiple': v2[-1],
            'annualised_pct': (v2[-1] ** (12.0 / (len(v2) - 1)) - 1) * 100,
            'max_drawdown': S.max_drawdown(m2, v2),
        },
    }


# ---------------------------------------------------------------- 版面小工具
def _textw(s, fs):
    """粗估字串寬度：中日韓字元算一個字寬，其餘算 0.56 個字寬。"""
    w = 0.0
    for ch in s:
        w += 1.0 if ord(ch) > 0x2E7F else 0.56
    return w * fs


def _rows(items, gap):
    """貪心排列：items 是 (左緣, 右緣, 資料)，回傳每一筆的列號（0＝最靠近圖的那一列）。"""
    ends = []
    out = []
    for lo, hi, _ in items:
        for r, e in enumerate(ends):
            if lo >= e + gap:
                ends[r] = hi
                out.append(r)
                break
        else:
            ends.append(hi)
            out.append(len(ends) - 1)
    return out


# ---------------------------------------------------------------- chart
def chart(res):
    import essay_charts as E

    months, values, evs = res['months'], res['values'], res['events']
    t0, t1 = _tnum(months[0]), _tnum(months[-1])
    ymin = min(res['y_ticks'] + [min(values)])
    ymax = max(res['y_ticks'] + [max(values)])
    lo_log, hi_log = math.log10(ymin * 0.94), math.log10(ymax * 1.06)
    idx = {m: k for k, m in enumerate(months)}
    warnings = []

    def build(lay):
        mob = lay.mobile
        fl = 9.6 if mob else 10.8            # 標籤帶的字
        band_h = fl + 4.4                     # 標籤帶一列的高度
        items = []
        for m, lab in evs:
            k = idx.get(m)
            if k is None:
                continue
            text = lab.split(' ', 1)[0] if mob else lab
            items.append((m, lab, k, text))
        # 手機版標籤帶只放編號
        if mob:
            items = [(m, lab, k, str(n + 1)) for n, (m, lab, k, _t) in enumerate(items)]

        left = lay.left + (6 if mob else 10)
        right = lay.right - 2

        def px(m):
            return left + (right - left) * (_tnum(m) - t0) / (t1 - t0)

        # 先排標籤帶，才知道圖要多高
        boxes = []
        for m, lab, k, text in items:
            w = _textw(text, fl)
            x = px(m)
            a = x - w / 2
            a = min(max(a, 0.0), lay.W - w)
            boxes.append((a, a + w, (m, lab, k, text, x)))
        rows = _rows(boxes, 5 if mob else 7)
        nrows = max(rows) + 1
        band = nrows * band_h + 4

        plot_top = lay.top + band
        list_h = 0
        if mob:
            cols = 2
            list_rows = (len(items) + cols - 1) // cols
            list_h = 12 + list_rows * (fl + 3.6)
        h = int(plot_top + (168 if mob else 232) + 24 + list_h)
        bottom = h - 20 - list_h

        def py(v):
            return bottom - (bottom - plot_top) * (math.log10(v) - lo_log) / (hi_log - lo_log)

        out = [E.svg_open(lay, h, res['aria'])]
        # 橫格線與刻度
        for v in res['y_ticks']:
            out.append(E.hline(left, right, py(v)))
            out.append(E.text(left - 5, py(v) + lay.fs * 0.36, res['y_fmt'](v), lay.fs, 'end', E.MUTED))
        for y in res['x_ticks']:
            mm = '%d-01' % y
            if _tnum(mm) < t0 or _tnum(mm) > t1:
                continue
            out.append(E.text(px(mm), bottom + lay.f + 5, str(y), lay.f, 'middle', E.MUTED))
        # 線
        step = 1 if len(months) < 700 else 1
        pts = [(px(m), py(v)) for m, v in zip(months[::step], values[::step])]
        out.append(E.poly(pts, E.TEAL, 1.6 if mob else 1.9))
        # 標籤帶＋引線＋圓點
        placed = []
        for (a, b, (m, lab, k, text, x)), r in zip(boxes, rows):
            ty = lay.top + (nrows - 1 - r) * band_h + fl
            yv = py(values[k])
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="0.8" '
                       'stroke-dasharray="2 3" stroke-opacity="0.75"/>' % (x, ty + 3.2, x, yv - 4, E.MUTED))
            out.append(E.dot(x, yv, E.ACCENT, 3.2 if mob else 3.4))
            out.append(E.text(a, ty, text, fl, 'start', E.INK, '700'))
            placed.append((a, b, r, text))
        # 手機版：圖下編號清單（放在同一個 SVG 裡，不佔「看得到的小字」額度）
        if mob:
            cols = 2
            list_rows = (len(items) + cols - 1) // cols
            cw = (lay.W - 8) / cols
            for n, (m, lab, k, _t) in enumerate(items):
                cx = 4 + (n // list_rows) * cw
                cy = bottom + 30 + (n % list_rows) * (fl + 3.6)
                out.append(E.text(cx, cy, '%d　%s' % (n + 1, lab), fl, 'start', E.MUTED))
        out.append('</svg>')

        # 自我檢查：同一列不得重疊、不得超出 viewBox
        for i in range(len(placed)):
            a1, b1, r1, t1_ = placed[i]
            if a1 < -0.01 or b1 > lay.W + 0.01:
                warnings.append('%s %s 標籤「%s」超出 viewBox' % (res['id'], lay.kind, t1_))
            for j in range(i + 1, len(placed)):
                a2, b2, r2, t2_ = placed[j]
                if r1 == r2 and a1 < b2 and a2 < b1:
                    warnings.append('%s %s 標籤「%s」和「%s」重疊' % (res['id'], lay.kind, t1_, t2_))
        return '\n'.join(out)

    svgs = [build(E.L('d')), build(E.L('m'))]
    for w in warnings:
        print('⚠ ' + w)
    more = ('<details class="more"><summary>想深入：這張圖的資料、期間和沒算進去的東西</summary>'
            '<p class="note">%s</p></details>' % E.esc(res['more']))
    return dict(title=res['title'], sub=res['sub'], svgs=svgs,
                extras=E.note(res['note']) + more, caption=res['caption'])


# ---------------------------------------------------------------- 三個進入點
def taiex():
    r = compute_taiex()
    b = r['basis']
    r['aria'] = '台股 1990 到 2025 年的長期走勢（對數刻度），線上標出十六件當時的大事'
    r['title'] = '台股這 36 年：每一件大事，事後看是線上的一個凹陷'
    r['sub'] = '發行量加權股價指數（不含股利），1990–2025，月底收盤，對數刻度'
    r['note'] = '這是價格指數，不含股利；把股利算進去，這條線會更陡。'
    r['more'] = ('證交所發行量加權股價指數，各月最後一個交易日收盤，%s 年 %d 月到 %s 年 %d 月，共 %d 個月。'
                 '含息的報酬指數官方只從 2003 年起提供，所以要看到 1990 年那一段就只能用價格指數；'
                 '本節另一張表和另一張圖用的是含息那一份。沒有扣物價、費用和稅。'
                 '圖上只標事件的名稱和年月，每一件的日期出處與當時的跌幅寫在本節來源卡。'
                 % (b['from'][:4], int(b['from'][5:7]), b['to'][:4], int(b['to'][5:7]), b['n_months']))
    r['caption'] = ('%s 年 %d 月 %d 日收在 %s 點的人，同一年十月就看到 %s 點；要等到 %s 年 %d 月，'
                    '指數才再收在那個價位以上，中間約三十年（逐日的日期在第 <a class="xref" href="#s4">7</a> 節'
                    '那張三個例子的圖）。每一件在當時都像世界末日；拉長看，是線上的一個凹陷。這是歷史，不是保證：'
                    '下一次不一定回得來得這麼快，也可能像 1990 年這一次一樣等很久。'
                    '縱軸是對數刻度：同樣高度代表同樣的百分比，早期的跌幅才看得到。'
                    % (b['high_date'][:4], int(b['high_date'][5:7]), int(b['high_date'][8:10]),
                       '{:,}'.format(int(b['high_close'])), '{:,}'.format(int(b['low_close'])),
                       b['back_to_high_month'][:4], int(b['back_to_high_month'][5:7])))
    return chart(r)


def _us_dress(r):
    b = r['basis']
    span = '%s–%s' % (b['from'][:4], b['to'][:4])
    r['aria'] = '美股 %s 年的長期走勢（對數刻度，含息），線上標出當時的大事' % span
    r['title'] = '美股這 %d 年：每一件大事，事後看是線上的一個凹陷' % round((len(r['months']) - 1) / 12)
    r['sub'] = 'S&P 500 含息、名目，%s，起點當 1 倍，對數刻度' % span
    r['note'] = '含息、名目，起點那個月當 1 倍；沒有扣物價、費用和稅，也不是台幣。'
    r['more'] = ('S&P 500 含息：%s 年 %d 月到 2023 年 6 月用 Robert Shiller 公開月資料（月報酬＝當月價格'
                 '加上當月股利的十二分之一，再除以上個月的價格），2023 年 7 月起用 S&P 500 總報酬指數的'
                 '月報酬串接到 %s 年 %d 月，共 %d 個月。串接是因為 Shiller 那份資料的股利欄到 2023 年 6 月'
                 '為止。兩邊的價格口徑不完全一樣：Shiller 用當月每日收盤的平均，總報酬指數用月底收盤。'
                 '圖上只標事件的名稱和年月，每一件的日期出處寫在本節來源卡。'
                 % (b['from'][:4], int(b['from'][5:7]), b['to'][:4], int(b['to'][5:7]), b['n_months']))
    r['caption'] = ('%s 年初投進去的 1 元，含息到 %s 年變成大約 %s 元；中間最深的一次，帳面少掉 %d%%。'
                    '每一件在當時都像世界末日；拉長看，是線上的一個凹陷。這是歷史，不是保證：'
                    '下一次不一定回得來得這麼快，也可能像第 <a class="xref" href="#s4">7</a> 節那三個例子一樣等很久。'
                    '縱軸同樣是對數刻度。'
                    % (b['from'][:4], b['to'][:4], '{:,}'.format(int(round(b['end_multiple']))),
                       round(-b['max_drawdown'][0])))
    return r


def sp500():
    return chart(_us_dress(compute_us('1950-01')))


def sp500_1929():
    return chart(_us_dress(compute_us('1929-01')))


if __name__ == '__main__':
    import json
    for f in (compute_taiex, compute_us):
        r = f()
        b = dict(r['basis'])
        print(r['id'], json.dumps(b, ensure_ascii=False, default=str))
