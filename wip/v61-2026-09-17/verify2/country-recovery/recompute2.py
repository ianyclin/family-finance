#!/usr/bin/env python3
"""裁判第二輪：country-recovery 獨立重算（不 import tools/v61_g9_country_recovery.py）。

原始資料（本資料夾，2026-09-17 重抓）：
  fed_1929.html                聯準會歷史頁 Stock Market Crash of 1929
  fred_nikkei_8524.csv         FRED NIKKEI225 1985-01..2024-03（前段用第一輪 verify/ 的完整檔確認 1985 以前）
  nippon_h01927.html           Nippon.com「34 years and 2 months」
  nikkei_tr.html               日經官方 Nikkei 225 Total Return 頁（含息版 2021-02）
  twse/fmtqik_YYYYMM.json      證交所 FMTQIK 逐日收盤 1990-01..1997-06、2020-07..09
  yahoo_twii_daily.json        Yahoo ^TWII 日收盤 1997-07..2020-07（只拿來確認中間沒有超過；邊界日用證交所）
  twse_19900201.json / twse_20200701.json  證交所 FMTQIK（抽查）
輸出：與預覽頁（fix/charts/country-recovery*.html）、lite/calc-results.json、指南 #s4 表逐項比對。
"""
import calendar, csv, datetime as dt, json, re
from decimal import Decimal, ROUND_HALF_UP
from html import unescape
from pathlib import Path

HERE = Path(__file__).resolve().parent
FF = HERE.parents[3]  # family-finance
V1 = FF / "wip/v61-2026-09-17/verify/country-recovery"
FIX = FF / "wip/v61-2026-09-17/fix/charts"
fails = []


def chk(cond, msg):
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


def hu(x, nd=0):
    return Decimal(repr(x)).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)


def flat(path):
    t = Path(path).read_text(encoding="utf-8", errors="ignore")
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", t)).split())


MONTHS = {m: i for i, m in enumerate(calendar.month_name) if m}

# ---------------------------------------------------------------- 美國
print("== 美國（聯準會歷史頁）")
fed = flat(HERE / "fed_1929.html")
m1 = re.search(r"peaked on (\w+) (\d+), (\d{4}), closing at (\d+\.\d+)", fed)
m2 = re.search(r"did not reach the 1929 high again until (\w+) (\d+), (\d{4})", fed)
us_peak = dt.date(int(m1.group(3)), MONTHS[m1.group(1)], int(m1.group(2)))
us_close = m1.group(4)
us_rec = dt.date(int(m2.group(3)), MONTHS[m2.group(1)], int(m2.group(2)))
print("  原文：", m1.group(0), "｜", m2.group(0))
chk((us_peak, us_close, us_rec) == (dt.date(1929, 9, 3), "381.17", dt.date(1954, 11, 23)), "美國 1929-09-03 收 381.17 → 1954-11-23")

# ---------------------------------------------------------------- 日本
print("== 日本（FRED NIKKEI225 收盤）")
def load_fred(p):
    out = []
    with open(p) as f:
        r = csv.reader(f); next(r)
        for d, v in r:
            if v not in ("", "."):
                out.append((dt.date.fromisoformat(d), float(v)))
    return out
