#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G12（v7 批 CU）：兩張指路圖。只在指南。規格：wip/v63-review/spec-v7-charts-cu.md。

    panic-map   「跌了，先看哪裡」：第 14 節急救卡 #plan-panic 開頭。四個分岔＋一條主路，
                全部照急救卡原句；急救卡對「借錢買的」只有「今天正在跌」一條路，圖不補路。
    first-route 「從今天到第一筆投資」：第 19 節 firstmonth 白話版之後、「第一週」之前。
                七站照第 19 節時間表的順序（開戶在第 2 站），尾巴接「每年一次的檢查表」。

原則：圖只指路，不下規則。圖上每一行字（SVG 的每一個 <text>）都必須逐字存在於指南內文；
compute() 讀 guide/index.html，先拿掉所有 figure.chart（圖自己的字、圖說不算數）、SVG、style、
script，再逐行比對，缺就 raise。比對分兩層：
    1. 全書可見文字裡找得到（規格的底線，急救卡在摺疊裡也算）；
    2. 找得到的範圍再收窄到「這句話該在的地方」：急救卡的字要在急救卡那張 div.data-card 裡，
       頂端那句要是某個指到 #plan-panic 的連結文字，各站要在各自那一節。
另外斷言每個分岔指到的錨點（#s5-fiveyear 等）還在，而且指對（見 ANCHOR_WINDOW 上面的說明）。
箭頭上不寫字；SVG 裡不放 xref、不寫「第 N 節」，節號只在 figcaption 用 xref。

