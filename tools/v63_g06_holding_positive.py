"""G06（v6.3 第三批 P1）：第 8 節「這段歷史裡，不同持有期間有多少比例是賺的」長條圖。

為什麼有這張圖
    S75：第 8 節原本用兩張表（台股、美股）講「抱越久、打開來是賺的比例越高」，
    和同節另外兩組（美國區間、台股區間）講的是同一件事，讀者到這裡已經累了。
    主線改成一張長條圖，兩張表收進同一個展開（表還在，第 9 節「現在是歷史新高」
    那一段引用的就是那張表）。

數字從哪裡來
    lite/calc-results.json 的 rolling（由 tools/calc_core.py 產生），
    台股 rolling.taiex.positive_share、美股 rolling.us.positive_share 的 pct_int，
    和指南展開裡兩張表逐格相同；這支模組不重算任何東西。

兩段歷史不能直接比
    台股是證交所含息報酬指數逐日收盤（2003-01-02 到 2025-12-31，每個交易日當一次買進日），
    只有到 10 年；美股是 Shiller 月資料的 S&P 500 含息、名目（1871 到 2023 年 6 月，
    每個月當一次買進日），有到 30 年。所以圖上分成兩塊、各自標明期間，不並排成同一組。

compute() 只用標準庫；chart(res) 才 lazy import essay_charts。
"""
import json
import os

CALC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'lite', 'calc-results.json')

# （JSON 的 key, 圖上的標籤）——順序就是圖上由上而下的順序
TW_ROWS = [('1天', '1 天'), ('1個月', '1 個月'), ('1年', '1 年'),
           ('3年', '3 年'), ('5年', '5 年'), ('10年', '10 年')]
US_ROWS = [('1年', '1 年'), ('5年', '5 年'), ('10年', '10 年'),
           ('20年', '20 年'), ('30年', '30 年')]

# 指南展開裡兩張表上的數字，改資料時這裡會先斷
TW_EXPECT = {'1天': 55, '1個月': 62, '1年': 77, '3年': 95, '5年': 96, '10年': 100}
US_EXPECT = {'1年': 72, '5年': 90, '10年': 97, '20年': 100, '30年': 100}


def compute():
    rolling = json.load(open(CALC, encoding='utf-8'))['rolling']
    tw, us = rolling['taiex'], rolling['us']
    groups = []
    for name, src, rows, expect in (
            ('台股　含息，2003–2025', tw, TW_ROWS, TW_EXPECT),
            ('美股　S&P 500 含息，1871–2023', us, US_ROWS, US_EXPECT)):
        bars = []
        for key, label in rows:
            share = src['positive_share'][key]
            pct = share['pct_int']
            assert pct == expect[key], (name, key, pct, expect[key])
            bars.append({'key': key, 'label': label, 'pct': pct,
                         'pct_raw': share['pct'], 'n': share['n']})
        groups.append({'name': name, 'bars': bars})
    return {
        'id': 'holding-positive',
        'basis': {
            'what': '每一天（美股是每個月）都當一次買進日，看滿 N 年後是不是比買進時高',
            'taiex': {'source': tw['source'], 'from': tw['from'], 'to': tw['to'],
                      'trading_days': tw['trading_days']},
            'us': {'source': us['source'], 'from': us['from'], 'to': us['to'],
                   'months': us['months']},
            'caveats': rolling['caveats'],
            'window_rule': rolling['window_rule'],
        },
        'source': {'file': 'lite/calc-results.json', 'key': 'rolling',
                   'produced_by': 'tools/calc_core.py'},
        'groups': groups,
        'printed': {},
    }


def chart(res):
    import essay_charts as E
    groups = res['groups']

    def draw(lay):
        mob = lay.mobile
        rh = 25 if mob else 27          # 一列（一根長條）的高度
        gh = 26 if mob else 28          # 每一塊的標題高度
        bh = 13 if mob else 15          # 長條粗細
        lw = 46 if mob else 58          # 左邊的期間標籤欄
        x0 = lw + 6
        x1 = lay.W - (50 if mob else 46)   # 右邊留給「100%」
        nbars = sum(len(g['bars']) for g in groups)
        h = int(lay.top + len(groups) * gh + nbars * rh + (24 if mob else 26))
        bottom = h - (16 if mob else 18)

        def px(v):
            return x0 + (x1 - x0) * v / 100.0

        out = [E.svg_open(lay, h, '台股與美股：每一天都當買進日，抱滿不同期間以後，打開來是賺的比例')]
        # 直向格線：0 用墨色，50 虛線（擲硬幣那條），100 虛線
        for v in (0, 50, 100):
            color = E.INK if v == 0 else E.LINE
            dash = '' if v == 0 else ' stroke-dasharray="3 4"'
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s"%s/>'
                       % (px(v), lay.top - 2, px(v), bottom - 4, color, 1.3 if v == 0 else 1, dash))
            lab = '50%（一半）' if v == 50 else '%d%%' % v
            out.append(E.text(px(v), bottom + lay.fs, lab, lay.fs, 'middle', E.MUTED))
        y = lay.top
        for gi, g in enumerate(groups):
            color = E.TEAL if gi == 0 else E.MUTED
            out.append(E.text(4, y + gh - 9, g['name'], lay.f, 'start', E.INK, '800'))
            y += gh
            for b in g['bars']:
                out.append(E.text(lw, y + bh - 3, b['label'], lay.f, 'end', E.MUTED))
                out.append(E.rect(px(0), y, max(2.0, px(b['pct']) - px(0)), bh, color))
                out.append(E.text(px(b['pct']) + 6, y + bh - 3, '%d%%' % b['pct'],
                                  lay.fl, 'start', E.INK, '800'))
                y += rh
        out.append('</svg>')
        return '\n'.join(out)

    lg = E.legend([(E.TEAL, '台股（含息，2003–2025）'), (E.MUTED, '美股（S&P 500 含息，1871–2023）')])
    tw, us = res['basis']['taiex'], res['basis']['us']

    def ym(s):
        y, m = s.split('-')
        return '%s 年 %d 月' % (y, int(m))
    nt = E.note('台股用證交所發行量加權股價報酬指數（含息）逐日收盤自算，%s 到 %s 共 %s 個交易日，'
                '每個交易日都當一次買進日；美股用 Robert Shiller 公開月資料的 S&P 500 含息、名目，'
                '%s 到 %s，每個月都當一次買進日（股利欄到這裡為止）。'
                '兩邊的市場和期間都不一樣，台股也只算到 10 年，所以上下兩塊不能直接比高低。'
                '這些期間彼此重疊，不是互相獨立的樣本；都沒有扣掉物價、費用和稅。'
                % (tw['from'], tw['to'], '{:,}'.format(tw['trading_days']),
                   ym(us['from']), ym(us['to'])))
    caption = ('同一筆錢，差別只在多久以後才打開來看：隔天打開差不多是擲硬幣，抱得越久，'
               '打開來是賺的比例越高。這是這兩段歷史裡的比例，不是未來的機率；'
               '台股只有 23 年，10 年那一條的 100% 只代表這段期間。')
    res['printed'] = {'taiex': {b['label']: b['pct'] for b in groups[0]['bars']},
                      'us': {b['label']: b['pct'] for b in groups[1]['bars']}}
    return dict(title='抱多久打開，是賺的比例有多高',
                sub='台股 2003–2025、美股 1871–2023，每一天（美股每個月）都當買進日，%',
                svgs=[draw(E.L('d')), draw(E.L('m'))], extras=lg + nt, caption=caption)


if __name__ == '__main__':
    r = compute()
    print(json.dumps(r, ensure_ascii=False, indent=1))
