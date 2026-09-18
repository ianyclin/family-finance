"""G03（v6.3 第二批 c）：第 9 節「每年少賺的 3.8 個百分點去哪了」。

資料來源
    指南第 9 節既有文字，出自 Barber, Lee, Liu & Odean (2009), Review of Financial Studies
    「台灣 1995–1999：個人投資人整體因為買賣，每年比買了不動少賺 3.8 個百分點」。
    四個比例也是原文既有：證交稅約 34%、手續費約 32%、買賣價差約 27%、進出時機約 7%。
    這支程式不算任何新數字，只把原文那三行條列畫成一條 100% 的堆疊長條。

口徑
    四個比例是「那 3.8 個百分點」的組成，不是報酬率本身；原文每個數字都寫「約」。
    四個加起來剛好 100（原文如此），程式用 assert 擋住被改壞。
    GDP 2.2% 那句不畫（審查 G03：國三讀者沒感覺）。

compute() 只用標準庫；chart(res) 才 lazy import essay_charts。
"""

# 原文第 9 節條列的四項（順序照原文）
PARTS = [
    ('證交稅', 34, 'teal'),
    ('手續費', 32, 'blue'),
    ('買賣價差', 27, 'amber'),
    ('進出時機', 7, 'muted'),
]
TOTAL_PP = 3.8          # 每年少賺的百分點（原文）
PERIOD = '1995 到 1999 年'
QUOTE = '證交稅約 34%、手續費約 32%：加起來大約三分之二，是每買賣一次就要付的錢。'


def compute():
    parts = [{'name': n, 'share_pct': p} for n, p, _ in PARTS]
    total = sum(p['share_pct'] for p in parts)
    assert total == 100, total
    trade_cost = PARTS[0][1] + PARTS[1][1]          # 稅＋手續費
    assert trade_cost == 66
    return {
        'id': 'drag-breakdown',
        'basis': {
            'what': '台灣個人投資人整體因為買賣，每年比「買了不動」少賺 %s 個百分點；這張圖拆的是那 %s 個百分點的組成，不是報酬率'
                    % (TOTAL_PP, TOTAL_PP),
            'period': PERIOD,
            'sample': '台灣證交所的完整交易紀錄（全體個人投資人）',
            'rounding': '四個比例原文都寫「約」，加起來剛好 100',
            'not_drawn': 'GDP 2.2% 那句不畫',
        },
        'source': {
            'name': 'Barber, Lee, Liu & Odean (2009), Review of Financial Studies',
            'via': '指南第 9 節既有文字（數字沒有重算）',
            'url': 'https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/'
                   'justhowmuchdoindividualinvestorslose_rfs_2009.pdf',
            'quote_in_guide': QUOTE,
        },
        'total_pp': TOTAL_PP,
        'parts': parts,
        'total_share_pct': total,
        'trade_cost_share_pct': trade_cost,
        'printed': {},
    }


