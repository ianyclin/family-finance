#!/usr/bin/env python3
"""投資專篇／指南的圖表 v2.0：一套設計系統，九張圖同一個框架。

設計規則（對齊作者提供的 J.P. Morgan、Schwab、Vanguard 風格參考圖）：
  - 每張圖出兩個 SVG：桌面版 viewBox 寬 640、手機版寬 360；CSS 依視窗寬度只顯示一個，
    所以字級在任何裝置上都是 11–13px，不會被縮小到看不見。
  - 標題、口徑副標、圖例、註解、圖說全部是 HTML，放在 SVG 外面。
  - 只有水平的淡色格線；零線用墨色；沒有直向軸線、沒有外框。
  - 資料標籤：長條上方粗體、圓點下方一般字重；標籤會避開鄰居。
  - 顏色：主色 teal（股票／主角）、次色 muted 灰（債券／對照）、amber（第三組）、accent 紅（下跌）。
    全部用 CSS 變數，深色模式自動對應。
  - 手機版減少標籤密度（隔一個標、只標極端值），不縮字。

對照（作者原圖 → 圖 id）：三圓 three-circles；Chloe 四人 four-people；$1M 里程碑 milestones；
SPIVA 圓餅 spiva；年內跌幅 intra-year；區間浮動長條 ranges；Schwab 五人 five-people；
幸運兒／倒楣鬼 dca-high-low；錯過最好的 N 天 missing-days；手冊沿用 smooth-vs-jagged、buckets。

用法：
  python3 tools/essay_charts.py            # 重畫專篇 essay/sections/*.html 的 11 張
  python3 tools/essay_charts.py --guide    # 只換指南 guide/index.html 裡的圖（保留指南自己的 figcaption）
                                           # 只在指南、專篇沒有的：human-capital、control-map、
                                           # taiex-recovery、asset-rotation（後兩張讀 lite/calc-results.json）
  python3 tools/essay_charts.py --all      # 兩者都做
"""
import csv
import json
import math
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "essay" / "sections"
DATA = ROOT / "research" / "data"
GUIDE = ROOT / "guide" / "index.html"
CALC = ROOT / "lite" / "calc-results.json"

# v7 批 7：指南模式不再把「官方原圖（英文）：…」那條出處聲明印在 figure 裡面。
# 它是出處、不是圖說，留在圖下會佔掉手機上「看得到的小字」的額度（每節 ≤350 字），
# 所以指南改成放在 figure 後面自己的 <details class="more">（可見的三張）或緊接著的 <p class="note">
# （本來就在摺疊裡的三張）。專篇 essay/sections 沒有那一層，維持印在 figure 裡。
GUIDE_MODE = False


def calc():
    """指南新增的兩張資料圖，數字一律取自 tools/calc_core.py 產生的 lite/calc-results.json，
    不在這支腳本裡重算，確保圖上與正文同一個來源。改資料要先跑 calc_core.py。"""
    return json.loads(CALC.read_text(encoding="utf-8"))

TEAL, MUTED, AMBER, ACCENT, INK, LINE, SURFACE = ("var(--teal)", "var(--muted)", "var(--amber)",
                                                  "var(--accent)", "var(--ink)", "var(--line)", "var(--surface)")
BLUE = "var(--blue)"   # 現金長條：--line 太淡看不見，改用已定義的藍


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------- 版面：桌面 d／手機 m ----------
class L:
    def __init__(self, kind):
        self.kind = kind
        self.mobile = kind == "m"
        self.W = 360 if self.mobile else 640
        self.f = 11 if self.mobile else 12.5      # 一般字（軸標籤）
        self.fs = 10 if self.mobile else 11       # 小字
        self.fl = 10.5 if self.mobile else 12     # 資料標籤
        self.left = 46 if self.mobile else 52
        self.right = self.W - (12 if self.mobile else 18)
        self.top = 14 if self.mobile else 18
        self.line = 2.2 if self.mobile else 2.6


def svg_open(lay, h, title):
    return ('<svg class="%s" viewBox="0 0 %d %d" role="img" aria-label="%s" font-family="var(--sans)">'
            % (lay.kind, lay.W, h, esc(title)))


def text(x, y, s, size, anchor="start", fill=INK, weight=None):
    w = ' font-weight="%s"' % weight if weight else ""
    return '<text x="%.1f" y="%.1f" font-size="%s" text-anchor="%s" fill="%s"%s>%s</text>' % (x, y, size, anchor, fill, w, esc(s))


def textw(s, fs):
    """粗估字串寬度（和 tools/v7_g08_long_run.py 的 _textw 同一套）：中日韓字元算一個字寬，其餘 0.56。
    用來判斷一個標籤放不放得進某一格；放不下就不標，不上下錯開成兩排。"""
    w = 0.0
    for ch in s:
        w += 1.0 if ord(ch) > 0x2E7F else 0.56
    return w * fs


def poly(points, stroke, width=2.4, dash=None, opacity=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    o = ' stroke-opacity="%s"' % opacity if opacity else ""
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s"%s%s stroke-linejoin="round" stroke-linecap="round"/>'
            % (" ".join("%.1f,%.1f" % p for p in points), stroke, width, d, o))


def rect(x, y, w, h, fill, rx=2.5, opacity=None):
    o = ' fill-opacity="%s"' % opacity if opacity else ""
    return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" fill="%s"%s/>' % (x, y, w, h, rx, fill, o)


def dot(x, y, fill, r=4):
    return '<circle cx="%.1f" cy="%.1f" r="%s" fill="%s" stroke="%s" stroke-width="1.5"/>' % (x, y, r, fill, SURFACE)


def hline(x1, x2, y, color=LINE, width=1, dash="3 4"):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    return '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s"%s/>' % (x1, y, x2, y, color, width, d)


def grid(lay, py, values, fmt, x1=None, x2=None, zero=INK, zero_dy=0.0):
    """水平格線＋左側刻度；0 用墨色實線。

    zero_dy（v7 批 W）：只把「0」那個刻度的字往上移幾個單位（負值往上）。原點上的 y 軸「0」和
    x 軸第一個標籤會擦到（主線在 1024 與 375 實量 getBBox），x 軸標籤挪不動的圖用這個。
    """
    out = []
    x1 = lay.left if x1 is None else x1
    x2 = lay.right if x2 is None else x2
    for v in values:
        if v == 0:
            out.append(hline(x1, x2, py(v), zero, 1.3, None))
        else:
            out.append(hline(x1, x2, py(v)))
        dy = zero_dy if v == 0 else 0.0
        out.append(text(x1 - 6, py(v) + lay.fs * 0.36 + dy, fmt(v), lay.fs, "end", MUTED))
    return out


def legend(items):
    """items 是 (顏色, 文字) 或 (顏色, 文字, 透明度)；給了透明度，色塊就和線一樣淡。"""
    out = []
    for it in items:
        c, t = it[0], it[1]
        op = ';opacity:%s' % it[2] if len(it) > 2 else ''
        out.append('<li><span class="swatch" style="background:%s%s"></span>%s</li>' % (c, op, esc(t)))
    return '<ul class="legend">' + "".join(out) + "</ul>"


def note(s, raw=False):
    """raw=True 的字串已經是 HTML（例如夾了 <a class="term">），不再跳脫。"""
    return '<p class="note">%s</p>' % (s if raw else esc(s))


def usd_tick(v, first):
    """美元金額的 y 軸刻度：只有第一格（最低的那一格）帶幣別，其餘只寫「萬」。"""
    if not v:
        return "0"
    return ("%d 萬美元" if v == first else "%d 萬") % (v / 10000)


GTR = "https://am.jpmorgan.com/us/en/asset-management/adv/insights/retirement-insights/guide-to-retirement/"
GTM = "https://am.jpmorgan.com/us/en/asset-management/adv/insights/market-insights/guide-to-the-markets/"
# 有官方原圖的圖：出處說明、連結。原圖有版權，本文不轉載（2026-09-16 起不再嵌入圖檔），
# 只寫出處並連到原始頁面；正文引用的數字以本文為準。
ORIGINALS = {
    "ranges": ("J.P. Morgan Asset Management，Guide to Retirement 2026，第 42 頁「Range of stock, bond and blended total returns」。本文的圖是同一頁的數字重畫。", GTR),
    "four-people": ("J.P. Morgan Asset Management，Guide to Retirement 2026，第 15 頁「Benefit of saving and investing early」。2026 年版的例子是每月 250 美元、7.25%；本文的四個人是每月 5,000 元、6% 的台幣版，形狀相同、數字不同。", GTR),
    "intra-year": ("J.P. Morgan Asset Management，Guide to the Markets U.S.（2026 年 6 月 30 日資料），第 17 頁「S&P 500 intra-year declines vs. calendar year returns」。這是美國版；本文的圖是台股同一種畫法。", GTM),
    "milestones": ("Four Pillar Freedom，「Money Lessons They Don't Teach You in School」一文「The Concept of Compound Interest」小節裡標題為「Accumulating $1 Million」的圖（每年 1 萬美元、7%）。本文改成『年儲蓄的倍數』畫，所以每桶的年數與原圖相同；作者自己用原圖算法重畫過一版。", "https://fourpillarfreedom.com/money-lessons-they-dont-teach-you-in-school-2/"),
    "missing-days": ("J.P. Morgan Asset Management，Guide to Retirement 2026，第 41 頁「Impact of being out of the market」。", GTR),
    "five-people": ("Charles Schwab，「Does Market Timing Work?」，2005–2024 年的五個人。", "https://www.schwab.com/learn/story/does-market-timing-work"),
}