calc_core.py 呼叫 missing_labels() 把缺的字接進「引用缺漏」（不在 calc-results.json 另開鍵）。
compute() 只用標準庫；chart_panic()／chart_route() 才 lazy import essay_charts。
"""
import os
import re
from html import unescape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GUIDE = os.path.join(ROOT, 'guide', 'index.html')

# ---------------------------------------------------------------------------
# 圖一：跌了，先看哪裡
# 每一行字是一個 SVG <text>；scope 是這一行字該在的地方：
#   'cta'   ＝ 某個 href="#plan-panic" 的連結文字（封面「正在跌，我很慌」那顆按鈕）
#   'card'  ＝ 急救卡（h4#plan-panic 所在的 div.data-card）
PANIC_TITLE = '跌了，先看哪裡'
PANIC_CAPTION = '先找自己是哪一種錢，再看那一格；圖上的每一條路，急救卡下面都有原文。'
PANIC_ROOT = '正在跌，我很慌'
# (條件, 目的地桌機行, 目的地手機行, 目的地錨點)
PANIC_BRANCHES = [
    ('這筆錢五年內要用的',
     ['「跌的時候、很久沒漲的時候，記得這幾句」第一條'],
     ['「跌的時候、很久沒漲的時候，記得這幾句」第一條'],
     's5-fiveyear'),
    ('借錢買的',
     ['「年齡、槓桿與退休」的「已經借錢投資、今天正在跌」'],
     ['「年齡、槓桿與退休」的「已經借錢投資、今天正在跌」'],
     'lifecycle-q2-today'),
    ('手上是以前買的個股',
     ['「處理套牢的舊部位」'],
     ['「處理套牢的舊部位」'],
     's13-stuck'),
]
PANIC_MAIN = '照這本書做長期、分散投資的'
PANIC_MAIN_D = ['照這本書做長期、', '分散投資的']        # 桌機欄窄，拆兩行（兩行各自也是原句的子字串）
PANIC_THREE = '今天先做三件事：不賣、計畫沒寫加碼的人不加碼、關掉 app 的漲跌推播'
# 批 DK（通讀評價實質 2）：急救卡改成「計畫沒寫加碼的人不加碼」，一行放不下（桌機約 361px 對 328px、手機 328 對 282），
# 圖上拆兩行；兩行各自也是急救卡原句的子字串（和 PANIC_MAIN_D 同一個做法）。aria 與 compute() 仍用整句。
PANIC_THREE_LINES = ['今天先做三件事：不賣、計畫沒寫加碼的人不加碼、', '關掉 app 的漲跌推播']
# (開頭, 內文行, 錨點)
PANIC_SUBS = [
    ('已經寫好計畫的人：', ['把那張紙拿出來，照「市場下跌時」那一行做'], None),
    ('還沒寫過計畫的人：', ['今天不是寫規則的日子', '挑一個平靜的日子回來，填下面的六行'], 'plan-starter'),
]

# ---------------------------------------------------------------------------
# 圖二：從今天到第一筆投資
# (桌機行, 手機行, 該在的那一節 id)；桌機一列七站，一站最多六個字一行。
ROUTE_TITLE = '從今天到第一筆投資'
ROUTE_STATIONS = [
    (['投資前的', '安全順序'], ['投資前的安全順序'], 'start'),
    # 批 CU 裁判後：開戶移到第 2 站，照第 19 節時間表的順序（第一週第 4 項就是開戶，「開戶不等於要投入」）。
    (['到合法券商', '開證券戶', '和交割戶'], ['到合法券商開證券戶和交割戶'], 'firstmonth'),
    (['每月投多少？'], ['每月投多少？'], 'page'),          # 起步版六行的第 3 行（問句寫法在書前的讀法說明）
    (['股票放幾成', '驗算一次'], ['股票放幾成', '驗算一次'], 's5'),
    (['起步版：六行'], ['起步版：六行'], 's11'),
    (['用小金額', '完成第一次'], ['用小金額完成第一次'], 'steps'),
    (['設成自動，', '留好紀錄'], ['設成自動，留好紀錄'], 'steps'),
]
ROUTE_TAIL = ('每年一次的檢查表', 'annual')
# figcaption：括號裡的節號用 xref（SVG 裡不放節號）。批 CU 裁判後：第一句拿掉「七站」
# （免得和第 20 節「七個步驟」混成同一組）；清單順序跟 ROUTE_STATIONS 一起改。
# 注意：essay_charts --guide 會保留指南裡已有的 figcaption，改這裡要同步改 guide/index.html 那一句。
ROUTE_CAPTION = ('照這個順序走；每一站的細節在括號裡那一節。'
                 '投資前的安全順序（第 <a class="xref" href="#start">2</a> 節）、'
                 '開證券戶和交割戶（第 <a class="xref" href="#steps">20</a> 節）、'
                 '每月投多少（第 <a class="xref" href="#plan-l3a">5</a> 節）、'
                 '股票放幾成和驗算一次（第 <a class="xref" href="#s5-check">8</a> 節）、'
                 '起步版六行（第 <a class="xref" href="#plan-starter">14</a> 節）、'
                 '用小金額完成第一次（第 <a class="xref" href="#steps">20</a> 節）、'
                 '設成自動，留好紀錄（第 <a class="xref" href="#steps">20</a> 節）；'
                 '每年一次的檢查表（第 <a class="xref" href="#annual">23</a> 節）。')
ROUTE_ANCHORS = ['start', 'plan-l3a', 's5-check', 'plan-starter', 'steps', 'annual']


def panic_labels():
    """[(字, scope)]：圖一每一個 SVG <text>，桌機與手機兩版的聯集。"""
    out = [(PANIC_ROOT, 'cta')]
    for cond, dd, dm, _a in PANIC_BRANCHES:
        out.append((cond, 'card'))
        out += [(s, 'card') for s in dd + dm]
    out.append((PANIC_MAIN, 'card'))
    out += [(s, 'card') for s in PANIC_MAIN_D]
    out += [(s, 'card') for s in PANIC_THREE_LINES]
    for head, body, _a in PANIC_SUBS:
        out.append((head, 'card'))
        out += [(s, 'card') for s in body]
    return _uniq(out)


def route_labels():
    out = []
    for dd, dm, sec in ROUTE_STATIONS:
        out += [(s, sec) for s in dd + dm]
    out.append(ROUTE_TAIL)
    return _uniq(out)


def _uniq(pairs):
    seen, out = set(), []
    for p in pairs:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


# ---------------------------------------------------------------------------
# 指南的可見文字
_BLOCK_END = re.compile(r'</(?:p|li|h[1-6]|td|th|tr|dt|dd|div|summary|figcaption|caption|ol|ul|table|section|header|nav)>')


def _strip_figures(h):
    """拿掉所有 figure.chart（圖上的字與圖說不能拿來證明自己）與 style、script、svg。"""
    h = re.sub(r'<style.*?</style>', '', h, flags=re.S)
    h = re.sub(r'<script.*?</script>', '', h, flags=re.S)
    # class 是 "chart" 或 "chart 另一個 class"（例如 figure.chart.photo）都拿掉；illus 不是 chart，不動。
    h = re.sub(r'<figure class="chart(?: [^"]*)?"[^>]*>.*?</figure>', '', h, flags=re.S)
    h = re.sub(r'<svg.*?</svg>', '', h, flags=re.S)
    return h


def _visible(frag):
    """去標籤後的可見文字：區塊結尾換行（一句話不會跨兩個區塊湊出來），行內標籤直接拿掉。"""
    t = _BLOCK_END.sub('\n', frag)
    t = re.sub(r'<[^>]+>', '', t)
    t = unescape(t).replace('\xa0', ' ')
    return re.sub(r'[ \t\r\f\v]+', ' ', t)


def _scopes(h):
    """回 {scope: 可見文字}；h 已經拿掉 figure.chart。"""
    sc = {'page': _visible(h)}
    for m in re.finditer(r'<section class="part" id="([^"]+)">(.*?)</section>', h, flags=re.S):
        sc[m.group(1)] = _visible(m.group(2))
    i = h.find('<h4 id="plan-panic">')
    if i >= 0:
        j0 = h.rfind('<div class="data-card">', 0, i)
        j1 = h.find('</div>', i)
        if j0 >= 0 and j1 > i and '<div' not in h[j0 + 1:i] and '<div' not in h[i:j1]:
            sc['card'] = _visible(h[j0:j1])
    sc['cta'] = '\n'.join(_visible(m.group(1)) for m in
                          re.finditer(r'<a\b[^>]*href="#plan-panic"[^>]*>(.*?)</a>', h, flags=re.S))
    return sc


# 錨點要「指對」，不只「存在」（批 CU 裁判後加）。圖一每個分岔的目的地字寫成「某一節」的「某一段」：
#   - 目的地字裡每一個「」片段，都要在錨點元素所在的那一節（section.part）的可見文字裡；
#   - 最後一個「」片段（讀者點過去真正要找的那一段），還要在錨點元素開頭往後 ANCHOR_WINDOW 個可見字以內
#     （不跨出那一節）。第一個片段常是節名（「年齡、槓桿與退休」），在錨點前面，所以只查同一節。
# ANCHOR_WINDOW：2026-09-28 實測 s5-remember 0 字、lifecycle-q2-today 0 字、s13-loss 1101 字
# （s13-loss 是「怕賠（12 題）」那個 h3，「處理套牢的舊部位」是底下第 4 題）。取 2000，留約 900 字
# （兩三題問答）的餘量；哪天超過，先回頭看錨點是不是還指對，不要直接把數字調大。
# 批 DF：兩個分岔改指得更準——#s5-fiveyear（「記得這幾句」第一條那個 li）、#s13-stuck（「處理套牢的舊部位」那一題的 li）。
# 批 DF-2（裁判後）：分岔分兩種，各只有一條路能過，窗口不再當後備——
#   - 目的地字寫成「X」第一條的（#s5-fiveyear）：X 是那張卡的標題、在錨點前面，窗口量不到，所以只認
#     _first_item_under：錨點元素是 <li>、是它那個清單的第一項，清單緊接在一個標題後面（中間沒有可見字），標題＝X。
#     錨點放到卡前面的段落、或放到第二條，都過不了。
#   - 其他分岔：往後 ANCHOR_WINDOW 字內要有最後一個片段，而且錨點元素本身要對到那一段——
#     錨點元素的可見文字以最後一個片段開頭（li 是那一題本身、p 以粗體題目開頭），或錨點是標題／段落
#     （h1–h6、p）而最後一個片段出現在它自己的字裡。只看窗口時，錨點放在前一題也會過（前一題後面就是這一題）；
#     多這一條，錨點就得是那一題自己。
ANCHOR_WINDOW = 2000


def _anchor_regions(h, aid):
    """回 (錨點所在那一節的可見文字, 錨點元素開頭往後 ANCHOR_WINDOW 字的可見文字)；h 已經拿掉 figure.chart。
    錨點不在任何 section.part 裡（或在圖裡被拿掉了）回 None。"""
    m = re.search(r'(?<![\w-])id="%s"' % re.escape(aid), h)
    if not m:
        return None
    i = h.rfind('<', 0, m.start())
    for s in re.finditer(r'<section class="part" id="[^"]+">.*?</section>', h, flags=re.S):
        if s.start() <= i < s.end():
            return _visible(h[s.start():s.end()]), _visible(h[i:s.end()])[:ANCHOR_WINDOW]
    return None


def _first_item_under(h, aid, title):
    """批 DF：錨點元素是 <li>、是它那個清單（ul／ol）的第一項，清單緊接在一個 h1–h6 後面（中間沒有可見字），
    那個標題的可見文字＝title。h 已經拿掉 figure.chart。"""
    m = re.search(r'(?<![\w-])id="%s"' % re.escape(aid), h)
    if not m:
        return False
    i = h.rfind('<', 0, m.start())
    if not re.match(r'<li\b', h[i:]):
        return False
    lo = max(h.rfind('<ul', 0, i), h.rfind('<ol', 0, i))
    if lo < 0 or '<li' in h[lo:i]:
        return False
    hd = list(re.finditer(r'<h([1-6])\b[^>]*>(.*?)</h\1>', h[max(0, lo - 4000):lo], flags=re.S))
    if not hd:
        return False
    between = h[max(0, lo - 4000) + hd[-1].end():lo]
    return _visible(hd[-1].group(2)).strip() == title and not _visible(between).strip()


def _anchor_element(h, aid):
    """批 DF-2：(錨點元素的標籤名, 錨點元素的可見文字)；h 已經拿掉 figure.chart。
    從 id 所在的開標籤往後數同名標籤的開與關（巢狀的 li、ol 也算對），取到配對的關標籤為止。找不到回 None。"""
    m = re.search(r'(?<![\w-])id="%s"' % re.escape(aid), h)
    if not m:
        return None
    i = h.rfind('<', 0, m.start())
    t = re.match(r'<([a-zA-Z][\w-]*)\b[^>]*>', h[i:])
    if not t:
        return None
    tag = t.group(1).lower()
    depth, pos = 1, i + t.end()
    pat = re.compile(r'<(/?)%s\b[^>]*>' % re.escape(tag), flags=re.I)
    for mm in pat.finditer(h, pos):
        depth += -1 if mm.group(1) else 1
        if depth == 0:
            return tag, _visible(h[pos:mm.start()]).strip()
    return None


def _anchor_is_the_piece(h, aid, piece):
    """批 DF-2：錨點元素本身就是 piece 那一段：可見文字以 piece 開頭，或錨點是標題／段落而 piece 在它自己的字裡。"""
    el = _anchor_element(h, aid)
    if el is None:
        return False
    tag, txt = el
    return txt.startswith(piece) or (re.fullmatch(r'h[1-6]|p', tag) is not None and piece in txt)


def _branch_points_ok(h, ids):
    """圖一每個分岔：錨點有沒有指到目的地字寫的那一段。回缺漏清單。"""
    miss = []
    for cond, dd, _dm, a in PANIC_BRANCHES:
        if a not in ids:
            continue            # 錨點不存在，下面的「錨點不在指南裡」已經會報
        dest = ''.join(dd)
        pieces = re.findall(r'「([^」]+)」', dest) or [dest]
        reg = _anchor_regions(h, a)
        if reg is None:
            miss.append('panic-map 分岔「%s」的錨點 #%s 不在任何一節（section.part）的內文裡' % (cond, a))
            continue
        sec, win = reg
        for p in pieces:
            if p not in sec:
                miss.append('panic-map 分岔「%s」的錨點 #%s 所在的那一節沒有「%s」' % (cond, a, p))
        if pieces[-1] not in sec:
            continue            # 上面已經報「那一節沒有」
        if dest.endswith('」第一條'):
            # 批 DF-2：「X」第一條只認 _first_item_under，窗口不當後備
            if not _first_item_under(h, a, pieces[-1]):
                miss.append('panic-map 分岔「%s」的錨點 #%s 不是「%s」標題下面清單的第一條'
                            % (cond, a, pieces[-1]))
            continue
        if pieces[-1] not in win:
            miss.append('panic-map 分岔「%s」的錨點 #%s 往後 %d 字內沒有「%s」'
                        % (cond, a, ANCHOR_WINDOW, pieces[-1]))
        elif not _anchor_is_the_piece(h, a, pieces[-1]):
            miss.append('panic-map 分岔「%s」的錨點 #%s 本身不是「%s」那一段（可見文字不以它開頭，也不是含它的標題／段落）'
                        % (cond, a, pieces[-1]))
    return miss


def missing_labels(path=GUIDE):
    """缺的字與缺的錨點，一筆一句中文；全部找得到回 []。calc_core 把它接進「引用缺漏」。"""
    raw = open(path, encoding='utf-8').read()
    ids = set(re.findall(r'(?<![\w-])id="([^"]+)"', raw))
    stripped = _strip_figures(raw)
    sc = _scopes(stripped)
    miss = []
    for chart, labels in (('panic-map', panic_labels()), ('first-route', route_labels())):
        for s, where in labels:
            if s not in sc['page']:
                miss.append('%s 圖上的「%s」全書找不到' % (chart, s))
            elif where != 'page' and s not in sc.get(where, ''):
                miss.append('%s 圖上的「%s」不在 %s 裡' % (chart, s, where))
    anchors = ['plan-panic'] + [b[3] for b in PANIC_BRANCHES] + [a for _h, _b, a in PANIC_SUBS if a] + ROUTE_ANCHORS
    for a in anchors:
        if a not in ids:
            miss.append('指路圖用到的錨點 #%s 不在指南裡' % a)
    miss += _branch_points_ok(stripped, ids)
    if 'card' not in sc:
        miss.append('找不到急救卡（h4#plan-panic 所在的 div.data-card）')
    return miss


def compute(path=GUIDE):
    miss = missing_labels(path)
    assert not miss, '指路圖的字或錨點對不上指南：\n  ' + '\n  '.join(miss)
    return {
        'id': 'route-maps',
        'illustrative': True,
        'basis': {'what': '兩張指路圖：圖上每一行字逐字取自指南內文，箭頭上不寫字、SVG 裡不寫節號',
                  'no_new_numbers': True},
        'panic_map': {
            'root': PANIC_ROOT,
            'branches': [{'if': c, 'go': ''.join(dd), 'anchor': a} for c, dd, _dm, a in PANIC_BRANCHES],
            'main': {'if': PANIC_MAIN, 'do': PANIC_THREE,
                     'then': [{'if': hd, 'go': body, 'anchor': a} for hd, body, a in PANIC_SUBS]},
        },
        'first_route': {
            'stations': [{'label': ''.join(dd), 'section_id': sec} for dd, _dm, sec in ROUTE_STATIONS],
            'tail': {'label': ROUTE_TAIL[0], 'section_id': ROUTE_TAIL[1]},
        },
        'labels_checked': len(panic_labels()) + len(route_labels()),
    }


# ---------------------------------------------------------------------------
# 畫圖（仿 v63_g01_plan_flow.py）
def _arrow(E, x1, y1, x2, y2, color):
    """直線箭頭：箭身是 <line>，箭頭是 <polygon>（量測腳本兩者都認得，查得到出不出 viewBox）。"""
    dx, dy = x2 - x1, y2 - y1
    ln = (dx * dx + dy * dy) ** 0.5 or 1.0
    ux, uy = dx / ln, dy / ln
    hl, hw = 5.5, 3.2
    bx, by = x2 - ux * hl, y2 - uy * hl
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.3"/>\n'
            '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
            % (x1, y1, bx, by, color, x2, y2, bx - uy * hw, by + ux * hw, bx + uy * hw, by - ux * hw, color))


def _seg(x1, y1, x2, y2, color):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.3"/>'
            % (x1, y1, x2, y2, color))


def _box(x, y, w, h, color, fill_op=0.10, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    f = 'fill="%s" fill-opacity="%s"' % (color, fill_op) if fill_op else 'fill="none"'
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" %s stroke="%s" stroke-width="1.2"%s/>'
            % (x, y, w, h, f, color, d))


def _lines_in_box(E, x, y, h, lines, anchor='start', pad=8.0, w=None):
    """lines：[(字, 字級, 顏色, 粗細)]；整組在盒子裡上下置中。"""
    lh = [sz * 1.35 for _t, sz, _c, _w in lines]
    total = sum(lh)
    yy = y + (h - total) / 2
    out = []
    for (t, sz, col, wt), l in zip(lines, lh):
        base = yy + l / 2 + sz * 0.36
        tx = x + pad if anchor == 'start' else x + w / 2
        out.append(E.text(tx, base, t, sz, anchor, col, wt))
        yy += l
    return out


def _box_h(lines, pad_v=7.0):
    return sum(sz * 1.35 for _t, sz, _c, _w in lines) + pad_v * 2


def _panic_aria():
    parts = [PANIC_ROOT]
    for cond, dd, _dm, _a in PANIC_BRANCHES:
        parts.append('%s：%s' % (cond, ''.join(dd)))
    subs = '；'.join('%s%s' % (hd, '，'.join(body)) for hd, body, _a in PANIC_SUBS)
    parts.append('%s：%s；%s' % (PANIC_MAIN, PANIC_THREE, subs))
    return '。'.join(parts) + '。'


def chart_panic():
    import essay_charts as E

    def draw(lay):
        mob = lay.mobile
        f, fs = lay.f, lay.fs
        out = []
        if not mob:
            # 桌機：由左到右。根 → 四個條件 → 目的地；主路的「三件事」底下再分兩格。
            pad = 6.0
            rx0, rw = pad, E.textw(PANIC_ROOT, f) + 18
            trunk_x = rx0 + rw + 13
            cx0 = trunk_x + 13
            cw = max(E.textw(s, f) for s in [c for c, *_ in PANIC_BRANCHES] + PANIC_MAIN_D) + 18
            dx0 = cx0 + cw + 22
            dw = lay.W - pad - dx0
            gap = 10.0
            rows = []          # (條件盒 y, h, 目的地盒 y, h)
            y = 8.0
            for cond, dd, _dm, _a in PANIC_BRANCHES:
                ch = _box_h([(cond, f, None, None)])
                dh = _box_h([(s, fs, None, None) for s in dd])
                hh = max(ch, dh)
                rows.append((y + (hh - ch) / 2, ch, y + (hh - dh) / 2, dh))
                y += hh + gap
            mh = _box_h([(s, f, None, None) for s in PANIC_MAIN_D])
            th = _box_h([(s, fs, None, None) for s in PANIC_THREE_LINES])
            hh = max(mh, th)
            rows.append((y + (hh - mh) / 2, mh, y + (hh - th) / 2, th))
            y += hh + gap
            sub_x0 = dx0 + 22
            sub_rows = []
            for head, body, _a in PANIC_SUBS:
                sh = _box_h([(head, fs, None, None)] + [(s, fs, None, None) for s in body])
                sub_rows.append((y, sh))
                y += sh + gap
            H = y - gap + 8
            out.append(E.svg_open(lay, H, _panic_aria()))
            centers = [r[0] + r[1] / 2 for r in rows]
            ry = (centers[0] + centers[-1]) / 2
            rh = _box_h([(PANIC_ROOT, f, None, None)])
            # 根
            out.append(_box(rx0, ry - rh / 2, rw, rh, E.INK, 0.06))
            out += _lines_in_box(E, rx0, ry - rh / 2, rh, [(PANIC_ROOT, f, E.INK, '800')], 'middle', w=rw)
            # 樹幹
            out.append(_seg(rx0 + rw, ry, trunk_x, ry, E.MUTED))
            out.append(_seg(trunk_x, centers[0], trunk_x, centers[-1], E.MUTED))
            for k, (cy_, chh, dy_, dhh) in enumerate(rows):
                c = centers[k]
                main = k == len(rows) - 1
                col = E.TEAL if main else E.AMBER
                out.append(_arrow(E, trunk_x, c, cx0 - 1, c, E.MUTED))
                out.append(_box(cx0, cy_, cw, chh, col, 0.12))
                clines = PANIC_MAIN_D if main else [PANIC_BRANCHES[k][0]]
                out += _lines_in_box(E, cx0, cy_, chh, [(s, f, E.INK, '800') for s in clines])
                out.append(_arrow(E, cx0 + cw + 1, c, dx0 - 1, c, E.MUTED))
                out.append(_box(dx0, dy_, dw, dhh, col, None))
                dlines = PANIC_THREE_LINES if main else PANIC_BRANCHES[k][1]
                out += _lines_in_box(E, dx0, dy_, dhh, [(s, fs, E.INK, '700' if main else None) for s in dlines])
            # 主路再分兩格
            ty0 = rows[-1][2] + rows[-1][3]
            lane = dx0 + 11
            out.append(_seg(lane, ty0, lane, sub_rows[-1][0] + sub_rows[-1][1] / 2, E.TEAL))
            for (head, body, _a), (sy, sh) in zip(PANIC_SUBS, sub_rows):
                out.append(_arrow(E, lane, sy + sh / 2, sub_x0 - 1, sy + sh / 2, E.TEAL))
                out.append(_box(sub_x0, sy, lay.W - pad - sub_x0, sh, E.TEAL, None))
                out += _lines_in_box(E, sub_x0, sy, sh, [(head, fs, E.INK, '800')] + [(s, fs, E.INK, None) for s in body])
        else:
            # 手機：由上到下。根在最上面，左邊一條樹幹；每一個條件底下接它的目的地。
            pad = 6.0
            rw = E.textw(PANIC_ROOT, f) + 18
            rh = _box_h([(PANIC_ROOT, f, None, None)])
            trunk_x = pad + 14
            cx0 = trunk_x + 12
            lane2 = cx0 + 12
            dx0 = lane2 + 12
            lane3 = dx0 + 12
            sx0 = lane3 + 12
            gap_in, gap_out = 6.0, 12.0
            y = 6.0
            items = []   # 依序：('root'|'cond'|'dest'|'three'|'sub', y, h, 資料)
            items.append(('root', y, rh, None))
            y += rh + gap_out
            for k, (cond, _dd, dm, _a) in enumerate(PANIC_BRANCHES + [(PANIC_MAIN, None, PANIC_THREE_LINES, None)]):
                ch = _box_h([(cond, f, None, None)])
                items.append(('cond', y, ch, k))
                y += ch + gap_in
                dh = _box_h([(s, fs, None, None) for s in dm])
                items.append(('dest', y, dh, k))
                y += dh + (gap_out if k < len(PANIC_BRANCHES) else gap_in)
            for j, (head, body, _a) in enumerate(PANIC_SUBS):
                sh = _box_h([(head, fs, None, None)] + [(s, fs, None, None) for s in body])
                items.append(('sub', y, sh, j))
                y += sh + gap_in
            H = y - gap_in + 6
            out.append(E.svg_open(lay, H, _panic_aria()))
            conds = [it for it in items if it[0] == 'cond']
            out.append(_box(pad, 6.0, rw, rh, E.INK, 0.06))
            out += _lines_in_box(E, pad, 6.0, rh, [(PANIC_ROOT, f, E.INK, '800')], 'middle', w=rw)
            out.append(_seg(trunk_x, 6.0 + rh, trunk_x, conds[-1][1] + conds[-1][2] / 2, E.MUTED))
            nb = len(PANIC_BRANCHES)
            for kind, iy, ih, k in items:
                if kind == 'root':
                    continue
                if kind == 'cond':
                    main = k == nb
                    col = E.TEAL if main else E.AMBER
                    txt = PANIC_MAIN if main else PANIC_BRANCHES[k][0]
                    w = E.textw(txt, f) + 18
                    out.append(_arrow(E, trunk_x, iy + ih / 2, cx0 - 1, iy + ih / 2, E.MUTED))
                    out.append(_box(cx0, iy, w, ih, col, 0.12))
                    out += _lines_in_box(E, cx0, iy, ih, [(txt, f, E.INK, '800')])
                    cond_bottom = iy + ih
                elif kind == 'dest':
                    main = k == nb
                    col = E.TEAL if main else E.AMBER
                    lines = PANIC_THREE_LINES if main else PANIC_BRANCHES[k][2]
                    out.append(_seg(lane2, cond_bottom, lane2, iy + ih / 2, E.MUTED))
                    out.append(_arrow(E, lane2, iy + ih / 2, dx0 - 1, iy + ih / 2, E.MUTED))
                    out.append(_box(dx0, iy, lay.W - pad - dx0, ih, col, None))
                    out += _lines_in_box(E, dx0, iy, ih, [(s, fs, E.INK, '700' if main else None) for s in lines])
                    three_bottom = iy + ih
                else:   # sub
                    head, body, _a = PANIC_SUBS[k]
                    if k == 0:
                        last = [it for it in items if it[0] == 'sub'][-1]
                        out.append(_seg(lane3, three_bottom, lane3, last[1] + last[2] / 2, E.TEAL))
                    out.append(_arrow(E, lane3, iy + ih / 2, sx0 - 1, iy + ih / 2, E.TEAL))
                    out.append(_box(sx0, iy, lay.W - pad - sx0, ih, E.TEAL, None))
                    out += _lines_in_box(E, sx0, iy, ih, [(head, fs, E.INK, '800')] + [(s, fs, E.INK, None) for s in body])
        out.append('</svg>')
        return '\n'.join(out)

    return dict(title=PANIC_TITLE, sub='',
                svgs=[draw(E.L('d')), draw(E.L('m'))], extras='', caption=PANIC_CAPTION)


def _route_aria():
    # 手機行拆成兩行的站（股票放幾成／驗算一次）用頓號接，不黏成一串。
    return '；'.join(['、'.join(dm) for _dd, dm, _s in ROUTE_STATIONS] + [ROUTE_TAIL[0]]) + '。'


def chart_route():
    import essay_charts as E

    def draw(lay):
        fs = lay.fs if not lay.mobile else lay.f
        pad = 6.0
        out = []
        if not lay.mobile:
            # 桌機：一列七站，站與站之間一支箭頭；最後一站往下接「每年一次的檢查表」。
            n = len(ROUTE_STATIONS)
            gap = 14.0
            bw = (lay.W - pad * 2 - gap * (n - 1)) / n
            maxl = max(len(dd) for dd, _dm, _s in ROUTE_STATIONS)
            bh = _box_h([('', fs, None, None)] * maxl, 8.0)
            y0 = 8.0
            tail_gap = 18.0
            th = _box_h([(ROUTE_TAIL[0], fs, None, None)])
            tw = E.textw(ROUTE_TAIL[0], fs) + 20
            H = y0 + bh + tail_gap + th + 8
            out.append(E.svg_open(lay, H, _route_aria()))
            xs = [pad + i * (bw + gap) for i in range(n)]
            for i, (dd, _dm, _s) in enumerate(ROUTE_STATIONS):
                out.append(_box(xs[i], y0, bw, bh, E.TEAL, 0.10))
                out += _lines_in_box(E, xs[i], y0, bh, [(s, fs, E.INK, '800') for s in dd], 'middle', w=bw)
                if i < n - 1:
                    out.append(_arrow(E, xs[i] + bw + 2, y0 + bh / 2, xs[i + 1] - 2, y0 + bh / 2, E.TEAL))
            cx = xs[-1] + bw / 2
            tx0 = min(cx - tw / 2, lay.W - pad - tw)
            ty = y0 + bh + tail_gap
            out.append(_arrow(E, cx, y0 + bh + 2, cx, ty - 2, E.MUTED))
            out.append(_box(tx0, ty, tw, th, E.MUTED, None, '4 3'))
            out += _lines_in_box(E, tx0, ty, th, [(ROUTE_TAIL[0], fs, E.INK, None)], 'middle', w=tw)
        else:
            # 手機：直向一欄，七站由上到下，最後接「每年一次的檢查表」。
            bw = max(E.textw(s, fs) for _dd, dm, _s in ROUTE_STATIONS for s in dm) + 28
            x0 = (lay.W - bw) / 2
            gap = 16.0
            boxes = []
            y = 6.0
            for _dd, dm, _s in ROUTE_STATIONS:
                h = _box_h([(s, fs, None, None) for s in dm])
                boxes.append((y, h))
                y += h + gap
            th = _box_h([(ROUTE_TAIL[0], fs, None, None)])
            H = y + th + 6
            out.append(E.svg_open(lay, H, _route_aria()))
            cx = lay.W / 2
            for i, ((_dd, dm, _s), (by, bh)) in enumerate(zip(ROUTE_STATIONS, boxes)):
                out.append(_box(x0, by, bw, bh, E.TEAL, 0.10))
                out += _lines_in_box(E, x0, by, bh, [(s, fs, E.INK, '800') for s in dm], 'middle', w=bw)
                nxt = boxes[i + 1][0] if i + 1 < len(boxes) else y
                out.append(_arrow(E, cx, by + bh + 2, cx, nxt - 2, E.TEAL if i + 1 < len(boxes) else E.MUTED))
            out.append(_box(x0, y, bw, th, E.MUTED, None, '4 3'))
            out += _lines_in_box(E, x0, y, th, [(ROUTE_TAIL[0], fs, E.INK, None)], 'middle', w=bw)
        out.append('</svg>')
        return '\n'.join(out)

    return dict(title=ROUTE_TITLE, sub='',
                svgs=[draw(E.L('d')), draw(E.L('m'))], extras='', caption=ROUTE_CAPTION)


if __name__ == '__main__':
    import json
    print(json.dumps(compute(), ensure_ascii=False, indent=1))
