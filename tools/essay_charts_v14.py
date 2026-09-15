#!/usr/bin/env python3
"""投資專篇的圖表（v1.4）：每一張都照作者當初提供的原圖樣式重畫，數字只用手冊已驗證的量級。

對照（作者原圖 → 專篇圖）：
  三圓「報酬／時間／風險」       → §1  three-circles（依 supplement-plan C1 改標籤）
  Chloe／Lyla／Quincy／Noah 曲線 → §2  four-people（台幣版，每月 5,000、6%／定存 1.7%）
  Accumulating $1M 里程碑曲線    → §2  milestones（手冊第 7 章表：60 萬一格，7.84 年→1.35 年）
  SPIVA 圓餅                     → §3  spiva（2024 年底 10／15／20 年）
  S&P 年內最大跌幅 vs 全年報酬    → §5  intra-year（台灣含息指數 2003–2025 自算）
  你以為的複利 vs 真實經歷        → §5  smooth-vs-jagged（直接沿用手冊第 7 章那張）
  持有期間報酬區間浮動長條        → §5  ranges（1950–2018，全股票 vs 一半一半）
  Schwab 五個人                  → §6  five-people
  幸運兒／平凡人／倒楣鬼 表＋曲線 → §7  dca-high-low（台股自算逐月序列）
  錯過最好的 N 天長條             → §8  missing-days
  三個桶                         → §11 buckets（直接沿用手冊第 9 章那張）

用法：python3 tools/essay_charts.py
SVG viewBox 寬 360，字級 11–14：手機（約 306px）縮到 0.85 倍仍可讀；桌機放大到 600px。
顏色只用 CSS 變數；不用紅綠對比。
"""
import csv
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "essay" / "sections"
DATA = ROOT / "research" / "data"
W = 360


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_open(h, title, w=None):
    return ('<svg viewBox="0 0 %d %d" role="img" aria-label="%s" font-family="var(--sans)">' % (w or W, h, esc(title)))


def text(x, y, s, size=13, anchor="start", fill="var(--ink)", weight=None, extra=""):
    w = ' font-weight="%s"' % weight if weight else ""
    return '<text x="%.1f" y="%.1f" font-size="%s" text-anchor="%s" fill="%s"%s%s>%s</text>' % (x, y, size, anchor, fill, w, extra, esc(s))


def poly(points, stroke, width=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%s"%s stroke-linejoin="round" stroke-linecap="round"/>' % (
        " ".join("%.1f,%.1f" % p for p in points), stroke, width, d)


def rect(x, y, w, h, fill, extra="", rx=3):
    return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" fill="%s"%s/>' % (x, y, w, h, rx, fill, extra)

GRID = 'stroke="var(--line)" stroke-width="1" stroke-dasharray="2 4"' 


# ---------- §1 三圓 ----------
def three_circles():
    h = 300
    r = 92
    cx = {"top": 180, "left": 128, "right": 232}
    cy = {"top": 108, "left": 190, "right": 190}
    out = [svg_open(h, "示意：報酬高、時間短、風險低，三樣同時答應你的，先問錢從哪裡來")]
    for k, fill in (("top", "var(--amber)"), ("left", "var(--teal)"), ("right", "var(--accent)")):
        out.append('<circle cx="%d" cy="%d" r="%d" fill="%s" fill-opacity="0.28" stroke="%s" stroke-width="1.5"/>' % (cx[k], cy[k], r, fill, fill))
    out.append(text(180, 58, "時間短", 15, "middle", weight="700"))
    out.append(text(88, 226, "風險低", 15, "middle", weight="700"))
    out.append(text(272, 226, "報酬高", 15, "middle", weight="700"))
    out.append(text(138, 138, "低報酬", 12, "middle", "var(--muted)"))
    out.append(text(222, 138, "高風險", 12, "middle", "var(--muted)"))
    out.append(text(180, 250, "長時間", 12, "middle", "var(--muted)"))
    out.append(text(180, 176, "先問錢從哪裡來", 12, "middle", weight="700"))
    out.append(text(6, 290, "示意・非承諾", 10, "start", "var(--muted)"))
    out.append("</svg>")
    return "\n".join(out), "三個圓兩兩相交，各拿得到兩樣：低報酬、高風險、或長時間。三樣同時答應你的，先問那多出來的報酬是誰在付。"


