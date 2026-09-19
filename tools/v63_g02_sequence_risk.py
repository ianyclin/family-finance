"""G02（v6.3 第二批 c）：「年齡、槓桿與退休」〈為什麼提領期怕一開始就跌〉的示意圖。

這張圖是示意，不是市場資料
    指南這一段有兩組東西：A、B 兩個人各 100 萬的比喻（沒有逐年數字），
    以及 Vanguard 的真實例子（1973 與 1974 年退休、各 50 萬美元、50/50、每年領 2.5 萬再隨通膨調；
    1973 年那位 23 年花光，1974 年那位大部分時間還留著 30 萬）。
    Vanguard 那份研究（Safeguarding retirement in a bear market，2020）只給結果，
    沒有公布逐年的資產數字（研究摘錄見 research/supp-leverage-lifecycle-retirement.md 第 140 行），
    所以這裡不畫它的曲線，改畫書上 A、B 兩人各 100 萬的示意，並在 sub 標明「示意」。

畫法（示意數字怎麼來的）
    兩條線用「同一組十個年報酬，只是順序不同」：先跌的那一條把三個下跌年放在最前面，
    後跌的那一條把同樣三個下跌年放在最後面。這樣「平均報酬一樣」不是估的，是同一組數字。
    每年年初各提領固定 5 萬（不隨物價調整），年底看餘額。
    這十個年報酬是為了畫出報酬順序而挑的，不是任何市場的實際報酬；程式用 assert 擋住：
      1. 兩條線的年報酬是同一個多重集合（排序後相等）；
      2. 算術平均相同；
      3. 完全不提領時，兩種順序十年後的資產一模一樣（順序只有在有現金流時才有影響）。

compute() 只用標準庫；chart(res) 才 lazy import essay_charts。
"""
from decimal import Decimal, ROUND_HALF_UP

START_WAN = 100          # 退休時各有 100 萬（書上 A、B 的設定）
WITHDRAW_WAN = 5         # 每年年初各領 5 萬（固定，不隨物價調整）
DOWN = [-35, -25, -15]   # 三個下跌年
UP = [20, 18, 22, 15, 25, 12, 28]
YEARS = len(DOWN) + len(UP)
PEOPLE = [('A', '先跌', DOWN + UP), ('B', '後跌', UP + DOWN)]
VANGUARD = {
    'source': 'Vanguard Research (2020), Safeguarding retirement in a bear market',
    'url': 'https://www.vanguard.co.uk/content/dam/intl/europe/documents/en/whitepapers/'
           'safeguarding-retirement-bear-market.pdf',
    'case': '兩個人各 50 萬美元、50/50、每年領 2.5 萬再隨通膨調；1973 年退休的人 23 年花光，'
            '1974 年退休的人大部分時間還留著 30 萬',
    'why_not_drawn': '原文只給結果，沒有公布逐年資產數字，所以本圖不畫它的曲線',
}