# 只有這三張是把原圖上的數字重畫一次；four-people、milestones 是台幣版、intra-year 是台股自算，
# 圖上的數字本來就不是原圖的數字，所以出處那句要分成兩種寫法。
REDRAWN = {"ranges", "missing-days", "five-people"}


def original_block(cid):
    if cid not in ORIGINALS or GUIDE_MODE:
        return ""
    credit, url = ORIGINALS[cid]
    claim = ("本文只重畫數字、不轉載原圖" if cid in REDRAWN
             else "本文的數字是自己算的，不是原圖上的數字，也不轉載原圖")
    return ('<p class="note">官方原圖（英文）：%s%s，原圖請看 '
            '<a href="%s" target="_blank" rel="noopener">原始頁面</a>；圖片版權屬原機構，本文引用的數字以正文為準。</p>\n'
            % (esc(credit), claim, url))


def figure(cid, title, sub, svgs, caption, extras="", caption_html=False, illustration_only=False, after=""):
    """caption_html=True：caption 已經是 HTML（指南模式保留 figcaption 裡的節號連結），不再跳脫。

    illustration_only=True：純示意圖（圖上沒有任何數字，圖說只會把緊鄰的內文重講一次）。
    這種圖不印 figcaption，也不該帶 p.note；螢幕閱讀器讀的是 SVG 的 aria-label。
    只有圖的腳本在 chart() 回傳裡明寫這個旗標才算數，不是每張圖都可以省。

    after（批 AO）：已經是 HTML，放在 figcaption 後面、出處聲明前面。給「圖說之後再補一句小字」
    用的；--guide 會跟著寫回指南，所以它和腳本這一份不會各走各的。
    """
    cap = "" if illustration_only else (
        "<figcaption>%s</figcaption>\n" % (caption if caption_html else esc(caption)))
    return ('<figure class="chart" data-chart="%s">\n<div class="chart-head"><span class="chart-title">%s</span><span class="chart-sub">%s</span></div>\n'
            '<div class="chart-body">\n%s\n</div>\n%s%s%s%s</figure>'
            % (cid, esc(title), esc(sub), "\n".join(svgs), extras, cap, after, original_block(cid)))


# ======================================================================
# §1 三圓
def three_circles():
    def draw(lay):
        r = 78 if lay.mobile else 100
        h = int(r * 3.0) + 16
        cx0 = lay.W / 2
        cy0 = r * 1.55 + 8
        dx = r * 0.62
        pos = {"top": (cx0, cy0 - r * 0.55), "left": (cx0 - dx, cy0 + r * 0.45), "right": (cx0 + dx, cy0 + r * 0.45)}
        out = [svg_open(lay, h, "示意：時間短、風險低、報酬高，三個一起要就得先問錢從哪裡來")]
        for k, fill in (("top", AMBER), ("left", TEAL), ("right", ACCENT)):
            x, y = pos[k]
            out.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s" fill-opacity="0.22" stroke="%s" stroke-width="1.6"/>' % (x, y, r, fill, fill))
        big = 13 if lay.mobile else 16
        small = lay.f
        out.append(text(pos["top"][0], pos["top"][1] - r * 0.45, "時間短", big, "middle", weight="800"))
        out.append(text(pos["left"][0] - r * 0.4, pos["left"][1] + r * 0.45, "風險低", big, "middle", weight="800"))
        out.append(text(pos["right"][0] + r * 0.4, pos["right"][1] + r * 0.45, "報酬高", big, "middle", weight="800"))
        out.append(text(cx0 - r * 0.58, cy0 - r * 0.22, "低報酬", small, "middle", MUTED, "700"))
        out.append(text(cx0 + r * 0.58, cy0 - r * 0.22, "高風險", small, "middle", MUTED, "700"))
        out.append(text(cx0, cy0 + r * 1.0, "長時間", small, "middle", MUTED, "700"))
        out.append(text(cx0, cy0 + r * 0.22, "先問錢從哪裡來", small, "middle", INK, "800"))
        out.append("</svg>")
        return "\n".join(out)
    return dict(title="「又快、又穩、又賺」不存在", sub="示意圖，不是資料",
                svgs=[draw(L("d")), draw(L("m"))], extras="",
                # 批 AJ（裁判 N-1／N-2）：圖說原本和下一行紅框「三樣都答應你的，一次問完這三題」
                # 近乎逐字重複，那一句拿掉；安全但書搬回圖說（它不是口徑，不該預設看不到）。
                caption="三個圓是時間短、風險低、報酬高，最多只能同時要兩個。當然，等很久也不保證換得到高報酬，更不保證不會虧。")


# ======================================================================
# §2 四個人
def four_people():
    def path(start, stop_contrib, r):
        m = r / 12
        v = 0.0
        pts = []
        for month in range(0, 40 * 12 + 1):
            age = 25 + month / 12
            if month:
                v *= 1 + m
                if start <= age - 1 / 12 + 1e-9 and age - 1 / 12 < stop_contrib - 1e-9:
                    v += 5000
            if age >= start:
                pts.append((age, v))
        return pts
    series = [
        ("25 到 65 歲，投 40 年", path(25, 65, 0.06), TEAL, 996, 240),
        ("35 歲才開始，投 30 年", path(35, 65, 0.06), ACCENT, 502, 180),
        ("25 到 35 歲投 10 年，之後不再投入", path(25, 35, 0.06), AMBER, 493, 60),
        ("25 到 65 歲都放定存 1.7%", path(25, 65, 0.017), MUTED, 343, 240),
    ]
    for _, pts, _, end, _ in series:
        assert abs(pts[-1][1] / 1e4 - end) < 6

    def draw(lay):
        h = 250 if lay.mobile else 330
        left, top, bottom = lay.left, lay.top, h - 30
        right = lay.right - (52 if lay.mobile else 64)
        ymax = 1050e4
        def px(a): return left + (right - left) * (a - 25) / 40
        def py(v): return bottom - (bottom - top) * v / ymax
        out = [svg_open(lay, h, "四個人 25 到 65 歲的資產曲線")]
        out += grid(lay, py, (0, 250e4, 500e4, 750e4, 1000e4), lambda v: ("%d 萬" % (v / 1e4)) if v else "0", x2=right)
        for a in (25, 35, 45, 55, 65):
            out.append(text(px(a), bottom + lay.f + 6, "%d 歲" % a, lay.f, "middle", MUTED))
        # 端點標籤：避免重疊（502 與 493 太近）
        ends = sorted([(py(s[1][-1][1]), s) for s in series], key=lambda t: t[0])
        placed = []
        for y, s in ends:
            yy = y
            for p in placed:
                if abs(yy - p) < lay.fl + 3:
                    yy = p + lay.fl + 3
            placed.append(yy)
            s_label = "%d 萬" % s[3]
            out.append(text(right + 8, yy + lay.fl * 0.36, s_label, lay.fl, "start", s[2], "800"))
        for label, pts, color, end, _ in series:
            out.append(poly([(px(a), py(v)) for a, v in pts], color, lay.line))
            out.append(dot(px(65), py(pts[-1][1]), color))
        out.append("</svg>")
        return "\n".join(out)
    lg = legend([(c, "%s：投入 %d 萬，65 歲約 %d 萬" % (l, put, e)) for l, _, c, e, put in series])
    return dict(title="四個人，每月 5,000 元，到 65 歲", sub="一年長 6%，定存 1.7%；固定報酬的算術，不是預測",
                svgs=[draw(L("d")), draw(L("m"))], extras=lg,
                caption="只投十年就停的那條，最後幾乎追上投了三十年的那條。差別不是他會挑，是他的錢多待了十年。")