# ---------- §2 四個人（Chloe 曲線） ----------
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
        ("25 到 65 歲，投 40 年", path(25, 65, 0.06), "var(--teal)", 996),
        ("35 歲才開始，投 30 年", path(35, 65, 0.06), "var(--accent)", 502),
        ("25 到 35 歲投 10 年，之後不再投入", path(25, 35, 0.06), "var(--amber)", 493),
        ("25 到 65 歲都放定存 1.7%", path(25, 65, 0.017), "var(--muted)", 343),
    ]
    h = 290
    left, right, top, bottom = 50, 348, 14, 250
    ymax = 1050e4
    def px(a): return left + (right - left) * (a - 25) / 40
    def py(v): return bottom - (bottom - top) * v / ymax
    out = [svg_open(h, "四個人 25 到 65 歲的資產曲線")]
    for v in (0, 250e4, 500e4, 750e4, 1000e4):
        out.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="var(--line)" stroke-width="1" stroke-dasharray="2 4"/>' % (left, py(v), right, py(v)))
        out.append(text(left - 6, py(v) + 4, "%d 萬" % (v / 1e4) if v else "0", 11, "end", "var(--muted)"))
    for a in (25, 35, 45, 55, 65):
        out.append(text(px(a), bottom + 16, "%d 歲" % a, 11, "middle", "var(--muted)"))
    out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="var(--line)" stroke-width="1.5"/>' % (left, bottom, right, bottom))
    for label, pts, color, end in series:
        out.append(poly([(px(a), py(v)) for a, v in pts], color, 2.2))
        out.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s" stroke="var(--surface)" stroke-width="1.5"/>' % (px(65), py(pts[-1][1]), color))
        assert abs(pts[-1][1] / 1e4 - end) < 6, (label, pts[-1][1])
    out.append(text(6, 282, "每月 5,000 元、一年長 6%（定存 1.7%）；示意・非承諾", 10, "start", "var(--muted)"))
    out.append("</svg>")
    legend = "".join('<li><span class="swatch" style="background:%s"></span>%s：投入 %d 萬，65 歲約 %d 萬</li>'
                     % (c, l, {996: 240, 502: 180, 493: 60, 343: 240}[e], e) for l, _, c, e in series)
    return "\n".join(out) + '\n<ul class="legend">%s</ul>' % legend, "只投十年就停的那條，最後幾乎追上投了三十年的那條。差別不是他會挑，是他的錢多待了十年。"


# ---------- §2 里程碑 ----------
def milestones():
    gaps = [7.84, 5.10, 3.78, 3.01, 2.50, 2.14, 1.87, 1.66, 1.49, 1.35]
    share = [22, 49, 62, 70, 75, 79, 81, 83, 85, 86]
    yrs = []
    t = 0
    for g in gaps:
        t += g
        yrs.append(t)
    T = yrs[-1]
    h = 356
    left, right, top, bottom = 44, 508, 34, 216
    def px(y): return left + (right - left) * y / T
    def py(v): return bottom - (bottom - top) * v / 620
    # 年投 6 萬、7%，逐月算資產與累計投入
    total, contrib = [], []
    v = 0.0
    for m in range(0, int(T * 12) + 2):
        if m:
            v *= 1 + 0.07 / 12
            v += 5000
        total.append((m / 12, v / 1e4))
        contrib.append((m / 12, m * 5000 / 1e4))
    out = [svg_open(h, "每多累積 60 萬要花幾年：前面慢，後面快", 520)]
    area_total = [(px(0), py(0))] + [(px(y), py(v)) for y, v in total if y <= T] + [(px(T), py(0))]
    area_contrib = [(px(0), py(0))] + [(px(y), py(v)) for y, v in contrib if y <= T] + [(px(T), py(0))]
    out.append('<polygon points="%s" fill="var(--teal)" fill-opacity="0.35"/>' % " ".join("%.1f,%.1f" % p for p in area_total))
    out.append('<polygon points="%s" fill="var(--muted)" fill-opacity="0.45"/>' % " ".join("%.1f,%.1f" % p for p in area_contrib))
    out.append(poly([(px(y), py(v)) for y, v in total if y <= T], "var(--teal)", 2))
    prev = 0
    for i, (y, g) in enumerate(zip(yrs, gaps)):
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%d" stroke="var(--ink)" stroke-width="1" stroke-dasharray="3 3"/>' % (px(y), py(60 * (i + 1)), px(y), bottom))
        if i < 6 or i == 9:   # 右端太密：420、480、540 不標，只留虛線
            out.append(text(px(y) - 5, py(60 * (i + 1)) - 7, "%d 萬" % (60 * (i + 1)), 10, "end"))
        mid = (prev + y) / 2
        out.append(text(px(mid), bottom + (14 if i % 2 == 0 else 27), ("%.2f 年" % g) if i < 3 else ("%.1f 年" % g), 9.5, "middle", "var(--muted)"))
        out.append(text(px(mid), bottom + (44 if i % 2 == 0 else 57), "%d%%" % share[i], 9.5, "middle", "var(--teal)", weight="700"))
        prev = y
    out.append(text(left - 4, bottom + 44, "報酬占", 10, "end", "var(--teal)"))
    out.append(text(left - 4, bottom + 14, "花幾年", 10, "end", "var(--muted)"))
    out.append(rect(left, 290, 12, 10, "var(--muted)", ' fill-opacity="0.45"') + text(left + 16, 299, "自己存進去的", 11))
    out.append(rect(left + 100, 290, 12, 10, "var(--teal)", ' fill-opacity="0.35"') + text(left + 116, 299, "長出來的報酬", 11))
    out.append(text(left, 322, "每月 5,000 元、一年長 7%；每格 60 萬。第一格 7.84 年，第十格 1.35 年。", 10, "start", "var(--muted)"))
    out.append(text(left, 338, "下排是那一格裡有多少是報酬：兩成多到八成多。示意・非承諾", 10, "start", "var(--muted)"))
    out.append("</svg>")
    return "\n".join(out), "同樣 60 萬一格，第一格要將近八年，第十格只要一年多。前面慢，是因為錢還沒開始幫忙；越後面，格子裡越多是它自己長出來的。"


