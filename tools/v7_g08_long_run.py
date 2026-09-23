"""G08／G09（v7 批 S2，批 T 改版）：兩張長線圖——台股 1990 起、美股 1929 起。

為什麼有這兩張圖
    第 8 節「跌的時候、很久沒漲的時候，記得這幾句」之後，讀者需要看見「每一件在當時
    都像世界末日，拉長看是線上的一個凹陷」。表和比例講得到「多少年是賺的」，講不到
    「那幾年長什麼樣子」。

口徑
    台股（批 W：作者「台股長線應該要直接用含股利的？有些點沒在線上」）：一條線、兩個口徑接起來。
          1990-01-04～2002-12-31 用證交所發行量加權股價指數（價格，不含股利）逐日收盤，
          2003-01-02 起用發行量加權股價報酬指數（含股利）逐日收盤，在 2003-01-02 那一天接上
          （接點那一天兩個指數的收盤差 0.05 點：4,524.87 對 4,524.92，比例 0.99999，線不跳動）。
          含息的報酬指數官方只從 2003 年起提供，所以前半段只有價格；序列的實作在 tools/v7_series.py。
    美股：S&P 500 含息、名目。1871-01 到 2023-06 用 Shiller 月資料，2023-07 起用
          S&P 500 總報酬指數串接（見 tools/v7_series.py）。指南放 1929 起（作者 2026-09-22 選）。
    事件點（批 W：作者要點在線上）：台股的線改成逐週收盤（每週最後一個交易日，約 1,859 點），
          事件點就標在事件那一週的收盤，所以點一定落在線上；週線也看得到 2003-04、2024-08
          這種一個月之內的凹陷。標籤上印的年月是事件本身的年月（例如九二一在 1999-09-27，
          那一週收在 1999-10-02，標籤仍寫 1999/9）。美股只有月資料，事件點就標在該月的值。

版式（批 T：作者「不要用編號，直接標注在編號處」）
    縱軸對數刻度（同樣高度＝同樣的百分比，早期的跌幅才看得到）。
    每個事件在線上一個圓點，標籤直接放在點的旁邊：第一行年月、第二行事件名，細引線
    連到點。相鄰的標籤上下錯開（一高一低，必要時再往外一層），排不下才換位置，不編號、
    圖下也沒有清單。桌機標全部事件，手機只標其中跌得深、讀者記得的那十幾件；
    aria-label 兩版都唸出全部事件。
    排完會自我檢查：同一版裡兩兩不重疊、不超出 viewBox，有問題就印 ⚠。
    圖上只寫事件名稱與年月，不寫跌幅；跌幅與每個事件的出處寫在第 8 節的來源卡。
"""
import datetime
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v7_series as S


# ---------------------------------------------------------------- 事件表
# (月份, 事件名)：第一行印年月、第二行印事件名，所以名稱要短（六個中文字以內）。
# 每一筆的日期都有官方或一手的出處，逐筆寫在第 8 節來源卡（見 spec-v7-content-t.md T1）。
# *_MOBILE 是手機版要標的那一份子集（跌得深的、讀者記得的），桌機版標全部。
# 台股改成逐日日期（批 W）：點畫在這一天所屬那一週的收盤上。每一個日期都是第 8 節來源卡
# 已經列過的那一天（1990 年最高的收盤、各事件當天台股大跌的那一天、升息用 FOMC 那一天）。
TAIEX_EVENTS = [
    ('1990-02-10', '歷史高點'),
    ('1995-08-05', '台海危機'),
    ('1997-10-28', '亞洲風暴'),
    ('1999-09-27', '九二一地震'),
    ('2000-03-13', '網路泡沫'),
    ('2001-09-13', '九一一'),
    ('2003-04-24', 'SARS'),
    ('2004-03-22', '三一九槍擊'),
    ('2008-09-16', '金融海嘯'),
    ('2011-08-05', '歐債危機'),
    ('2015-08-24', '中國股災'),
    ('2018-10-11', '貿易戰'),
    ('2020-03-19', '疫情'),
    ('2022-03-16', '升息'),
    ('2024-08-05', '單日大跌'),
    ('2025-04-07', '關稅'),
]
TAIEX_MOBILE = ['1990-02-10', '1997-10-28', '1999-09-27', '2000-03-13', '2003-04-24',
                '2004-03-22', '2008-09-16', '2011-08-05', '2015-08-24', '2020-03-19',
                '2022-03-16', '2024-08-05', '2025-04-07']

