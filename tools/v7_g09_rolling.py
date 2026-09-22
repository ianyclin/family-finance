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
    圖上只標最差、最好、中位三個數字，百分位在圖說講。指南放全期（1871 起）那一組，
    近 30 年那一組做成樣張。
圖 B（sp500-rolling-30y）滾動 30 年的年化報酬
    橫軸是視窗的結束年份，縱軸從 0 起，標最低點與最高點。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v7_series as S

PERIODS = (1, 3, 5, 10, 20, 30)


def _tnum(m):
    y, mm = m.split('-')
    return int(y) + (int(mm) - 1) / 12.0


def _ym(m):
    return '%s 年 %d 月' % (m[:4], int(m[5:7]))


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


def compute_rolling30(years=30):
    months, tr = S.shiller_tr_extended()
    pts = S.rolling_annualised(months, tr, years)
    lo = min(pts, key=lambda x: x[1])
    hi = max(pts, key=lambda x: x[1])
    return {'id': 'sp500-rolling-30y', 'years': years, 'points': pts,
            'n': len(pts), 'from': pts[0][0], 'to': pts[-1][0],
            'min': lo, 'max': hi, 'last': pts[-1],
            'data_from': months[0], 'data_to': months[-1]}


# ---------------------------------------------------------------- 圖 A
def chart_box(res):
    import essay_charts as E
    rows = res['rows']
    vmax = max(r['max'] for r in rows)
    vmin = min(r['min'] for r in rows)

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
        pad = (vmax - vmin) * 0.09

        def py(v):
            return bottom - (bottom - top) * (v - (vmin - pad)) / ((vmax + pad) - (vmin - pad))

        out = [E.svg_open(lay, h, res['aria'])]
        ticks = [t for t in (-60, -40, -20, 0, 20, 40, 60, 80, 100, 120, 140)
                 if vmin - pad <= t <= vmax + pad]
        out += E.grid(lay, py, ticks, lambda v: '%+d%%' % v if v else '0')
        for k, r in enumerate(rows):
            cx = left + gw * (k + 0.5)
            col = E.TEAL
            # 鬚：最差到最好
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2"/>'
                       % (cx, py(r['max']), cx, py(r['min']), E.MUTED))
            for v in (r['max'], r['min']):
                out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2"/>'
                           % (cx - bw * 0.28, py(v), cx + bw * 0.28, py(v), E.MUTED))
            # 箱：第 15 到第 85 百分位
            y0, y1 = py(r['p85']), py(r['p15'])
            out.append(E.rect(cx - bw / 2, y0, bw, max(2.0, y1 - y0), col, rx=2, opacity=0.35))
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="none" stroke="%s" stroke-width="1.2"/>'
                       % (cx - bw / 2, y0, bw, max(2.0, y1 - y0), col))
            # 中線
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.2"/>'
                       % (cx - bw / 2, py(r['median']), cx + bw / 2, py(r['median']), col))
            # 三個數字。抱久了以後範圍很窄，整數會讓 3.6% 看成 4%，所以小數字留一位小數。
            def num(v):
                return ('%+.1f%%' if abs(v) < 25 else '%+.0f%%') % v
            out.append(E.text(cx, py(r['max']) - 5, num(r['max']), fl, 'middle', E.INK, '700'))
            out.append(E.text(cx, py(r['min']) + fl + 3, num(r['min']), fl, 'middle', E.INK, '700'))
            # 中位數標在箱的右邊；右邊放不下（最後一組）就改標在箱的左邊，不出 viewBox
            med = '%.1f%%' % r['median']
            wmed = len(med) * fl * 0.56 + 3
            if cx + bw / 2 + wmed <= lay.W - 6:
                out.append(E.text(cx + bw / 2 + 3, py(r['median']) + fl * 0.36, med, fl, 'start', E.TEAL, '800'))
            else:
                out.append(E.text(cx - bw / 2 - 3, py(r['median']) + fl * 0.36, med, fl, 'end', E.TEAL, '800'))
            out.append(E.text(cx, bottom + lay.f + 8, '%d 年' % r['years'], lay.f, 'middle', E.INK, '700'))
        out.append('</svg>')
        return '\n'.join(out)

    lg = E.legend([(E.TEAL, '箱＝第 15 到第 85 百分位，中線＝中位數，細鬚＝最差到最好')])
    return dict(title=res['title'], sub=res['sub'],
                svgs=[draw(E.L('d')), draw(E.L('m'))],
                extras=lg + E.note(res['note']) + res['more'], caption=res['caption'])


# ---------------------------------------------------------------- 圖 B
def chart_rolling30(res):
    import essay_charts as E
    pts = res['points']
    t0, t1 = _tnum(pts[0][0]), _tnum(pts[-1][0])
    vmax = max(x[1] for x in pts)

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
            return bottom - (bottom - top) * v / (vmax * 1.12)

        out = [E.svg_open(lay, h, res['aria'])]
        out += E.grid(lay, py, (0, 4, 8, 12), lambda v: '%d%%' % v)
        for y in range(1920, int(pts[-1][0][:4]) + 1, 20 if mob else 20):
            m = '%d-01' % y
            if t0 <= _tnum(m) <= t1:
                out.append(E.text(px(m), bottom + lay.f + 6, str(y), lay.f, 'middle', E.MUTED))
        out.append(E.poly([(px(m), py(v)) for m, v, _s in pts], E.TEAL, 1.8 if mob else 2.0))
        for key, label, dy, anchor in (('min', '最低', fl + 9, 'middle'), ('max', '最高', -8, 'middle')):
            m, v, st = res[key]
            x, y = px(m), py(v)
            out.append(E.dot(x, y, E.ACCENT, 3.6))
            tx = min(max(x, left + 34), right - 34)
            out.append(E.text(tx, y + dy, '%s %.1f%%（%s）' % (label, v, m[:4]), fl, anchor, E.INK, '700'))
        out.append('</svg>')
        return '\n'.join(out)

    return dict(title=res['title'], sub=res['sub'],
                svgs=[draw(E.L('d')), draw(E.L('m'))],
                extras=E.note(res['note']) + res['more'], caption=res['caption'])


