"""G04（v6.3 第二批 c）：第 3 節「每年差 1 個百分點，三十年差 86 萬」。

資料來源
    lite/calc-results.json 的 fee_gap（由 tools/calc_core.py 產生，是書裡這組數字的唯一算處）：
    每月 5,000 元、360 個月，一年 6% 約 502 萬、一年 5% 約 416 萬、差 86 萬、少 17.1%。
    本金 180 萬＝5,000 × 360，也是第 3 節原文寫的。

口徑
    和 calc_core 的 fv() 同一套：每月月底投入，年率 ÷ 12 按月複利，不扣物價、稅、手續費。
    6% 是第 1 節的中情境（全部放股票，還沒扣費用和稅）；5% 是費用等吃掉 1 個百分點後的數字。
    這是固定報酬的算術，不是市場預測；真實市場不會每年一樣。
    曲線上每一年的點是那一年月底的餘額；只有第 30 年的三個數字印在圖上，
    中間年份不印數字（書上沒有那些數字）。

演算法
    1. 用和 calc_core 相同的 fv 迴圈逐月推進，記下每 12 個月（第 1…30 年）的餘額。
    2. 終值用 calc_core 的 wan()（half-up 取整，單位萬）對過 calc-results.json，對不上就 assert 擋下。

compute() 只用標準庫；chart(res) 才 lazy import essay_charts。
"""
import os
import json
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CALC = os.path.join(ROOT, 'lite', 'calc-results.json')

RATES = (6, 5)          # 高的那條在前
YEARS = 30