nk = load_fred(HERE / "fred_nikkei_8524.csv")
nk_full = load_fred(V1 / "fred_nikkei225.csv")
pre = [x for x in nk_full if x[0] < dt.date(1985, 1, 1)]
print("  1985 以前最高收盤：", max(pre, key=lambda x: x[1]))
upto90 = [x for x in nk if x[0] <= dt.date(1990, 12, 31)]
jp_pk = max(upto90, key=lambda x: x[1])
jp_rc = next(x for x in nk if x[0] > jp_pk[0] and x[1] > jp_pk[1])
between = [x for x in nk if jp_pk[0] < x[0] < jp_rc[0]]
print("  高點", jp_pk, "；第一次收盤超越", jp_rc, "；中間最高", max(between, key=lambda x: x[1]))
chk((jp_pk[0], jp_rc[0]) == (dt.date(1989, 12, 29), dt.date(2024, 2, 22)), "日本 1989-12-29 → 2024-02-22")
chk(abs(jp_pk[1] - 38915.87) < 0.005 and abs(jp_rc[1] - 39098.68) < 0.005, "日本 38,915.87 → 39,098.68")
nip = flat(HERE / "nippon_h01927.html")
chk("34 years and 2 months" in nip, "Nippon.com 原文寫 34 years and 2 months")
ntr = flat(HERE / "nikkei_tr.html")
chk("dividend-included index reached its highest price ever in February 2021" in ntr, "日經官方：含息版 2021 年 2 月創歷史新高")

# ---------------------------------------------------------------- 台灣
print("== 台灣（證交所 FMTQIK 逐日收盤＋Yahoo ^TWII 中段）")
tw = {}
def roc(s):
    y, m, d = (int(x) for x in s.strip().split("/"))
    return dt.date(y + 1911, m, d)
for f in sorted((HERE / "twse").glob("fmtqik_*.json")) + [HERE / "twse_19900201.json", HERE / "twse_20200701.json"]:
    j = json.loads(f.read_text())
    for row in j.get("data", []):
        d, c = roc(row[0]), float(row[4].replace(",", ""))
        if d in tw:
            assert abs(tw[d] - c) < 1e-9, (d, tw[d], c)
        tw[d] = c
months_have = sorted({(d.year, d.month) for d in tw})
exp = [(y, m) for y in range(1990, 1998) for m in range(1, 13) if y * 100 + m <= 199706] + [(2020, 7), (2020, 8), (2020, 9)]
missing = [x for x in exp if x not in months_have]
chk(not missing, "證交所月份齊全（缺：%s）" % missing)
yj = json.loads((HERE / "yahoo_twii_daily.json").read_text())["chart"]["result"][0]
off = dt.timedelta(seconds=yj["meta"].get("gmtoffset", 28800))
yahoo = {}
for ts, c in zip(yj["timestamp"], yj["indicators"]["quote"][0]["close"]):
    if c is not None:
        yahoo[(dt.datetime(1970, 1, 1) + dt.timedelta(seconds=ts) + off).date()] = c
tw90 = {d: c for d, c in tw.items() if d.year == 1990}
tw_pk = max(tw90.items(), key=lambda x: x[1])
print("  1990 年最高收盤：", tw_pk)
chk(tw_pk == (dt.date(1990, 2, 10), 12495.34), "台灣 1990-02-10 收 12,495.34（1990 年最高收盤；證交所 FMTQIK 從 1990-01-04 起才有）")
mid_twse = {d: c for d, c in tw.items() if tw_pk[0] < d < dt.date(1997, 7, 1)}
mid_yahoo = {d: c for d, c in yahoo.items() if dt.date(1997, 7, 1) <= d < dt.date(2020, 7, 1)}
print("  1990-02-11..1997-06 證交所最高：", max(mid_twse.items(), key=lambda x: x[1]))
print("  1997-07..2020-06 Yahoo 最高：", max(mid_yahoo.items(), key=lambda x: x[1]), "（Yahoo 日數 %d）" % len(mid_yahoo))
chk(max(mid_twse.values()) < tw_pk[1] and max(mid_yahoo.values()) < tw_pk[1], "1990-02-10 到 2020-06 之間沒有收盤超過 12,495.34")
jul = sorted((d, c) for d, c in tw.items() if d >= dt.date(2020, 7, 1))
tw_rc = next(x for x in jul if x[1] > tw_pk[1])
print("  2020-07 起第一次收盤超越：", tw_rc, "；前一日：", [x for x in jul if x[0] < tw_rc[0]][-1])
chk(tw_rc[0] == dt.date(2020, 7, 27), "台灣 第一次收盤超越 2020-07-27")
# Yahoo 與證交所在 1997-07 以後有重疊的月份抽查（第一輪抓的 199708、200002、2018、2019-11..2020-12）
v1 = {}
for f in V1.glob("twse_*.json"):
    j = json.loads(f.read_text())
    for row in j.get("data", []) or []:
        v1[roc(row[0])] = float(row[4].replace(",", ""))