def r1(x):
    return float(Decimal(repr(x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))


def r0(x):
    return int(Decimal(repr(x)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def run(returns):
    """每年年初提領，之後套用當年報酬；回傳第 0 到第 10 年年底的餘額（單位萬）。"""
    v = float(START_WAN)
    out = [{'year': 0, 'wan': v}]
    for i, r in enumerate(returns, 1):
        v = (v - WITHDRAW_WAN) * (1 + r / 100)
        out.append({'year': i, 'wan': v})
    return out


def compute():
    people = []
    for key, label, rs in PEOPLE:
        p = run(rs)
        people.append({'key': key, 'label': label, 'returns_pct': rs,
                       'series': [{'year': r['year'], 'wan': r1(r['wan'])} for r in p],
                       'end_wan_rounded': r0(p[-1]['wan']), 'end_wan': r1(p[-1]['wan'])})
    a, b = people
    # 1. 同一組年報酬，只是順序不同
    assert sorted(a['returns_pct']) == sorted(b['returns_pct'])
    # 2. 算術平均相同
    mean = sum(a['returns_pct']) / YEARS
    assert abs(mean - sum(b['returns_pct']) / YEARS) < 1e-12
    # 3. 不提領的話，兩種順序十年後一模一樣
    def compound(rs):
        v = float(START_WAN)
        for r in rs:
            v *= 1 + r / 100
        return v
    no_wd = compound(a['returns_pct'])
    assert abs(no_wd - compound(b['returns_pct'])) < 1e-9
    # 這張圖要成立的前提：先跌那一條最後比較少
    assert a['end_wan'] < b['end_wan']
    return {
        'id': 'sequence-risk',
        'illustrative': True,
        'basis': {
            'what': '示意：兩個人退休時各有 %d 萬，每年年初各領 %d 萬（固定，不隨物價調整），'
                    '十年的年報酬是同一組數字，只是順序不同' % (START_WAN, WITHDRAW_WAN),
            'years': YEARS,
            'start_wan': START_WAN,
            'withdraw_wan_per_year': WITHDRAW_WAN,
            'withdraw_timing': '每年年初提領，之後套用當年報酬',
            'first_year_withdraw_rate_pct': WITHDRAW_WAN / START_WAN * 100,
            'not_real_data': '這十個年報酬不是任何市場的實際報酬，只是為了畫出「順序不同」而挑的',
            'excludes': '沒有扣物價、費用、稅；提領金額固定不調整',
        },
        'returns_pool_pct': sorted(DOWN + UP),
        'mean_return_pct': r1(mean),
        'no_withdrawal_end_wan': r1(no_wd),
        'no_withdrawal_end_wan_rounded': r0(no_wd),
        'people': people,
        'guide_real_case': VANGUARD,
        'printed': {},
    }


def chart(res):
    import essay_charts as E
    a, b = res['people']
    years = res['basis']['years']
    vmax = 300
    ca, cb = E.ACCENT, E.TEAL

    def draw(lay):
        mob = lay.mobile
        h = 250 if mob else 300
        left = lay.left - (8 if mob else 6)
        right = lay.right - (40 if mob else 48)
        top, bottom = lay.top + (14 if mob else 16), h - 26

        def px(y):
            return left + (right - left) * y / years

        def py(v):
            return bottom - (bottom - top) * v / vmax

        out = [E.svg_open(lay, h, '示意：兩個人退休時各有 %d 萬，每年各領 %d 萬，'
                                  '同一組年報酬換順序，一個先跌、一個後跌，十年後的餘額'
                          % (res['basis']['start_wan'], res['basis']['withdraw_wan_per_year']))]
        out += E.grid(lay, py, [0, 100, 200, 300], lambda v: ('%d 萬' % v) if v else '0')
        for t in ([0, 5, 10] if mob else [0, 2, 4, 6, 8, 10]):
            out.append(E.text(px(t), bottom + 17, '%d' % t, lay.fs, 'middle', E.MUTED))
        out.append(E.text(right + (14 if mob else 18), bottom + 17, '年', lay.fs, 'start', E.MUTED))
        for p, col in ((b, cb), (a, ca)):
            out.append(E.poly([(px(r['year']), py(r['wan'])) for r in p['series']], col, lay.line))
        # 起點：兩條線從同一點出發（金額看左邊的刻度，不另外標字，免得壓到線）
        out.append(E.dot(px(0), py(res['basis']['start_wan']), E.INK, 3.5))
        # 終點
        for p, col in ((b, cb), (a, ca)):
            v = p['series'][-1]['wan']
            out.append(E.dot(px(years), py(v), col))
            out.append(E.text(px(years) + 7, py(v) + 4, '%d 萬' % p['end_wan_rounded'],
                              lay.fl, 'start', col, '800'))
        # 兩段下跌的註記：A 放在自己那條線下面的空白處，B 放在高點右邊的下坡外側
        out.append(E.text(px(1.1), py(a['series'][3]['wan'] / 2) + lay.fs * 0.36,
                          'A：一退休就跌' if mob else 'A：一退休就遇到大跌',
                          lay.fs, 'start', ca, '700'))
        out.append(E.text(px(7.6), py(vmax * 0.77), 'B：後面幾年才跌', lay.fs, 'start', cb, '700'))
        out.append('</svg>')
        return '\n'.join(out)

    lg = E.legend([(ca, 'A：前三年先跌'), (cb, 'B：同樣三年的下跌放在最後')])
    # v7 批 7：圖下 p.note 原本 277 字，害 lifecycle「看得到的小字」超過 350。
    # 沒有被 calc_core quotes 盯著的兩句（年報酬怎麼挑的、正文那組 Vanguard 數字為什麼沒拿來畫）
    # 移到圖後面的 <details class="more">（指南裡那一份，和這裡同一份文字）。
    nt = E.note('示意圖，不是市場資料。兩條線用的是同一組十個年報酬，只是順序不同：'
                'A 把三個下跌的年份排在最前面，B 排在最後面，所以兩個人的平均報酬一樣（一年 %s%%）。'
                '兩個人退休時都有 %d 萬，每年年初各領 %d 萬（固定金額，這張圖沒有隨物價調整），'
                '沒有扣物價、費用和稅。'
                '如果完全不提領，同一組報酬不管什麼順序，十年後都是 %d 萬——順序會有差，是因為中途要拿錢出來。'
                % (res['mean_return_pct'], res['basis']['start_wan'],
                   res['basis']['withdraw_wan_per_year'], res['no_withdrawal_end_wan_rounded']))
    # 搬去的地方：guide/index.html #lifecycle，sequence-risk 圖後面那個
    # 「想深入：1973 和 1974 年退休的兩個真實例子」摺疊的最後一段 p.small——
    #   「上面那張圖用的那十個年報酬是為了畫出「順序不同」挑的，不是任何市場的實際報酬。
    #     正文那組真實的數字（1973 和 1974 年退休的兩個人）出自 Vanguard 的研究，
    #     原文只公布結果、沒有公布逐年資產，所以這張圖沒有用它的數字。」
    # 改那一段時，這裡的註解要跟著改。
    caption = ('兩個人退休時都是 %d 萬，每年年初都領 %d 萬，十年的年報酬是同一組數字、只是順序不同。'
               '先跌的那一個第 %d 年剩約 %d 萬，後跌的那一個剩約 %d 萬。'
               '差別發生在前三年：A 在下跌的時候還要賣股票拿生活費。'
               % (res['basis']['start_wan'], res['basis']['withdraw_wan_per_year'], years,
                  a['end_wan_rounded'], b['end_wan_rounded']))
    lead = ('把 A 和 B 畫出來會長這樣。兩條線的十個年報酬完全一樣，只是順序不同；'
            '兩個人每年拿出來花的錢也一樣。')
    res['printed'] = {'a_end_wan': a['end_wan_rounded'], 'b_end_wan': b['end_wan_rounded'],
                      'mean_return_pct': res['mean_return_pct'],
                      'no_withdrawal_end_wan': res['no_withdrawal_end_wan_rounded'],
                      'lead_sentence': lead}
    return dict(title='一樣的平均、一樣的提領：先跌還是後跌',
                sub='示意：同一組十個年報酬換順序，每年年初各領 %d 萬（不是真實市場資料）'
                    % res['basis']['withdraw_wan_per_year'],
                svgs=[draw(E.L('d')), draw(E.L('m'))], extras=lg + nt, caption=caption)


if __name__ == '__main__':
    import json
    print(json.dumps(compute(), ensure_ascii=False, indent=1))
