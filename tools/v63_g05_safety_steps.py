"""G05（v6.3 第二批 c）：「投資前的安全順序」那一節的五階樓梯。

內容來源
    指南「投資前的安全順序」（id="start"）的五點清單，逐項照抄標題：
    ①看懂每月現金流 ②先處理高利率債務 ③留緊急預備金 ④補上重大風險保障 ⑤把錢按使用日期分桶，
    做完這五項才決定投入金額（該節行動句：「完成現金流、債務、預備金、保障與用錢日期五項檢查，
    再決定投入金額」）。

只畫樓梯，不畫三個桶
    第 5 項「分桶」已經有自己的圖：第 14 節的 buckets（按用錢日期分三桶），
    所以這張圖只畫樓梯，第五階寫「分桶」並指過去，不重複畫桶。

純示意
    階梯的高低只表示先後順序，不表示難易、金額或時間長短；沒有任何新數字。
    圖下說明裡的 4%、三到六個月、五年都是該節原文既有的數字。

compute() 只用標準庫；chart(res) 才 lazy import essay_charts。
"""

# （編號, 完整名稱, 桌面第一行, 桌面第二行）
STEPS = [
    ('①', '看懂每月現金流', '看懂每月', '現金流'),
    ('②', '先處理高利率債務', '先處理', '高利率債務'),
    ('③', '留緊急預備金', '留緊急', '預備金'),
    ('④', '補上重大風險保障', '補上重大', '風險保障'),
    ('⑤', '把錢按使用日期分桶', '把錢按使用', '日期分桶'),
]
TOP = ('', '才開始投資', '才開始', '投資')
ACTION = '完成現金流、債務、預備金、保障與用錢日期五項檢查，再決定投入金額。'


def compute():
    assert len(STEPS) == 5
    return {
        'id': 'safety-steps',
        'illustrative': True,
        'basis': {
            'what': '「投資前的安全順序」五項的順序，最上面一階才是投資',
            'meaning_of_height': '階梯高低只表示先後順序，不表示難易、金額或時間長短',
            'no_new_numbers': True,
            'buckets_not_redrawn': '第 5 項「分桶」已經有第 14 節的 buckets 圖，這裡不重畫三個桶',
        },
        'steps': [{'n': n, 'name': name} for n, name, _, _ in STEPS],
        'top': TOP[1],
        'source': {'section_id': 'start', 'via': '指南「投資前的安全順序」五點清單（逐項照抄標題）',
                   'action_sentence': ACTION},
        'printed': {},
    }


def chart(res):
    import essay_charts as E

    def draw_desktop(lay):
        pad = 8
        cols = len(STEPS) + 1
        cw = (lay.W - pad * 2) / cols
        rise = 38
        h = rise * cols + 36
        base = h - 8
        fs = 11.5
        lh = 14
        out = [E.svg_open(lay, h, '投資前的安全順序：五階樓梯，由低到高是看懂現金流、'
                                  '處理高利率債務、留預備金、補保障、按用錢日期分桶，最上面一階才是投資')]
        items = [(n, l1, l2, False) for n, _, l1, l2 in STEPS] + [(TOP[0], TOP[2], TOP[3], True)]
        for i, (n, l1, l2, top) in enumerate(items):
            x = pad + i * cw
            y = base - (i + 1) * rise
            col = E.AMBER if top else E.TEAL
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="%s"/>'
                       % (x, y, cw, base - y, col, '0.22' if top else '0.13'))
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.4"/>'
                       % (x, y, x + cw, y, col))
            cx = x + cw / 2
            head = (n + ' ' + l1) if n else l1
            out.append(E.text(cx, y - lh - 6, head, fs, 'middle', E.INK, '700'))
            out.append(E.text(cx, y - 6, l2, fs, 'middle', E.INK, '700'))
        out.append('</svg>')
        return '\n'.join(out)

    def draw_mobile(lay):
        pitch = 40
        rows = len(STEPS) + 1
        h = pitch * rows + 12
        rh = 30
        items = [(n, name, False) for n, name, _, _ in STEPS] + [(TOP[0], TOP[1], True)]
        out = [E.svg_open(lay, h, '投資前的安全順序：由下往上五階，看懂現金流、處理高利率債務、'
                                  '留預備金、補保障、按用錢日期分桶，最上面一階才是投資')]
        for i, (n, name, top) in enumerate(items):
            x0 = 6 + i * 11
            x1 = lay.W - 6
            y = h - 8 - (i + 1) * pitch
            col = E.AMBER if top else E.TEAL
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" rx="4" fill="%s" fill-opacity="%s"/>'
                       % (x0, y, x1 - x0, rh, col, '0.22' if top else '0.13'))
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.4"/>'
                       % (x0, y, x1, y, col))
            out.append(E.text(x0 + 10, y + rh / 2 + lay.f * 0.36,
                              (n + ' ' + name) if n else name, lay.f, 'start', E.INK, '700'))
        out.append('</svg>')
        return '\n'.join(out)

    # v7 批 1：圖說原本把下面那五點整段複述一遍（含 4%、第 14 節、行動句），和正文重複，改成一句指路。
    nt = E.note('示意圖，沒有新數字：階梯的高低只表示先後順序，不表示哪一階比較難、要花多少錢或多久。'
                '每一階要做什麼，在下面那五點裡。')
    caption = ('由低到高五階：%s。五階做完，最上面那一階才是投資。'
               % '、'.join(s['name'] for s in res['steps']))
    lead = '投資前要做的五件事有先後：下面這張圖先把它們排成一道樓梯，最上面那一階才是投資。'
    res['printed'] = {'steps': [s['name'] for s in res['steps']], 'top': res['top'],
                      'lead_sentence': lead}
    return dict(title='投資前的五階：走完才輪到投資',
                sub='示意：階梯高低只表示先後順序，不表示難易或金額',
                svgs=[draw_desktop(E.L('d')), draw_mobile(E.L('m'))], extras=nt, caption=caption)


if __name__ == '__main__':
    import json
    print(json.dumps(compute(), ensure_ascii=False, indent=1))
