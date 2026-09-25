#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G11（v7 批 BJ）：綠角時間軸——每一筆錢都有自己的三十年。只在指南（第 24 節第三題）。

為什麼有這張
    讀者容易把退休想成「某一天把錢全部拿出來」，於是覺得接近退休的那幾筆錢「只剩幾年可以長」。
    實際上退休後是分三十年慢慢花：35 歲存的那筆對到 65 歲那年的花費，64 歲存的最後一筆
    要到 94 歲才用得到。
    這個整齊的對應有一個前提：累積期和提領期一樣長（35 歲開始存、65 歲退休、領 30 年）。
    起步年齡不同，年數就不同，不變的只有順序：最早投的最早花，最晚投的最晚花。
    批 BR 起，這個假設寫在 chart-sub 上，不再讓讀者自己猜；批 BU 起圖說不再重複寫一次
    （同一張圖上寫兩遍），所以現在整張圖的口徑只有 chart-sub 這一處。
    概念出自綠角 2009-11〈Unfounded Fear for Long-Term Investing〉，這張圖是本文重畫。

畫法
    兩條水平時間軸。上排是「存進去的年齡」，下排是「拿出來花的年齡」，都取樣成
    35–39、…、60–64（下排 +30 就是 65–69、…、90–94），中段用省略號。
    下排整條往右平移一個固定距離，所以「第 i 個年齡」對到「第 i 個年齡 +30」的那條虛線
    是一支斜線；十條虛線互相平行。中間省略號那一格沒有虛線，粗箭頭就畫在那個空走廊裡。

為什麼下排停在 94，不是 104
    作者的示意圖下排畫到 104，那是把「提領期本身有多長」也畫進去。這張圖只講
    「每一筆對到三十年後」，畫到 104 會讓讀者以為 100 歲那年還對應到某一筆存款。

圖上沒有金額、沒有倍數，只有年齡與「30 年」。真正的提領規則、退休後的股債比、
報酬順序風險都在同一節的正文與卡片裡，p.note 指過去。

