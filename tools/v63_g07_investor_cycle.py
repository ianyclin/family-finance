"""G07（v6.3）：第 13 節「散戶的一趟：從聽說到再也不看」示意圖（id `investor-cycle`）。

這張圖做什麼
    第 13 節現在是十二條偏誤的清單，一條一條都對，但讀者不會照清單的順序犯錯——
    真實的順序是一條路：聽到消息、忍不住買、賺一點就賣、追回來、抱到最高點、跌回成本還在等、
    再買一張把成本拉低、不敢打開帳戶、回到平均成本就賣掉、後來它又漲上去。
    這張圖把那條路畫成一條價格線，沿線標十一站，每一站旁邊標「這本書哪一節擋它」。

圖上沒有任何數字，也沒有任何一段真實行情
    曲線是自己畫的（先漲、急漲、崩、反彈、盤整、再漲），只有形狀，沒有刻度、沒有幣別、沒有年份。
    唯一一條水平虛線是「第一次買進的價格」，用來讓「跌回成本」和「回到成本」兩站看得出來。

形狀從哪裡來（見 wip/v63/stock-vs-index/evidence.md 第三題）
    「投資人情緒循環」這種圖至少有三條互相獨立的血脈；流傳最廣的一版，轉載的人普遍在圖下標
    "Source: Westcore Funds / Denver Investment Advisers LLC, 1998."，原件已經找不到、也沒有公開授權。
    中文版那一串站名（聽說→…→再也不看）查不到原作者。
    所以這裡只借「先漲、崩、反彈、再漲」這個形狀（概念），曲線自己畫、站名自己寫，
    不轉載、不描圖、不照抄任何一版獨有的用字串（那 15 個英文情緒詞的順序、
    "Point of maximum financial risk / opportunity" 兩句標記都沒有出現）。
    compute() 裡有 BANNED 一組字，會擋掉流傳版本的中文站名用語。

作者點名的六種行為，站在哪一站（BEHAVIORS，compute() 會斷言六種都有人接）
    ①抱上又爆下 → 第 7 站　②不知道什麼時候該賣 → 第 6 站　③賺一點點就賣 → 第 4 站
    ④一直跌一直買、住進去 → 第 8、9 站　⑤回到平均成本就賣、錯過後面 → 第 10、11 站
    ⑥只買一張，漲很多也只有一點錢 → 第 3 站

規格未定處（都寫在回傳裡）
    1. 站名旁邊只印節號（例如「第 11 節」），節名與「擋它的是哪一句」放在圖下的註解，
       因為 640 寬放不下十一條節名。
    2. 桌面版十一個站名沿線放，位置是手排的（LAYOUT 表），chart() 會自己算方框、
       自測腳本會斷言兩兩不重疊、不壓到曲線、不超出畫布。
    3. 手機版曲線上只放編號徽章，站名改成圖下的編號清單（同一個 SVG 裡）。

compute() 只用標準庫；chart(res) 才 lazy import essay_charts。
"""
import math

# ---- 自己畫的價格曲線：(t, v)，t 是左到右的位置、v 是高度，兩個都沒有單位 ----
# 先漲（0–0.28）、急漲（0.28–0.52）、崩（0.52–0.70）、反彈（0.70–0.79）、
# 盤整（0.79–0.92）、再漲（0.92–1.00）
KEY = [(0.00, 26), (0.10, 32), (0.20, 40), (0.28, 50), (0.36, 60), (0.42, 70),
       (0.47, 86), (0.52, 100), (0.56, 88), (0.60, 50), (0.65, 33), (0.70, 19),
       (0.75, 33), (0.79, 50), (0.83, 45), (0.88, 44), (0.92, 52), (0.96, 70), (1.00, 88)]
COST_V = 50           # 第一次買進的價格（第 3 站的高度）

PHASES = ['先漲一段', '急漲', '崩下來', '反彈', '盤整', '再漲']