# ---------------------------------------------------------------- 三個進入點
def _box_dress(r):
    span = '%s–%s' % (r['from'][:4], r['to'][:4])
    n1 = [x for x in r['rows'] if x['years'] == 1][0]
    n30 = [x for x in r['rows'] if x['years'] == 30]
    r['aria'] = '美股 %s，抱 1、3、5、10、20、30 年的年化報酬範圍（箱型）' % span
    r['title'] = '抱幾年，報酬落在哪個範圍'
    r['sub'] = 'S&P 500 含息、名目，%s，每個月都當一次買進日，年化 %%' % span
    r['note'] = ('每個月都當一次買進日，抱滿 N 年，再換算成平均一年的報酬。'
                 '1 年那一根有 %s 個視窗%s。視窗彼此重疊，不是互相獨立的樣本。'
                 % ('{:,}'.format(n1['n']),
                    '，30 年那一根有 %s 個' % '{:,}'.format(n30[0]['n']) if n30 else ''))
    r['more'] = ('<details class="more"><summary>想深入：這張圖的資料、口徑，和它跟下面那張區間表的差別</summary>'
                 '<p class="note">S&amp;P 500 含息、名目：%s到 2023 年 6 月用 Robert Shiller 公開月資料，'
                 '2023 年 7 月起用 S&amp;P 500 總報酬指數串接到 %s。沒有扣物價、費用和稅，也不是台幣。'
                 '箱是第 15 到第 85 百分位（把所有視窗從小排到大，切掉最前面 15%% 和最後面 15%%），'
                 '中線是中位數，細鬚兩端是這段歷史裡最差和最好的那一次。'
                 '這張圖和下面那張 J.P. Morgan 的區間表講的是同一件事，口徑不一樣，數字不會一致：'
                 '那張表是 J.P. Morgan 自己的資料、1950 年起、以整年為單位（1 月 1 日到 12 月 31 日）；'
                 '這張圖是 1871 年起、逐月起算。期間越長、起算方式越細，最好和最差就越極端。</p></details>'
                 % (_ym(r['from']), _ym(r['to'])))
    r['caption'] = ('往右看，鬚越來越短：抱 1 年最差 %+.0f%%、最好 %+.0f%%，抱 30 年最差 %s。'
                    '中間那條線是中位數，一半的視窗在它上面、一半在下面。這是歷史，不是保證；'
                    '而且每一根的視窗互相重疊，不是獨立的樣本。'
                    % (n1['min'], n1['max'],
                       ('%+.1f%%、最好 %+.1f%%' % (n30[0]['min'], n30[0]['max'])) if n30 else '（這一組資料不夠長）'))
    return r


def holding_box():
    return chart_box(_box_dress(compute_box()))


def holding_box_recent30():
    months, _tr = S.shiller_tr_extended()
    # 近 30 年＝最後一個月往前推 30 年
    y, m = int(months[-1][:4]) - 30, months[-1][5:7]
    return chart_box(_box_dress(compute_box('%d-%s' % (y, m))))


def rolling_30y():
    r = compute_rolling30()
    r['aria'] = '美股滾動 30 年的年化報酬：每一個月都當一次買進日，抱滿 30 年'
    r['title'] = '滾動 30 年的年化報酬：每一個起點各算一次'
    r['sub'] = 'S&P 500 含息、名目，橫軸是抱滿 30 年的那個月，%s–%s，年化 %%' % (r['from'][:4], r['to'][:4])
    r['note'] = ('%s 個視窗：從 %s到 %s之間的每一個月各算一次，抱滿 30 年。'
                 '橫軸標的是視窗結束的年份，不是開始的年份。'
                 % ('{:,}'.format(r['n']), _ym(r['data_from']), _ym(r['data_to'])))
    r['more'] = ('<details class="more"><summary>想深入：這張圖的資料和口徑</summary>'
                 '<p class="note">S&amp;P 500 含息、名目：%s到 2023 年 6 月用 Robert Shiller 公開月資料，'
                 '2023 年 7 月起用 S&amp;P 500 總報酬指數串接到 %s。沒有扣物價、費用和稅，也不是台幣；'
                 '扣掉物價以後，最差的那幾段會低很多（同一節「二十年扣掉物價最差」那一句）。'
                 '視窗彼此重疊，不是互相獨立的樣本。最低的那一次結束在 %s，最高的那一次結束在 %s，'
                 '最後一個算得出來的視窗結束在 %s，是 %.1f%%。</p></details>'
                 % (_ym(r['data_from']), _ym(r['data_to']), _ym(r['min'][0]), _ym(r['max'][0]),
                    _ym(r['last'][0]), r['last'][1]))
    r['caption'] = ('這條線上每一個點，都是從某個月開始、抱滿 30 年的平均一年報酬。'
                    '最差的那一次也有 %.1f%% 上下，最好的 %.1f%% 上下；哪一年開始你決定不了，但抱多久你決定得了。'
                    '到 %s為止，這條線沒有低於 0。這是歷史，不是保證。'
                    % (r['min'][1], r['max'][1], _ym(r['data_to'])))
    return chart_rolling30(r)


if __name__ == '__main__':
    import json
    b = compute_box()
    print(json.dumps(b['rows'], ensure_ascii=False, indent=1))
    r = compute_rolling30()
    print(r['n'], r['min'], r['max'], r['last'])
