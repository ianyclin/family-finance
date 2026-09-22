"""G10／G11（v7 批 S6）：兩張滾動報酬圖，都用美股 S&P 500 含息的月序列。

為什麼有這兩張
    第 8 節的兩張區間表只給「最好／最差」兩個端點，讀者看不出中間長什麼樣，也看不出
    「抱越久，範圍越窄」是怎麼一路收斂的。作者 2026-09-22 指名要這兩種畫法。

口徑（兩張同一條序列，實作在 tools/v7_series.py）
    S&P 500 含息、名目。1871-01 到 2023-06 用 Robert Shiller 公開月資料
    （月報酬＝(P_t＋D_t/12)÷P_{t−1}），2023-07 起用 S&P 500 總報酬指數的月報酬串接到
    2026-08。每個月都當一次買進日，抱滿 N 年；視窗彼此重疊，不是互相獨立的樣本。
    沒有扣物價、費用和稅，也不是台幣。

圖 A（sp500-holding-box）抱幾年，報酬落在哪個範圍
    橫軸 1、3、5、10、20、30 年；鬚＝最差到最好，箱＝第 15 到第 85 百分位，中線＝中位。
    圖上只標最差、最好、中位三個數字，百分位在圖說講。指南放全期（1871 起）那一組；
    起點換成別的年份時（compute_box(start=…)），視窗數少於 30 的那一根不畫，改標「樣本太少」。
    口徑字串一律從資料的起訖年份算出來，不寫死年份。
圖 B（sp500-rolling-30y）滾動 10、20、30 年的年化報酬（v7 批 X：作者 2026-09-22 要三條線）
    同一張圖三條線：10 年（淡灰、最細）、20 年（淡綠、中等）、30 年（深綠，最上層、最粗）。橫軸是視窗
    結束的年份（「抱滿的那個月」），所以 10 年線從 1881 年才開始有點、20 年線 1891、30 年線 1901。
    縱軸從 −5% 起（10 年最差 −4.0%），0% 是墨色的基準線。圖上只標三個點（批 Y：作者要三條線各自的
    最低，拿掉 30 年最高）：10 年最低 −4.0%（1939）、20 年最低 2.0%（1949）、30 年最低 3.6%（1932）；
    其餘數字在圖說。錨點與 data-chart 名稱沿用 sp500-rolling-30y。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v7_series as S

PERIODS = (1, 3, 5, 10, 20, 30)
# v7 批 X：兩張圖的 p.note 各補這一句。1926 年以前那一段資料的來歷，以及它對「最差」的影響——
# 給讀者的誠實揭露，不是但書。7.6% 由 calc_core 的 us_rolling_post1926 算出來並 assert。
# 批 AG：這一段現在直接拼進 r['more'] 的 HTML（不再經過 E.note 跳脫），所以 & 要自己寫成 &amp;。
COWLES_NOTE = ('1926 年以前的月資料是 Shiller 依 Cowles 委員會的指數回推的（那時還沒有 S&amp;P 500）；'
               '把它算進來，30 年最差那一段（結束在 1932 年 6 月）才會出現，'
               '拿掉它 30 年最差會變成 7.6%。本文選擇把最差的留著。')
# 批 AH（D 表）：這一段在兩張長線圖的「想深入」裡逐字重複兩次，滾動圖那一份改成指路。
ROLL_COWLES_REF = '1926 年以前的資料怎麼來、為什麼留著，見上一張圖的「想深入」。'
# 視窗數少於這個數就不畫那一根：四、五個重疊的視窗畫成箱型，會看起來像「歷史上就是這樣」。
MIN_N = 30
# v7 批 Y（作者「縱軸為了兩個極端值而變長」）：縱軸固定不再跟著極端值伸縮，格線每 20%。
# 批 AD（作者 2026-09-22：10 年和 20 年那兩根的差別看不出來）再從 ±70% 收到 ±50%：
# 3 年那一根的兩端（+39.7%／−40.2%）仍在軸內，10、20、30 年那三根又多了四成高度可讀。
# 刻度只標到 ±40，±50 是邊界、不標字。落在範圍外的端點（全期那一組是 1 年的最好 +139.8%
# 與最差 −62.3%）鬚畫到上（下）緣、以箭頭收尾，數字照樣標在箭頭旁，明示它超出了圖的範圍；
# 圖說也會講一句。
AX_LO, AX_HI = -50.0, 50.0
ARROW = 6.0


def _tnum(m):
    y, mm = m.split('-')
    return int(y) + (int(mm) - 1) / 12.0


def _ym(m):
    return '%s 年 %d 月' % (m[:4], int(m[5:7]))


def _textw(s, fs):
    """粗估字串寬度：中日韓字元算一個字寬，其餘算 0.56 個字寬（和 G08 同一個估法）。"""
    w = 0.0
    for ch in s:
        w += 1.0 if ord(ch) > 0x2E7F else 0.56
    return w * fs


def _over_range(rows):
    """哪幾根的端點落在縱軸範圍外（要用箭頭收尾）：回傳 (超出上緣的, 超出下緣的) 兩份年數清單。"""
    drawn = [r for r in rows if r['n'] >= MIN_N]
    return ([r['years'] for r in drawn if r['max'] > AX_HI],
            [r['years'] for r in drawn if r['min'] < AX_LO])


def _pct(v):
    """圖上和圖說的百分比：六根一律一位小數（整數會讓 3.6%% 看成 4%%），負號用全形。"""
    return ('%+.1f%%' % v).replace('-', '−')


def _tick(v):
    """箱型圖縱軸的刻度文字：0 只寫「0%」，其餘帶正負號，負號用全形（和 _pct 的資料標籤一致）。"""
    return ('%+d%%' % v).replace('-', '−') if v else '0%'


def _lab(x, y, t, fs, anchor='middle'):
    """一段文字大概佔住的方框（x, y 是 E.text 的座標，y 是基線）。"""
    w = _textw(t, fs)
    x0 = x - w / 2 if anchor == 'middle' else (x - w if anchor == 'end' else x)
    return (x0, y - fs * 0.88, x0 + w, y + fs * 0.25, t)


def _cols(polys, W):
    """把幾條線壓成「每一個整數 x 那一欄，線佔到哪一段 y」，用來判斷標籤有沒有蓋到線（和 G08 同一套）。"""
    col = [None] * (int(W) + 2)
    for pts in polys:
        for i in range(1, len(pts)):
            x1, y1 = pts[i - 1]
            x2, y2 = pts[i]
            for c in range(int(min(x1, x2)), int(max(x1, x2)) + 1):
                if 0 <= c < len(col):
                    lo, hi = min(y1, y2), max(y1, y2)
                    col[c] = (lo, hi) if col[c] is None else (min(col[c][0], lo), max(col[c][1], hi))
    return col


def _on_line(col, b):
    """標籤方框壓到線的寬度（有幾欄）；0 就是完全沒碰到任何一條線。"""
    n = 0
    for c in range(max(0, int(b[0])), min(len(col) - 1, int(b[2]) + 1)):
        if col[c] is not None and col[c][0] <= b[3] and b[1] <= col[c][1]:
            n += 1
    return n


# 批 AE（作者 2026-09-22：「10 年最低」「20 年最低」被推到整張圖的最上方，引線穿過所有線）：
# 候選不再是「上下九層 × 水平位移」那種只會往上下長的格子，改成以點為圓心的八個方向 × 由近到遠
# 六個距離。距離是「點到標籤框邊」的空隙，不是到框中心——這樣八個方向上的空隙看起來一樣寬。
DIRS = ((1.0, 0.0), (0.7071, 0.7071), (0.0, 1.0), (-0.7071, 0.7071),
        (-1.0, 0.0), (-0.7071, -0.7071), (0.0, -1.0), (0.7071, -0.7071))
DISTS = (14.0, 22.0, 32.0, 46.0, 64.0, 90.0)
CROSS_PENALTY = 150.0      # 引線每穿過一條線一次的罰分：大到「寧可拉遠也不要穿過去」
# 標籤框蓋到線，每蓋住一欄的罰分。抓 20 是讓「蓋住七、八欄」大約等於「引線穿過一次線」：
# 桌機三個標籤都不必蓋線，這個值用不到；手機三個標籤搶同一條空白帶，只能二選一（見 _place_all）。
OVER_PENALTY = 20.0


def _stem(x, yv, box):
    """引線的另一端＝標籤框上離那個點最近的一點（對角擺放時不再只走上下緣）。"""
    x0, y0, x1, y1 = box
    return (min(max(x, x0), x1), min(max(yv, y0), y1))


def _seg_hit(p, q, a, b):
    """兩條線段有沒有交點（共線的情況當作沒交；引線很短，夠用）。"""
    d = (q[0] - p[0]) * (b[1] - a[1]) - (q[1] - p[1]) * (b[0] - a[0])
    if abs(d) < 1e-12:
        return False
    t = ((a[0] - p[0]) * (b[1] - a[1]) - (a[1] - p[1]) * (b[0] - a[0])) / d
    u = ((a[0] - p[0]) * (q[1] - p[1]) - (a[1] - p[1]) * (q[0] - p[0])) / d
    return 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0


def _seg_index(polys, W):
    """把三條線的每一小段依 x 分欄存起來，之後查「這條引線穿過幾次線」只要看它經過的那幾欄。"""
    segs = []
    cols = [[] for _ in range(int(W) + 2)]
    for pts in polys:
        for i in range(1, len(pts)):
            k = len(segs)
            segs.append((pts[i - 1], pts[i]))
            for c in range(int(min(pts[i - 1][0], pts[i][0])), int(max(pts[i - 1][0], pts[i][0])) + 1):
                if 0 <= c < len(cols):
                    cols[c].append(k)
    return segs, cols


def _cross_count(x, yv, box, index, skip=4.5):
    """引線從點連到標籤框，中間穿過幾次線。起算點退開 skip：點本身就坐在自己那條線上。"""
    segs, cols = index
    ex, ey = _stem(x, yv, box)
    L = math.hypot(ex - x, ey - yv)
    if L <= skip:
        return 0
    t = skip / L
    p = (x + (ex - x) * t, yv + (ey - yv) * t)
    q = (ex, ey)
    n, seen = 0, set()
    for c in range(max(0, int(min(p[0], q[0])) - 1), min(len(cols) - 1, int(max(p[0], q[0])) + 1) + 1):
        for k in cols[c]:
            if k in seen:
                continue
            seen.add(k)
            if _seg_hit(p, q, segs[k][0], segs[k][1]):
                n += 1
    return n


def _candidates(x, yv, w, bh, W, bottom, blocked, col, index):
    """列出一個標籤所有合格的位置，照代價由小到大排。

    候選＝八個方向 × 由近到遠幾個距離；距離量的是「點到標籤框邊」的空隙，所以八個方向上的
    空隙看起來一樣寬。標籤一律夾進畫線的那塊方框裡（左右夾進 viewBox、上下夾到橫軸那條線）——
    1939 那個點右邊「0% 到 −5%」的空白帶只有四十幾 px 高，不夾就永遠選不到它。
    硬排除：壓到 blocked（y 軸刻度文字、橫軸年份、0% 基準線、三個圓點）。
    代價＝標籤中心到自己那個點的距離 ＋ 引線穿線次數 × CROSS_PENALTY ＋ 蓋住線的欄數 × OVER_PENALTY。
    「蓋到線」在桌機是硬條件（代價一大就不會被選），但不做硬排除：手機三個標籤只有兩個位置放得下，
    硬排除的話就只剩「把一個標籤丟到 115px 外、引線穿過 9 條線」那種解，那正是批 AE 要修掉的毛病。
    """
    out, seen = [], set()
    for d in DISTS:
        for ux, uy in DIRS:
            sup = abs(ux) * w / 2 + abs(uy) * bh / 2      # 標籤框在這個方向上的「半徑」
            x0 = min(max(x + ux * (d + sup) - w / 2, 1.5), W - w - 1.5)
            y0 = min(max(yv + uy * (d + sup) - bh / 2, 1.5), bottom - 1.5 - bh)
            key = (round(x0, 1), round(y0, 1))
            if key in seen or bottom - 1.5 - bh < 1.5:
                continue
            seen.add(key)
            box = (x0, y0, x0 + w, y0 + bh)
            # 對固定物不留額外餘裕：它們的方框本來就含了自己的（0% 線給到 ±1.5、圓點給到半徑＋2.5），
            # 再多留 2px 會把只有四十幾 px 高的空白帶整條排除掉。
            if any((box[0] < q[2] and q[0] < box[2] and box[1] < q[3] and q[1] < box[3]) for q in blocked):
                continue
            over = _on_line(col, box)
            cost = (math.hypot(x0 + w / 2 - x, y0 + bh / 2 - yv)
                    + CROSS_PENALTY * _cross_count(x, yv, box, index)
                    + OVER_PENALTY * over)
            out.append((cost, box))
    out.sort(key=lambda t: t[0])
    return out


def _place_all(items, W, bottom, blocked, col, index, keep=20):
    """三個標籤一起挑位置：先各自列出合格候選，再找「彼此不重疊、總代價最小」的一組。

    批 AD 是一個一個貪心放的：先放好的「10 年最低」佔掉那條空白帶，後面兩個就被擠到整張圖的
    最上方，引線一路穿過所有線。三個標籤搶的是同一條帶，只能一起看。
    每個標籤只留代價最小的 keep 個候選，再配上「已經比目前最好的貴就不用往下試」的剪枝；
    三個標籤 × 二十個候選，全部組合都試得完。回 None 表示連一組不互相重疊的都排不出來。
    """
    lists = [_candidates(x, yv, w, bh, W, bottom, blocked, col, index)[:keep]
             for (x, yv, w, bh) in items]

    def search(lists):
        best = [None]

        def rec(i, chosen, cost):
            if best[0] is not None and cost >= best[0][0]:
                return
            if i == len(lists):
                best[0] = (cost, list(chosen))
                return
            for c, box in lists[i]:
                if best[0] is not None and cost + c >= best[0][0]:
                    break                               # 已排序，後面只會更貴
                if any((box[0] < q[2] + 2 and q[0] - 2 < box[2] and
                        box[1] < q[3] + 2 and q[1] - 2 < box[3]) for q in chosen):
                    continue                            # 標籤和標籤之間留 2px 才看得出是兩張卡
                chosen.append(box)
                rec(i + 1, chosen, cost + c)
                chosen.pop()

        rec(0, [], 0.0)
        return None if best[0] is None else best[0][1]

    return search(lists)


def _check(cid, kind, boxes, W, H, warn):
    """和 G08 同款的自檢：同一版裡兩兩不重疊、不超出 viewBox。"""
    for i in range(len(boxes)):
        x0, y0, x1, y1, t = boxes[i]
        if x0 < 0 or x1 > W or y0 < 0 or y1 > H:
            warn.append('%s %s 標籤「%s」超出 viewBox' % (cid, kind, t))
        for j in range(i + 1, len(boxes)):
            q = boxes[j]
            if x0 < q[2] and q[0] < x1 and y0 < q[3] and q[1] < y1:
                warn.append('%s %s 標籤「%s」和「%s」重疊' % (cid, kind, t, q[4]))


# ---------------------------------------------------------------- compute
def compute_box(start=None):
    """start=None 用全期（1871-01）；給月份就只用那個月以後的資料（樣張用近 30 年）。"""
    months, tr = S.shiller_tr_extended()
    if start:
        i = months.index(start)
        months, tr = months[i:], tr[i:]
    rows = []
    for y in PERIODS:
        if len(tr) <= y * 12:
            continue
        row = S.rolling_summary(months, tr, y)
        # 批 AG：圖說要講「抱 5 年十次裡大約九次是賺的、抱滿 20 年沒有一次是賠的」，
        # 所以每一根多算一個「負的視窗數」（和 calc_core 的 us_rolling_negative_share 同一個算法）。
        pts = S.rolling_annualised(months, tr, y)
        row['neg'] = sum(1 for _m, v, _s in pts if v < 0)
        row['neg_pct'] = row['neg'] * 100.0 / len(pts)
        rows.append(row)
    return {'id': 'sp500-holding-box' if not start else 'sp500-holding-box-30y',
            'from': months[0], 'to': months[-1], 'rows': rows,
            'full_period': not start}


def compute_rolling(years_list=(10, 20, 30)):
    """三條滾動年化報酬線。每一條：每個月都當一次買進日，抱滿 N 年。"""
    months, tr = S.shiller_tr_extended()
    series = []
    for y in years_list:
        pts = S.rolling_annualised(months, tr, y)
        neg = sum(1 for _m, v, _s in pts if v < 0)
        series.append({
            'years': y, 'points': pts, 'n': len(pts),
            'from': pts[0][0], 'to': pts[-1][0],
            'first_start': pts[0][2], 'last_start': pts[-1][2],
            'min': min(pts, key=lambda x: x[1]), 'max': max(pts, key=lambda x: x[1]),
            'last': pts[-1], 'neg': neg, 'neg_pct': neg * 100.0 / len(pts),
        })
    # 批 AE：同一條序列扣掉物價（÷ 同一份 Shiller 資料的消費者物價指數欄）再算一次，
    # 圖說和「想深入」各要用一組。物價欄止於 2023-09，所以扣物價的視窗比名目的少幾個。
    cpi = S.shiller_cpi()
    real = {}
    for y in years_list:
        pts = S.rolling_real(months, tr, cpi, y)
        worst = min(pts, key=lambda x: x[1])
        neg = sum(1 for _m, v, _s in pts if v < 0)
        real[y] = {'n': len(pts), 'worst': worst[1], 'worst_start': worst[2], 'worst_end': worst[0],
                   'neg': neg, 'neg_pct': neg * 100.0 / len(pts),
                   'first_end': pts[0][0], 'last_end': pts[-1][0]}
    return {'id': 'sp500-rolling-30y', 'series': series, 'real': real,
            'data_from': months[0], 'data_to': months[-1]}


# ---------------------------------------------------------------- 圖 A
def chart_box(res):
    import essay_charts as E
    rows = res['rows']
    warn = []

    def draw(lay):
        mob = lay.mobile
        fl = 9.2 if mob else 11
        h = 300 if mob else 350
        top = lay.top + 12
        bottom = h - 34
        left = lay.left - 4
        right = lay.right - (12 if mob else 4)   # 最後一組的中位數標在箱的右邊，右邊要留得下
        gw = (right - left) / len(rows)
        bw = gw * (0.40 if mob else 0.36)

        def py(v):
            return bottom - (bottom - top) * (v - AX_LO) / (AX_HI - AX_LO)

        def pyc(v):
            """畫圖用的 y：落在縱軸範圍外的值先夾回範圍內（端點另外用箭頭表示超出）。"""
            return py(min(max(v, AX_LO), AX_HI))

        out = [E.svg_open(lay, h, res['aria'])]
        ticks = list(range(-40, 41, 20))      # ±50 是邊界，不標字（批 AD）
        out += E.grid(lay, py, ticks, _tick)
        boxes = [_lab(lay.left - 6, py(t) + lay.fs * 0.36,
                      _tick(t), lay.fs, 'end') for t in ticks]
        for k, r in enumerate(rows):
            cx = left + gw * (k + 0.5)
            col = E.TEAL
            boxes.append(_lab(cx, bottom + lay.f + 8, '%d 年' % r['years'], lay.f))
            if r['n'] < MIN_N:
                # 視窗太少（例如起點往後挪以後的 30 年那一根）：不畫箱和鬚，只說樣本太少。
                # 字放在貼近橫軸的地方：那一帶沒有別的標籤，不會壓到隔壁那一根的數字。
                out.append(E.text(cx, bottom - 4, '樣本太少', lay.f, 'middle', E.MUTED, '700'))
                boxes.append(_lab(cx, bottom - 4, '樣本太少', lay.f))
                out.append(E.text(cx, bottom + lay.f + 8, '%d 年' % r['years'], lay.f, 'middle', E.INK, '700'))
                continue
            # 鬚：最差到最好。超出縱軸範圍的那一端不畫橫槓，改成畫到上（下）緣、以箭頭收尾。
            hi_out, lo_out = r['max'] > AX_HI, r['min'] < AX_LO
            ytop = (py(AX_HI) + ARROW + 1.0) if hi_out else pyc(r['max'])
            ybot = (py(AX_LO) - ARROW - 1.0) if lo_out else pyc(r['min'])
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2"/>'
                       % (cx, ytop, cx, ybot, E.MUTED))
            for yend, out_of_range, up in ((ytop, hi_out, True), (ybot, lo_out, False)):
                if out_of_range:
                    tip = yend - ARROW if up else yend + ARROW
                    out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                               % (cx, tip, cx - 3.4, yend, cx + 3.4, yend, E.MUTED))
                else:
                    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2"/>'
                               % (cx - bw * 0.28, yend, cx + bw * 0.28, yend, E.MUTED))
            # 箱：第 15 到第 85 百分位
            y0, y1 = pyc(r['p85']), pyc(r['p15'])
            out.append(E.rect(cx - bw / 2, y0, bw, max(2.0, y1 - y0), col, rx=2, opacity=0.35))
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="none" stroke="%s" stroke-width="1.2"/>'
                       % (cx - bw / 2, y0, bw, max(2.0, y1 - y0), col))
            # 中線
            ymed = pyc(r['median'])
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.2"/>'
                       % (cx - bw / 2, ymed, cx + bw / 2, ymed, col))
            # 三個數字。六根的精度一致（都一位小數）：抱久了以後範圍很窄，整數會讓 3.6% 看成 4%。
            def num(v):
                return _pct(v)
            ymaxlab = (ytop - ARROW - 5) if hi_out else (ytop - 5)
            # 下緣超出範圍時（批 AD 把縱軸收到 ±50 之後，全期那一組的 1 年最差 −62.3% 也超出了）：
            # 批 AE（作者：現在標在下箭頭的正下方，貼著「1 年」那個字）改成標在箭頭尖的右邊、
            # 和箭頭尖垂直置中（上面的 +139.8% 標在上箭頭的上方，維持原樣）。
            yminlab = ((py(AX_LO) - 1) + fl * 0.36) if lo_out else (ybot + fl + 3)
            xmin, amin = ((cx + 5, 'start') if lo_out else (cx, 'middle'))
            boxes += [_lab(cx, ymaxlab, num(r['max']), fl), _lab(xmin, yminlab, num(r['min']), fl, amin)]
            out.append(E.text(cx, ymaxlab, num(r['max']), fl, 'middle', E.INK, '700'))
            out.append(E.text(xmin, yminlab, num(r['min']), fl, amin, E.INK, '700'))
            # 中位數標在箱的右邊；右邊放不下（最後一組）就改標在箱的左邊，不出 viewBox
            med = '%.1f%%' % r['median']
            wmed = len(med) * fl * 0.56 + 3
            if cx + bw / 2 + wmed <= lay.W - 6:
                out.append(E.text(cx + bw / 2 + 3, ymed + fl * 0.36, med, fl, 'start', E.TEAL, '800'))
                boxes.append(_lab(cx + bw / 2 + 3, ymed + fl * 0.36, med, fl, 'start'))
            else:
                out.append(E.text(cx - bw / 2 - 3, ymed + fl * 0.36, med, fl, 'end', E.TEAL, '800'))
                boxes.append(_lab(cx - bw / 2 - 3, ymed + fl * 0.36, med, fl, 'end'))
            out.append(E.text(cx, bottom + lay.f + 8, '%d 年' % r['years'], lay.f, 'middle', E.INK, '700'))
        out.append('</svg>')
        _check(res['id'], lay.kind, boxes, lay.W, h, warn)
        return '\n'.join(out)

    svgs = [draw(E.L('d')), draw(E.L('m'))]
    for w in warn:
        print('⚠ ' + w)
    lg = E.legend([(E.TEAL, '箱＝第 15 到第 85 百分位，中線＝中位數，細鬚＝最差到最好')])
    return dict(title=res['title'], sub=res['sub'],
                svgs=svgs,
                extras=lg + (E.note(res['note']) if res['note'] else '') + res['more'],
                caption=res['caption'])


# ---------------------------------------------------------------- 圖 B
# 三條線的顏色都取自既有調色盤（沒有新增顏色）：--line 淺灰、--teal 綠。
# 第四欄是線的透明度。批 AD（作者 2026-09-22：10 年和 20 年灰得太像，分不出來）：20 年那條從
# --muted 改成 --teal、40% 不透明，三條線變成「淡灰最細 → 淡綠中等 → 深綠最粗」，
# 用同一個顏色的濃淡表示同一件事抱得越久；深色模式沿用同一個變數，自動跟著換。
# 批 AE（作者看 PNG：0.4 還是偏灰）再抬到 0.5；圖例讀的是同一格，自動跟著改。
LINE_STYLE = {10: ('LINE', 1.2, 1.4, None), 20: ('TEAL', 1.5, 1.7, 0.5), 30: ('TEAL', 1.9, 2.2, None)}


def chart_rolling(res):
    import essay_charts as E

    series = sorted(res['series'], key=lambda x: x['years'])   # 10 先畫、30 最後畫（壓在最上層）
    allpts = [p for sr in series for p in sr['points']]
    t0 = min(_tnum(sr['points'][0][0]) for sr in series)
    t1 = max(_tnum(sr['points'][-1][0]) for sr in series)
    lo_v, hi_v = -5.0, max(x[1] for x in allpts) * 1.06
    by_year = {sr['years']: sr for sr in series}
    warn = []

    def draw(lay):
        mob = lay.mobile
        fl = 9.6 if mob else 11
        h = 268 if mob else 306
        top = lay.top + 16
        bottom = h - 30
        left = lay.left
        right = lay.right - 2

        def px(m):
            return left + (right - left) * (_tnum(m) - t0) / (t1 - t0)

        def py(v):
            return bottom - (bottom - top) * (v - lo_v) / (hi_v - lo_v)

        out = [E.svg_open(lay, h, res['aria'])]
        ticks = (-5, 0, 5, 10, 15, 20)
        # 0% 用 grid() 預設的墨色實線，其餘是淡虛線：讀者一眼看得出線有沒有掉到 0 以下
        out += E.grid(lay, py, ticks, lambda v: ('%d%%' % v).replace('-', '−'))
        boxes = [_lab(lay.left - 6, py(t) + lay.fs * 0.36, ('%d%%' % t).replace('-', '−'), lay.fs, 'end')
                 for t in ticks]
        for y in range(1880, int(max(sr['to'] for sr in series)[:4]) + 1, 20):
            m = '%d-01' % y
            if t0 <= _tnum(m) <= t1:
                out.append(E.text(px(m), bottom + lay.f + 6, str(y), lay.f, 'middle', E.MUTED))
                boxes.append(_lab(px(m), bottom + lay.f + 6, str(y), lay.f))
        for sr in series:
            name, wd, wm, op = LINE_STYLE[sr['years']]
            out.append(E.poly([(px(m), py(v)) for m, v, _s in sr['points']],
                              getattr(E, name), wd if mob else wm, opacity=op))
        # 只標三個點（批 Y）：三條線各自的最低。批 AD（作者：標籤壓在線上）：不再用固定偏移，
        # 改成和 G08 長線圖同一套——在點的上下幾層、左右幾格的候選裡，挑一個不壓到任何一條線、
        # 不壓 0% 基準線與刻度文字、不和別的標籤重疊、又離自己那個點最近的位置；標籤畫底色框、
        # 用虛線引線連回點，三個圓點最後畫（才不會被標籤的底色蓋掉）。
        pad = 2.6
        lh = fl * 1.16
        bh = 2 * lh + 2 * pad      # 兩行：第一行「N 年最低」，第二行數字與年份（和 G08 同款）
        polys = [[(px(m), py(v)) for m, v, _s in sr['points']] for sr in series]
        col = _cols(polys, lay.W)
        index = _seg_index(polys, lay.W)
        marks = [(10, 'min', '10 年最低'), (20, 'min', '20 年最低'), (30, 'min', '30 年最低')]
        pts3 = [(px(by_year[y][k][0]), py(by_year[y][k][1])) for y, k, _l in marks]
        dr = 3.6 + 2.5
        fixed = [tuple(b[:4]) for b in boxes]                      # 刻度文字、橫軸年份
        fixed.append((left, py(0) - 1.5, right, py(0) + 1.5))      # 0% 是墨色基準線
        fixed += [(a - dr, b - dr, a + dr, b + dr) for a, b in pts3]
        texts, items = [], []
        for (yrs, key, label), (x, yy) in zip(marks, pts3):
            m, v, _st = by_year[yrs][key]
            l1, l2 = label, '%s（%s）' % (('%.1f%%' % v).replace('-', '−'), m[:4])
            texts.append((l1, l2))
            items.append((x, yy, max(_textw(l1, fl), _textw(l2, fl)) + 2 * pad, bh))
        spots = _place_all(items, lay.W, bottom, fixed, col, index)
        placed, drawn = [], []
        if spots is None:
            warn.append('%s %s 三個最低標籤排不下' % (res['id'], lay.kind))
            spots = []
        for (x, yy, w, _bh), (l1, l2), box in zip(items, texts, spots):
            placed.append(box)
            drawn.append((x, yy, box[0], box[1], w, l1, l2))
            boxes.append((box[0], box[1], box[2], box[3], '%s %s' % (l1, l2)))
        for x, yy, x0, y0, w, _l1, _l2 in drawn:   # 先畫全部引線，字才不會被別人的引線壓到
            ex, ey = _stem(x, yy, (x0, y0, x0 + w, y0 + bh))   # 框上離點最近的那一點
            d = math.hypot(ex - x, ey - yy)
            if d > 2.0:                                        # 收短 1.5px，虛線不要頂到框邊
                ex, ey = x + (ex - x) * (d - 1.5) / d, yy + (ey - yy) * (d - 1.5) / d
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="0.8" '
                       'stroke-dasharray="2 3" stroke-opacity="0.75"/>'
                       % (x, yy, ex, ey, E.MUTED))
        for x, yy, x0, y0, w, l1, l2 in drawn:
            out.append(E.rect(x0, y0, w, bh, E.SURFACE, 3, 0.86))
            out.append(E.text(x0 + pad, y0 + pad + fl * 0.88, l1, fl, 'start', E.MUTED))
            out.append(E.text(x0 + pad, y0 + pad + fl * 0.88 + lh, l2, fl, 'start', E.INK, '700'))
        for x, yy in pts3:                     # 圓點最後畫
            out.append(E.dot(x, yy, E.ACCENT, 3.6))
        out.append('</svg>')
        _check(res['id'], lay.kind, boxes, lay.W, h, warn)
        # 批 AD 起的自檢：標籤不要蓋住線。批 AE 放寬成「蓋住自己寬度的四分之一以上才算不合格」，
        # 另加一條「引線不准穿過線」。為什麼放寬：手機只有 300 px 寬的畫線區，三個標籤都得擠進
        # 0% 線以下那條四十幾 px 高的帶子，「20 年最低」會蓋到 10 年線 1974 年那個凹谷 8 欄
        # （佔自己寬度 12%）。要完全不蓋，就得把「30 年最低」推到 115 px 外、引線穿過 9 條線——
        # 那正是這一批要修掉的毛病。桌機三個標籤是 0 欄、0 穿線。
        for (x0, y0, x1, y1), d in zip(placed, drawn):
            over = _on_line(col, (x0, y0, x1, y1))
            if over > 0.25 * (x1 - x0):
                warn.append('%s %s 標籤「%s %s」蓋住線 %d 欄（標籤寬 %.0f）'
                            % (res['id'], lay.kind, d[5], d[6], over, x1 - x0))
            cross = _cross_count(d[0], d[1], (x0, y0, x1, y1), index)
            if cross:
                warn.append('%s %s 標籤「%s %s」的引線穿過線 %d 次'
                            % (res['id'], lay.kind, d[5], d[6], cross))
        return '\n'.join(out)

    svgs = [draw(E.L('d')), draw(E.L('m'))]
    for w in warn:
        print('⚠ ' + w)
    lg = E.legend([(E.LINE, '抱 10 年'),
                   (E.TEAL, '抱 20 年', LINE_STYLE[20][3]),
                   (E.TEAL, '抱 30 年')])
    return dict(title=res['title'], sub=res['sub'], svgs=svgs,
                extras=lg + (E.note(res['note']) if res['note'] else '') + res['more'],
                caption=res['caption'])


# ---------------------------------------------------------------- 三個進入點
def _box_dress(r):
    span = '%s–%s' % (r['from'][:4], r['to'][:4])
    n1 = [x for x in r['rows'] if x['years'] == 1][0]
    n30 = [x for x in r['rows'] if x['years'] == 30 and x['n'] >= MIN_N]
    r['aria'] = '美股 %s，抱 1、3、5、10、20、30 年的年化報酬範圍（箱型）' % span
    r['title'] = '抱幾年，報酬落在哪個範圍'
    r['sub'] = 'S&P 500 含息、名目，資料 %s，每個月都當一次買進日，年化 %%' % span
    hi_out, lo_out = _over_range(r['rows'])
    # 縱軸固定（批 Y 定 ±70%、批 AD 收成 ±50%）：落在範圍外的端點用箭頭收尾，圖說要講明白。
    # 同一根的兩端都超出時合成一句，不要一模一樣的句型講兩次（批 AD）。
    yrs = lambda ys: '、'.join('%d 年' % y for y in ys)
    over = ''
    if hi_out and hi_out == lo_out:
        over = '%s那一根的最好和最差都超出了圖的範圍，用箭頭表示。' % yrs(hi_out)
    else:
        if hi_out:
            over = '%s那一根的最好一次超出了圖的範圍，用箭頭表示。' % yrs(hi_out)
        if lo_out:
            over += '%s那一根的最差一次超出了圖的範圍，用箭頭表示。' % yrs(lo_out)
    # 批 AG（作者 2026-09-22）：p.note 整段與原圖說整段都搬進「想深入」，圖上只留「這張圖告訴我什麼」。
    r['note'] = ''
    r['more'] = ('<details class="more" data-print="open">'
                 '<summary>想深入：這張圖的資料、口徑，和它跟「想深入」裡那張區間表的差別</summary>'
                 '<p class="note">'
                 # 這一段原本是圖下的 p.note
                 '每個月都當一次買進日，抱滿 N 年，再換算成平均一年的報酬。'
                 '1 年那一根有 %s 個視窗%s。視窗彼此重疊，不是互相獨立的樣本。'
                 '這張圖和下面「想深入」裡 J.P. Morgan 的區間表講的是同一件事，'
                 '口徑不一樣（起始年、整年 vs 逐月、資料來源），數字不會一致。'
                 '縱軸畫到 ±50%%，超出的用箭頭收尾。%s'
                 'S&amp;P 500 含息、名目：%s到 2023 年 6 月用 Robert Shiller 公開月資料，'
                 '2023 年 7 月起用 S&amp;P 500 總報酬指數串接到 %s。沒有扣物價、費用和稅，也不是台幣。'
                 '箱是第 15 到第 85 百分位（把所有視窗從小排到大，切掉最前面 15%% 和最後面 15%%），'
                 '中線是中位數，細鬚兩端是這段歷史裡最差和最好的那一次。'
                 # 批 AH：和區間表口徑不同這件事，上面那一句已經講過，這裡不再重述一次。
                 '期間越長、起算方式越細，最好和最差就越極端。'
                 # 以下是批 AG 從圖說搬下來的，順序照舊（%s 是端點超出縱軸範圍的那一句）
                 '往右看，鬚越來越短：抱 1 年最差 %s、最好 %s，%s。'
                 '中間那條線是中位數，一半的視窗在它上面、一半在下面。%s'
                 # 批 AH：「視窗彼此重疊」上面已經講過一次，這裡收掉。
                 '這是歷史，不是保證。</p></details>'
                 % ('{:,}'.format(n1['n']),
                    '，30 年那一根有 %s 個' % '{:,}'.format(n30[0]['n']) if n30 else '',
                    COWLES_NOTE,
                    _ym(r['from']), _ym(r['to']),
                    _pct(n1['min']), _pct(n1['max']),
                    ('抱 30 年最差 %s、最好 %s' % (_pct(n30[0]['min']), _pct(n30[0]['max']))) if n30
                    else '30 年那一根的視窗太少，沒有畫', over))
    # 批 AG：作者定稿的兩句。「十次裡大約九次」＝抱 5 年為正的比例（10.23% 是負的，
    # calc_core 的 us_rolling_negative_share 也 assert 同一個數字）；「這 155 年」＝資料起訖年份相減。
    n5 = [x for x in r['rows'] if x['years'] == 5][0]
    n20 = [x for x in r['rows'] if x['years'] == 20][0]
    span_years = int(r['to'][:4]) - int(r['from'][:4])
    assert r['full_period'], '批 AG 的圖說只適用全期那一組；別的起點要另外寫圖說'
    assert round((100.0 - n5['neg_pct']) / 10.0) == 9, n5            # 十次裡大約九次
    assert n20['neg'] == 0, n20                                       # 抱滿 20 年沒有一次是賠的
    assert span_years == 155, (span_years, r['from'], r['to'])        # 資料延長就要改圖說的年數
    r['caption'] = ('抱越久，報酬越穩定。抱 5 年，十次裡大約九次是賺的；'
                    '抱滿 20 年，這 %d 年裡沒有一次是賠的。' % span_years)
    return r


def holding_box():
    return chart_box(_box_dress(compute_box()))


def holding_box_recent30():
    months, _tr = S.shiller_tr_extended()
    # 近 30 年＝最後一個月往前推 30 年
    y, m = int(months[-1][:4]) - 30, months[-1][5:7]
    return chart_box(_box_dress(compute_box('%d-%s' % (y, m))))


def rolling_30y():
    """三條線的滾動報酬圖。函式名、錨點與 data-chart 都沿用 sp500-rolling-30y，所以書裡的連結不用改；
    但兩處引用圖名的句子（第 10 節的指路、第 8 節來源卡）跟著改成新標題。"""
    r = compute_rolling()
    by = {sr['years']: sr for sr in r['series']}
    rl = r['real']                      # 扣掉物價的同一組（批 AE）
    span = '%s–%s' % (r['data_from'][:4], r['data_to'][:4])
    r['aria'] = ('美股滾動 10、20、30 年的年化報酬：每一個月都當一次買進日，分別抱滿 10、20、30 年；'
                 '抱 10 年最差 %s、抱 20 年最差 %s、抱 30 年最差 %s'
                 % tuple(('%.1f%%' % by[y]['min'][1]).replace('-', '−') for y in (10, 20, 30)))
    r['title'] = '滾動 10、20、30 年的年化報酬：每一個起點各算一次'
    r['sub'] = 'S&P 500 含息、名目，資料 %s；橫軸是抱滿的那個月，年化 %%' % span
    # 批 AG（作者 2026-09-22）：p.note 整段、圖說末尾扣物價那兩句與「這是歷史，不是保證」都搬進「想深入」。
    r['note'] = ''
    r['more'] = ('<details class="more" data-print="open">'
                 '<summary>想深入：這張圖的資料和口徑</summary>'
                 '<p class="note">'
                 # 這一段原本是圖下的 p.note
                 '三條線的橫軸都是「抱滿的那個月」；最早的視窗從 %s起算，'
                 '所以 10 年線從 %s 年開始有點、20 年線 %s 年、30 年線 %s 年。'
                 # 批 AH（D 表）：Cowles 那一整段和上一張圖逐字重複，這裡改成指路。
                 '視窗彼此重疊，不是互相獨立的樣本。%s'
                 'S&amp;P 500 含息、名目：%s到 2023 年 6 月用 Robert Shiller 公開月資料，'
                 '2023 年 7 月起用 S&amp;P 500 總報酬指數串接到 %s。沒有扣物價、費用和稅，也不是台幣。'
                 '扣掉物價以後，這張圖自己算出來的最差是：'
                 '10 年 %s（%s起）、20 年 %s（%s起）、30 年 %s（%s起）。'
                 # 批 AG 從圖說搬下來的：同樣的三組數字原本在圖說裡又講了一次，只留這一份，
                 # 圖說多出來的那兩件事（虧錢的起點比例、所以那句結論）接在後面。
                 '虧錢的起點也從 %d%% 變成 %d%%，'
                 '所以「二十年沒有一個起點是虧的」只在不扣物價時成立。'
                 '同一節「二十年扣掉物價最差」那一句算的是 1950 年以後、整年為單位的另一組，'
                 '起點不同，數字也不一樣。'
                 '三條線各自的視窗數：10 年 %s 個、20 年 %s 個、30 年 %s 個。'
                 '10 年線有 %d 個視窗是負的（%.1f%%），最低的那一次結束在 %s；'
                 '20 年線最低 %.1f%%，結束在 %s；'
                 '30 年線最低的那一次結束在 %s，最高的那一次結束在 %s，'
                 '最後一個算得出來的 30 年視窗從 %s起、結束在 %s，是 %.1f%%。'
                 '這是歷史，不是保證。</p></details>'
                 % (_ym(r['data_from']), by[10]['from'][:4], by[20]['from'][:4], by[30]['from'][:4],
                    ROLL_COWLES_REF,
                    _ym(r['data_from']), _ym(r['data_to']),
                    _pct(rl[10]['worst']), _ym(rl[10]['worst_start']),
                    _pct(rl[20]['worst']), _ym(rl[20]['worst_start']),
                    _pct(rl[30]['worst']), _ym(rl[30]['worst_start']),
                    round(by[10]['neg_pct']), round(rl[10]['neg_pct']),
                    '{:,}'.format(by[10]['n']), '{:,}'.format(by[20]['n']), '{:,}'.format(by[30]['n']),
                    by[10]['neg'], by[10]['neg_pct'], _ym(by[10]['min'][0]),
                    by[20]['min'][1], _ym(by[20]['min'][0]),
                    _ym(by[30]['min'][0]), _ym(by[30]['max'][0]),
                    _ym(by[30]['last_start']), _ym(by[30]['last'][0]), by[30]['last'][1]))
    # 批 AG：作者定稿。「沒扣物價」從原本末尾那兩句提到括號裡，扣物價的細節在「想深入」。
    r['caption'] = ('三條線各是從某個月開始、抱滿 10、20、30 年的平均一年報酬。'
                    '抱 10 年，歷史上有大約 %d%% 的起點是虧的，最差一年 %s；'
                    '抱 20 年，沒有一個起點是虧的（沒扣物價），最差一年 %.1f%%；'
                    '抱 30 年，最差也有 %.1f%%。'
                    '哪一年開始你決定不了，抱多久你決定得了，'
                    '何況多數人是分批投入，起點本來就散在很多個月。'
                    % (round(by[10]['neg_pct']), ('%.1f%%' % by[10]['min'][1]).replace('-', '−'),
                       by[20]['min'][1], by[30]['min'][1]))
    return chart_rolling(r)


if __name__ == '__main__':
    import json
    b = compute_box()
    print(json.dumps(b['rows'], ensure_ascii=False, indent=1))
    r = compute_rolling()
    for sr in r['series']:
        print(sr['years'], sr['n'], sr['min'], sr['max'], sr['last'], sr['neg'], round(sr['neg_pct'], 3))
