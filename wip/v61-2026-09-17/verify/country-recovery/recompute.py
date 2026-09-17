#!/usr/bin/env python3
"""裁判獨立重算 G9 country-recovery。不 import 起草者模組。

A. 用 html.parser 自己解析 guide/index.html #s4 表。
B. 兩種算法重算年數標籤（表上精度、到日精度），half-up。
C. 證交所 FMTQIK 逐日收盤：1990 收盤高點、2020 首度收盤超越、中間抽查。
D. FRED NIKKEI225 逐日：1989-12-29 收盤高點、首度收盤超越。
E. 美國含息 vs 價格：Shiller 月資料（月均價）＋ Damodaran 年資料（xlrd），看「含息版早多少」與「年度資料低估跌幅」。
F. 解析兩版 SVG：長條座標對年份、文字框估計重疊/超框、顏色只用設計系統變數。
G. 圖說、引導句、note、calc-results 的數字比對。
"""
import calendar, csv, json, re
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path("/Users/linyenchu/Cladue Code/family-finance")
HERE = Path(__file__).resolve().parent
W3 = ROOT / "wip/v61-2026-09-17/w3"


def hu(x, nd=0):
    return Decimal(str(x)).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)


# ---------------- A ----------------
class TableGrab(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_s4 = False; self.depth_sec = 0
        self.h3 = False; self.h3text = ""; self.want = False
        self.in_table = False; self.rows = []; self.cell = None; self.row = None; self.done = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section" and a.get("id") == "s4":
            self.in_s4 = True
        if not self.in_s4 or self.done:
            return
        if tag == "h3":
            self.h3 = True; self.h3text = ""
        if tag == "table" and self.want:
            self.in_table = True
        if self.in_table:
            if tag == "tr": self.row = []
            if tag in ("td", "th"): self.cell = ""

    def handle_endtag(self, tag):
        if not self.in_s4 or self.done:
            return
        if tag == "h3":
            self.h3 = False
            self.want = self.h3text.startswith("單一市場可能等很久")
            if self.want: self.heading = self.h3text
        if self.in_table:
            if tag in ("td", "th") and self.cell is not None:
                self.row.append(self.cell.strip()); self.cell = None
            if tag == "tr": self.rows.append(self.row)
            if tag == "table": self.in_table = False; self.done = True
        if tag == "section":
            self.in_s4 = False

    def handle_data(self, d):
        if self.h3: self.h3text += d
        if self.cell is not None: self.cell += d


guide = (ROOT / "guide/index.html").read_text(encoding="utf-8")
tg = TableGrab(); tg.feed(guide)
print("A. 表標題：", tg.heading)
for r in tg.rows: print("   ", r)
rows = {r[0]: r for r in tg.rows[1:]}

# ---------------- B ----------------
def ym(s):
    p = [int(x) for x in s.split("-")]
    return p


def months_month_prec(a, b):
    return (b[0] - a[0]) * 12 + (b[1] - a[1])


def ymd_diff(d0, d1):
    """整年、整月、剩日（日曆算法）＋總月數（剩日÷ 起算月的長度 與 ÷30.436 兩種）"""
    y = d1.year - d0.year; m = d1.month - d0.month; d = d1.day - d0.day
    if d < 0:
        m -= 1
        pm_y, pm_m = (d1.year, d1.month - 1) if d1.month > 1 else (d1.year - 1, 12)
        d += calendar.monthrange(pm_y, pm_m)[1]
    if m < 0:
        y -= 1; m += 12
    days = (d1 - d0).days
    return y, m, d, days, days / 30.436875


full_dates = {  # 一手出處的到日日期（supp-market-history.md、chapters/07 src-07-11、表上查核說明）
    "美國": (date(1929, 9, 3), date(1954, 11, 23)),
    "日本": (date(1989, 12, 29), date(2024, 2, 22)),
    "台灣": (date(1990, 2, 10), date(2020, 7, 27)),
}
B = {}
for k, r in rows.items():
    a_s, b_s = [x.strip() for x in r[1].split("→")]
    a, b = ym(a_s), ym(b_s)
    mm = months_month_prec(a, b)
    y, m, d, days, mo = ymd_diff(*full_dates[k])
    B[k] = dict(span=r[1], table=r[2], month_prec_months=mm, month_prec_years=round(mm / 12, 4),
                label_month_prec="約 %s 年" % hu(mm / 12),
                exact=f"{y} 年 {m} 個月 {d} 天", days=days, exact_years=round(days / 365.2425, 4),
                exact_months=round(mo, 3), label_exact_months="%d 年 %d 個月" % divmod(int(hu(mo)), 12),
                label_exact_years="約 %s 年" % hu(days / 365.2425))
    print("B.", k, B[k])

# ---------------- C ----------------
tw = json.loads((HERE / "twse_months.json").read_text())
def tw_rows():
    for k, data in sorted(tw.items()):
        for row in data or []:
            ry, rm, rd = [int(x) for x in row[0].strip().split("/")]
            yield date(ry + 1911, rm, rd), float(row[4].replace(",", ""))
tws = sorted(tw_rows())
pre = [x for x in tws if x[0] <= date(1990, 5, 31)]
mx = max(pre, key=lambda x: x[1])
print("C. 1989-06..1990-05 最高收盤：", mx)
first = next(x for x in tws if x[0] > date(1990, 6, 1) and x[1] > mx[1])
print("C. 1990 後首度收盤超越（抓到的月份裡）：", first)
for k in ("1997-08", "2000-02", "2018-01", "2018-10", "2019-04", "2019-11", "2019-12", "2020-01", "2020-06", "2020-07"):
    vals = [float(r[4].replace(",", "")) for r in tw[k]]
    print("   ", k, "月內最高收盤", max(vals))

# ---------------- D ----------------
nk = [(date.fromisoformat(r["observation_date"]), float(r["NIKKEI225"])) for r in csv.DictReader(open(HERE / "fred_nikkei225.csv")) if r["NIKKEI225"] not in ("", ".")]
nk_pre = [x for x in nk if x[0] <= date(1990, 12, 31)]
nmx = max(nk_pre, key=lambda x: x[1])
nfirst = next(x for x in nk if x[0] > nmx[0] and x[1] > nmx[1])
print("D. 日經 1990 年底前最高收盤：", nmx, "；首度收盤超越：", nfirst, ymd_diff(nmx[0], nfirst[0]))

# ---------------- E ----------------
sh = [(r["Date"][:7], float(r["SP500"]), float(r["Dividend"])) for r in csv.DictReader(open(ROOT / "research/data/shiller_sp_monthly.csv"))]
sh = [x for x in sh if "1925-01" <= x[0] <= "1960-12"]
pk = max((x for x in sh if x[0] <= "1932-12"), key=lambda x: x[1])
i0 = sh.index(pk)
p_rec = next(x for x in sh[i0 + 1:] if x[1] >= pk[1])
tr = 1.0; tr_rec = None; tr_series = []
for j in range(i0 + 1, len(sh)):
    prev, cur = sh[j - 1], sh[j]
    tr *= (cur[1] + cur[2] / 12) / prev[1]
    tr_series.append((cur[0], tr))
    if tr >= 1 and tr_rec is None:
        tr_rec = cur[0]
tr_perm = None
for j in range(len(tr_series)):
    if all(v >= 1 for _, v in tr_series[j:j + 1] ) and all(v >= 1 for _, v in tr_series[j:]):
        tr_perm = tr_series[j][0]; break
trough = min((x for x in sh[i0:] if x[0] <= "1933-12"), key=lambda x: x[1])
print("E. Shiller S&P 綜合（月均價）：高點", pk, "價格再回到", p_rec, "；含息首次回到", tr_rec, "；含息此後不再跌破", tr_perm,
      "；價格最低", trough, "跌幅 %.1f%%" % ((trough[1] / pk[1] - 1) * 100))

import xlrd
wb = xlrd.open_workbook(str(ROOT / "research/data/damodaran_histret.xls"))
s = wb.sheet_by_name("Returns by year")
ret = {}
for r in range(20, s.nrows):
    y = s.cell_value(r, 0)
    if isinstance(y, float) and 1928 <= y <= 2030 and isinstance(s.cell_value(r, 1), float):
        ret[int(y)] = s.cell_value(r, 1)
raw = wb.sheet_by_name("S&P 500 & Raw Data")
lvl = {int(raw.cell_value(r, 0)): raw.cell_value(r, 1) for r in range(2, raw.nrows) if isinstance(raw.cell_value(r, 0), float) and isinstance(raw.cell_value(r, 1), float)}
v = 1.0; tr_year = None
for y in range(1929, 1960):
    v *= 1 + ret[y]
    if v >= 1 and tr_year is None: tr_year = y
p_year = next(y for y in range(1930, 1970) if lvl[y] >= lvl[1928])
dd = min(lvl[y] for y in range(1929, 1935)) / lvl[1928] - 1
print("E. Damodaran 年資料：從 1928 年底算，含息首次回到年底", tr_year, "；價格（年底點位）回到", p_year,
      "；年底點位最大跌幅 %.1f%%（月/日資料 Dow 約 -89%%）" % (dd * 100))

# ---------------- F ----------------
html = (W3 / "country-recovery.html").read_text(encoding="utf-8")
svgs = re.findall(r'(<svg class="([dm])" viewBox="0 0 (\d+) (\d+)".*?</svg>)', html, re.S)
print("F. SVG 數：", len(svgs), [(k, w, h) for _, k, w, h in svgs])
colors = set(re.findall(r'(?:fill|stroke)="([^"]+)"', "".join(x[0] for x in svgs)))
print("F. 用到的顏色：", colors, "；swatch：", set(re.findall(r'background:([^";]+)', html)))
peaks = {"美國": (1929, 9, 1), "日本": (1989, 12, 29), "台灣": (1990, 2, 1)}
recs = {"美國": (1954, 11, 1), "日本": (2024, 2, 22), "台灣": (2020, 7, 1)}
def fy(t):
    y, m, d = t
    return y + (m - 1) / 12 + (d - 1) / calendar.monthrange(y, m)[1] / 12


def est_w(s, fs):
    w = 0
    for ch in s:
        if ord(ch) > 0x2E80: w += fs
        elif ch == " ": w += fs * 0.28
        elif ch in "→": w += fs * 1.0
        else: w += fs * 0.58
    return w


for svg, kind, W, H in svgs:
    W, H = int(W), int(H)
    mob = kind == "m"
    x0 = 12 if mob else 124; x1 = W - (14 if mob else 20)
    px = lambda yr: x0 + (x1 - x0) * (yr - 1925) / (2030 - 1925)
    rects = [tuple(map(float, m)) for m in re.findall(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', svg)]
    for (k, rc) in zip(["美國", "日本", "台灣"], rects):
        ex_a, ex_b = px(fy(peaks[k])), px(fy(recs[k]))
        print("   ", kind, k, "rect x=%.1f..%.1f  預期 %.1f..%.1f  差 %.2f/%.2f" % (rc[0], rc[0] + rc[2], ex_a, ex_b, rc[0] - ex_a, rc[0] + rc[2] - ex_b))
    boxes = []
    for x, y, fs, anc, s_ in re.findall(r'<text x="([\d.]+)" y="([\d.]+)" font-size="([\d.]+)" text-anchor="(\w+)"[^>]*>([^<]*)</text>', svg):
        x, y, fs = float(x), float(y), float(fs)
        w = est_w(s_, fs)
        l = x if anc == "start" else x - w if anc == "end" else x - w / 2
        boxes.append((l, y - fs * 0.8, l + w, y + fs * 0.2, s_))
    for r_ in rects:
        boxes.append((r_[0], r_[1], r_[0] + r_[2], r_[1] + r_[3], "[rect]"))
    bad = []
    for i, a in enumerate(boxes):
        if a[0] < 0 or a[2] > W or a[1] < 0 or a[3] > H:
            bad.append(("超框", a))
        for b_ in boxes[i + 1:]:
            if a[0] < b_[2] and b_[0] < a[2] and a[1] < b_[3] and b_[1] < a[3]:
                bad.append(("重疊", a[4], b_[4]))
    print("   ", kind, "估計重疊/超框：", bad if bad else "無")
    # 最小垂直間隙：上一列日期字 與 下一列年數標籤
    if not mob:
        ys = sorted(set(round(b[1], 1) for b in boxes if b[4] != "[rect]"))
        print("    d 文字列頂端 y：", ys)

# ---------------- G ----------------
cr = json.loads((ROOT / "lite/calc-results.json").read_text())["country_recovery"]
cap_nums = re.findall(r"figcaption>(.*?)</figcaption", html, re.S)
note_txt = re.findall(r'<p class="note">(.*?)</p>', html, re.S)
print("G. figcaption：", cap_nums)
print("G. note：", note_txt)
print("G. calc-results labels：", [(r["market"], r["years_label"], r["peak"], r["recover"]) for r in cr["rows"]])