compute() 只用標準庫；chart(res) 才 lazy import essay_charts。
"""

# 上排取樣的年齡；None 是中段的省略號那一格。
TOP_AGES = [35, 36, 37, 38, 39, None, 60, 61, 62, 63, 64]
SHIFT = 30           # 存進去到拿出來花，差三十年
FIRST, LAST = 35, 64  # 存進去的第一年與最後一年

TITLE = '每一筆錢都有自己的三十年'
SUB = '示意：假設 35 歲開始存、65 歲退休、領 30 年'
NOTE = ('錢是可以互換的，這是想法上的對應，不是分開的帳戶。退休後整桶錢的股債比，照本節第一題還是要往下降。'
        '提領那幾年開頭就跌的風險也不會因此消失（下面「為什麼提領期怕一開始就跌」）。')
ARIA = ('兩排年齡時間軸。上排是存進去的年齡，從 35、36、37、38、39 歲一路到 60、61、62、63、64 歲；'
        '下排是拿出來花的年齡，從 65、66、67、68、69 歲一路到 90、91、92、93、94 歲。'
        '每一個存進去的年齡各有一條虛線，斜斜對到三十年後的那一年。')
# 箭頭旁的字手機只畫「30 年」一行，所以兩版的 aria 尾句不一樣（批 BR nit-2）。
# 批 BT：第 2 行原本是「錢長 30 年」，和圖說「快要輪到的那幾筆，退休前幾年就搬到波動小的地方」
# 打折——最早那幾筆照書自己的規則大約在退休前五年就離開股票，在市場裡 25 到 27 年，不是 30 年。
# 改成「從投入到花掉」：那支箭頭量的是投入年到花掉年的距離，這句話在任何起步年齡下都成立。
ARIA_ARROW = {False: '中間一支箭頭標「30 年」：從投入到花掉，物價也漲 30 年。',
              True: '中間一支箭頭標「30 年」。'}

BOX_CLEAR = 6.5      # 標籤盒離箭身（那條粗線）的最小淨距，兩版都要守住。
                     # 規格要的是 6px；座標輸出到小數一位，多留 0.5 給進位。

TOP_AXIS = '存進去的年齡'
BOT_AXIS = '拿出來花的年齡'
ARROW_LABEL = '30 年'
ARROW_LINES = ['從投入到花掉', '物價也漲 30 年']


def compute():
    ages = [a for a in TOP_AGES if a is not None]
    assert ages[0] == FIRST and ages[-1] == LAST
    assert all(FIRST <= a <= LAST for a in ages)
    assert LAST + SHIFT == 94
    return {
        'id': 'money-age',
        # 這張圖是假設出來的排程，不是市場資料（chart-sub 的「示意」兩個字就是它）。
        # 注意別和 chart() 回的 illustration_only 搞混：那個是 essay_charts 的開關，
        # True 會把圖說整個略掉，這張圖有圖說，所以那邊必須是 False。
        'illustrative': True,
        'basis': {
            'what': '上排每一個存進去的年齡，對到下排 +%d 年那一個花掉的年齡' % SHIFT,
            'no_amounts': True,          # 圖上沒有金額、沒有倍數
            'bottom_stops_at': LAST + SHIFT,
            'why_not_104': '這張圖只講「每一筆對到三十年後」，不畫提領期本身有多長',
            'fungible': '錢可以互換，這是想法上的對應，不是分開的帳戶',
        },
        'top_ages': list(TOP_AGES),
        'shift_years': SHIFT,
        'source': {'section_id': 'lifecycle',
                   'via': '綠角 2009-11〈Unfounded Fear for Long-Term Investing〉，概念參考，圖是本文重畫'},
        'printed': {'title': TITLE, 'sub': SUB, 'note': NOTE},
    }


def _geom(lay):
    """一張圖的所有座標都從這裡出來，量測腳本也用同一組。"""
    if lay.mobile:
        pad, dx, band, yt = 8.0, 58.0, 94.0, 38.0
    else:
        pad, dx, band, yt = 14.0, 110.0, 118.0, 42.0
    x0 = pad
    span = (lay.W - pad) - pad - dx
    pitch = span / (len(TOP_AGES) - 1)
    yb = yt + band
    y_top_lab = yt - 7
    y_bot_lab = yb + lay.f + 5
    y_top_axis_name = 16.0 if not lay.mobile else 14.0
    y_bot_axis_name = y_bot_lab + lay.fs + 10
    h = y_bot_axis_name + 7
    return dict(x0=x0, dx=dx, span=span, pitch=pitch, yt=yt, yb=yb, band=band,
                y_top_lab=y_top_lab, y_bot_lab=y_bot_lab,
                y_top_axis_name=y_top_axis_name, y_bot_axis_name=y_bot_axis_name, h=h)


def chart(res):
    import essay_charts as E

    def draw(lay):
        g = _geom(lay)
        x0, dx, pitch, yt, yb, band = g['x0'], g['dx'], g['pitch'], g['yt'], g['yb'], g['band']
        f, fs = lay.f, lay.fs
        out = [E.svg_open(lay, g['h'], ARIA + ARIA_ARROW[lay.mobile])]

        # 兩條軸：上排靠左、下排整條往右平移 dx，所以每一條對應線都是同一個斜度。
        out.append(E.hline(x0, x0 + g['span'], yt, E.LINE, 1.4, None))
        out.append(E.hline(x0 + dx, x0 + dx + g['span'], yb, E.LINE, 1.4, None))
        out.append(E.text(x0, g['y_top_axis_name'], TOP_AXIS, fs, 'start', E.MUTED))
        out.append(E.text(x0 + dx, g['y_bot_axis_name'], BOT_AXIS, fs, 'start', E.MUTED))

        # 每一個存進去的年齡，一條虛線斜對到三十年後；省略號那一格不畫線，留給中間的箭頭。
        for i, age in enumerate(TOP_AGES):
            xt = x0 + i * pitch
            xbm = xt + dx
            if age is None:
                out.append(E.text(xt, g['y_top_lab'], '…', f, 'middle', E.MUTED))
                out.append(E.text(xbm, g['y_bot_lab'], '…', f, 'middle', E.MUTED))
                continue
            out.append(E.poly([(xt, yt), (xbm, yb)], E.MUTED, 1.1, '3 4', 0.75))
            out.append(E.text(xt, g['y_top_lab'], str(age), f, 'middle', E.INK, '700'))
            out.append(E.text(xbm, g['y_bot_lab'], str(age + SHIFT), f, 'middle', E.INK, '700'))

        # 中間那一支粗箭頭：畫在省略號那一格的空走廊裡，斜度和虛線相同。
        gap = 10.0
        t0, t1 = gap / band, 1 - gap / band
        cx = x0 + 5 * pitch
        ax0, ay0 = cx + t0 * dx, yt + t0 * band
        ax1, ay1 = cx + t1 * dx, yt + t1 * band
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="3.2" '
                   'stroke-linecap="round"/>' % (ax0, ay0, ax1, ay1, E.TEAL))
        ln = (dx * dx + band * band) ** 0.5
        ux, uy = dx / ln, band / ln
        hl, hw = 10.0, 5.0
        bx, by = ax1 - ux * hl, ay1 - uy * hl
        out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                   % (ax1, ay1, bx - uy * hw, by + ux * hw, bx + uy * hw, by - ux * hw, E.TEAL))

        # 箭頭旁的字。手機放不下兩行小字（左右兩條虛線只隔一個 pitch），只留「30 年」。
        lines = [(ARROW_LABEL, f, E.TEAL, '800')]
        if not lay.mobile:
            lines += [(s, fs, E.MUTED, None) for s in ARROW_LINES]
        lh = f + 3
        pad = 5.0
        bw = max(E.textw(t, sz) for t, sz, _c, _w in lines) + pad * 2
        bh = lh * len(lines) + pad * 2
        ly = yt + band / 2 - bh / 2
        # 盒子整個放在箭身右側。離箭身最近的是盒子左下角，用它到箭身的垂直距離
        # 把盒子往右推到 BOX_CLEAR 以外（批 BJ 那版 lx 固定在箭身中點右邊 10px，
        # 桌機版會蓋掉約 24px 的箭身，手機版剛好沒蓋到）。
        lx = ax0 + (BOX_CLEAR + (ly + bh - ay0) * ux) / uy
        # var(--surface) 是底色板：字要壓在虛線上面才讀得到（同 tools/v7_g09_rolling.py 的標籤盒）。
        out.append(E.rect(lx, ly, bw, bh, E.SURFACE, 3, 0.9))
        for k, (t, sz, col, wt) in enumerate(lines):
            out.append(E.text(lx + pad, ly + pad + lh * k + sz * 0.85, t, sz, 'start', col, wt))

        out.append('</svg>')
        return '\n'.join(out)

    return dict(title=TITLE, sub=SUB,
                svgs=[draw(E.L('d')), draw(E.L('m'))],
                extras=E.note(NOTE), caption='', illustration_only=False)


if __name__ == '__main__':
    import json
    print(json.dumps(compute(), ensure_ascii=False, indent=1))
