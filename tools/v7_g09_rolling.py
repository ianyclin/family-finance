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
    同一張圖三條線：10 年（淺灰）、20 年（中灰）、30 年（綠色，最上層、最粗）。橫軸是視窗
    結束的年份（「抱滿的那個月」），所以 10 年線從 1881 年才開始有點、20 年線 1891、30 年線 1901。
    縱軸從 −5% 起（10 年最差 −4.0%），0% 是墨色的基準線。圖上只標三個點（批 Y：作者要三條線各自的
    最低，拿掉 30 年最高）：10 年最低 −4.0%（1939）、20 年最低 2.0%（1949）、30 年最低 3.6%（1932）；
    其餘數字在圖說。錨點與 data-chart 名稱沿用 sp500-rolling-30y。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v7_series as S

PERIODS = (1, 3, 5, 10, 20, 30)
# v7 批 X：兩張圖的 p.note 各補這一句。1926 年以前那一段資料的來歷，以及它對「最差」的影響——
# 給讀者的誠實揭露，不是但書。7.6% 由 calc_core 的 us_rolling_post1926 算出來並 assert。
COWLES_NOTE = ('1926 年以前的月資料是 Shiller 依 Cowles 委員會的指數回推的（那時還沒有 S&P 500）；'
               '把它算進來，30 年最差那一段（結束在 1932 年 6 月）才會出現，'
               '拿掉它 30 年最差會變成 7.6%。本文選擇把最差的留著。')
# 視窗數少於這個數就不畫那一根：四、五個重疊的視窗畫成箱型，會看起來像「歷史上就是這樣」。
MIN_N = 30
# v7 批 Y（作者「縱軸為了兩個極端值而變長」）：縱軸固定 −70%～+70%、格線每 20%，不再跟著極端值伸縮。
# 10、20、30 年那幾根箱子因此有兩倍的高度可讀。落在範圍外的端點（全期那一組是 1 年的最好 +139.8%）
# 鬚畫到上緣、以箭頭收尾，數字照樣標在箭頭旁，明示它超出了圖的範圍；圖說也會講一句。
AX_LO, AX_HI = -70.0, 70.0
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
        rows.append(S.rolling_summary(months, tr, y))
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
    return {'id': 'sp500-rolling-30y', 'series': series,
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
        ticks = list(range(-60, 61, 20))
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
            yminlab = (ybot + ARROW + fl + 3) if lo_out else (ybot + fl + 3)
            boxes += [_lab(cx, ymaxlab, num(r['max']), fl), _lab(cx, yminlab, num(r['min']), fl)]
            out.append(E.text(cx, ymaxlab, num(r['max']), fl, 'middle', E.INK, '700'))
            out.append(E.text(cx, yminlab, num(r['min']), fl, 'middle', E.INK, '700'))
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
                extras=lg + E.note(res['note']) + res['more'], caption=res['caption'])