# ======================================================================
# §2 里程碑
def milestones():
    gaps = [7.84, 5.10, 3.78, 3.01, 2.50, 2.14, 1.87, 1.66, 1.49, 1.35]
    share = [22, 49, 62, 70, 75, 79, 81, 83, 85, 86]
    yrs, t = [], 0
    for g in gaps:
        t += g
        yrs.append(t)
    T = yrs[-1]
    # 批 AN：縱軸的單位從「萬」改成「一年儲蓄的倍數」，一桶＝十倍。
    # 每年年底投入 1 份年儲蓄、年複利 7%：V(t) = (1.07^t − 1) / 0.07，整數年時等於逐年投入的精確值；
    # 這是舊的 6 萬版除以 6，所以 7.84／5.10／…／1.35 年一個字都沒變。
    TOP = 640 / 6      # 版面最上緣對應幾倍（＝舊版的 640 萬 ÷ 每年 6 萬），格線位置照舊
    total, contrib = [], []
    for m in range(0, int(T * 12) + 2):
        t = m / 12
        if t >= T:
            break
        total.append((t, (1.07 ** t - 1) / 0.07))
        contrib.append((t, t))
    # 批 AP-2（作者追加）：以月為步長取樣，最後一個點落在 T 之前不到一個月（T=30.74，最後一點
    # 30.667），多邊形再用 (px(T), py(0)) 收底，右緣就變成一小段斜線，和第 10 桶那條 px(T) 的
    # 虛線對不上。這裡把精確的終點補進兩條序列（total 的 f(T)=(1.07**T−1)/0.07＝100.04 倍，
    # contrib 的 f(T)=T），曲線和兩塊底色都用同一組點，右緣就正好落在 px(T)。
    total.append((T, (1.07 ** T - 1) / 0.07))
    contrib.append((T, T))

    def draw(lay):
        # 批 AO：圖下只留「花幾年」一排（「報酬占」移到圖下的小表），所以下方留白從 66／84
        # 收成 24／28；top 和 bottom 的像素位置與批 AN 完全一樣，每一桶的位置一格都沒動。
        h = 258 if lay.mobile else 304
        left, top = lay.left, lay.top + 10
        # 批 AP-3：右側留白 36／44 → 14／20，圖畫得更滿；第 10 桶的年數仍靠右對齊在 px(T)-2。
        right = lay.right - (14 if lay.mobile else 20)
        bottom = h - (24 if lay.mobile else 28)
        def px(y): return left + (right - left) * y / T
        def py(v): return bottom - (bottom - top) * v / TOP
        out = [svg_open(lay, h, "十桶金：每一桶是一年儲蓄的十倍，第 1 桶 10 倍、第 10 桶 100 倍，前面慢、後面快")]
        # 「0」往上移 6：正下方的「花幾年」是左欄的列名，跟著右邊那排年數對齊，挪不動
        out += grid(lay, py, (0, 20, 40, 60, 80, 100), lambda v: ("%d 倍" % v) if v else "0", x2=right, zero_dy=-6)
        # 批 AS（作者拍板）：原本「長出來的報酬」畫的是整塊 total 多邊形，再把 contrib 疊上去，
        # 下半塊其實是兩色相混，圖例卻是兩個實心色塊，顏色對不上。改成兩塊不重疊：下面那塊還是
        # contrib（自己存進去的），上面那塊只畫 contrib 曲線和 total 曲線之間的帶狀（長出來的報酬）。
        area_contrib = [(px(0), py(0))] + [(px(y), py(v)) for y, v in contrib] + [(px(T), py(0))]
        area_gain = ([(px(y), py(v)) for y, v in contrib]
                     + [(px(y), py(v)) for y, v in reversed(total)])
        out.append('<polygon points="%s" fill="%s" fill-opacity="0.5"/>' % (" ".join("%.1f,%.1f" % p for p in area_contrib), MUTED))
        out.append('<polygon points="%s" fill="%s" fill-opacity="0.5"/>' % (" ".join("%.1f,%.1f" % p for p in area_gain), TEAL))
        out.append(poly([(px(y), py(v)) for y, v in total], TEAL, lay.line))
        show = {0, 1, 2, 4, 9} if lay.mobile else {0, 1, 2, 3, 4, 5, 9}
        # 批 AP-2（作者追加）：第 10 桶的年數靠右對齊到最右那條虛線，允許往左長到第 9、8 桶
        # 上方（那幾桶本來就窄到不標）。先算出它的左緣，中間各桶碰到就不標。
        last_lab = "%.1f 年" % gaps[-1]
        last_left = px(T) - 2 - textw(last_lab, lay.fs)
        prev = 0
        for i, (y, g) in enumerate(zip(yrs, gaps)):
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%d" stroke="%s" stroke-width="1" stroke-dasharray="3 3"/>' % (px(y), py(10 * (i + 1)), px(y), bottom, INK))
            if i in show:
                # 批 AO（作者拍板的橋接版）：頭尾兩桶把舊的倍數寫在括號裡，中間八桶只寫「第 N 桶」。
                # 第 1 桶的括號往左長，手機上會壓到縱軸，放不下就只寫「第 1 桶」；第 10 桶的括號一定留。
                lab_b = "第 %d 桶" % (i + 1)
                if i == 0 and px(y) - 4 - textw(lab_b + "（10 倍）", lay.fl) >= left:
                    lab_b += "（10 倍）"
                elif i == 9:
                    lab_b += "（100 倍）"
                out.append(text(px(y) - 4, py(10 * (i + 1)) - 6, lab_b, lay.fl, "end", INK, "700"))
            # 批 AO：「花幾年」只標放得下的格子（字寬＋6 的餘裕還塞得進這一格才標），
            # 放不下就不標，不再上下錯開兩排。後面幾桶的年數看圖下的小表。
            # 批 AP-2（作者追加）：第 1 桶與第 10 桶兩版一律要標，不看寬度；第 10 桶靠右對齊
            # 到最右那條虛線。中間各桶除了放得下，還不能碰到第 10 桶那個標籤框。
            lab = "%.1f 年" % g
            if i == len(gaps) - 1:
                out.append(text(px(T) - 2, bottom + 16, lab, lay.fs, "end", MUTED))
            elif i == 0 or (px(y) - px(prev) >= textw(lab, lay.fs) + 6
                            and px((prev + y) / 2) + textw(lab, lay.fs) / 2 <= last_left):
                out.append(text(px((prev + y) / 2), bottom + 16, lab, lay.fs, "middle", MUTED))
            prev = y
        out.append(text(left - 6, bottom + 16, "花幾年", lay.fs, "end", MUTED))
        out.append("</svg>")
        return "\n".join(out)
    lg = legend([(MUTED, "自己存進去的", 0.5), (TEAL, "長出來的報酬", 0.5)])
    # 批 AP-3：「想深入」（作者定稿那兩段）從 figure 裡搬到指南本體，接在 </figure> 之後那段
    # 主線「這張圖要說的其實是兩件事…」後面，所以這裡不再產生 more，figure 的 after 也空著。
    # 批 AO：圖下兩排片段會被視窗壓扁，改成一張可以左右滑的小表；數字由 gaps／share 產生，
    # 年數四捨五入到小數點後一位（和 SVG 上那一排一致，完整的兩位數字在下面那張 60 萬版的表）。
    tbl = ('<div class="table-wrap"><table class="compact tight-mobile sticky-first">'
           '<thead><tr><th>第幾桶</th>%s</tr></thead><tbody>'
           '<tr><td>花幾年</td>%s</tr><tr><td>報酬占</td>%s</tr>'
           '</tbody></table></div>'
           % ("".join("<th>%d</th>" % (i + 1) for i in range(len(gaps))),
              "".join("<td>%.1f</td>" % g for g in gaps),
              "".join("<td>%d%%</td>" % s for s in share)))
    # 批 AH（G3）：固定報酬試算的圖一律寫「固定報酬的算術，不是預測」。
    # 批 AO 例外：這張圖用圖說裡那句括號附註（「7% 是為了畫圖簡化的，真實的路一定會上下晃」）
    # 講同一件事。批 AP-3：原本圖下那條 p.note（「每年年底投入同一筆錢…」）和 chart-sub 說的是
    # 同一件事，整段刪掉只留 chart-sub；圖說後面那行 7% 的 p.note 也拿掉，附註併進圖說的括號裡。
    # 所以整張圖現在是：圖 → 圖例 → 表 → figcaption →（出處聲明，指南模式印在 figure 外面）。
    return dict(title="十桶金：每一桶是一年儲蓄的十倍", sub="每年投一樣的錢、一年長 7%：第一桶 7.8 年，第十桶 1.4 年",
                svgs=[draw(L("d")), draw(L("m"))], extras=lg + tbl,
                caption='資產到一年儲蓄的 100 倍，不用 100 年，大約 31 年。前面三分之二的時間只走完四桶，到第四桶時，帳戶裡一半是你存的、一半是長出來的；後面三分之一的時間走完剩下六桶，一桶比一桶快，也越來越不靠你存。目標沒有那麼遙不可及，也不是一路平地（7% 是為了畫圖簡化的，真實的路一定會上下晃）。')