# 作者點名的六種行為（只給裁判核對用，不會印在圖上）
BEHAVIORS = {
    1: '抱上又爆下',
    2: '不知道什麼時候該賣',
    3: '賺一點點就賣',
    4: '一直跌一直買、住進去',
    5: '一回本就賣，錯過後面的漲幅',
    6: '只買一張，漲很多報酬也只有一點',
}

# 這五節是這本書擋這條路的地方；(節號, 節名, 擋它的是哪一句)
SECTIONS = {
    5: ('現在開始會不會太晚？', '前幾年帳戶裡多半是自己存進去的錢，越往後自己長出來的部分越多'),
    9: ('要不要等跌下來再買？', '猜低點要猜對兩次，等待也有代價'),
    11: ('漲了要不要先賣一些？', '賣掉以後，那筆錢就不再跟著漲跌；如果之後還想買回來，就要再猜一次什麼時候買'),
    13: ('明明知道，為什麼還是想動手？', '捨不得認賠：買進的價格是過去的事；還有冷卻期'),
    14: ('把答案寫成一張紙：我的投資計畫', 'F 區先寫好跌多少各做什麼、什麼情況才賣，再加一次大跌演練'),
}

# (編號, t, 桌面站名, 手機站名, 節號, 行為編號或 None)
STATIONS = [
    (1, 0.04, '有人說這檔會漲', '有人說這檔會漲', 13, None),
    (2, 0.20, '想等跌一點再買，它一直漲', '想等跌一點再買，它一直漲', 9, None),
    (3, 0.28, '忍不住買了，只買得起一張', '忍不住買了，只買一張', 5, 6),
    (4, 0.36, '賺一點，先賣掉安心', '賺一點，先賣掉安心', 11, 3),
    (5, 0.42, '它又漲，用更貴的價格買回來', '它又漲，用更貴的買回來', 11, None),
    (6, 0.52, '帳上終於多了不少，想再等等', '帳上終於多了不少，再等等', 11, 2),
    (7, 0.60, '跌回買進的價格，還在等它回來', '跌回買進的價格，還在等', 13, 1),
    (8, 0.65, '再買一張，把成本拉低', '再買一張，把成本拉低', 14, 4),
    (9, 0.70, '不敢再打開帳戶', '不敢再打開帳戶', 13, 4),
    # 第 8 站再買一張以後平均成本比第一次買進低，所以這一站落在虛線下面（t=0.77 剛好是兩次買價的平均）
    (10, 0.77, '回到我的平均成本，趕快賣掉', '回到我的平均成本就賣掉', 13, 5),
    (11, 0.97, '後來它又漲上去，我不在裡面', '後來它又漲上去，我不在', 11, 5),
]

# 流傳版本（中文）那一串用語：站名裡一個都不准出現，確保不是把別人的字換句話說
BANNED = ['聽說', '定力', '抱上去', '爆下來', '套牢', '解套', '攤平', '再也不看',
          '樂觀', '興奮', '狂熱', '焦慮', '恐慌', '絕望', '希望', '投降']

# 桌面版站名的手排位置：編號 -> (anchor, dx, 名字那一行的基線 y)
# anchor 是 SVG 的 text-anchor；dx 是相對於站點 x 的位移（配合 anchor 決定方框左右緣）。
LAYOUT = {
    1: ('start', -11, 213),
    2: ('end', 36, 244),
    3: ('start', 8, 213),
    4: ('end', -7, 72),
    5: ('end', 30, 42),
    6: ('start', 38, 30),
    7: ('end', 23, 244),
    8: ('middle', 0, 275),
    9: ('start', -24, 244),
    10: ('middle', 0, 72),
    11: ('end', 21, 196),
}


def curve_v(t):
    """自己畫的曲線：兩個關鍵點之間用餘弦補間（不會超過兩端的高度）。"""
    t = min(max(t, 0.0), 1.0)
    for (t0, v0), (t1, v1) in zip(KEY, KEY[1:]):
        if t0 - 1e-9 <= t <= t1 + 1e-9:
            u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return v0 + (v1 - v0) * (1 - math.cos(math.pi * u)) / 2
    return KEY[-1][1]