ov = [(d, v1[d], yahoo[d]) for d in v1 if d in yahoo]
mx = max(abs(a - b) for _, a, b in ov)
print("  Yahoo 與證交所重疊 %d 天，最大差 %.2f 點" % (len(ov), mx))
v1max = max((x for x in v1.items() if tw_pk[0] < x[0] < dt.date(2020, 7, 27)), key=lambda x: x[1])
print("  第一輪證交所月份中（1990-02-11..2020-07-26）最高：", v1max)

# ---------------------------------------------------------------- 期間
print("== 期間（三種算法，half-up）")
def ymd(a, b):
    y, m, d = b.year - a.year, b.month - a.month, b.day - a.day
    if d < 0:
        m -= 1
        pm = b.month - 1 or 12
        py = b.year if b.month > 1 else b.year - 1
        d += calendar.monthrange(py, pm)[1]
    if m < 0:
        y -= 1; m += 12
    return y, m, d
def add_months(a, n):
    y, m = divmod(a.month - 1 + n, 12)
    y += a.year; m += 1
    return dt.date(y, m, min(a.day, calendar.monthrange(y, m)[1]))
def months_calendar(a, b):
    """方法 1：整月數＋剩下天數÷（最後那段不足一月所在區間的天數：訖日前一個整月週年日 → 再下一個週年日）"""
    n = (b.year - a.year) * 12 + b.month - a.month
    if add_months(a, n) > b:
        n -= 1
    s, e = add_months(a, n), add_months(a, n + 1)
    return n + (b - s).days / (e - s).days
def months_days(a, b):
    return (b - a).days / (365.2425 / 12)

res = {}
for key, a, b in (("us", us_peak, us_rec), ("jp", jp_pk[0], jp_rc[0]), ("tw", tw_pk[0], tw_rc[0])):
    y, m, d = ymd(a, b)
    mc, md = months_calendar(a, b), months_days(a, b)
    # 方法 3：模組描述的算法（借訖日前一個月天數）— 自己照文字寫一次
    whole = (b.year - a.year) * 12 + (b.month - a.month)
    dd = b.day - a.day
    if dd < 0:
        whole -= 1
        pm = b.month - 1 or 12; py = b.year if b.month > 1 else b.year - 1
        dim = calendar.monthrange(py, pm)[1]; dd += dim
    else:
        dim = calendar.monthrange(b.year, b.month)[1]
    mt = whole + dd / dim
    labs = []
    for mm in (mc, md, mt):
        yrs = int(hu(mm / 12)); tot = int(hu(mm))
        labs.append((yrs, divmod(tot, 12), round(mm, 4), round(mm / 12, 4)))
    res[key] = dict(a=a, b=b, days=(b - a).days, ymd=(y, m, d), labs=labs, mt=mt)
    print("  %s %s → %s：%d 天；%d 年 %d 個月 %d 天" % (key, a, b, (b - a).days, y, m, d))
    for name, l in zip(("週年日法", "天數÷30.44", "模組文字所述"), labs):
        print("     %-10s 月數 %.4f  年數 %.4f  → 約 %d 年；總月數 half-up 拆成 %d 年 %d 個月" % (name, l[2], l[3], l[0], l[1][0], l[1][1]))
    chk(len({(l[0], l[1]) for l in labs}) == 1, "%s 三種算法的年標籤與年月標籤一致" % key)