# ======================================================================
# §2 人力資本與財務資本（示意，只給指南）
def human_capital():
    def draw(lay):
        h = 230 if lay.mobile else 290
        left, top = lay.left, lay.top + 8
        right = lay.right - (10 if lay.mobile else 16)
        bottom = h - 30
        def px(a): return left + (right - left) * (a - 25) / 60
        def py(v): return bottom - (bottom - top) * v
        # 人力資本：25 歲最高，隨年齡下降，65 歲歸零；財務資本：從 0 慢慢上升，越後面越快
        hc = [(a, max(0.0, (65 - a) / 40) ** 1.15) for a in range(25, 86)]
        fc = [(a, min(1.0, 0.95 * ((a - 25) / 40) ** 1.8)) for a in range(25, 66)] + [(a, 0.95) for a in range(66, 86)]
        out = [svg_open(lay, h, "示意：人力資本隨年齡下降，財務資本靠持續投入上升")]
        out.append(hline(left, right, py(0), INK, 1.3, None))
        for a in (25, 35, 45, 55, 65, 75, 85):
            out.append(text(px(a), bottom + lay.f + 5, "%d 歲" % a, lay.f, "middle", MUTED))
        out.append(poly([(px(a), py(v)) for a, v in hc], AMBER, lay.line))
        out.append(poly([(px(a), py(v)) for a, v in fc], TEAL, lay.line))
        # 交叉點
        cross = min(range(25, 66), key=lambda a: abs(hc[a - 25][1] - fc[a - 25][1]))
        out.append(dot(px(cross), py(fc[cross - 25][1]), INK, 4.5))
        out.append(text(px(cross) + 6, py(fc[cross - 25][1]) - 18, "交叉：財務資本可以接手", lay.fl, "start" if lay.mobile else "middle", INK, "800"))
        out.append(text(px(27), py(hc[2][1]) - 10, "人力資本（還能賺的薪水）", lay.fl, "start", AMBER, "800"))
        out.append(text(px(84), py(0.95) - 12, "財務資本", lay.fl, "end", TEAL, "800"))
        out.append("</svg>")
        return "\n".join(out)
    lg = legend([(AMBER, "人力資本：未來還能賺的薪水，隨年齡變小"), (TEAL, "財務資本：靠持續投入，越後面長越快")])
    # v7 第 20 版 I：chart-sub 的「越早換，交叉越早」和 figcaption 逐字重複，收成「示意圖」；
    # p.note 開頭的「示意圖，不是資料：」和 chart-sub 講同一件事，拿掉。
    nt = note("兩條線的高度和交叉的年齡因人而異；人力資本那條線也可能因為生病、失能、被裁提早歸零。原理出自 Ibbotson、Milevsky、Chen、Zhu 2007。")
    return dict(title="兩條線：你在把哪一種資本換成哪一種", sub="示意圖",
                svgs=[draw(L("d")), draw(L("m"))], extras=lg + nt,
                caption="年輕時最大的資產是還能賺的薪水，它每年都在變小，也可能提早消失；投資做的事，是持續把它換成會自己工作的財務資本。越早換，交叉點越早。交叉不等於可以退休：能不能停下來，要看財務資本長出來的錢夠不夠支應生活費。")

# ======================================================================
# §3 SPIVA
def spiva():
    data = [("10 年", 85.59), ("15 年", 89.93), ("20 年", 92.89)]

    def draw(lay):
        h = 170 if lay.mobile else 210
        r = 46 if lay.mobile else 60
        out = [svg_open(lay, h, "美國大型股主動基金輸給 S&P 500 的比例，截至 2025 年底")]
        for i, (label, lose) in enumerate(data):
            cx = lay.W * (i + 0.5) / 3
            cy = h / 2 + 8
            a = 2 * math.pi * lose / 100
            x1, y1 = cx, cy - r
            x2, y2 = cx + r * math.sin(a), cy - r * math.cos(a)
            out.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s"/>' % (cx, cy, r, TEAL))
            out.append('<path d="M%.1f,%.1f L%.1f,%.1f A%d,%d 0 1,1 %.1f,%.1f Z" fill="%s"/>' % (cx, cy, x1, y1, r, r, x2, y2, ACCENT))
            out.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s"/>' % (cx, cy, r * 0.6, SURFACE))
            out.append(text(cx, cy + lay.fl * 0.4, "%.1f%%" % lose, lay.fl + 1, "middle", INK, "800"))
            out.append(text(cx, cy - r - 8, label, lay.f, "middle", INK, "700"))
        out.append("</svg>")
        return "\n".join(out)
    lg = legend([(ACCENT, "輸給整個市場的平均"), (TEAL, "贏過的")])
    return dict(title="輸給大盤的比例", sub="扣掉費用之後；中途收掉的基金算輸",
                svgs=[draw(L("d")), draw(L("m"))], extras=lg,
                caption="10、15、20 年三個長度，輸的比例都在八成五以上。所以呢：想靠挑基金贏，要先從不到一成五的贏家裡挑中一檔，而且要在二十年前就挑中。")


# ======================================================================
# §5 台股年內最大跌幅 vs 全年報酬
def intra_year():
    rows = list(csv.DictReader(open(DATA / "algo_b_yearly.csv", encoding="utf-8")))
    ys = [(int(r["year"]), float(r["year_return_pct"]), -float(r["max_drawdown_pct"])) for r in rows]

    def draw(lay):
        h = 270 if lay.mobile else 340
        left, top, right = lay.left, lay.top + 6, lay.right
        bottom = h - 26
        vmax, vmin = 90, -62
        def py(v): return top + (bottom - top) * (vmax - v) / (vmax - vmin)
        n = len(ys)
        slot = (right - left) / n
        bw = slot * 0.64
        out = [svg_open(lay, h, "台灣含息指數 2003 到 2025 年：每年的全年報酬（長條）與年內最大跌幅（圓點）")]
        out += grid(lay, py, (-60, -40, -20, 0, 20, 40, 60, 80), lambda v: "%d%%" % v)
        last_dd_label_y = {}
        for i, (yr, ret, dd) in enumerate(ys):
            x = left + i * slot + (slot - bw) / 2
            cx = x + bw / 2
            y0, y1 = py(max(ret, 0)), py(min(ret, 0))
            out.append(rect(x, y0, bw, max(1.5, y1 - y0), MUTED))
            show_bar = (not lay.mobile) or abs(ret) >= 25
            if show_bar:
                out.append(text(cx, (y0 - 4) if ret >= 0 else (y1 + lay.fl), "%d" % round(ret), lay.fl - (1 if lay.mobile else 0), "middle", INK, "700"))
            out.append(dot(cx, py(dd), ACCENT, 3.2 if lay.mobile else 4))
            show_dd = (not lay.mobile) or dd <= -20
            if show_dd:
                ly = py(dd) + lay.fl + 3
                # 和前一個標籤太近就往下錯開
                if i - 1 in last_dd_label_y and abs(last_dd_label_y[i - 1] - ly) < lay.fl + 1 and not lay.mobile:
                    ly = last_dd_label_y[i - 1] + lay.fl + 1
                # 別壓到負的長條標籤
                if ret < 0 and abs(ly - (y1 + lay.fl)) < lay.fl:
                    ly = y1 + lay.fl * 2 + 2
                last_dd_label_y[i] = ly
                out.append(text(cx, ly, "%d" % round(dd), lay.fl - 1, "middle", ACCENT))
            if yr % 5 == 0 or yr == 2003:
                out.append(text(cx, bottom + lay.f + 4, "'%02d" % (yr % 100), lay.f, "middle", MUTED))
        out.append("</svg>")
        return "\n".join(out)
    lg = legend([(MUTED, "全年含息報酬"), (ACCENT, "年內從高點最多跌掉")])
    # 批 AH（8-4）：圖外只留一句手機版提示。
    # 批 AJ（裁判 S-7）：AH 把「平均年內最多跌 17.73%／23 年裡 18 年全年為正」和資料來源句
    # 直接刪掉，沒有照 spec G5 在圖內新開摺疊；這裡補開一個，兩個數字與來源句放回去。
    nt = note("手機版只標較大的數字。")
    more = ('<details class="more"><summary>想深入：這張圖的資料</summary>'
            '<p class="note">資料是證交所發行量加權股價報酬指數，逐日收盤自算。'
            '平均年內最多跌 17.73%；23 年裡 18 年全年為正。</p></details>')
    return dict(title="台股每一年：年底的報酬，和年中曾經跌掉多少", sub="2003 到 2025 年，含息，%",
                svgs=[draw(L("d")), draw(L("m"))], extras=lg + nt + more,
                caption="中途跌一成很平常，也不等於資產壞掉：這 23 年裡，中途跌過一成以上的有 18 年，年底收正的也有 18 年。")