def wan(x):             # 和 calc_core.wan 同一種取法（half-up 取整）
    return int(Decimal(str(x / 10000)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def path(rate_pct, monthly, months):
    """每月月底投入、年率 ÷ 12 按月複利；回傳逐月餘額（1..months）。"""
    r = rate_pct / 100 / 12
    v = 0.0
    out = []
    for _ in range(months):
        v = v * (1 + r) + monthly
        out.append(v)
    return out


def compute():
    fg = json.load(open(CALC, encoding='utf-8'))['fee_gap']
    monthly, months = fg['monthly'], fg['months']
    assert months == YEARS * 12
    series = {}
    for rate in RATES:
        p = path(rate, monthly, months)
        series[str(rate)] = [{'year': y, 'value': p[y * 12 - 1], 'wan': wan(p[y * 12 - 1])}
                             for y in range(1, YEARS + 1)]
    hi, lo = [series[str(r)][-1]['value'] for r in RATES]
    # 對 calc-results.json：三個印出來的數字必須一模一樣
    assert wan(hi) == fg['fv_6pct_wan'] == 502, (wan(hi), fg['fv_6pct_wan'])
    assert wan(lo) == fg['fv_5pct_wan'] == 416, (wan(lo), fg['fv_5pct_wan'])
    assert wan(hi - lo) == fg['gap_wan'] == 86, (wan(hi - lo), fg['gap_wan'])
    principal = monthly * months
    assert wan(principal) == 180
    return {
        'id': 'fee-gap',
        'basis': {
            'monthly': monthly, 'months': months, 'years': YEARS,
            'compounding': '每月月底投入，年率 ÷ 12 按月複利（和 tools/calc_core.py 的 fv() 同一套）',
            'rates_pct': list(RATES),
            'rate_6_means': '第 1 節的中情境（全部放股票），還沒扣費用和稅',
            'rate_5_means': '被費用等因素吃掉 1 個百分點以後',
            'excludes': '沒有扣物價、稅、手續費；固定報酬的算術，不是市場預測',
        },
        'source': {'file': 'lite/calc-results.json', 'key': 'fee_gap',
                   'produced_by': 'tools/calc_core.py', 'raw': fg},
        'principal_wan': wan(principal),
        'series': series,
        'end': {'6': wan(hi), '5': wan(lo), 'gap_wan': wan(hi - lo),
                'gap_share_pct': fg['gap_share_pct']},
        'printed': {},
    }


def chart(res):
    import essay_charts as E
    s6 = res['series']['6']
    s5 = res['series']['5']
    end6, end5, gap = res['end']['6'], res['end']['5'], res['end']['gap_wan']
    prin = res['principal_wan']
    monthly, years = res['basis']['monthly'], res['basis']['years']
    vmax = 550

    def draw(lay):
        mob = lay.mobile
        h = 246 if mob else 300
        left = lay.left - (8 if mob else 6)
        right = lay.right - (44 if mob else 54)     # 右邊留給終點標籤
        top, bottom = lay.top + (16 if mob else 18), h - 26

        def px(y):
            return left + (right - left) * y / years

        def py(v):
            return bottom - (bottom - top) * v / vmax

        out = [E.svg_open(lay, h, '每月 5,000 元投 30 年，一年 6%% 和一年 5%% 兩條累積曲線，第 30 年差 %d 萬' % gap)]
        out += E.grid(lay, py, [0, 100, 200, 300, 400, 500],
                      lambda v: ('%d 萬' % v) if v else '0')
        for t in ([0, 10, 20, 30] if mob else [0, 5, 10, 15, 20, 25, 30]):
            out.append(E.text(px(t), bottom + 17, '%d' % t, lay.fs, 'middle', E.MUTED))
        out.append(E.text(right + (16 if mob else 20), bottom + 17, '年', lay.fs, 'start', E.MUTED))
        # 兩條曲線之間填色：差距
        pts6 = [(px(0), py(0))] + [(px(r['year']), py(r['value'] / 10000)) for r in s6]
        pts5 = [(px(0), py(0))] + [(px(r['year']), py(r['value'] / 10000)) for r in s5]
        out.append('<polygon points="%s" fill="%s" fill-opacity="0.18"/>'
                   % (' '.join('%.1f,%.1f' % p for p in pts6 + pts5[::-1]), E.AMBER))
        # 本金（直線）
        out.append(E.poly([(px(0), py(0)), (px(years), py(prin))], E.MUTED, lay.line - 0.8, '5 5'))
        out.append(E.poly(pts6, E.TEAL, lay.line))
        out.append(E.poly(pts5, E.ACCENT, lay.line))
        # 終點標籤
        for v, col, lab in ((end6, E.TEAL, '%d 萬' % end6), (end5, E.ACCENT, '%d 萬' % end5)):
            out.append(E.dot(px(years), py(v), col))
            out.append(E.text(px(years) + 7, py(v) + 4, lab, lay.fl, 'start', col, '800'))
        out.append(E.text(px(years) - 4, py(prin) - 8, '本金 %d 萬' % prin,
                          lay.fs, 'end', E.MUTED, '700'))
        # 差距：第 30 年的雙箭頭
        gx = px(years) - (7 if mob else 9)
        y6, y5 = py(end6), py(end5)
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4"/>'
                   % (gx, y6 + 3, gx, y5 - 3, E.INK))
        for yy, dy in ((y6 + 3, 4), (y5 - 3, -4)):
            out.append('<path d="M%.1f,%.1f l-3,%d l6,0 Z" fill="%s"/>' % (gx, yy, dy, E.INK))
        glab = '差 %d 萬' % gap
        gw = len(glab) * lay.fl * 0.8
        gmy = (y6 + y5) / 2
        out.append(E.rect(gx - 8 - gw, gmy - lay.fl + 1, gw + 6, lay.fl + 7, E.SURFACE, 3))
        out.append(E.text(gx - 6, gmy + 4, glab, lay.fl, 'end', E.INK, '800'))
        out.append('</svg>')
        return '\n'.join(out)

    lg = E.legend([(E.TEAL, '一年 6%'), (E.ACCENT, '一年 5%（被費用等吃掉 1 個百分點）'),
                   (E.MUTED, '自己放進去的本金')])
    nt = E.note('每月 %s 元、投 %d 年，每月月底投入、按月複利。'
                '6%% 是第 1 節的中情境（全部放股票），還沒扣費用和稅；5%% 是被費用等因素吃掉 1 個百分點以後的數字。'
                '兩條線都沒有扣物價和稅。'
                '這是固定報酬的算術，用來看費用差距，不是市場預測：真實的市場不會每年長一樣多。'
                '數字出自本書的試算檔（tools/calc_core.py），和第 3 節那張卡是同一組。'
                % ('{:,}'.format(monthly), years))
    caption = ('每月 %s 元投 %d 年，自己放進去的本金 %d 萬。一年 6%% 到約 %d 萬，一年 5%% 到約 %d 萬，'
               '第 %d 年差 %d 萬。兩條線前幾年幾乎疊在一起，中間那片淺色就是每年差 1 個百分點累出來的距離。'
               % ('{:,}'.format(monthly), years, prin, end6, end5, years, gap))
    lead = ('每年差 1 個百分點，看起來很小。下面這張圖把每月 %s 元、投 %d 年的兩條路畫在一起：'
            '一條一年 6%%，一條被費用吃掉 1 個百分點、只剩 5%%。'
            % ('{:,}'.format(monthly), years))
    res['printed'] = {'end_6': end6, 'end_5': end5, 'gap_wan': gap, 'principal_wan': prin,
                      'lead_sentence': lead}
    return dict(title='每年差 1 個百分點，三十年差 %d 萬' % gap,
                sub='每月 %s 元、投 %d 年；固定報酬的算術，不是市場預測' % ('{:,}'.format(monthly), years),
                svgs=[draw(E.L('d')), draw(E.L('m'))], extras=lg + nt, caption=caption)


if __name__ == '__main__':
    r = compute()
    print(json.dumps({k: v for k, v in r.items() if k != 'series'}, ensure_ascii=False, indent=1))