US = res["us"]["labs"][2]; JP = res["jp"]["labs"][2]; TW = res["tw"]["labs"][2]
lab_us, lab_tw = "約 %d 年" % US[0], "約 %d 年" % TW[0]
lab_jp = "%d 年 %d 個月" % JP[1]
chk((lab_us, lab_jp, lab_tw) == ("約 25 年", "34 年 2 個月", "約 30 年"), "標籤：%s／%s／%s" % (lab_us, lab_jp, lab_tw))
chk((US[2], US[3], JP[2], JP[3], TW[2], TW[3]) == (302.6667, 25.2222, 409.7742, 34.1478, 365.5484, 30.4624),
    "修的人說明裡的月數與年數（302.6667/25.2222、409.7742/34.1478、365.5484/30.4624）")
chk((US[1], TW[1]) == ((25, 3), (30, 6)), "若美國、台灣也標到月：25 年 3 個月、30 年 6 個月")
chk((str(hu(US[3], 2)), str(hu(JP[3], 2)), str(hu(TW[3], 2))) == ("25.22", "34.15", "30.46"), "關鍵數字清單 25.22／34.15／30.46 年")

# 長條位置
def frac_mod(d):
    return d.year + (d.month - 1) / 12 + (d.day - 1) / calendar.monthrange(d.year, d.month)[1] / 12
def frac_doy(d):
    return d.year + (d.timetuple().tm_yday - 1) / (366 if calendar.isleap(d.year) else 365)
print("== 長條位置（小數年份）")
for k in ("us", "jp", "tw"):
    for d in (res[k]["a"], res[k]["b"]):
        print("  %s %s  月日換算 %.4f  年內日序 %.4f  差 %.4f 年" % (k, d, frac_mod(d), frac_doy(d), frac_mod(d) - frac_doy(d)))
chk(max(abs(frac_mod(d) - frac_doy(d)) for k in res for d in (res[k]["a"], res[k]["b"])) < 0.01, "兩種換算差不到 0.01 年（桌面約 0.08px）")

# ---------------------------------------------------------------- calc-results
print("== lite/calc-results.json")
cr = json.loads((FF / "lite/calc-results.json").read_text())["country_recovery"]
rows = {r["key"]: r for r in cr["rows"]}
for k, lab in (("us", lab_us), ("jp", lab_jp), ("tw", lab_tw)):
    r = rows[k]; R = res[k]
    chk((r["peak"], r["recover"]) == (R["a"].isoformat(), R["b"].isoformat()), "%s 起訖 %s → %s" % (k, r["peak"], r["recover"]))
    chk(r["years_label"] == lab, "%s 標籤 %s" % (k, r["years_label"]))
    chk(abs(r["months_exact"] - R["mt"]) < 1e-4 and r["months_rounded"] == int(hu(R["mt"])), "%s months_exact/rounded" % k)
    chk(abs(r["peak_frac_year"] - round(frac_mod(R["a"]), 4)) < 1e-9 and abs(r["recover_frac_year"] - round(frac_mod(R["b"]), 4)) < 1e-9, "%s frac_year" % k)
chk(rows["jp"]["total_return_first_year"] == 2021, "日本含息年份 2021")
chk((cr["axis_from"], cr["axis_to"]) == (1925, 2030), "軸 1925–2030，涵蓋 %.2f..%.2f" % (frac_mod(us_peak), frac_mod(jp_rc[0])))