# ---------------------------------------------------------------- 圖 B
# 三條線的顏色都取自既有調色盤（沒有新增顏色）：--line 淺灰、--muted 中灰、--teal 綠。
# 第四欄是線的透明度（批 Y：作者要 20 年那條再淡一些，落在 10 年淺灰與 20 年中灰之間）：
# --muted 畫成 45% 不透明（＝55% 透明），深色模式沿用同一個變數，自動跟著換。
LINE_STYLE = {10: ('LINE', 1.2, 1.4, None), 20: ('MUTED', 1.4, 1.6, 0.45), 30: ('TEAL', 1.9, 2.2, None)}


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
        # 只標三個點（批 Y）：三條線各自的最低。三個點的年份離得近（1932、1939、1949），
        # 標籤一定會在橫向重疊，所以靠縱向交錯開：30 年最低（y≈3.6%）往上、20 年最低（y≈2.0%）往下、
        # 10 年最低那個點貼著圖框底部只能往上（往下會壓到 x 軸的年份）。
        marks = [(10, 'min', '10 年最低', -8), (20, 'min', '20 年最低', fl + 9),
                 (30, 'min', '30 年最低', -8)]
        for yrs, key, label, dy in marks:
            m, v, _st = by_year[yrs][key]
            x, yy = px(m), py(v)
            out.append(E.dot(x, yy, E.ACCENT, 3.6))
            tx = min(max(x, left + 44), right - 44)
            t = '%s %s（%s）' % (label, ('%.1f%%' % v).replace('-', '−'), m[:4])
            out.append(E.text(tx, yy + dy, t, fl, 'middle', E.INK, '700'))
            boxes.append(_lab(tx, yy + dy, t, fl))
        out.append('</svg>')
        _check(res['id'], lay.kind, boxes, lay.W, h, warn)
        return '\n'.join(out)

    svgs = [draw(E.L('d')), draw(E.L('m'))]
    for w in warn:
        print('⚠ ' + w)
    lg = E.legend([(E.LINE, '抱 10 年'),
                   (E.MUTED, '抱 20 年', LINE_STYLE[20][3]),
                   (E.TEAL, '抱 30 年')])
    return dict(title=res['title'], sub=res['sub'], svgs=svgs,
                extras=lg + E.note(res['note']) + res['more'], caption=res['caption'])