# ---------- §3 SPIVA 圓餅 ----------
def spiva():
    data = [("10 年", 85.59), ("15 年", 89.93), ("20 年", 92.89)]
    h = 190
    out = [svg_open(h, "美國大型股主動基金輸給大盤的比例，截至 2025 年底")]
    for i, (label, lose) in enumerate(data):
        cx, cy, r = 62 + i * 118, 92, 46
        a = 2 * math.pi * lose / 100
        x1, y1 = cx, cy - r
        x2, y2 = cx + r * math.sin(a), cy - r * math.cos(a)
        large = 1 if lose > 50 else 0
        out.append('<circle cx="%d" cy="%d" r="%d" fill="var(--teal)"/>' % (cx, cy, r))
        out.append('<path d="M%d,%d L%.1f,%.1f A%d,%d 0 %d,1 %.1f,%.1f Z" fill="var(--accent)"/>' % (cx, cy, x1, y1, r, r, large, x2, y2))
        out.append('<circle cx="%d" cy="%d" r="%d" fill="var(--surface)"/>' % (cx, cy, 27))
        out.append(text(cx, cy + 5, "%.2f%%" % lose, 12, "middle", weight="700"))
        out.append(text(cx, cy - r - 10, label, 13, "middle"))
    out.append(rect(30, 160, 12, 10, "var(--accent)") + text(46, 169, "輸給整個市場的平均", 11))
    out.append(rect(200, 160, 12, 10, "var(--teal)") + text(216, 169, "贏過的", 11))
    out.append("</svg>")
    return "\n".join(out), "時間拉得越長，輸的比例越高。中途收掉的基金也算輸；15 年期只有 50.55% 撐到期末。美國市場、扣掉費用之後的比較，SPIVA 2025 年底報告。"