# ---------------------------------------------------------------- 預覽頁
print("== 預覽頁文字與 SVG")
for fn, mob in (("country-recovery.html", False), ("country-recovery-mobile.html", True)):
    h = (FIX / fn).read_text(encoding="utf-8")
    fig = h[h.find("<figure"):]
    title = unescape(re.search(r'chart-title">(.*?)<', fig).group(1))
    sub = unescape(re.search(r'chart-sub">(.*?)<', fig).group(1))
    cap = unescape(re.search(r"<figcaption>(.*?)</figcaption>", fig, re.S).group(1))
    note = unescape(re.search(r'<p class="note">(.*?)</p>', fig, re.S).group(1))
    if not mob:
        print("  title:", title); print("  sub:", sub); print("  caption:", cap); print("  note:", note)
        chk("美國%s、日本 %s、台灣%s" % (lab_us, lab_jp, lab_tw) in cap, "圖說三個期間")
        chk("日本含息版 2021 年就先過了高點（價格版是 %d 年）" % jp_rc[0].year in note, "note 含息 2021／價格版 2024")
        chk('class="legend"' not in fig and "只到月" not in fig and "還沒回到買進時的點位" not in fig and "早一些" not in fig, "沒有圖例、沒有「只到月」、沒有投資人那句、沒有「早一些」")
        nums = sorted(set(re.findall(r"\d+(?:[.,]\d+)*", title + sub + cap + note)))
        print("  圖說／note／標題裡出現的所有數字：", nums)
    svg_kind = "m" if mob else "d"
    svg = re.search(r'<svg class="%s".*?</svg>' % svg_kind, fig, re.S).group(0)
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    texts = [unescape(t) for t in re.findall(r"<text[^>]*>(.*?)</text>", svg)]
    rects = [tuple(float(x) for x in re.search(r'x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', r).groups())
             for r in re.findall(r"<rect[^>]*>", svg)]
    print("  [%s] viewBox %s；texts：%s" % (svg_kind, vb, texts))
    W = vb[2]; x0 = 12 if mob else 124; x1 = W - (14 if mob else 20)
    px = lambda yr: x0 + (x1 - x0) * (yr - 1925) / 105
    bars = [r for r in rects if r[3] in (14.0, 16.0)]
    for k, r in zip(("us", "jp", "tw"), bars):
        ea, eb = px(frac_mod(res[k]["a"])), px(frac_mod(res[k]["b"]))
        chk(abs(r[0] - ea) < 0.15 and abs(r[0] + r[2] - eb) < 0.15, "[%s] %s 長條 x=%.1f..%.1f（應 %.2f..%.2f）" % (svg_kind, k, r[0], r[0] + r[2], ea, eb))
    for k in ("us", "jp", "tw"):
        s = "%s → %s" % (res[k]["a"], res[k]["b"])
        chk(s in texts, "[%s] 日期字串 %s" % (svg_kind, s))
    ticks = [t for t in texts if re.fullmatch(r"\d{4}", t)]
    chk(ticks == [str(t) for t in range(1925, 2031) if t % (20 if mob else 10) == 0], "[%s] 刻度 %s" % (svg_kind, ticks))

# ---------------------------------------------------------------- 指南 #s4 表
print("== 指南 #s4 表")
g = (FF / "guide/index.html").read_text(encoding="utf-8")
t = re.search(r"<h3>單一市場可能等很久.*?</table>", g, re.S).group(0)
trs = [[" ".join(unescape(re.sub(r"<[^>]+>", "", c)).split()) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)] for tr in re.findall(r"<tr>(.*?)</tr>", t, re.S)]
trs = [r for r in trs if r]
for r in trs:
    print("  ", r[:3])
tab = {r[0]: r for r in trs}
chk(tab["美國"][1:3] == ["1929-09 → 1954-11", "25 年"], "表 美國 1929-09 → 1954-11、25 年（算出 %.2f 年）" % US[3])
chk(tab["日本"][1:3] == ["1989-12-29 → 2024-02-22", lab_jp], "表 日本 = 圖 %s" % lab_jp)
chk(tab["台灣"][1:3] == ["1990-02 → 2020-07", lab_tw], "表 台灣 = 圖 %s" % lab_tw)
chk("1990-02-10 收 12,495.34，2020-07-27 首度收盤超越" in tab["台灣"][3] and "含息版 2021 年先過高點" in tab["日本"][3], "表查核說明欄與重算一致")

print("\nFAILS:", len(fails))
for f in fails:
    print(" -", f)