# ---------------------------------------------------------------- 三個進入點
def _box_dress(r):
    span = '%s–%s' % (r['from'][:4], r['to'][:4])
    n1 = [x for x in r['rows'] if x['years'] == 1][0]
    n30 = [x for x in r['rows'] if x['years'] == 30 and x['n'] >= MIN_N]
    r['aria'] = '美股 %s，抱 1、3、5、10、20、30 年的年化報酬範圍（箱型）' % span
    r['title'] = '抱幾年，報酬落在哪個範圍'
    r['sub'] = 'S&P 500 含息、名目，資料 %s，每個月都當一次買進日，年化 %%' % span
    r['note'] = ('每個月都當一次買進日，抱滿 N 年，再換算成平均一年的報酬。'
                 '1 年那一根有 %s 個視窗%s。視窗彼此重疊，不是互相獨立的樣本。'
                 '這張圖和下面那張 J.P. Morgan 的區間表講的是同一件事，'
                 '口徑不一樣（起始年、整年 vs 逐月、資料來源），數字不會一致。'
                 % ('{:,}'.format(n1['n']),
                    '，30 年那一根有 %s 個' % '{:,}'.format(n30[0]['n']) if n30 else '')
                 + COWLES_NOTE)
    r['more'] = ('<details class="more" data-print="open">'
                 '<summary>想深入：這張圖的資料、口徑，和它跟下面那張區間表的差別</summary>'
                 '<p class="note">S&amp;P 500 含息、名目：%s到 2023 年 6 月用 Robert Shiller 公開月資料，'
                 '2023 年 7 月起用 S&amp;P 500 總報酬指數串接到 %s。沒有扣物價、費用和稅，也不是台幣。'
                 '箱是第 15 到第 85 百分位（把所有視窗從小排到大，切掉最前面 15%% 和最後面 15%%），'
                 '中線是中位數，細鬚兩端是這段歷史裡最差和最好的那一次。'
                 '和下面那張 J.P. Morgan 區間表的口徑差在哪：'
                 '那張表是 J.P. Morgan 自己的資料、1950 年起、以整年為單位（1 月 1 日到 12 月 31 日）；'
                 '這張圖是 %s 年起、逐月起算。期間越長、起算方式越細，最好和最差就越極端。</p></details>'
                 % (_ym(r['from']), _ym(r['to']), r['from'][:4]))
    hi_out, lo_out = _over_range(r['rows'])
    # 縱軸固定 −70%～+70%（批 Y）：落在範圍外的端點用箭頭收尾，圖說要講明白。
    over = ''
    if hi_out:
        over = ('%s那一根的最好一次超出了圖的範圍，用箭頭表示。'
                % '、'.join('%d 年' % y for y in hi_out))
    if lo_out:
        over += ('%s那一根的最差一次超出了圖的範圍，用箭頭表示。'
                 % '、'.join('%d 年' % y for y in lo_out))
    r['caption'] = ('往右看，鬚越來越短：抱 1 年最差 %s、最好 %s，%s。'
                    '中間那條線是中位數，一半的視窗在它上面、一半在下面。%s'
                    '這是歷史，不是保證；'
                    '而且每一根的視窗互相重疊，不是獨立的樣本。'
                    % (_pct(n1['min']), _pct(n1['max']),
                       ('抱 30 年最差 %s、最好 %s' % (_pct(n30[0]['min']), _pct(n30[0]['max']))) if n30
                       else '30 年那一根的視窗太少，沒有畫', over))
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
    span = '%s–%s' % (r['data_from'][:4], r['data_to'][:4])
    r['aria'] = ('美股滾動 10、20、30 年的年化報酬：每一個月都當一次買進日，分別抱滿 10、20、30 年；'
                 '抱 10 年最差 %s、抱 20 年最差 %s、抱 30 年最差 %s'
                 % tuple(('%.1f%%' % by[y]['min'][1]).replace('-', '−') for y in (10, 20, 30)))
    r['title'] = '滾動 10、20、30 年的年化報酬：每一個起點各算一次'
    r['sub'] = 'S&P 500 含息、名目，資料 %s；橫軸是抱滿的那個月，年化 %%' % span
    r['note'] = ('三條線的橫軸都是「抱滿的那個月」；最早的視窗從 %s起算，'
                 '所以 10 年線從 %s 年開始有點、20 年線 %s 年、30 年線 %s 年。'
                 '視窗彼此重疊，不是互相獨立的樣本。'
                 % (_ym(r['data_from']), by[10]['from'][:4], by[20]['from'][:4], by[30]['from'][:4])
                 + COWLES_NOTE)
    r['more'] = ('<details class="more" data-print="open">'
                 '<summary>想深入：這張圖的資料和口徑</summary>'
                 '<p class="note">S&amp;P 500 含息、名目：%s到 2023 年 6 月用 Robert Shiller 公開月資料，'
                 '2023 年 7 月起用 S&amp;P 500 總報酬指數串接到 %s。沒有扣物價、費用和稅，也不是台幣；'
                 '扣掉物價以後，最差的那幾段會低很多（同一節「二十年扣掉物價最差」那一句）。'
                 '三條線各自的視窗數：10 年 %s 個、20 年 %s 個、30 年 %s 個。'
                 '10 年線有 %d 個視窗是負的（%.1f%%），最低的那一次結束在 %s；'
                 '20 年線最低 %.1f%%，結束在 %s；'
                 '30 年線最低的那一次結束在 %s，最高的那一次結束在 %s，'
                 '最後一個算得出來的 30 年視窗從 %s起、結束在 %s，是 %.1f%%。</p></details>'
                 % (_ym(r['data_from']), _ym(r['data_to']),
                    '{:,}'.format(by[10]['n']), '{:,}'.format(by[20]['n']), '{:,}'.format(by[30]['n']),
                    by[10]['neg'], by[10]['neg_pct'], _ym(by[10]['min'][0]),
                    by[20]['min'][1], _ym(by[20]['min'][0]),
                    _ym(by[30]['min'][0]), _ym(by[30]['max'][0]),
                    _ym(by[30]['last_start']), _ym(by[30]['last'][0]), by[30]['last'][1]))
    r['caption'] = ('三條線各是從某個月開始、抱滿 10、20、30 年的平均一年報酬。'
                    '抱 10 年，歷史上有大約 %d%% 的起點是虧的，最差一年 %s；'
                    '抱 20 年，沒有一個起點是虧的，最差一年 %.1f%%；抱 30 年，最差也有 %.1f%%。'
                    '哪一年開始你決定不了，抱多久你決定得了，'
                    '何況多數人是分批投入，起點本來就散在很多個月。三個數字都沒扣物價。'
                    '這是歷史，不是保證。'
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