# ======================================================================
# §5 區間浮動長條
def ranges():
    data = [("連續 1 年", (-37, 52), (-13, 33), (-16, 29), (0, 14)), ("連續 5 年", (-2, 29), (-2, 18), (2, 19), (0, 11)),
            ("連續 10 年", (-1, 20), (1, 14), (2, 16), (0, 9)), ("連續 20 年", (6, 18), (1, 11), (5, 14), (1, 8))]
    tones = (AMBER, MUTED, TEAL, BLUE)

    def draw(lay):
        rows_n = 2 if lay.mobile else 1
        per = 2 if lay.mobile else 4
        rh = 210 if lay.mobile else 300
        h = rh * rows_n
        left, right = lay.left, lay.right
        vmax, vmin = 58, -44
        out = [svg_open(lay, h, "持有越久，最好與最差越靠近；一半債券讓最差那端縮小")]
        for rI in range(rows_n):
            top = rI * rh + lay.top + 8
            bottom = rI * rh + rh - 30
            def py(v, top=top, bottom=bottom): return top + (bottom - top) * (vmax - v) / (vmax - vmin)
            out += grid(lay, py, (-40, -20, 0, 20, 40), lambda v: "%d%%" % v)
            gw = (right - left) / per
            bw = (gw - 16) / 4 - 4
            for k in range(per):
                i = rI * per + k
                label, *cols = data[i]
                gx = left + k * gw + 8
                for j, ((lo, hi), color) in enumerate(zip(cols, tones)):
                    x = gx + j * (bw + 4)
                    out.append(rect(x, py(hi), bw, max(2, py(lo) - py(hi)), color))
                    out.append(text(x + bw / 2, py(hi) - 4, "%+d" % hi, lay.fl - 1.5, "middle", INK, "700"))
                    out.append(text(x + bw / 2, py(lo) + lay.fl, "%+d" % lo, lay.fl - 1.5, "middle", INK))
                out.append(text(gx + (gw - 16) / 2, bottom + lay.f + 6, label, lay.f, "middle", INK, "700"))
        out.append("</svg>")
        return "\n".join(out)
    lg = legend([(AMBER, "全放股票"), (MUTED, "全部債券"), (TEAL, "一半股票一半債券"), (BLUE, "現金")])
    # 這一段是指南裡手改過的長版，2026-09-16 起以腳本為正本（兩邊同源；do_guide 會比對）
    nt = note("美國 1950 到 2025 年，以整年報酬為單位，連續放 1 到 20 年，換算成平均一年的報酬區間（%）。這張表每一段都是從 1 月 1 日算到 12 月 31 日。如果從某個高點那一天起算，一年後會比表上最差的那格更差，所以表上的最差值是偏好看的。J.P. Morgan「Guide to Retirement 2026」第 42 頁。")
    return dict(title="放 1、5、10、20 年，最好的一段和最差的一段（換算成平均一年）", sub="美國 1950–2025，平均一年報酬區間，%",
                svgs=[draw(L("d")), draw(L("m"))], extras=lg + nt,
                caption="往右看，最好和最差越來越近，但最差不是零。比較股票和一半一半，防守那一塊把最差的一年切掉一大半，也切掉一些最好的。這裡的債券是美國整體的投資等級債券（1976 年前用 Strategas/Ibbotson，之後用 Bloomberg Aggregate），2022 年股債同跌那一年已經算在裡面。")


# ======================================================================
# §6 五個人
def five_people():
    data = [(("精準買在", "最低點"), 186077), (("一拿到", "就投入"), 170555), (("分 12 個月", "慢慢投"), 166591), (("倒楣買在", "最高點"), 151343), (("一直等", "機會"), 47357)]

    def draw(lay):
        h = 230 if lay.mobile else 280
        lay.left += 12          # 第一格刻度要標「萬美元」，左邊留寬一點
        left, top, right = lay.left, lay.top + 10, lay.right
        bottom = h - 40
        vmax = 200000
        def py(v): return bottom - (bottom - top) * v / vmax
        out = [svg_open(lay, h, "五個人 20 年後手上的美元")]
        out += grid(lay, py, (0, 50000, 100000, 150000, 200000), lambda v: usd_tick(v, 50000))
        gw = (right - left) / 5
        bw = gw * 0.56
        for i, (label, v) in enumerate(data):
            x = left + i * gw + (gw - bw) / 2
            out.append(rect(x, py(v), bw, bottom - py(v), TEAL if i < 4 else MUTED))
            out.append(text(x + bw / 2, py(v) - 5, format(v, ","), lay.fl, "middle", INK, "800"))
            out.append(text(x + bw / 2, bottom + lay.f + 4, label[0], lay.fs, "middle", INK))
            out.append(text(x + bw / 2, bottom + lay.f * 2 + 6, label[1], lay.fs, "middle", INK))
        out.append("</svg>")
        return "\n".join(out)
    # 批 AH（9-3）：Schwab 的 80 段檢驗移進圖下「想深入：樣本、官方原圖與版權」。
    nt = note("每年各拿到 2,000 美元、美股 2005 到 2024 年。")
    return dict(title="20 年後，五個人手上各有多少", sub="Schwab 試算，美元",
                svgs=[draw(L("d")), draw(L("m"))], extras=nt,
                caption="最大的差距不在買在哪一天（最準和最倒楣差兩成三），而在錢有沒有進去（一直等的比一拿到就投入少了七成）。")


# ======================================================================
# §7 幸運兒／倒楣鬼
def dca_high_low():
    rows = list(csv.DictReader(open(DATA / "algo_a_monthly_stats.csv", encoding="utf-8")))
    def run(key):
        units, series = 0.0, []
        for r in rows:
            units += 10000 / float(r[key])
            series.append(units * float(r["last_close"]))
        return series
    hi, lo = run("max"), run("min")
    assert abs(hi[-1] - 14703632.84) < 1 and abs(lo[-1] - 15780597.76) < 1
    n = len(rows)

    def draw(lay):
        h = 240 if lay.mobile else 300
        left, top = lay.left + 6, lay.top
        right = lay.right - (44 if lay.mobile else 56)
        bottom = h - 28
        ymax = 1700e4
        def px(i): return left + (right - left) * i / (n - 1)
        def py(v): return bottom - (bottom - top) * v / ymax
        out = [svg_open(lay, h, "台股每月投 1 萬元，都買在當月最高與都買在當月最低，資產累積走勢")]
        out += grid(lay, py, (0, 500e4, 1000e4, 1500e4), lambda v: ("%d 萬" % (v / 1e4)) if v else "0", x2=right)
        for i, r in enumerate(rows):
            if int(r["month"]) == 1 and int(r["year"]) % 4 == 3:
                # 第一個年份靠左對齊，才不會往左長到 y 軸的「0」上面（v7 批 W）
                out.append(text(px(i), bottom + lay.f + 4, r["year"], lay.f,
                                "start" if i == 0 else "middle", MUTED))
        out.append(poly([(px(i), py(v)) for i, v in enumerate(lo)], TEAL, 1.8))
        out.append(poly([(px(i), py(v)) for i, v in enumerate(hi)], ACCENT, 1.8))
        out.append(dot(px(n - 1), py(lo[-1]), TEAL, 3.5))
        out.append(dot(px(n - 1), py(hi[-1]), ACCENT, 3.5))
        out.append(text(right + 8, py(lo[-1]) - 2, "1,578 萬", lay.fl, "start", TEAL, "800"))
        out.append(text(right + 8, py(hi[-1]) + lay.fl + 2, "1,470 萬", lay.fl, "start", ACCENT, "800"))
        out.append("</svg>")
        return "\n".join(out)
    lg = legend([(TEAL, "幸運兒：都買在當月最低收盤"), (ACCENT, "倒楣鬼：都買在當月最高收盤")])
    table = """<table class="stack-mobile-cols dca">
<thead><tr><th></th><th>幸運兒</th><th>平凡人</th><th>倒楣鬼</th></tr></thead>
<tbody>
<tr><th>買在</th><td>每月最低收盤</td><td>每月平均收盤</td><td>每月最高收盤</td></tr>
<tr><th>總投入</th><td>276 萬</td><td>276 萬</td><td>276 萬</td></tr>
<tr><th>期末資產</th><td>1,578 萬</td><td>1,519 萬</td><td>1,470 萬</td></tr>
<tr><th>平均一年長</th><td>13.23%</td><td>12.97%</td><td>12.74%</td></tr>
</tbody></table>"""
    # 批 AH（10-1）：「兩條線幾乎疊在一起」圖說已經講過；三個期末精確值移進「想深入：七種頻率的數字表」。
    nt = note("證交所發行量加權股價報酬指數 2003 到 2025 年，每月投入 1 萬元，自算。")
    return dict(title="每月 1 萬元：永遠買在最高，對上永遠買在最低", sub="台股含息 2003–2025，自算",
                svgs=[draw(L("d")), draw(L("m"))], extras=lg + table + nt,
                caption="永遠最衰和永遠神準，二十三年下來只差 7.3%。要看的是兩條線的距離，不是高度：這 23 年事後看報酬偏高，換一段期間會不同。")