def compute():
    ts = [s[1] for s in STATIONS]
    assert 10 <= len(STATIONS) <= 12, len(STATIONS)
    assert ts == sorted(ts) and len(set(ts)) == len(ts), '站的順序要由左到右、不重疊'
    names = [s[2] for s in STATIONS] + [s[3] for s in STATIONS]
    assert len(set(s[2] for s in STATIONS)) == len(STATIONS), '站名不能重複'
    for n in names:
        for b in BANNED:
            assert b not in n, (n, b)
    covered = sorted(set(s[5] for s in STATIONS if s[5]))
    assert covered == [1, 2, 3, 4, 5, 6], covered
    assert set(s[4] for s in STATIONS) <= set(SECTIONS), '只用第 5、9、11、13、14 節'
    # 兩個「買進的價格」站要真的落在那條水平線上
    assert abs(curve_v(0.28) - COST_V) < 1e-6 and abs(curve_v(0.60) - COST_V) < 1e-6
    # 第 10 站要落在「兩次買價的平均」上，也就是虛線以下（第 3 站買 1 張、第 8 站再買 1 張）
    AVG_COST = (curve_v(0.28) + curve_v(0.65)) / 2
    assert AVG_COST < COST_V and abs(curve_v(0.77) - AVG_COST) < 1e-6, (AVG_COST, curve_v(0.77))
    stations = [{'n': n, 't': t, 'name': d, 'name_mobile': m, 'section': sec,
                 'section_title': SECTIONS[sec][0], 'blocked_by': SECTIONS[sec][1],
                 'behavior': (BEHAVIORS[b] if b else None), 'behavior_no': b,
                 'v': round(curve_v(t), 2)}
                for n, t, d, m, sec, b in STATIONS]
    return {
        'id': 'investor-cycle',
        'illustrative': True,
        'basis': {
            'what': '一條自己畫的價格線，沿線十一站，每一站標這本書哪一節擋它',
            'no_numbers_on_chart': True,
            'no_market_data': '曲線與「第一次買進的價格」那條線都是畫出來的，沒有刻度、沒有幣別、沒有年份',
            'phases': PHASES,
            'cost_line': '第一次買進的價格（第 3 站的高度），讓第 7 站看得出來是同一個高度；'
                         '第 10 站在虛線以下，因為第 8 站再買一張以後平均成本比它低（兩次買價的平均）',
            'average_cost_after_second_buy': round((curve_v(0.28) + curve_v(0.65)) / 2, 2),
        },
        'stations': stations,
        'behaviors': {str(k): [s['n'] for s in stations if s['behavior_no'] == k]
                      for k in sorted(BEHAVIORS)},
        'behavior_names': {str(k): v for k, v in BEHAVIORS.items()},
        'sections_used': {str(k): {'title': SECTIONS[k][0], 'blocked_by': SECTIONS[k][1]}
                          for k in sorted(SECTIONS)},
        'source': {
            'shape': '借自流傳很廣的「投資人情緒循環」示意；最早的版本常標 Westcore Funds'
                     '（Denver Investment Advisers LLC），1998',
            'reproduced': False,
            'station_names': '站名是本文自己寫的，沒有沿用任何一版的用字',
            'evidence': 'wip/v63/stock-vs-index/evidence.md 第三題',
        },
        'printed': {},
    }


# 桌面版的畫布與座標（chart() 與 layout_boxes() 共用同一份，才不會兩邊算出不同的框）
D_X0, D_X1, D_PT, D_SC = 10.0, 630.0, 34.0, 2.0
D_FNAME, D_FSEC = 11.0, 10.0


def tw(s, size):
    """字串寬度估計：中日韓與全形標點算一個字寬，其餘算 0.55。"""
    w = 0.0
    for ch in s:
        w += size if (ord(ch) > 0x2E7F or ch in '，。、；：？！（）') else size * 0.55
    return w


def d_px(t):
    return D_X0 + (D_X1 - D_X0) * t


def d_py(v):
    return D_PT + (100 - v) * D_SC