# ---------- §5 年內最大跌幅 vs 全年報酬（台股） ----------
def intra_year():
    rows = list(csv.DictReader(open(DATA / "algo_b_yearly.csv", encoding="utf-8")))
    ys = [(int(r["year"]), float(r["year_return_pct"]), -float(r["max_drawdown_pct"])) for r in rows]
    h = 300
    left, right, top, bottom = 34, 354, 30, 240
    vmax, vmin = 80, -62
    def py(v): return top + (bottom - top) * (vmax - v) / (vmax - vmin)
    n = len(ys)
    slot = (right - left) / n
    out = [svg_open(h, "台灣含息指數 2003 到 2025 年：每年的全年報酬（長條）與年內最大跌幅（圓點）")]
    for v in (-60, -40, -20, 0, 20, 40, 60, 80):
        out.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="%s"/>' % (left, py(v), right, py(v), "var(--ink)" if v == 0 else "var(--line)", 1.5 if v == 0 else 1))
        out.append(text(left - 4, py(v) + 4, "%d%%" % v, 10, "end", "var(--muted)"))
    for i, (yr, ret, dd) in enumerate(ys):
        x = left + i * slot + slot * 0.15
        bw = slot * 0.7
        y0, y1 = py(max(ret, 0)), py(min(ret, 0))
        out.append(rect(x, y0, bw, max(1, y1 - y0), "var(--muted)"))
        out.append(text(x + bw / 2, (y0 - 3) if ret >= 0 else (y1 + 10), "%d" % round(ret), 8, "middle", "var(--ink)"))
        out.append('<circle cx="%.1f" cy="%.1f" r="3" fill="var(--accent)" stroke="var(--surface)" stroke-width="1"/>' % (x + bw / 2, py(dd)))
        out.append(text(x + bw / 2, py(dd) + (11 if i % 2 == 0 else 20), "%d" % round(dd), 8, "middle", "var(--accent)"))
        if yr % 5 == 0 or yr == 2003:
            out.append(text(x + bw / 2, bottom + 14, "'%02d" % (yr % 100), 10, "middle", "var(--muted)"))
    out.append(rect(left, 264, 12, 10, "var(--muted)") + text(left + 16, 273, "全年報酬", 11))
    out.append('<circle cx="%d" cy="%d" r="4" fill="var(--accent)"/>' % (left + 110, 269) + text(left + 120, 273, "年內從高點最多跌掉", 11))
    out.append(text(left, 292, "證交所含息報酬指數自算；平均年內最多跌 17.73%，23 年裡 18 年為正", 10, "start", "var(--muted)"))
    out.append("</svg>")
    return "\n".join(out), "幾乎每一年中途都跌過一成以上，但多數年份年底是正的。跌是常態，不是警訊；最差的 2008 年整年跌 43.07%。"


# ---------- §5 區間浮動長條 ----------
def ranges():
    # JPM Guide to Retirement 2026 第 42 頁，1950–2025 曆年總報酬：股票／全部債券／一半一半／現金
    data = [("任何 1 年", (-37, 52), (-13, 33), (-16, 29), (0, 14)), ("任何 5 年", (-2, 29), (-2, 18), (2, 19), (0, 11)),
            ("任何 10 年", (-1, 20), (1, 14), (2, 16), (0, 9)), ("任何 20 年", (6, 18), (1, 11), (5, 14), (1, 8))]
    h = 272
    left, right, top, bottom = 8, 412, 24, 196
    vmax, vmin = 56, -42
    def py(v): return top + (bottom - top) * (vmax - v) / (vmax - vmin)
    out = [svg_open(h, "持有越久，最好與最差越靠近；一半債券讓最差那端縮小", 420)]
    out.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="var(--ink)" stroke-width="1.2"/>' % (left, py(0), right, py(0)))
    gw = (right - left) / 4
    tones = ("var(--amber)", "var(--muted)", "var(--teal)", "var(--line)")
    for i, (label, *cols) in enumerate(data):
        gx = left + i * gw
        for j, ((lo, hi), color) in enumerate(zip(cols, tones)):
            x = gx + 6 + j * 24
            out.append(rect(x, py(hi), 20, max(2, py(lo) - py(hi)), color))
            out.append(text(x + 10, py(hi) - 3, "%+d" % hi, 8.5, "middle", "var(--ink)"))
            out.append(text(x + 10, py(lo) + 10, "%+d" % lo, 8.5, "middle", "var(--ink)"))
        out.append(text(gx + gw / 2, bottom + 22, label, 12, "middle"))
    for k, (lab, tone) in enumerate((("全放股票", "var(--amber)"), ("全部債券", "var(--muted)"), ("一半股票一半債券", "var(--teal)"), ("現金", "var(--line)"))):
        x = left + k * 100
        out.append(rect(x, 234, 12, 10, tone) + text(x + 16, 243, lab, 10))
    out.append(text(left, 266, "美國 1950 到 2025 年，平均一年的報酬區間（%）；摩根「Guide to Retirement 2026」", 9, "start", "var(--muted)"))
    out.append("</svg>")
    return "\n".join(out), "往右看，最好和最差越來越近，但最差不是零。比較股票和一半一半，防守那一塊把最差的一年切掉一大半，也切掉一些最好的。這裡的債券是美國整體的投資等級債券（1976 年前用 Strategas/Ibbotson，之後用 Bloomberg Aggregate），2022 年股債同跌那一年已經算在裡面。"