# ======================================================================
# §8 錯過最好的日子
def missing_days():
    data = [("全程持有", 80619), ("錯過最好的 10 天", 35866), ("錯過最好的 30 天", 13826)]

    def draw(lay):
        h = 220 if lay.mobile else 270
        lay.left += 12          # 第一格刻度要標「萬美元」，左邊留寬一點
        left, top, right = lay.left + 8, lay.top + 10, lay.right
        bottom = h - 30
        vmax = 90000
        def py(v): return bottom - (bottom - top) * v / vmax
        out = [svg_open(lay, h, "標普 500 含息，2006 到 2025 年投入 1 萬美元的結果")]
        out += grid(lay, py, (0, 20000, 40000, 60000, 80000), lambda v: usd_tick(v, 20000))
        gw = (right - left) / 3
        bw = gw * 0.5
        for i, (label, v) in enumerate(data):
            x = left + i * gw + (gw - bw) / 2
            out.append(rect(x, py(v), bw, bottom - py(v), TEAL if i == 0 else MUTED))
            out.append(text(x + bw / 2, py(v) - 6, format(v, ","), lay.fl, "middle", INK, "800"))
            out.append(text(x + bw / 2, bottom + lay.f + 4, label, lay.f, "middle", INK))
        out.append("</svg>")
        return "\n".join(out)
    # 只留 J.P. Morgan 自己那一句；反方向（Estrada、道瓊 1900–2006）留在正文，那裡有期間、口徑與但書
    nt = note("10 個最好的日子裡，有 6 天落在最差的 10 天的兩週內（J.P. Morgan Guide to Retirement 2026）。")
    return dict(title="全程待著，和少了最好的那幾天", sub="S&P 500 含息，投入 1 萬美元，20 年後",
                svgs=[draw(L("d")), draw(L("m"))], extras=nt,
                caption="「先出來一下」的代價。最好的日子和最差的日子擠在一起，想躲掉一邊，常常連另一邊也躲掉。")


# ======================================================================
# 沿用手冊的兩張（維持手冊的 SVG，只套新外框）
def handbook_figure(chapter_file):
    s = (ROOT / "chapters" / chapter_file).read_text(encoding="utf-8")
    m = re.search(r"<figure class=\"chart\">\s*(<svg.*?</svg>)", s, re.S)
    if not m:
        raise SystemExit("找不到手冊圖：" + chapter_file)
    return m.group(1).replace("<svg ", '<svg class="d m" ', 1)


def smooth_vs_jagged():
    """資料取自手冊第 7 章那張圖的兩條折線（x 46–340 ＝ 0–30 年，y 272 ＝ 0、每 72 ＝ 200 萬），套新框架重畫。"""
    src = (ROOT / "chapters" / "07-time-inflation-compounding.html").read_text(encoding="utf-8")
    svg = re.search(r"<figure class=\"chart\">\s*(<svg.*?</svg>)", src, re.S).group(1)
    lines = re.findall(r'<polyline points="([^"]+)"', svg)
    def parse(pts):
        out = []
        for p in pts.split():
            x, y = map(float, p.split(","))
            out.append(((x - 46) / (340 - 46) * 30, (272 - y) / 72 * 200))
        return out
    smooth, jagged = parse(lines[0]), parse(lines[1])

    def draw(lay):
        h = 240 if lay.mobile else 300
        left, top, right = lay.left, lay.top, lay.right
        bottom = h - 28
        def px(t): return left + (right - left) * t / 30
        def py(v): return bottom - (bottom - top) * v / 620
        out = [svg_open(lay, h, "示意：每月投入 5,000 元、年化同為 6%、30 年，平滑假想線與中途下跌的鋸齒線")]
        out += grid(lay, py, (0, 200, 400, 600), lambda v: ("%d 萬" % v) if v else "0")
        for t in (0, 10, 20, 30):
            # 最右邊那個刻度靠右對齊，手機版才不會超出圖框被切掉；
            # 最左邊那個靠左對齊，才不會往左長到 y 軸的「0」上面（v7 批 W）
            anc = "end" if t == 30 else ("start" if t == 0 else "middle")
            out.append(text(px(t), bottom + lay.f + 4, "%d 年" % t, lay.f, anc, MUTED))
        out.append(poly([(px(t), py(v)) for t, v in smooth], MUTED, lay.line - 0.4, dash="6 5"))
        out.append(poly([(px(t), py(v)) for t, v in jagged], ACCENT, lay.line))
        out.append(dot(px(jagged[-1][0]), py(jagged[-1][1]), ACCENT))
        out.append("</svg>")
        return "\n".join(out)
    lg = legend([(MUTED, "假設每年都剛好 6%（虛線）"), (ACCENT, "年化同樣 6%，中途有漲有跌")])
    # v7 第 20 版 I：p.note 和指南的 figcaption 幾乎逐字相同，整條收掉；它唯一多出來的那半句
    # （「每個月都在投入的人，先跌後漲和先漲後跌，終點也會不同」）併進指南的 figcaption。
    return dict(title="你以為的複利，和你真實經歷的", sub="示意：每月 5,000 元、30 年；兩條線的終點刻意畫成一樣",
                svgs=[draw(L("d")), draw(L("m"))], extras=lg,
                caption="兩條線的終點一樣，走的路完全不同。你以為的複利是虛線，你真實經歷的是實線：三十年裡有九年是負的。")


def buckets():
    """三桶：橫式版（桌面 640、手機 360）。SVG 裡不放標題，外層 chart-head 是唯一標題。
    橫條長度＝這一桶容得下的波動，比例沿用手冊那張直式圖（21.5/280、118.5/280）；
    三桶用同一個灰底槽，第三桶不畫長度、由讀者自己填（虛線全寬框會被讀成「可以跌 100%」）。"""
    rows = [("一年內要用", "緊急金、保費、近期要繳的錢", 0.077, "隨時拿得到、幾乎不能跌：放活存、定存"),
            ("一到五年要用", "頭期款、換車、三年後的學費", 0.423, "只容得下小幅波動：放定存或短天期的工具"),
            ("五年以上不動", "退休、日期不固定的長期目標", None, "這一桶才討論股票要放幾成")]

    def draw(lay):
        rh = 92 if lay.mobile else 64
        h = (6 if lay.mobile else 8) + rh * 3
        bx0 = 4 if lay.mobile else 186
        bx1 = lay.W - (8 if lay.mobile else 20)
        bh = 14 if lay.mobile else 16
        out = [svg_open(lay, h, "示意：按什麼時候要用分成三桶；前兩桶的橫條表示相對大小，第三桶由讀者自己填")]
        for i, (name, eg, frac, cond) in enumerate(rows):
            y0 = (6 if lay.mobile else 8) + i * rh
            if i:
                out.append(hline(0, bx1, y0 - (16 if lay.mobile else 8), LINE, 1, None))
            out.append(text(4, y0 + lay.f + 3, name, lay.f, "start", INK, "800"))
            out.append(text(4, y0 + lay.f * 2 + 7, eg, lay.fs, "start", MUTED))
            by = y0 + (40 if lay.mobile else 6)
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" rx="3" fill="none" stroke="%s" stroke-width="1.5"/>'
                       % (bx0, by, bx1 - bx0, bh, LINE))
            if frac is None:
                out.append(text(bx0 + 7, by + bh - 3.5, "？", lay.fs, "start", MUTED, "800"))
                out.append(text(bx0 + 21, by + bh - 4, "你自己填：股票＿%", lay.fs, "start", MUTED))
            else:
                out.append(rect(bx0, by, (bx1 - bx0) * frac, bh, TEAL, 3))
            out.append(text(bx0, by + bh + lay.fs + 6, cond, lay.fs, "start", INK))
        out.append("</svg>")
        return "\n".join(out)
    return dict(title="按用錢日期分三桶", sub="示意：長度只表示三桶的相對大小",
                svgs=[draw(L("d")), draw(L("m"))], extras="",
                caption="按「什麼時候要用」分成三桶。橫條越長，代表這一桶的錢越容得下上上下下；第三桶留白，是要你自己填。")


# ======================================================================
# §12 控制地圖（只在指南）：三層——控制得了、部分控制、控制不了。
# 自己的畫法：三個並排（手機改成上下三塊）的欄，欄頭一條淡色底，底下條列。
# 不模仿任何機構的原圖，文字也是本文自己的。
CONTROL_MAP = [
    ("控制得了", TEAL, ["存多少", "付多少費用", "股債比與規則卡", "照不照計畫做", "多久看一次"]),
    ("部分控制", AMBER, ["什麼時候開始", "什麼時候退休", "收入穩不穩定、能不能替代", "保障買不買"]),
    ("控制不了", MUTED, ["市場報酬", "匯率", "物價", "政策與稅制", "活多久"]),
]