US_EVENTS = [
    ('1929-10', '華爾街崩盤'),
    ('1932-06', '大蕭條谷底'),
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
    ('2018-12', '貿易戰'),
    ('2020-03', '疫情'),
    ('2022-03', '升息'),
    ('2023-03', '銀行倒閉'),
    ('2025-04', '關稅'),
]
US_MOBILE = ['1929-10', '1932-06', '1941-12', '1962-10', '1973-10', '1987-10', '2000-03',
             '2001-09', '2008-09', '2011-08', '2020-03', '2022-03', '2025-04']


def _tnum(k):
    """把 'YYYY-MM' 或 'YYYY-MM-DD' 換成小數年（兩種都以該年 1 月 1 日為 .0，混用不會錯位）。"""
    p = k.split('-')
    if len(p) == 2:
        return int(p[0]) + (int(p[1]) - 1) / 12.0
    d = datetime.date(int(p[0]), int(p[1]), int(p[2]))
    return d.year + (d.toordinal() - datetime.date(d.year, 1, 1).toordinal()) / 365.25


# ---------------------------------------------------------------- compute
def compute_taiex():
    dates, values = S.taiex_spliced_weekly()
    _d, _v, factor = S.taiex_spliced_daily()
    # 1990 年那一段：當年收盤最高的那一天、之後當年收盤最低的那一天。
    # 只有收盤價可查：證交所線上的開高低收（MI_5MINS_HIST）只到 1999-01-05，
    # 常被引用的盤中 12,682 點查不到官方逐日資料、確切日期也查不到，所以本文一律用收盤高點。
    y1990 = [(d, v) for d, v in zip(_d, _v) if d < '1991-01-01']
    hi_date, hi_close = max(y1990, key=lambda r: r[1])
    lo_date, lo_close = min((r for r in y1990 if r[0] >= hi_date), key=lambda r: r[1])
    # ①價格指數（不含股利）什麼時候再收在那個高度：月內最高收盤的那一份逐月檔還在，用它查。
    #   對到第 7 節那張三個例子的圖（台灣 1990-02-10 → 2020-07-27，約 30 年）。
    pm_rows = S.taiex_price_monthly()[2]
    back_price = next((r['month'] for r in pm_rows
                       if r['month'] > hi_date[:7] and float(r['month_high_close']) >= hi_close), None)
    # ②串接後（2003 年起含股利）第一次收在那個高度的那一週。
    back_tr = next((d for d, v in zip(dates, values) if d > hi_date and v >= hi_close), None)
    # 事件點：事件那一天所屬那一週的收盤（所以點一定在線上）；標籤上印的仍是事件本身的年月。
    ev_week = {ev: S.week_of(dates, ev) for ev, _lab in TAIEX_EVENTS}
    events = [(ev_week[ev], lab) for ev, lab in TAIEX_EVENTS if ev_week.get(ev)]
    return {
        'id': 'taiex-long-run',
        'market': 'taiex',
        'months': dates, 'values': values,
        'events': events,
        'label_month': {ev_week[ev]: ev[:7] for ev, _lab in TAIEX_EVENTS if ev_week.get(ev)},
        'event_y': {},          # 點就在線上：用該週的收盤（chart 裡的預設）
        'mobile_events': [ev_week[ev] for ev in TAIEX_MOBILE if ev_week.get(ev)],
        'y_ticks': [2000, 3000, 5000, 10000, 20000, 30000, 50000],
        'y_fmt': lambda v: ('%d,000' % (v // 1000)),
        'x_ticks': [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025],
        'basis': {
            'source': '1990–2002 證交所發行量加權股價指數（價格），2003 起發行量加權股價報酬指數（含股利）',
            'file': ('research/data/taiex_price_daily_1990_2002.csv＋'
                     'research/data/taiex_tr_monthly_raw.csv'),
            'splice_date': S.TAIEX_SPLICE_DATE, 'splice_factor': factor,
            'from': dates[0], 'to': dates[-1], 'n_weeks': len(dates),
            'high_close': hi_close, 'high_date': hi_date,
            'low_close': lo_close, 'low_date': lo_date,
            'back_to_high_month_price': back_price,
            'back_to_high_week_total': back_tr,
            'max_drawdown': S.max_drawdown(dates, values),
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


def _ev_lines(key, name):
    """標籤的兩行：第一行年月，第二行事件名。key 是 'YYYY-MM' 或 'YYYY-MM-DD'。"""
    p = key.split('-')
    return ('%s/%d' % (p[0], int(p[1])), name)


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


def _behind(prev, cur):
    """時序倒置的程度：後面的標籤中心 x 比前一個小就是倒置，回傳差了幾 px（沒倒置回 0）。

    prev／cur 都是 (中心 x, 右緣 x, 是不是被釘在右邊界)。兩個都貼在右邊界時中心 x 只差在框寬
    （批 AB：美股桌機「2022/3」和「2023/3」差 3.7px），那不是倒置，改比右緣。
    """
    if prev is None:
        return 0.0
    if prev[2] and cur[2]:
        return max(0.0, prev[1] - cur[1])
    return max(0.0, prev[0] - cur[0])


def _place(x, yv, w, bh, prefer_up, lay, bottom, placed, col, gap=9.0, blocked=(), last_cx=None,
           dots=()):
    """替一個標籤找位置：在點的附近試一格一格的候選，挑「離點最近、又不撞到別人」的那一個。

    候選＝上下各九層（由內而外）× 水平位移（從正中往兩邊各挪到兩個半標籤寬）。
    （批 AB：事件點變成硬障礙之後，右邊界那一疊排不下，層數從七層加到九層。）
    每一個候選都要在 viewBox 內、和已放好的標籤不重疊、不壓到 y 軸刻度的文字（blocked），
    也不壓到任何一個事件的圓點（dots，含後面還沒放標籤的事件；圓點最後才畫，壓上去就蓋住字）；
    合格的裡面挑代價最小的：
    代價＝標籤中心到事件點的距離（橫向加重，擠在一起的寧可往下排，不要橫著挪到別的年份上面）
    ＋標籤蓋到線的罰分（蓋住就看不出那一年的線長什麼樣）
    ＋引線穿過別人標籤的罰分（穿過就看不出這條線連的是哪一件）
    ＋放在不偏好那一邊的罰分（相鄰事件一高一低，自然錯開）
    ＋時序倒置的罰分（批 Y：作者「2025/4 關稅被推到 2023/3 銀行倒閉的左下方，讀起來像時序錯亂」）。
      last_cx 記著同一側（上／下）上一個、也就是時間上更早的那個標籤的中心 x；
      事件是照時間順序排的，所以同一側後面的標籤中心 x 不可以比它小。罰分大到實質等於禁止，
      但不直接剔除候選，免得整個標籤排不下。
      last_cx['any'] 記著上一個標籤（不分上下側）的中心 x：跨側也倒置一樣罰（批 AA N8），
      但不硬禁。批 AB 把跨側的罰分從 25 抬到 150：事件點變成硬障礙之後，標籤被擠得比以前開，
      25 已經壓不住倒置（實測美股桌機跨側倒置 2 → 5）。
    ＋橫向漂太遠的罰分（批 AA）：標籤中心 x 離自己的事件點超過 40px 開始罰、超過 60px 重罰。
      只靠距離代價不夠——美股 1930–50 那幾件擠在一起，整排標籤會一路往右漂到別的年代上面。
      批 AB 把這兩個係數加倍（3→6、8→16）：躲開事件點會多出橫移的誘因，原來的係數壓不住。
    """
    best = None
    for lv in range(9):
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
                if any((x0 < q[2] and q[0] < x0 + w and
                        y0 < q[3] and q[1] < y0 + bh) for q in dots):
                    continue
                d = math.hypot(1.25 * (x0 + w / 2 - x), y0 + bh / 2 - yv)
                cost = d + 0.012 * d * d      # 拉遠一點還好，拉很遠就看不出連的是哪一件
                over = _on_line(col, x0, y0, x0 + w, y0 + bh)
                if over:
                    cost += 60.0 + 4.0 * over      # 寧可多退一層，也不要騎在線上（批 AB）
                cost += 75.0 * _crosses(_stem(x, yv, x0, y0, w, bh), list(placed) + list(blocked))
                if up != prefer_up:
                    cost += 10.0
                cx = x0 + w / 2
                if last_cx is not None:
                    cur = (cx, x0 + w, x0 + w > lay.W - 3.0)
                    d_side = _behind(last_cx.get(up), cur)
                    if d_side > 0:
                        cost += 400.0 + d_side
                    d_any = _behind(last_cx.get('any'), cur)
                    if d_any > 0:
                        cost += 150.0 + 4.0 * d_any
                adx = abs(cx - x)
                if adx > 40.0:
                    cost += 6.0 * (adx - 40.0)
                if adx > 60.0:
                    cost += 16.0 * (adx - 60.0)
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
    infos = []

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
        # 美股手機版「1932/6」壓住「1 倍」）。文字靠右對齊畫在 left-5，往左長。
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

        # 事件點本身也是障礙物（批 AB）：圓點是最後畫的，壓在標籤上就把字蓋掉
        # （主線 2026-09-22 在手機上實量到美股「2020/3 疫情」的字被 2022/3 的點壓住）。
        # 先把全部事件點（含後面還沒放標籤的）算成方框，放標籤時硬性避開。
        dr = (3.0 if mob else 3.4) + 2.5        # 圓點半徑再留一點空隙
        epts = [(px(m), py(res['event_y'].get(m, values[idx[m]]))) for m, _lab in evs]
        dot_box = [(ex - dr, ey - dr, ex + dr, ey + dr) for ex, ey in epts]

        # 標籤：直接放在點旁邊，上下交錯
        placed, draw = [], []
        last_cx = {}            # 同一側最後一個（時間上最近的前一個）標籤的中心 x
        for n, (m, name) in enumerate(evs):
            x, yv = epts[n]
            l1, l2 = _ev_lines(res.get('label_month', {}).get(m, m), name)
            w = max(_textw(l1, fl), _textw(l2, fl)) + 2 * pad
            spot = _place(x, yv, w, bh, n % 2 == 0, lay, bottom, placed, col,
                          blocked=blocked, last_cx=last_cx, dots=dot_box)
            if spot is None:
                warnings.append('%s %s 標籤「%s %s」排不下' % (res['id'], lay.kind, l1, l2))
                continue
            x0, y0 = spot
            last_cx[(y0 + bh) <= yv] = last_cx['any'] = (x0 + w / 2, x0 + w, x0 + w > lay.W - 3.0)
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
            for q in dot_box:
                if x0 < q[2] and q[0] < x1 and y0 < q[3] and q[1] < y1:
                    warnings.append('%s %s 標籤「%s」壓到事件點'
                                    % (res['id'], lay.kind, draw[i][6]))
        # 排不開的時候線還是會穿過標籤，不當警告，只回報數量；量法和裁判一致（批 AB）：
        # 依繪製順序配對標籤框與事件點，算「線穿過標籤」「中心 x 離自己的點 >40px」「時序倒置」。
        crossed = sum(1 for r in placed if _on_line(col, r[0], r[1], r[2], r[3]))
        far = sum(1 for i, r in enumerate(placed) if abs((r[0] + r[2]) / 2 - draw[i][0]) > 40.0)
        inv_any = inv_side = 0
        prev_any, prev_side = None, {}
        for i, r in enumerate(placed):
            cur = ((r[0] + r[2]) / 2, r[2], r[2] > lay.W - 3.0)
            up = r[3] <= draw[i][1]
            inv_side += 1 if _behind(prev_side.get(up), cur) > 0 else 0
            inv_any += 1 if _behind(prev_any, cur) > 0 else 0
            prev_any, prev_side[up] = cur, cur
        infos.append('%s %s 標籤 %d：線穿過 %d、中心離點>40px %d、時序倒置 跨側 %d／同側 %d'
                     % (res['id'], lay.kind, len(placed), crossed, far, inv_any, inv_side))
        return '\n'.join(out)

    svgs = [build(E.L('d')), build(E.L('m'))]
    for w in warnings:
        print('⚠ ' + w)
    for i in infos:
        print('· ' + i)
    # 批 AG：p.note 併進「想深入」以後 res['note'] 是空字串，就不印那一條 p.note；
    # res['more'] 改成 HTML（裡面有 a.xref 的節號連結），所以不再 E.esc。
    more = ('<details class="more" data-print="open">'
            '<summary>想深入：這張圖的資料和期間</summary>'
            '<p class="note">%s</p></details>' % res['more'])
    return dict(title=res['title'], sub=res['sub'], svgs=svgs,
                extras=(E.note(res['note']) if res['note'] else '') + more,
                caption=res['caption'])


# ---------------------------------------------------------------- 兩個進入點
def _aria_events(evs):
    """aria-label 唸出全部事件（年月＋名稱）：手機版只標其中十幾件，唸的是同一份全表。

    evs 的第一欄是要唸出來的年月 'YYYY-MM'（台股的線是逐週，事件那一週不一定和事件同月）。
    """
    return '、'.join('%s/%d %s' % (m[:4], int(m[5:7]), lab) for m, lab in evs)



def taiex():
    r = compute_taiex()
    b = r['basis']
    evs = [(r['label_month'][k], lab) for k, lab in r['events']]
    r['aria'] = ('台股 1990 到 2025 年的長期走勢（對數刻度，逐週收盤；1990 到 2002 年是價格指數，'
                 '2003 年起含股利），線上標出這 %d 件當時的大事：%s'
                 % (len(evs), _aria_events(evs)))
    r['title'] = '台股這 36 年：每一件大事，事後看是線上的一個凹陷'
    r['sub'] = '每週收盤，對數刻度；1990–2002 只有價格（證交所的含息指數 2003 年才開始編），2003 起含股利'
    # 批 AG（作者 2026-09-22）：主線只留「這張圖告訴我什麼」，口徑與但書全部收進「想深入」。
    r['note'] = ''
    r['more'] = ('證交所的發行量加權股價報酬指數（含股利）自民國 92 年（2003 年）1 月起才開始提供，'
                 '所以 1990 到 2002 年沒有官方的含息指數，那一段只有價格；2003 年起含股利。'
                 '前半段因此偏低。1991 到 2002 年偏低多少，下面有估算；兩段接在一起，看整體方向就好。'
                 '%s 年 %d 月到 2002 年 12 月用證交所發行量加權股價指數（價格，不含股利）的逐日收盤，'
                 '2003 年 1 月 2 日起用發行量加權股價報酬指數（含股利）的逐日收盤，兩段在那一天接起來；'
                 '接點那一天兩個指數的收盤只差 0.05 點（4,524.87 對 4,524.92），線沒有跳動。'
                 '圖上畫的是每週最後一個交易日的收盤，'
                 '到 %s 年 %d 月為止共 %s 週。沒有扣物價、費用和稅。'
                 '圖上只標事件的名稱和年月，每一件的日期出處與當時的跌幅寫在本節來源卡。'
                 # 批 AJ（裁判 S-4）：批 AG 精簡圖說時，「逐日的日期在第 7 節那張三個例子的圖」
                 # 這個指路整個掉了，沒有搬到任何地方，補回這裡。
                 '逐日的日期在第 <a class="xref" href="#s4">7</a> 節那張三個例子的圖。'
                 # 以下五句是批 AG 從圖說搬下來的，順序照舊
                 '從 1990 年底算起的那十二年（1991 到 2002），若也把股利算進去，'
                 '一年大約多 2 個百分點：價格指數平均一年是 −0.1%%，算進股利大約 +2%%，還是接近打平。'
                 '1990 年那一整年的崩盤沒算在裡面；那一段有多深，看圖最左邊那一截就知道。'
                 '這一段的股利是估算的，用證交所公布的市場殖利率回推，估法寫在本節來源卡。'
                 '這是歷史，不是保證：下一次不一定回得來得這麼快，'
                 '也可能像 1990 年這一次一樣等很久。'
                 '縱軸是對數刻度：同樣高度代表同樣的百分比，早期的跌幅才看得到；'
                 '線是每週最後一個交易日的收盤，事件點標在事件那一週的收盤。'
                 % (b['from'][:4], int(b['from'][5:7]), b['to'][:4], int(b['to'][5:7]),
                    '{:,}'.format(b['n_weeks'])))
    r['caption'] = ('%s 年 %d 月收在 %s 點的人，同一年十月就看到 %s 點。'
                    '只算價格，要等到 %s 年 %d 月才回到那個價位，中間約三十年；'
                    # 批 AJ（裁判 S-4）：圖外只寫「算進股利」會被讀成 1990 起就含息，補回口徑。
                    '算進 2003 年起的股利，%s 年 %d 月就回到了。'
                    % (b['high_date'][:4], int(b['high_date'][5:7]),
                       '{:,}'.format(int(b['high_close'])), '{:,}'.format(int(b['low_close'])),
                       b['back_to_high_month_price'][:4], int(b['back_to_high_month_price'][5:7]),
                       b['back_to_high_week_total'][:4], int(b['back_to_high_week_total'][5:7])))
    return chart(r)


def _us_dress(r):
    b = r['basis']
    span = '%s–%s' % (b['from'][:4], b['to'][:4])
    r['aria'] = ('美股 %s 年的長期走勢（對數刻度，含息），線上標出這 %d 件當時的大事：%s'
                 % (span, len(r['events']), _aria_events(r['events'])))
    r['title'] = '美股這 %d 年：每一件大事，事後看是線上的一個凹陷' % round((len(r['months']) - 1) / 12)
    r['sub'] = 'S&P 500 含息、名目，%s，起點當 1 倍，對數刻度' % span
    r['note'] = ''      # 批 AG：併進下面的「想深入」
    r['more'] = ('含息、<a class="term" href="#g-annual" title="沒扣物價、帳面上看到的數字。">名目</a>，起點那個月當 1 倍；沒有扣物價、費用和稅，也不是台幣。'
                 'S&amp;P 500 含息：%s 年 %d 月到 2023 年 6 月用 Robert Shiller 公開月資料（月報酬＝當月價格'
                 '加上當月股利的十二分之一，再除以上個月的價格），2023 年 7 月起用 S&amp;P 500 總報酬指數的'
                 '月報酬串接到 %s 年 %d 月，共 %s 個月。串接是因為 Shiller 那份資料的股利欄到 2023 年 6 月'
                 '為止。兩邊的價格口徑不完全一樣：Shiller 用當月每日收盤的平均，總報酬指數用月底收盤。'
                 '圖上只標事件的名稱和年月，每一件的日期出處寫在本節來源卡。'
                 # 以下兩句是批 AG 從圖說搬下來的，順序照舊
                 # 批 AJ（裁判 S-3）：冒號前半「這是歷史，不是保證：」留在圖說外面，
                 # 搬進來的後半沒有承接，補回一句（台股那張圖本來就是整句一起搬）。
                 '歷史不等於保證：下一次不一定回得來得這麼快，'
                 '也可能像第 <a class="xref" href="#s4">7</a> 節那三個例子一樣等很久。'
                 '縱軸同樣是對數刻度；美股只有月資料，事件點標在該月。'
                 % (b['from'][:4], int(b['from'][5:7]), b['to'][:4], int(b['to'][5:7]),
                    '{:,}'.format(b['n_months'])))
    r['caption'] = ('%s 年初投進去的 1 元，含息到 %s 年變成大約 %s 元；中間最深的一次，帳面少掉 %d%%。'
                    '這是歷史，不是保證。'
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
