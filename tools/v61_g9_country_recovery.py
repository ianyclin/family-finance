#!/usr/bin/env python3
"""G9 替代方案 A：第 7 節「單一市場可能等很久」三段期間 → 三條共用年份軸的時間軸長條（calc_key: country_recovery）。

資料來源（不是新資料，是指南已查核過的三筆事實；寫死成下面的 ROWS 常數，不再讀 guide/index.html）：
  美國：聯準會歷史頁（Federal Reserve History, "Stock Market Crash of 1929"），道瓊工業指數價格。
        原文「the index peaked on September 3, 1929, closing at 381.17」
        「did not reach the 1929 high again until November 23, 1954」。
        查核紀錄：research/supp-market-history.md 第 129–137 行。
  日本：日經官方，日經 225 價格指數，1989-12-29 → 2024-02-22；
        含息版 2021 年 2 月先過高點（research/supp-market-history.md 第 92–98 行）。
  台灣：證交所發行量加權股價指數逐日收盤，1990-02-10 收 12,495.34 → 2020-07-27 第一次收盤超越；
        含息版沒有官方數字（指南 #s4 表的查核說明欄）。
  另見 chapters/07-time-inflation-compounding.html 的 src-07-11。
口徑：
  - 三條都是價格指數（不含股利）、名目、各自幣別；沒有扣物價、費用和稅。
  - 長條終點是「第一次收盤超過舊高點」，不代表之後不會再跌回舊高點以下。
  - 三個指數、幣別不同，不能直接比快慢；這三段是挑出來的著名例子，不是平均。
演算法：
  1. 起訖都是收盤日（到日）。
  2. 經過月數 = 整月數 + 剩下天數 ÷ 一個月的天數（訖日的日 < 起日的日時借訖日前一個月的天數，否則用訖日那個月）。
  3. 標籤粒度跟指南 #s4 表「約多久」那一欄一致：表上寫到月的（日本）顯示「X 年 Y 個月」（總月數 half-up 後拆年、月）；
     表上只寫年的（美國、台灣）顯示「約 N 年」（月數 ÷ 12 後 half-up）。
  4. 指南 #s4 表還在時才比對：表上年（與月）的數字必須等於算出來的，表上起訖（只到月的）必須是日期的前綴；
     不一致就 raise，不自己改數字。表不在或標題改了，就不比對，只在結果裡記一筆 table_check。
  5. 長條位置用「年 + (月-1)/12 + (日-1)/當月天數/12」換算成小數年份。
只用標準庫。
"""
import calendar
import re
from decimal import Decimal, ROUND_HALF_UP
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / "guide" / "index.html"

AXIS_FROM, AXIS_TO = 1925, 2030

# 三列事實（出處與查核見檔頭）。granularity：指南表上「約多久」寫到哪一層（year／month）。
ROWS = [
    dict(key="us", market="美國", index="道瓊工業指數", source="聯準會歷史頁（Federal Reserve History）",
         url="https://www.federalreservehistory.org/essays/stock-market-crash-of-1929",
         peak="1929-09-03", recover="1954-11-23", granularity="year", total_return_first_year=None),
    dict(key="jp", market="日本", index="日經 225 指數", source="日經官方（Nikkei Inc.）", url=None,
         peak="1989-12-29", recover="2024-02-22", granularity="month", total_return_first_year=2021),
    dict(key="tw", market="台灣", index="加權股價指數", source="臺灣證券交易所逐日收盤", url=None,
         peak="1990-02-10", recover="2020-07-27", granularity="year", total_return_first_year=None),
]
TABLE_HEAD_PREFIX = "單一市場可能等很久"


def half_up(x, nd=0):
    q = Decimal(1).scaleb(-nd)
    return Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP)


def _plain(s):
    return unescape(re.sub(r"<[^>]+>", "", s)).strip()