def control_map():
    def head_box(x, y, w, h, color, label, fsize):
        return ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" fill="%s" fill-opacity="0.22" stroke="%s" stroke-width="1.4"/>'
                % (x, y, w, h, color, color),
                text(x + w / 2, y + h / 2 + fsize * 0.36, label, fsize, "middle", INK, "800")]

    def bullet(x, y, color):
        return '<rect x="%.1f" y="%.1f" width="5" height="5" rx="1.5" fill="%s"/>' % (x, y, color)

    def draw(lay):
        title = "示意：把和投資有關的事分成三層，控制得了、部分控制、控制不了"
        if lay.mobile:
            pad, step, hh = 6, 20, 26
            h = int(sum(hh + len(it) * step + 12 for _, _, it in CONTROL_MAP)) + 6
            out = [svg_open(lay, h, title)]
            y = 4
            for label, color, items in CONTROL_MAP:
                out += head_box(pad, y, lay.W - pad * 2, hh, color, label, lay.f)
                y += hh + 8
                for it in items:
                    out.append(bullet(pad + 6, y + lay.fs * 0.30, color))
                    out.append(text(pad + 18, y + lay.fs * 0.85, it, lay.fs, "start", INK))
                    y += step
                y += 4
            out.append("</svg>")
            return "\n".join(out)
        pad, gap, step, hh = 8, 10, 24, 30
        cw = (lay.W - pad * 2 - gap * 2) / 3
        h = int(6 + hh + 12 + (max(len(it) for _, _, it in CONTROL_MAP) - 1) * step) + 10
        out = [svg_open(lay, h, title)]
        for i, (label, color, items) in enumerate(CONTROL_MAP):
            x = pad + i * (cw + gap)
            out += head_box(x, 6, cw, hh, color, label, 13)
            y = 6 + hh + 12
            for it in items:
                out.append(bullet(x + 8, y - lay.fs * 0.62, color))
                out.append(text(x + 20, y, it, lay.fs, "start", INK))
                y += step
        out.append("</svg>")
        return "\n".join(out)
    return dict(title="三層：控制得了、部分控制、控制不了", sub="示意圖，不是資料；每一項在哪一節，看圖下那三條清單",
                svgs=[draw(L("d")), draw(L("m"))], extras="",
                caption="第一層是你今天就做得了決定的事；最後一層不管想多久，都不會因為你想而改變。中間那一層，一半由你決定、一半由環境決定。")


# ======================================================================
# §13 台股跌 20% 以上的七次，各花多久回到前高（只在指南）
def taiex_recovery():
    d = calc()["taiex_drawdowns"]
    eps = d["episodes"]
    top = max(e["years_peak_to_recover"] for e in eps)

    def draw(lay):
        rh = 30 if not lay.mobile else 34
        lw = 92 if lay.mobile else 150
        x0 = lw + (6 if lay.mobile else 6)
        x1 = lay.W - (58 if lay.mobile else 62)
        bh = 13 if lay.mobile else 15
        h = int(6 + len(eps) * rh) + 4
        out = [svg_open(lay, h, "台股含息指數 2003 年以來跌兩成以上的七次，各花多久回到前一個高點")]
        for i, e in enumerate(eps):
            y = 6 + i * rh
            yr = e["peak_date"][:4]
            drop = "%d%%" % int(abs(e["drawdown_pct"]) + 0.5)   # 四捨五入取整（不用 round，避免 banker's rounding）
            lab = ("%s 跌 %s" % (yr, drop)) if lay.mobile else ("%s 年的高點，跌 %s" % (yr, drop))
            out.append(text(4, y + bh, lab, lay.f, "start", INK))
            w = (x1 - x0) * e["years_peak_to_recover"] / top
            wd = (x1 - x0) * e["years_peak_to_trough"] / top
            out.append(rect(x0, y + bh - bh + 2, w, bh, TEAL, 3))
            out.append(rect(x0, y + 2, wd, bh, ACCENT, 3))
            out.append(text(x0 + w + 6, y + bh, "%.1f 年" % e["years_peak_to_recover"], lay.fl, "start", INK, "800"))
        out.append("</svg>")
        return "\n".join(out)
    lg = legend([(ACCENT, "從高點跌到最低點"), (TEAL, "整段：高點跌下去，到回到同一個高點")])
    # v7 第 20 版 I：結尾「這七段都回到了前高，最快 x 年、最慢 y 年」和 figcaption 是同一句結論，
    # 不是口徑；結論只留 figcaption 那一份，p.note 收在算法那一句為止。
    # 批 AH（8-11）：跌幅與回本的算法移進圖下那個展開的說明段，圖外只留資料來源。
    nt = note("證交所發行量加權股價報酬指數（含息）逐日收盤自算，2003-01-02 到 2025-12-31。")
    return dict(title="跌下去要多久才回得來：台股 2003 年以來的七次",
                sub="含息報酬指數，2003-01-02 到 2025-12-31，跌兩成以上的每一段",
                svgs=[draw(L("d")), draw(L("m"))], extras=lg + nt,
                caption="七次跌兩成以上，各花多久才回到跌之前的那個高點。這七次都回來了，是台股這 23 年的紀錄；第 <a class=\"xref\" href=\"#s4\">7</a> 節那張表裡，也有等 25 到 34 年的例子。")


# ======================================================================
# §14 四類資產逐年輪換（只在指南）
ROT_COLOR = {"美股": TEAL, "台股": AMBER, "公債": MUTED, "現金": BLUE}


def rot_pct(v):
    if abs(v) < 0.05:
        return "0.0%"
    return ("+%.1f%%" if v > 0 else "−%.1f%%") % abs(v)


def asset_rotation():
    d = calc()["asset_rotation"]
    rows = d["rows"]

    def draw(lay):
        rh = 21 if lay.mobile else 22
        th = 17 if lay.mobile else 18
        lw = 34 if lay.mobile else 44
        gap = 3 if lay.mobile else 4
        x0 = lw + 4
        x1 = lay.W - (8 if lay.mobile else 18)
        tw = (x1 - x0 - gap * 3) / 4
        top = 18
        h = int(top + len(rows) * rh) + 4
        out = [svg_open(lay, h, "美股、台股、公債、現金四類資產，%d 到 %d 年每一年的名次" % (d["from"], d["to"]))]
        for k in range(4):
            out.append(text(x0 + k * (tw + gap) + tw / 2, 11, "第 %d 名" % (k + 1), lay.fs, "middle", MUTED, "700"))
        for i, r in enumerate(rows):
            y = top + i * rh
            out.append(text(4, y + th * 0.72, str(r["year"]), lay.fs, "start", MUTED))
            for k, item in enumerate(r["ranking"]):
                x = x0 + k * (tw + gap)
                c = ROT_COLOR[item["label"]]
                out.append(rect(x, y, tw, th, c, 3, opacity="0.28"))
                out.append(text(x + 5, y + th * 0.72, item["label"], lay.fs, "start", INK, "700"))
                out.append(text(x + tw - 5, y + th * 0.72, rot_pct(item["return_pct"]), lay.fs, "end", INK))
        out.append("</svg>")
        return "\n".join(out)
    lg = legend([(TEAL, "美股（S&P 500 含息，美元）"), (AMBER, "台股（含息報酬指數，台幣）"),
                 (MUTED, "美國 10 年期公債（美元）"), (BLUE, "現金（美國 3 個月國庫券，美元）")])
    nt = note("美國三類出自 Damodaran（紐約大學 Stern）公開的年度報酬資料集，台股是證交所含息報酬指數自算；"
              '都是<a class="term" href="#g-annual" title="沒扣物價、帳面上看到的數字。">名目</a>、含息，沒有扣物價、費用和稅。台股以台幣計、其餘三類以美元計，沒有換成同一種貨幣，'
              "所以這張表比的是「各自市場那一年漲跌多少」，不是台灣人換回台幣實際拿到的報酬。", raw=True)
    return dict(title="每一年的第一名是誰：%d 到 %d 年" % (d["from"], d["to"]),
                sub="美股、台股、美國 10 年期公債、現金，四類各自市場的當年報酬排名",
                svgs=[draw(L("d")), draw(L("m"))], extras=lg + nt,
                caption="由上往下看第一欄：四種都當過第一名，也會連著好幾年是同一個（美股 2012 到 2015、台股 2023 到 2025）。連這四種最基本的東西都排不出固定順序。哪一年會換人，前一年看不出來。")


# ======================================================================
# G9/G10：兩張只在指南的新圖，各自的 compute()/chart() 寫在 tools/v61_g*.py
def country_recovery():
    import v61_g9_country_recovery as _g9
    return _g9.chart(calc()["country_recovery"])


def rebalance_drift():
    import v61_g10_rebalance_drift as _g10
    return _g10.chart(calc()["rebalance_drift"])


# ======================================================================
# v6.3 第二批 G01–G05：五張只在指南的新圖，compute()/chart() 寫在 tools/v63_g0*.py
def plan_flow():
    import v63_g01_plan_flow as _g01
    return _g01.chart(calc()["plan_flow"])


def sequence_risk():
    import v63_g02_sequence_risk as _g02
    return _g02.chart(calc()["sequence_risk"])


def drag_breakdown():
    import v63_g03_drag_breakdown as _g03
    return _g03.chart(calc()["drag_breakdown"])


def fee_gap():
    import v63_g04_fee_gap as _g04
    return _g04.chart(calc()["fee_gap_chart"])


def safety_steps():
    import v63_g05_safety_steps as _g05
    return _g05.chart(calc()["safety_steps"])


# v6.3 第三批 P1 的 G06：數字直接讀 lite/calc-results.json 的 rolling（calc_core.py 已經算好），
# 所以 compute() 也在模組裡，不需要 calc-results.json 另開一個鍵。
def holding_positive():
    import v63_g06_holding_positive as _g06
    return _g06.chart(_g06.compute())


# v6.3 第三批 P2 的 G07：散戶心境圖（示意，圖上沒有數字），compute() 在 tools/v63_g07_investor_cycle.py，
# 由 calc_core.py 收進 calc-results.json 的 investor_cycle。
def investor_cycle():
    import v63_g07_investor_cycle as _g07
    return _g07.chart(calc()["investor_cycle"])


