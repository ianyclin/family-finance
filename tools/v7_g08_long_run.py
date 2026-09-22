"""G08／G09（v7 批 S2，批 T 改版）：兩張長線圖——台股 1990 起、美股 1929 起。

為什麼有這兩張圖
    第 8 節「跌的時候、很久沒漲的時候，記得這幾句」之後，讀者需要看見「每一件在當時
    都像世界末日，拉長看是線上的一個凹陷」。表和比例講得到「多少年是賺的」，講不到
    「那幾年長什麼樣子」。

口徑
    台股：證交所發行量加權股價指數（價格，不含息）各月最後一個交易日收盤，1990-01 到
          2025-12。含息的報酬指數官方只從 2003 年起提供，所以 1990 那一段只能用價格指數；
          含息會比這條線更陡。
    美股：S&P 500 含息、名目。1871-01 到 2023-06 用 Shiller 月資料，2023-07 起用
          S&P 500 總報酬指數串接（見 tools/v7_series.py）。指南放 1929 起（作者 2026-09-22 選）。
    事件點（批 V 第 5 條）：線是月底收盤，事件點標在「事件當天或當月最低的收盤」——台股有
          月內最高／最低收盤可查，1990-02 那一件事本身就是高點，標當月最高的收盤
          （1990-02-10 的 12,495.34），其餘都是跌，標當月最低的收盤（例如 2024-08-05 的
          19,830.88），比月底收盤貼近凹陷。美股只有月資料，事件點就標在該月的值。

版式（批 T：作者「不要用編號，直接標注在編號處」）
    縱軸對數刻度（同樣高度＝同樣的百分比，早期的跌幅才看得到）。
    每個事件在線上一個圓點，標籤直接放在點的旁邊：第一行年月、第二行事件名，細引線
    連到點。相鄰的標籤上下錯開（一高一低，必要時再往外一層），排不下才換位置，不編號、
    圖下也沒有清單。桌機標全部事件，手機只標其中跌得深、讀者記得的那十幾件；
    aria-label 兩版都唸出全部事件。
    排完會自我檢查：同一版裡兩兩不重疊、不超出 viewBox，有問題就印 ⚠。
    圖上只寫事件名稱與年月，不寫跌幅；跌幅與每個事件的出處寫在第 8 節的來源卡。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v7_series as S


# ---------------------------------------------------------------- 事件表
# (月份, 事件名)：第一行印年月、第二行印事件名，所以名稱要短（六個中文字以內）。
# 每一筆的日期都有官方或一手的出處，逐筆寫在第 8 節來源卡（見 spec-v7-content-t.md T1）。
# *_MOBILE 是手機版要標的那一份子集（跌得深的、讀者記得的），桌機版標全部。
TAIEX_EVENTS = [
    ('1990-02', '歷史高點'),
    ('1995-08', '台海危機'),
    ('1997-10', '亞洲風暴'),
    ('1999-09', '九二一地震'),
    ('2000-03', '網路泡沫'),
    ('2001-09', '九一一'),
    ('2003-04', 'SARS'),
    ('2004-03', '三一九槍擊'),
    ('2008-09', '金融海嘯'),
    ('2011-08', '歐債危機'),
    ('2015-08', '中國股災'),
    ('2018-10', '貿易戰'),
    ('2020-03', '疫情'),
    ('2022-03', '升息'),
    ('2024-08', '單日大跌'),
    ('2025-04', '關稅'),
]
# 標在「當月最高的收盤」的事件（它本身就是高點）；其餘標在當月最低的收盤。
TAIEX_AT_HIGH = {'1990-02'}
TAIEX_MOBILE = ['1990-02', '1997-10', '1999-09', '2000-03', '2003-04', '2004-03', '2008-09',
                '2011-08', '2015-08', '2020-03', '2022-03', '2024-08', '2025-04']

US_EVENTS = [
    ('1929-10', '華爾街崩盤'),
    ('1932-07', '大蕭條谷底'),
    ('1933-03', '銀行休業'),
    ('1937-05', '二次衰退'),
    ('1941-12', '珍珠港'),
    ('1950-06', '韓戰'),
    ('1962-10', '古巴危機'),
    ('1973-10', '石油危機'),
    ('1979-10', '打通膨升息'),
    ('1987-10', '黑色星期一'),
    ('1990-08', '波灣戰爭'),
    ('1997-07', '亞洲風暴'),
    ('2000-03', '網路泡沫'),
    ('2001-09', '九一一'),
    ('2003-03', '伊拉克戰爭'),
    ('2008-09', '金融海嘯'),
    ('2011-08', '歐債危機'),
    ('2020-03', '疫情'),
    ('2022-03', '升息'),
    ('2023-03', '銀行倒閉'),
    ('2025-04', '關稅'),
]
US_MOBILE = ['1929-10', '1932-07', '1941-12', '1962-10', '1973-10', '1987-10', '2000-03',
             '2001-09', '2008-09', '2011-08', '2020-03', '2022-03', '2025-04']


def _tnum(m):
    y, mm = m.split('-')
    return int(y) + (int(mm) - 1) / 12.0


# ---------------------------------------------------------------- compute
def compute_taiex():
    months, values, rows = S.taiex_price_monthly()
    # 1990 年那一段：當年收盤最高的那一天、當年收盤最低的那一天，以及收盤再站回那個高點的月份。
    # 只有收盤價可查：證交所線上的開高低收（MI_5MINS_HIST）只到 1999-01-05，
    # 常被引用的盤中 12,682 點查不到官方逐日資料、確切日期也查不到，所以本文一律用收盤高點。
    rowmap = {r['month']: r for r in rows}
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
        'events': [(m, lab) for m, lab in TAIEX_EVENTS if months[0] <= m <= months[-1]],
        # 事件點的 y：事件當天或當月最低的收盤（見檔頭「事件點」）。
        'event_y': {m: float(rowmap[m]['month_high_close'] if m in TAIEX_AT_HIGH
                             else rowmap[m]['month_low_close'])
                    for m, _lab in TAIEX_EVENTS if m in rowmap},
        'mobile_events': TAIEX_MOBILE,
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


def compute_us(start='1929-01'):
    months, tr = S.shiller_tr_extended()
    i = months.index(start)
    m2 = months[i:]
    v2 = [v / tr[i] for v in tr[i:]]
    evs = [(m, lab) for m, lab in US_EVENTS if m >= start]
    y0 = int(start[:4])
    decade = 20 if (int(m2[-1][:4]) - y0) > 60 else 10
    ticks = list(range(y0 - y0 % decade + (decade if y0 % decade else 0), int(m2[-1][:4]) + 1, decade))
    hi = max(v2)
    tk = [1]
    while tk[-1] * 10 < hi * 1.2:
        tk.append(tk[-1] * 10)
    return {
        'id': 'sp500-long-run',
        'market': 'us',
        'months': m2, 'values': v2,
        'events': evs,
        'event_y': {},          # 美股只有月資料：事件點就用該月的值（chart 裡的預設）
        'mobile_events': [m for m in US_MOBILE if m >= start],
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


def _ev_lines(month, name):
    """標籤的兩行：第一行年月，第二行事件名。"""
    y, m = month.split('-')
    return ('%s/%d' % (y, int(m)), name)


def _stem(x, yv, x0, y0, w, bh):
    """引線的兩端：從事件點，連到標籤靠近它的那一邊。"""
    xc = min(max(x, x0 + 5), x0 + w - 5)
    ye = (y0 + bh) if (y0 + bh) < yv else y0
    return (x, yv, xc, ye)


def _crosses(seg, rects):
    """引線有沒有穿過別人的標籤（沿線取樣 24 點，夠用）。"""
    x1, y1, x2, y2 = seg
    n = 0
    for r in rects:
        for i in range(1, 24):
            px_ = x1 + (x2 - x1) * i / 24.0
            py_ = y1 + (y2 - y1) * i / 24.0
            if r[0] - 1 <= px_ <= r[2] + 1 and r[1] - 1 <= py_ <= r[3] + 1:
                n += 1
                break
    return n


def _cols(pts, W):
    """把線壓成「每一個整數 x 那一欄，線佔到哪一段 y」，用來判斷標籤有沒有蓋到線。"""
    col = [None] * (int(W) + 2)
    for i in range(1, len(pts)):
        x1, y1 = pts[i - 1]
        x2, y2 = pts[i]
        for c in range(int(min(x1, x2)), int(max(x1, x2)) + 1):
            if 0 <= c < len(col):
                lo, hi = min(y1, y2), max(y1, y2)
                col[c] = (lo, hi) if col[c] is None else (min(col[c][0], lo), max(col[c][1], hi))
    return col


def _on_line(col, x0, y0, x1, y1):
    """標籤蓋到線的寬度（有幾欄）：蓋一點點還好，整段蓋住就不行。"""
    n = 0
    for c in range(max(0, int(x0)), min(len(col) - 1, int(x1) + 1)):
        if col[c] is not None and col[c][0] <= y1 and y0 <= col[c][1]:
            n += 1
    return n


def _place(x, yv, w, bh, prefer_up, lay, bottom, placed, col, gap=9.0, blocked=()):
    """替一個標籤找位置：在點的附近試一格一格的候選，挑「離點最近、又不撞到別人」的那一個。

    候選＝上下各七層（由內而外）× 水平位移（從正中往兩邊各挪到兩個半標籤寬）。
    每一個候選都要在 viewBox 內、和已放好的標籤不重疊、也不壓到 y 軸刻度的文字（blocked）；合格的裡面挑代價最小的：
    代價＝標籤中心到事件點的距離（橫向加重，擠在一起的寧可往下排，不要橫著挪到別的年份上面）
    ＋標籤蓋到線的罰分（蓋住就看不出那一年的線長什麼樣）
    ＋引線穿過別人標籤的罰分（穿過就看不出這條線連的是哪一件）
    ＋放在不偏好那一邊的罰分（相鄰事件一高一低，自然錯開）。
    """
    best = None
    for lv in range(7):
        for step in range(-7, 8):
            dx = step * 0.36 * w
            x0 = min(max(x + dx - w / 2, 1.5), lay.W - w - 1.5)
            for up in (True, False):
                y0 = (yv - gap - lv * (bh + 3.0) - bh) if up else (yv + gap + lv * (bh + 3.0))
                if y0 < 1.5 or y0 + bh > bottom - 1.5:
                    continue
                if any((x0 < q[2] + 2 and q[0] - 2 < x0 + w and
                        y0 < q[3] + 2 and q[1] - 2 < y0 + bh) for q in list(placed) + list(blocked)):
                    continue
                d = math.hypot(1.25 * (x0 + w / 2 - x), y0 + bh / 2 - yv)
                cost = d + 0.012 * d * d      # 拉遠一點還好，拉很遠就看不出連的是哪一件
                over = _on_line(col, x0, y0, x0 + w, y0 + bh)
                if over:
                    cost += 18.0 + 1.6 * over
                cost += 75.0 * _crosses(_stem(x, yv, x0, y0, w, bh), list(placed) + list(blocked))
                if up != prefer_up:
                    cost += 10.0
                if best is None or cost < best[0]:
                    best = (cost, x0, y0)
    return None if best is None else (best[1], best[2])


# ---------------------------------------------------------------- chart
def chart(res):
    import essay_charts as E

    months, values = res['months'], res['values']
    t0, t1 = _tnum(months[0]), _tnum(months[-1])
    ymin = min(res['y_ticks'] + [min(values)])
    ymax = max(res['y_ticks'] + [max(values)])
    lo_log, hi_log = math.log10(ymin * 0.94), math.log10(ymax * 1.06)
    idx = {m: k for k, m in enumerate(months)}
    warnings = []

    def build(lay):
        mob = lay.mobile
        # 手機版 10.0：viewBox 寬 360 在 375px 的螢幕上大約縮到 0.87 倍，實際渲染約 8.7px
        # （規格要求不低於 8.5px；確切值等主線在瀏覽器量）。
        fl = 10.0 if mob else 11.5
        lh = fl * 1.16
        pad = 2.6
        bh = 2 * lh + 2 * pad
        evs = [(m, lab) for m, lab in res['events']
               if (not mob or m in res['mobile_events']) and m in idx]

        left = lay.left + (6 if mob else 10)
        right = lay.right - 2
        h = 336 if mob else 436
        plot_top = lay.top
        bottom = h - (20 if mob else 24)

        def px(m):
            return left + (right - left) * (_tnum(m) - t0) / (t1 - t0)

        def py(v):
            return bottom - (bottom - plot_top) * (math.log10(v) - lo_log) / (hi_log - lo_log)

        out = [E.svg_open(lay, h, res['aria'])]
        # y 軸刻度的文字也是障礙物：標籤壓上去兩邊都看不清楚（主線 2026-09-22 在 375px 實量到
        # 美股手機版「1932/7」壓住「1 倍」）。文字靠右對齊畫在 left-5，往左長。
        blocked = []
        for v in res['y_ticks']:
            out.append(E.hline(left, right, py(v)))
            lab = res['y_fmt'](v)
            yb = py(v) + lay.fs * 0.36
            out.append(E.text(left - 5, yb, lab, lay.fs, 'end', E.MUTED))
            blocked.append((left - 5 - _textw(lab, lay.fs), yb - lay.fs, left - 5, yb + lay.fs * 0.25))
        for y in res['x_ticks']:
            mm = '%d-01' % y
            if _tnum(mm) < t0 or _tnum(mm) > t1:
                continue
            out.append(E.text(px(mm), bottom + lay.f + 5, str(y), lay.f, 'middle', E.MUTED))
        pts = [(px(m), py(v)) for m, v in zip(months, values)]
        out.append(E.poly(pts, E.TEAL, 1.6 if mob else 1.9))
        col = _cols(pts, lay.W)

        # 標籤：直接放在點旁邊，上下交錯
        placed, draw = [], []
        for n, (m, name) in enumerate(evs):
            k = idx[m]
            x, yv = px(m), py(res['event_y'].get(m, values[k]))
            l1, l2 = _ev_lines(m, name)
            w = max(_textw(l1, fl), _textw(l2, fl)) + 2 * pad
            spot = _place(x, yv, w, bh, n % 2 == 0, lay, bottom, placed, col, blocked=blocked)
            if spot is None:
                warnings.append('%s %s 標籤「%s %s」排不下' % (res['id'], lay.kind, l1, l2))
                continue
            x0, y0 = spot
            placed.append((x0, y0, x0 + w, y0 + bh))
            draw.append((x, yv, x0, y0, w, l1, l2))
        # 先畫全部引線，再畫全部標籤：別人的引線才不會壓在字上
        for x, yv, x0, y0, w, l1, l2 in draw:
            sx1, sy1, sx2, sy2 = _stem(x, yv, x0, y0, w, bh)
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="0.8" '
                       'stroke-dasharray="2 3" stroke-opacity="0.75"/>'
                       % (sx1, sy1, sx2, sy2 + (1.5 if sy2 == y0 else -1.5), E.MUTED))
        for x, yv, x0, y0, w, l1, l2 in draw:
            out.append(E.rect(x0, y0, w, bh, E.SURFACE, 3, 0.86))
            out.append(E.text(x0 + pad, y0 + pad + fl * 0.88, l1, fl, 'start', E.MUTED))
            out.append(E.text(x0 + pad, y0 + pad + fl * 0.88 + lh, l2, fl, 'start', E.INK, '700'))
        # 圓點最後畫：標籤的底色不會把它蓋掉
        for x, yv, x0, y0, w, l1, l2 in draw:
            out.append(E.dot(x, yv, E.ACCENT, 3.0 if mob else 3.4))
        out.append('</svg>')

        # 自我檢查：同一版裡兩兩不重疊、不超出 viewBox
        for i in range(len(placed)):
            x0, y0, x1, y1 = placed[i]
            if x0 < 0 or x1 > lay.W or y0 < 0 or y1 > h:
                warnings.append('%s %s 標籤「%s」超出 viewBox' % (res['id'], lay.kind, draw[i][6]))
            for j in range(i + 1, len(placed)):
                q = placed[j]
                if x0 < q[2] and q[0] < x1 and y0 < q[3] and q[1] < y1:
                    warnings.append('%s %s 標籤「%s」和「%s」重疊'
                                    % (res['id'], lay.kind, draw[i][6], draw[j][6]))
            for q in blocked:
                if x0 < q[2] and q[0] < x1 and y0 < q[3] and q[1] < y1:
                    warnings.append('%s %s 標籤「%s」和 y 軸刻度重疊'
                                    % (res['id'], lay.kind, draw[i][6]))
        return '\n'.join(out)

    svgs = [build(E.L('d')), build(E.L('m'))]
    for w in warnings:
        print('⚠ ' + w)
    more = ('<details class="more" data-print="open">'
            '<summary>想深入：這張圖的資料、期間和沒算進去的東西</summary>'
            '<p class="note">%s</p></details>' % E.esc(res['more']))
    return dict(title=res['title'], sub=res['sub'], svgs=svgs,
                extras=E.note(res['note']) + more, caption=res['caption'])


# ---------------------------------------------------------------- 兩個進入點
def _aria_events(evs):
    """aria-label 唸出全部事件（年月＋名稱）：手機版只標其中十幾件，唸的是同一份全表。"""
    return '、'.join('%s/%d %s' % (m[:4], int(m[5:7]), lab) for m, lab in evs)



def taiex():
    r = compute_taiex()
    b = r['basis']
    r['aria'] = ('台股 1990 到 2025 年的長期走勢（對數刻度），線上標出這 %d 件當時的大事：%s'
                 % (len(r['events']), _aria_events(r['events'])))
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
                    '縱軸是對數刻度：同樣高度代表同樣的百分比，早期的跌幅才看得到；'
                    '線是月底收盤，事件點標在事件當天或當月最低的收盤。'
                    % (b['high_date'][:4], int(b['high_date'][5:7]), int(b['high_date'][8:10]),
                       '{:,}'.format(int(b['high_close'])), '{:,}'.format(int(b['low_close'])),
                       b['back_to_high_month'][:4], int(b['back_to_high_month'][5:7])))
    return chart(r)


def _us_dress(r):
    b = r['basis']
    span = '%s–%s' % (b['from'][:4], b['to'][:4])
    r['aria'] = ('美股 %s 年的長期走勢（對數刻度，含息），線上標出這 %d 件當時的大事：%s'
                 % (span, len(r['events']), _aria_events(r['events'])))
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
                    '縱軸同樣是對數刻度；美股只有月資料，事件點標在該月。'
                    % (b['from'][:4], b['to'][:4], '{:,}'.format(int(round(b['end_multiple']))),
                       round(-b['max_drawdown'][0])))
    return r


def sp500():
    return chart(_us_dress(compute_us('1929-01')))


if __name__ == '__main__':
    import json
    for f in (compute_taiex, compute_us):
        r = f()
        b = dict(r['basis'])
        print(r['id'], json.dumps(b, ensure_ascii=False, default=str))