def read_table():
    """回傳 {市場: (起訖文字, 約多久文字)}；表不在就回 None（不 raise）。"""
    try:
        html = GUIDE.read_text(encoding="utf-8")
    except OSError:
        return None
    i = html.find('id="s4"')
    if i < 0:
        return None
    j = html.find("<section", i + 10)
    sec = html[i:j if j > 0 else len(html)]
    m = re.search(r'<h3>%s.*?</h3>.*?<table[^>]*>(.*?)</table>' % TABLE_HEAD_PREFIX, sec, re.S)
    if not m or "<tbody>" not in m.group(1):
        return None
    out = {}
    for tr in re.findall(r"<tr>(.*?)</tr>", m.group(1).split("<tbody>", 1)[1], re.S):
        cells = [_plain(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(cells) >= 3:
            out[cells[0]] = (cells[1], cells[2])
    return out


def parse_date(s):
    y, m, d = (int(x) for x in s.split("-"))
    return dict(text=s, y=y, m=m, d=d)


def frac_year(dt):
    return dt["y"] + (dt["m"] - 1) / 12 + (dt["d"] - 1) / calendar.monthrange(dt["y"], dt["m"])[1] / 12


def months_between(a, b):
    whole = (b["y"] - a["y"]) * 12 + (b["m"] - a["m"])
    days = b["d"] - a["d"]
    if days < 0:
        whole -= 1
        py, pm = (b["y"], b["m"] - 1) if b["m"] > 1 else (b["y"] - 1, 12)
        dim = calendar.monthrange(py, pm)[1]
        days += dim
    else:
        dim = calendar.monthrange(b["y"], b["m"])[1]
    return whole + days / dim


def compute():
    table = read_table()
    out, checks = [], []
    for r in ROWS:
        a, b = parse_date(r["peak"]), parse_date(r["recover"])
        months = months_between(a, b)
        tot = int(half_up(months))
        years_int = int(half_up(months / 12))
        if r["granularity"] == "month":
            yy, mm = divmod(tot, 12)
            label, computed = "%d 年 %d 個月" % (yy, mm), [yy, mm]
        else:
            label, computed = "約 %d 年" % years_int, [years_int]
        row = dict(r, date_precision="day",
                   peak_frac_year=round(frac_year(a), 4), recover_frac_year=round(frac_year(b), 4),
                   months_exact=round(months, 4), years_exact=round(months / 12, 4),
                   months_rounded=tot, years_label=label, years_int=computed[0],
                   months_rem=computed[1] if len(computed) > 1 else None)
        if table is not None:
            if r["market"] not in table:
                raise RuntimeError("#s4 表還在，但找不到「%s」那一列" % r["market"])
            span, dur = table[r["market"]]
            t_a, t_b = [x.strip() for x in span.split("→")]
            if not (r["peak"].startswith(t_a) and r["recover"].startswith(t_b)):
                raise RuntimeError("%s：表上起訖「%s」和 %s → %s 不一致" % (r["market"], span, r["peak"], r["recover"]))
            nums = [int(x) for x in re.findall(r"\d+", dur)]
            if nums != computed:
                raise RuntimeError("%s：算出 %s，表上寫「%s」，不一致" % (r["market"], computed, dur))
            row["table_span_text"], row["table_duration_text"] = span, dur
            checks.append("%s 相符" % r["market"])
        out.append(row)
    return dict(
        calc_key="country_recovery",
        source=("模組常數（聯準會歷史頁、日經官方、證交所逐日收盤；查核見 research/supp-market-history.md、"
                "chapters/07 src-07-11、指南 #s4 表查核說明欄）"),
        table_check=("指南 #s4 表：" + "、".join(checks)) if table is not None else "指南 #s4 表不在，未比對",
        basis="價格指數（不含股利）、名目、各自幣別；沒有扣物價、費用和稅",
        endpoint="高點＝當時最高的收盤；終點＝第一次收盤超過它",
        selection="著名的挑出來的例子，不是平均",
        axis_from=AXIS_FROM, axis_to=AXIS_TO,
        rule=("起訖都到日；經過月數＝整月數＋剩下天數÷當月天數；表上寫到月的顯示「X 年 Y 個月」（總月數 half-up），"
              "表上只寫年的顯示「約 N 年」（月數÷12 half-up）；表還在時必須等於表上的數字"),
        rows=out,
    )


# ======================================================================
def chart(res):
    import essay_charts as E

    rows = res["rows"]
    a0, a1 = res["axis_from"], res["axis_to"]
    by_key = {r["key"]: r for r in rows}
    us, jp, tw = by_key["us"], by_key["jp"], by_key["tw"]

    def span_w(s, size):   # 估字寬：數字與「-」約 0.56em，箭頭與空白約 1em
        return sum(size * (0.56 if ch.isdigit() or ch == "-" else 1.0 if ch == "→" else 0.3) for ch in s)

    def draw(lay):
        mob = lay.mobile
        x0 = 12 if mob else 124
        x1 = lay.W - (14 if mob else 20)
        px = lambda yr: x0 + (x1 - x0) * (yr - a0) / (a1 - a0)
        rh = 50 if mob else 58
        bh = 14 if mob else 16
        top = 6
        axis_y = top + len(rows) * rh + 4
        h = int(axis_y + (20 if mob else 22))
        step = 20 if mob else 10
        ticks = [t for t in range(a0, a1 + 1) if t % step == 0]
        out = [E.svg_open(lay, h, "美國、日本、台灣三個市場，價格指數從歷史高點到第一次收盤再創新高各花了多久")]
        out.append(E.hline(x0, x1, axis_y, E.INK, 1.1, None))
        for t in ticks:   # 只畫軸上的短刻度，不畫直向格線（設計系統：沒有直向軸線，也免得穿過日期字）
            out.append(E.poly([(px(t), axis_y), (px(t), axis_y + 4)], E.INK, 1.1))
            out.append(E.text(px(t), axis_y + (15 if mob else 17), str(t), lay.fs, "middle", E.MUTED))
        for i, r in enumerate(rows):
            y = top + i * rh
            xa, xb = px(r["peak_frac_year"]), px(r["recover_frac_year"])
            dates = "%s → %s" % (r["peak"], r["recover"])
            by = y + 20
            if mob:
                ly = y + 13
                out.append(E.text(x0, ly, "%s　%s" % (r["market"], r["years_label"]), lay.f, "start", E.INK, "800"))
                out.append(E.text(x1, ly, dates, lay.fs, "end", E.MUTED))
                out.append(E.rect(xa, by, xb - xa, bh, E.TEAL, 3))
            else:
                out.append(E.text(4, y + 30, r["market"], lay.f, "start", E.INK, "800"))
                out.append(E.text(4, y + 45, r["index"], lay.fs, "start", E.MUTED))
                out.append(E.text((xa + xb) / 2, y + 14, r["years_label"], lay.fl, "middle", E.INK, "800"))
                out.append(E.rect(xa, by, xb - xa, bh, E.TEAL, 3))
                # 起訖日期合成一串、置中在長條下方；美國那條太短放不下兩端各一個日期，所以統一這樣排
                w = span_w(dates, lay.fs)
                cx = min(max((xa + xb) / 2, x0 + w / 2), x1 - w / 2)
                out.append(E.text(cx, by + bh + 13, dates, lay.fs, "middle", E.MUTED))
        out.append("</svg>")
        return "\n".join(out)

    parts = [
        "三條都是價格指數（不含股利）、名目、各自幣別，沒有扣物價、費用和稅。",
        "美國：道瓊工業指數，聯準會歷史頁；日本：日經 225 指數，日經官方；台灣：加權股價指數，證交所逐日收盤。",
        "日期都是收盤日。長條畫到第一次收盤超過舊高點；之後還是可能再跌回舊高點以下。",
    ]
    if jp.get("total_return_first_year"):   # 常數寫死，不會是 None；保險起見缺了就整句不寫
        parts.append("含息版會比較早回到高點：日本含息版 %d 年就先過了高點（價格版是 %s 年）；美國、台灣本文沒有含息版的日期。"
                     % (jp["total_return_first_year"], jp["recover"][:4]))
    parts.append("三個指數、幣別不同，不能直接比快慢。")
    nt = E.note("".join(parts))
    return dict(
        title="單押一個市場，回到高點等了多久：三個著名例子",
        sub="美國、日本、台灣的價格指數（不含股利），從歷史高點到第一次收盤再創新高",
        svgs=[draw(E.L("d")), draw(E.L("m"))], extras=nt,
        caption=("每一條是一個市場的價格指數，從當時最高的收盤，到第一次收盤超過它為止：美國%s、日本 %s、台灣%s。"
                 "這是三個挑出來的例子，不是每次下跌都這麼久，也不代表下跌一定回得來。")
        % (us["years_label"], jp["years_label"], tw["years_label"]),
    )


if __name__ == "__main__":
    import json
    print(json.dumps(compute(), ensure_ascii=False, indent=2))