def chart(res):
    import essay_charts as E
    COLOR = {'teal': E.TEAL, 'blue': E.BLUE, 'amber': E.AMBER, 'muted': E.MUTED}
    parts = res['parts']
    cols = [COLOR[c] for _, _, c in PARTS]
    trade = res['trade_cost_share_pct']

    def tw(s, fs):
        """粗估字寬：全形字算 1 em，其餘算 0.55 em。"""
        return sum(fs if ord(ch) > 0x2000 else fs * 0.55 for ch in s)

    def draw(lay):
        mob = lay.mobile
        x0 = 6 if mob else 10
        x1 = lay.W - (6 if mob else 10)
        bw = x1 - x0
        by = (44 if mob else 50)                 # 長條上緣
        bh = 30 if mob else 36
        fs = lay.fs if mob else lay.f
        h = by + bh + (54 if mob else 58)
        out = [E.svg_open(lay, h, '台灣個人投資人每年少賺的 %s 個百分點，拆成證交稅、手續費、買賣價差、進出時機四塊，加起來是 100%%' % res['total_pp'])]
        # 上方括號：稅＋手續費
        tx = x0 + bw * trade / 100
        bry = by - (16 if mob else 18)
        out.append('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f" fill="none" stroke="%s" stroke-width="1.2"/>'
                   % (x0 + 1, bry + 6, x0 + 1, bry, tx - 1, bry, tx - 1, bry + 6, E.MUTED))
        lab = '每買賣一次就要付的錢 %d%%' % trade if mob else '每買賣一次就要付的錢：%d%%' % trade
        out.append(E.text((x0 + tx) / 2, bry - 5, lab, fs, 'middle', E.INK, '700'))
        # 100% 堆疊長條
        acc = 0.0
        centers = []
        for (name, share), col in zip([(p['name'], p['share_pct']) for p in parts], cols):
            w = bw * share / 100
            x = x0 + bw * acc / 100
            out.append(E.rect(x, by, w, bh, col, 2))
            centers.append((x + w / 2, x + w, name, share, col))
            acc += share
        # 下方標籤：兩排交錯，第 1、3 塊在上排，第 2、4 塊在下排
        r1y = by + bh + (17 if mob else 19)
        r2y = r1y + (17 if mob else 19)
        for i, (cx, xr, name, share, col) in enumerate(centers):
            ly = r1y if i % 2 == 0 else r2y
            s = '%s %d%%' % (name, share)
            anchor, lx = 'middle', cx
            half = tw(s, fs) / 2
            if lx + half > x1:                    # 最後一塊太窄，靠右對齊
                anchor, lx = 'end', x1
            elif lx - half < x0:
                anchor, lx = 'start', x0
            out.append(E.text(lx, ly, s, fs, anchor, E.INK, '700'))
            # 從長條下緣拉一條短引線到那一排
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
                       % (cx, by + bh + 1, cx, ly - fs - 1, col))
        out.append('</svg>')
        return '\n'.join(out)

    lg = E.legend([(COLOR[c], '%s 約 %d%%' % (n, p)) for n, p, c in PARTS])
    nt = E.note('台灣 %s，個人投資人整體因為買賣，每年比「買了不動」少賺 %s 個百分點；'
                '這條長條拆的是那 %s 個百分點是怎麼組成的，不是報酬率本身。'
                '四個比例都是原文寫的約略值，加起來剛好 100%%。'
                '資料是台灣證交所當年的完整交易紀錄，算的是全體個人投資人合起來，不是每個人都一樣。'
                '研究年代久遠，交易稅率和工具都變了。'
                '出自 Barber、Lee、Liu、Odean 2009 年的研究（連結在第 9 節「直接來源」）。'
                % (PERIOD, res['total_pp'], res['total_pp']))
    caption = ('每年少賺的 %s 個百分點，%d%% 是證交稅、%d%% 是手續費、%d%% 是買賣價差，'
               '剩下 %d%% 才是進出時機。前兩塊加起來 %d%%，是每買賣一次就要付出去的錢。'
               '所以呢：少買賣。F 區三格都寫照常投入，這三塊錢就省下來了。'
               % (res['total_pp'], parts[0]['share_pct'], parts[1]['share_pct'],
                  parts[2]['share_pct'], parts[3]['share_pct'], trade))
    lead = ('把上面那幾塊畫成一條長條：整條就是那 %s 個百分點，四塊加起來剛好是全部。'
            % res['total_pp'])
    res['printed'] = {'parts': [(p['name'], p['share_pct']) for p in parts],
                      'trade_cost_share_pct': trade, 'total_pp': res['total_pp'],
                      'lead_sentence': lead}
    return dict(title='多數損失是每次買賣都要付的錢',
                sub='台灣 %s，個人投資人每年少賺的 %s 個百分點拆成四塊' % (PERIOD, res['total_pp']),
                svgs=[draw(E.L('d')), draw(E.L('m'))], extras=lg + nt, caption=caption)


if __name__ == '__main__':
    import json
    print(json.dumps(compute(), ensure_ascii=False, indent=1))