# ---------- §6 五個人 ----------
def five_people():
    data = [(("精準買在", "最低點"), 186077), (("一拿到", "就投入"), 170555), (("分 12 個月", "慢慢投"), 166591), (("倒楣買在", "最高點"), 151343), (("一直等", "機會"), 47357)]
    h = 258
    left, top, bottom = 14, 36, 180
    vmax = 200000
    def py(v): return bottom - (bottom - top) * v / vmax
    out = [svg_open(h, "五個人 20 年後手上的美元")]
    for i, (label, v) in enumerate(data):
        x = left + i * 68
        out.append(rect(x + 8, py(v), 50, bottom - py(v), "var(--teal)" if i < 4 else "var(--muted)"))
        out.append(text(x + 33, py(v) - 5, format(v, ","), 10, "middle", weight="700"))
        out.append(text(x + 33, bottom + 14, label[0], 10, "middle"))
        out.append(text(x + 33, bottom + 26, label[1], 10, "middle"))
    out.append(text(left, 232, "每年各拿到 2,000 美元、美股 2005 到 2024 年", 10, "start", "var(--muted)"))
    out.append(text(left, 246, "80 段不同的 20 年裡，有 70 段排名相同", 10, "start", "var(--muted)"))
    out.append("</svg>")
    return "\n".join(out), "最會挑的只比一拿到就投入多約 9%；一直等的連三分之一都不到。差的是錢有沒有在裡面，不是買的時點。"


# ---------- §7 幸運兒／平凡人／倒楣鬼 ----------
def dca_high_low():
    rows = list(csv.DictReader(open(DATA / "algo_a_monthly_stats.csv", encoding="utf-8")))
    def run(key):
        units, series = 0.0, []
        for r in rows:
            units += 10000 / float(r[key])
            series.append(units * float(r["last_close"]))
        return series
    hi, lo = run("max"), run("min")
    assert abs(hi[-1] - 14703632.84) < 1 and abs(lo[-1] - 15780597.76) < 1, (hi[-1], lo[-1])
    n = len(rows)
    h = 250
    left, right, top, bottom = 44, 350, 14, 190
    ymax = 1700e4
    def px(i): return left + (right - left) * i / (n - 1)
    def py(v): return bottom - (bottom - top) * v / ymax
    out = [svg_open(h, "台股每月投 1 萬元，都買在當月最高與都買在當月最低，資產累積走勢")]
    for v in (0, 500e4, 1000e4, 1500e4):
        out.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="var(--line)" stroke-width="1" stroke-dasharray="2 4"/>' % (left, py(v), right, py(v)))
        out.append(text(left - 6, py(v) + 4, "%d 萬" % (v / 1e4) if v else "0", 10, "end", "var(--muted)"))
    for i, r in enumerate(rows):
        if int(r["month"]) == 1 and int(r["year"]) % 4 == 3:
            out.append(text(px(i), bottom + 14, r["year"], 10, "middle", "var(--muted)"))
    out.append(poly([(px(i), py(v)) for i, v in enumerate(lo)], "var(--teal)", 1.8))
    out.append(poly([(px(i), py(v)) for i, v in enumerate(hi)], "var(--accent)", 1.8))
    out.append(rect(left, 214, 12, 10, "var(--teal)") + text(left + 16, 223, "幸運兒：都買在當月最低", 11))
    out.append(rect(left + 160, 214, 12, 10, "var(--accent)") + text(left + 176, 223, "倒楣鬼：都買在當月最高", 11))
    out.append(text(left, 242, "證交所含息報酬指數 2003–2025 自算；兩條線幾乎疊在一起", 10, "start", "var(--muted)"))
    out.append("</svg>")
    table = """<table class="dca">
<thead><tr><th></th><th>幸運兒</th><th>平凡人</th><th>倒楣鬼</th></tr></thead>
<tbody>
<tr><th>買在</th><td>每月最低收盤</td><td>每月平均收盤</td><td>每月最高收盤</td></tr>
<tr><th>總投入</th><td>276 萬</td><td>276 萬</td><td>276 萬</td></tr>
<tr><th>期末資產</th><td>15,780,598 元</td><td>15,189,340 元</td><td>14,703,633 元</td></tr>
<tr><th>平均一年長</th><td>13.23%</td><td>12.97%</td><td>12.74%</td></tr>
</tbody></table>"""
    return "\n".join(out) + "\n" + table, "永遠最衰和永遠神準，二十三年下來只差 7.3%。要看的是兩條線的距離，不是高度：這 23 年事後看報酬偏高，換一段期間會不同。"