# v7 批 S2 的 G08／G09：兩張長線圖。資料直接讀 research/data 的兩份 CSV（序列太長，
# 不進 calc-results.json），口徑與 calc_core 共用 tools/v7_series.py，所以兩邊不會各算各的。
def taiex_long_run():
    import v7_g08_long_run as _g08
    return _g08.taiex()


def sp500_long_run():
    import v7_g08_long_run as _g08
    return _g08.sp500()


# v7 批 S6 的 G10／G11：兩張滾動報酬圖，和 G09 同一條美股序列（tools/v7_series.py）。
def sp500_holding_box():
    import v7_g09_rolling as _g09
    return _g09.holding_box()


def sp500_rolling_30y():
    import v7_g09_rolling as _g09
    return _g09.rolling_30y()


CHARTS = [
    ("three-circles", "01-where-return-comes-from.html", "順便講「又穩又高」", "aside", three_circles),
    ("four-people", "02-time.html", "手冊算過四個人", "aside", four_people),
    ("milestones", "02-time.html", "把資產每滿 60 萬當一格", "aside", milestones),
    ("spiva", "03-cost.html", "美國大型股、由人幫你挑股票的基金", "aside", spiva),
    ("smooth-vs-jagged", "05-volatility.html", "前一種要變成真的傷害", "p", smooth_vs_jagged),
    ("intra-year", "05-volatility.html", "美國大盤 1980 到 2025 年", "aside", intra_year),
    ("ranges", "05-volatility.html", "另一件事跟比例有關", "aside", ranges),
    ("five-people", "06-timing.html", "有人用 1920 年起的美股資料試過一件事", "aside", five_people),
    ("dca-high-low", "07-frequency.html", "台股大盤把股利也算進去", "aside", dca_high_low),
    ("missing-days", "08-take-profit-dividend.html", "「先出來一下」的代價算得出來", "aside", missing_days),
    ("buckets", "11-rules.html", "卡上只寫動作，不寫心情", "p", buckets),
]

FIG_RE = r'\n?\s*<figure class="chart" data-chart="%s">.*?</figure>'


def strip_all(s):
    return re.sub(FIG_RE % '[^"]+', "", s, flags=re.S)


def insert(s, cid, anchor, mode, fig):
    i = s.find(anchor)
    if i < 0:
        return s, "找不到錨點：%s" % anchor
    end_tag = "</aside>" if mode == "aside" else "</p>"
    j = s.find(end_tag, i)
    if j < 0:
        return s, "錨點後找不到 %s" % end_tag
    j += len(end_tag)
    return s[:j] + "\n\n    " + fig + s[j:], None


def build(cid, fn_chart, caption=None, caption_html=False):
    d = fn_chart()
    illus = bool(d.get("illustration_only"))
    if illus and (d.get("extras") or d.get("caption")):
        # 旗標和內容對不起來就吵，免得「純示意」被拿來當省略圖說的後門
        print("⚠ %s 標了 illustration_only，卻還帶著 extras 或 caption；圖說已被略過。" % cid)
    return figure(cid, d["title"], d["sub"], d["svgs"], caption if caption is not None else d.get("caption", ""), d["extras"],
                  caption_html=caption_html, illustration_only=illus, after=d.get("after", ""))


def do_essay():
    errors, files = [], {}
    for fn in sorted(SEC.glob("[0-9]*.html")):
        files[fn.name] = strip_all(fn.read_text(encoding="utf-8"))
    for cid, fn, anchor, mode, fn_chart in CHARTS:
        files[fn], err = insert(files[fn], cid, anchor, mode, build(cid, fn_chart))
        if err:
            errors.append("%s：%s" % (cid, err))
        else:
            print("專篇 插入 %s → %s" % (cid, fn))
    for fn, s in files.items():
        (SEC / fn).write_text(s, encoding="utf-8")
    for e in errors:
        print("✗", e)
    return 1 if errors else 0


def fig_note(fig_html):
    """圖下說明（figure 裡 figcaption 之前那條 p.note；figcaption 後面那條是原圖出處，不算）。"""
    m = re.search(r'<p class="note">(.*?)</p>', fig_html.split("<figcaption", 1)[0], re.S)
    return unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else None


def do_guide():
    """指南：只換同 id 的圖，保留指南自己的 figcaption。"""
    global GUIDE_MODE
    GUIDE_MODE = True   # 出處聲明不印在 figure 裡；指南把它放在 figure 後面（見 GUIDE_MODE 的說明）
    s = GUIDE.read_text(encoding="utf-8")
    funcs = {cid: f for cid, _, _, _, f in CHARTS}
    funcs["human-capital"] = human_capital   # 只在指南
    funcs["control-map"] = control_map       # 只在指南
    funcs["taiex-recovery"] = taiex_recovery  # 只在指南
    funcs["asset-rotation"] = asset_rotation  # 只在指南
    funcs["country-recovery"] = country_recovery  # 只在指南
    funcs["rebalance-drift"] = rebalance_drift    # 只在指南
    funcs["plan-flow"] = plan_flow                # 只在指南
    funcs["sequence-risk"] = sequence_risk        # 只在指南
    funcs["drag-breakdown"] = drag_breakdown      # 只在指南
    funcs["fee-gap"] = fee_gap                    # 只在指南
    funcs["safety-steps"] = safety_steps          # 只在指南
    funcs["holding-positive"] = holding_positive  # 只在指南
    funcs["investor-cycle"] = investor_cycle      # 只在指南
    funcs["taiex-long-run"] = taiex_long_run      # 只在指南
    funcs["sp500-long-run"] = sp500_long_run      # 只在指南
    funcs["sp500-holding-box"] = sp500_holding_box    # 只在指南
    funcs["sp500-rolling-30y"] = sp500_rolling_30y    # 只在指南
    n = 0
    diffs = []
    def repl(m):
        nonlocal n
        cid = m.group(1)
        # 指南的 figcaption 原樣保留（含 <a class="xref"> 節號連結，migration-plan §10.3），不去標籤、不再跳脫；
        # 指南是空殼沒有 figcaption 時，用腳本的預設圖說（預設圖說也當 HTML，裡面可以放節號連結）。
        cap = re.search(r"<figcaption>(.*?)</figcaption>", m.group(0), re.S)
        cap = cap.group(1) if cap else None
        n += 1
        fig = build(cid, funcs[cid], cap, caption_html=True)
        before, after = fig_note(m.group(0)), fig_note(fig)
        if before != after:
            diffs.append((cid, before, after))
        return fig
    s2 = re.sub(r'<figure class="chart" data-chart="([^"]+)">.*?</figure>', repl, s, flags=re.S)
    GUIDE.write_text(s2, encoding="utf-8")
    print("指南 換了 %d 張圖" % n)
    # 指南裡手改過的 p.note 會被腳本蓋掉，所以蓋之前先比一次，不同就吵
    for cid, before, after in diffs:
        print("⚠ %s 的圖下說明和指南原本的不一樣，指南那份已被蓋掉：" % cid)
        print("   指南原本：%s" % (before if before is not None else "（沒有）"))
        print("   腳本寫回：%s" % (after if after is not None else "（沒有）"))
    if diffs:
        print("⚠ 共 %d 張圖的 p.note 被蓋掉。要留指南那版，就把它寫回 tools/essay_charts.py。" % len(diffs))
    return 0


# v7 批 S2／S6：作者要挑版本的圖，產成獨立 HTML 樣張（不進指南）。
# 樣張帶指南的 <style>，所以顏色、字級、深色模式和書上完全一樣。
SAMPLES_DIR = ROOT / "wip" / "v63-review" / "samples"


def sample_charts():
    # 批 T：兩張樣張都作廢了——美股長線圖改成指南直接放 1929 年起那一版（作者選的），
    # 箱型圖的「只用最近 30 年」那一版 30 年那一根只有 1 個視窗、沒有意義。
    # 下一次要給作者挑版本時，照上面兩筆的格式加回來就好。
    return []


def do_samples():
    global GUIDE_MODE
    GUIDE_MODE = True
    css = re.search(r"<style>.*?</style>", GUIDE.read_text(encoding="utf-8"), re.S).group(0)
    n = 0
    for cid, title, fn in sample_charts():
        fig = build(cid, fn, caption_html=True)
        html = ('<!doctype html><html lang="zh-Hant"><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>%s</title>%s<body class="part" style="max-width:700px;margin:0 auto;padding:18px">'
                '<p class="small">樣張：%s。手機看請直接縮放視窗到 375px 寬。</p>\n%s\n</body></html>\n'
                % (esc(title), css, esc(title), fig))
        (SAMPLES_DIR / (cid + ".html")).write_text(html, encoding="utf-8")
        print("樣張 %s → wip/v63-review/samples/%s.html" % (cid, cid))
        n += 1
    return 0


def main(argv):
    if "--samples" in argv:
        return do_samples()
    if "--all" in argv:
        return do_essay() or do_guide()
    if "--guide" in argv:
        return do_guide()
    return do_essay()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