def desktop_boxes(stations):
    """每一個站名的方框（含節號那一行）與站點座標；手排位置在 LAYOUT。"""
    boxes = []
    for s in stations:
        anchor, dx, yb = LAYOUT[s['n']]
        w = max(tw(s['name'], D_FNAME), tw('第 %d 節' % s['section'], D_FSEC))
        ax = d_px(s['t']) + dx
        left = {'start': ax, 'middle': ax - w / 2, 'end': ax - w}[anchor]
        boxes.append({'s': s, 'n': s['n'], 'name': s['name'], 'anchor': anchor, 'ax': ax, 'yb': yb,
                      'x0': left, 'x1': left + w, 'y0': yb - 10, 'y1': yb + 17,
                      'dot': (d_px(s['t']), d_py(s['v']))})
    return boxes


def chart(res):
    import essay_charts as E

    def draw_curve(x0, x1, py, n=180):
        pts = [(x0 + (x1 - x0) * i / n, py(curve_v(i / n))) for i in range(n + 1)]
        return E.poly(pts, E.TEAL, 2.6)

    def badge(cx, cy, n, r, fs):
        return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" stroke-width="1.5"/>'
                % (cx, cy, r, E.AMBER, E.SURFACE)
                + E.text(cx, cy + fs * 0.36, str(n), fs, 'middle', E.SURFACE, '800'))

    ARIA = ('示意圖：一條自己畫的價格線，先漲一段、急漲、崩下來、反彈、盤整、再漲；'
            '沿線十一站依序是' + '、'.join('%d %s' % (s['n'], s['name']) for s in res['stations'])
            + '；每一站旁邊標這本書哪一節擋它。圖上沒有任何數字，也不是任何市場的資料。')

    # ---------------- 桌面 640：站名沿線 ----------------
    def draw_desktop():
        lay = E.L('d')
        x0, x1, px, py = D_X0, D_X1, d_px, d_py
        f_name, f_sec = D_FNAME, D_FSEC
        boxes = desktop_boxes(res['stations'])
        h = max(b['y1'] for b in boxes) + 10

        out = [E.svg_open(lay, h, ARIA)]
        # 第一次買進的價格：一條水平虛線
        out.append(E.hline(x0, x1, py(COST_V), E.MUTED, 1.1, '5 4'))
        out.append(E.text(x0 + 2, py(COST_V) - 6, '第一次買進的價格', lay.fs, 'start', E.MUTED, '700'))
        out.append(draw_curve(x0, x1, py))
        # 指引線：先從站點垂直拉到站名那一行，必要時再橫過去接到方框邊
        for b in boxes:
            cx, cy = b['dot']
            above = b['y1'] < cy
            ty = (b['y1'] + 3) if above else (b['y0'] - 3)
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
                       % (cx, cy + (-11 if above else 11), cx, ty, E.LINE))
            if cx < b['x0'] - 1 or cx > b['x1'] + 1:
                edge = b['x0'] - 4 if cx < b['x0'] else b['x1'] + 4
                my = b['yb'] - 4
                out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
                           % (cx, ty, cx, my, E.LINE))
                out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
                           % (cx, my, edge, my, E.LINE))
        for b in boxes:
            s = b['s']
            out.append(badge(b['dot'][0], b['dot'][1], s['n'], 9, 10))
            out.append(E.text(b['ax'], b['yb'], s['name'], f_name, b['anchor'], E.INK, '700'))
            out.append(E.text(b['ax'], b['yb'] + 13, '第 %d 節' % s['section'], f_sec,
                              b['anchor'], E.MUTED))
        out.append('</svg>')
        return '\n'.join(out), boxes, (x0, x1, px, py)

    # ---------------- 手機 360：線上只放編號，站名做成圖下清單 ----------------
    def draw_mobile():
        lay = E.L('m')
        x0, x1 = 12.0, 348.0
        pt, sc = 24.0, 1.45
        f = 10.0

        def px(t):
            return x0 + (x1 - x0) * t

        def py(v):
            return pt + (100 - v) * sc

        rows_y0 = py(19) + 26
        rh = 16.5
        h = rows_y0 + rh * len(res['stations']) + 6
        out = [E.svg_open(lay, h, ARIA)]
        out.append(E.hline(x0, x1, py(COST_V), E.MUTED, 1.1, '5 4'))
        out.append(E.text(x0 + 1, py(COST_V) - 5, '第一次買進的價格', lay.fs, 'start', E.MUTED, '700'))
        out.append(draw_curve(x0, x1, py))
        for s in res['stations']:
            out.append(badge(px(s['t']), py(s['v']), s['n'], 7.5, 9))
        rows = []
        for i, s in enumerate(res['stations']):
            y = rows_y0 + rh * i
            out.append(badge(x0 + 7, y - 3, s['n'], 7, 8.5))
            out.append(E.text(x0 + 19, y, s['name_mobile'], f, 'start', E.INK, '700'))
            out.append(E.text(x1, y, '第 %d 節' % s['section'], f, 'end', E.MUTED))
            rows.append({'n': s['n'], 'y': y,
                         'name_x1': x0 + 19 + tw(s['name_mobile'], f),
                         'sec_x0': x1 - tw('第 %d 節' % s['section'], f)})
        out.append('</svg>')
        return '\n'.join(out), rows

    d_svg, boxes, geo = draw_desktop()
    m_svg, rows = draw_mobile()

    lg = E.legend([(E.TEAL, '一條自己畫的價格線：先漲一段、急漲、崩下來、反彈、盤整、再漲'),
                   (E.AMBER, '沿線十一站：很多人走過的順序'),
                   (E.MUTED, '橫的虛線是第一次買進的價格')])
    # v6.3 批 3 修正（裁判 note-5）：note 裡的節號改成 xref 連結，和內文體例一致。
    # v7 批 7：後半（逐站重述第 5、9、11、13、14 節在講什麼，約 215 字）刪掉——圖上每一站旁邊
    # 本來就標著節號，那段只是把各節的 lede 再念一次；形狀的出處那兩句和圖下「想深入：流傳很廣的
    # 那張『經典散戶圖』」逐句重複，也刪掉，出處留在那個摺疊裡。s10 看得到的小字因此回到 350 以內。
    # v7 第 20 版 I：「不是任何市場的資料」chart-sub 已經講了，figcaption 又講一次；
    # 「橫的虛線是第一次買進的價格」圖例就寫著。p.note 只留圖上看不出來的那一句。
    nt = E.note('第 8 站再買一張以後，平均成本比第一次買進的價格低，所以第 10 站落在虛線下面。')
    # figcaption 刪掉「線的高度是畫出來的，不是任何市場的資料」那半句（和 chart-sub 重複）。
    caption = ('這條線是很多人走過的順序：漲一段、急漲、崩下來、反彈、盤整、再漲；'
               '每一站旁邊寫的是這本書哪一節擋它。這不是說接下來會照這個順序走。')
    lead = ('前面十二條是一條一條列的，真正發生的時候它們會連成一條路。'
            '下面這張圖把那條路畫出來，每一站旁邊標的是這本書哪一節擋它。')
    res['printed'] = {
        'stations': ['%d %s（第 %d 節）' % (s['n'], s['name'], s['section']) for s in res['stations']],
        'stations_mobile': ['%d %s' % (s['n'], s['name_mobile']) for s in res['stations']],
        'behaviors': res['behaviors'],
        'lead_sentence': lead,
        'caption': caption,
    }
    return dict(title='散戶的一趟：從聽說到再也不看',
                sub='示意，不是任何市場的資料',
                svgs=[d_svg, m_svg], extras=lg + nt, caption=caption)


def layout_boxes():
    """自測用：桌面版的站名方框、站點座標與曲線取樣點，讓測試機械檢查重疊與超框。"""
    res = compute()
    boxes = desktop_boxes(res['stations'])
    curve = [(d_px(i / 400.0), d_py(curve_v(i / 400.0))) for i in range(401)]
    return {'W': 640, 'boxes': [{k: v for k, v in b.items() if k != 's'} for b in boxes],
            'curve': curve, 'height': max(b['y1'] for b in boxes) + 10}


if __name__ == '__main__':
    import json
    print(json.dumps(compute(), ensure_ascii=False, indent=1))