# ---------- §8 錯過最好的日子 ----------
def missing_days():
    data = [("全程持有", 80619), ("錯過最好的 10 天", 35866), ("錯過最好的 30 天", 13826)]
    h = 246
    left, top, bottom = 20, 40, 180
    vmax = 88000
    def py(v): return bottom - (bottom - top) * v / vmax
    out = [svg_open(h, "標普 500 含息，2006 到 2025 年投入 1 萬美元的結果")]
    for i, (label, v) in enumerate(data):
        x = left + i * 100
        out.append(rect(x + 14, py(v), 60, bottom - py(v), "var(--teal)" if i == 0 else "var(--muted)"))
        out.append(text(x + 44, py(v) - 6, "$" + format(v, ","), 11, "middle", weight="700"))
        out.append(text(x + 44, bottom + 16, label, 11, "middle"))
    out.append(text(left, 220, "10 個最好的日子裡，有 6 天落在最差的 10 天的兩週內。", 10, "start", "var(--muted)"))
    out.append(text(left, 236, "另一份資料算過另一邊：避開最差的 10 天，最後的錢多兩倍。", 10, "start", "var(--muted)"))
    out.append("</svg>")
    return "\n".join(out), "「先出來一下」的代價。最好的日子和最差的日子擠在一起，躲掉一邊就躲掉另一邊。"


# ---------- 沿用手冊的兩張 ----------
def handbook_figure(chapter_file, caption):
    s = (ROOT / "chapters" / chapter_file).read_text(encoding="utf-8")
    m = re.search(r"<figure class=\"chart\">\s*(<svg.*?</svg>)", s, re.S)
    if not m:
        raise SystemExit("找不到手冊圖：" + chapter_file)
    return m.group(1), caption


def smooth_vs_jagged():
    return handbook_figure("07-time-inflation-compounding.html",
                           "兩條線的終點一樣，走的路完全不同。你以為的複利是虛線，你真實經歷的是實線：三十年裡有九年是負的。")


def buckets():
    svg, cap = handbook_figure("09-rules-card.html",
                               "按「什麼時候要用」分成三桶。越快要用的錢，越不能跌；第三桶留白，由你自己填。")
    return svg.replace("看你第 8 章的答案", "由你自己填"), cap


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


def strip_all(s):
    return re.sub(r'\n?\s*<figure class="chart" data-chart="[^"]+">.*?</figure>', "", s, flags=re.S)


def insert(s, cid, anchor, mode, body, caption):
    i = s.find(anchor)
    if i < 0:
        return s, "找不到錨點：%s" % anchor
    end_tag = "</aside>" if mode == "aside" else "</p>"
    j = s.find(end_tag, i)
    if j < 0:
        return s, "錨點後找不到 %s" % end_tag
    j += len(end_tag)
    fig = ('\n\n    <figure class="chart" data-chart="%s">\n<div class="scroll">\n%s\n</div>\n      <figcaption>%s</figcaption>\n    </figure>'
           % (cid, body, esc(caption)))
    return s[:j] + fig + s[j:], None


def main():
    errors, files = [], {}
    for fn in sorted(SEC.glob("[0-9]*.html")):
        files[fn.name] = strip_all(fn.read_text(encoding="utf-8"))
    for cid, fn, anchor, mode, fn_chart in CHARTS:
        body, caption = fn_chart()
        files[fn], err = insert(files[fn], cid, anchor, mode, body, caption)
        if err:
            errors.append("%s：%s" % (cid, err))
        else:
            print("插入 %s → %s" % (cid, fn))
    for fn, s in files.items():
        (SEC / fn).write_text(s, encoding="utf-8")
    for e in errors:
        print("✗", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
