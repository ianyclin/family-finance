#!/usr/bin/env python3
"""G9 替代方案 A：第 4 節「高點到再創高」表 → 三條共用年份軸的時間軸長條（calc_key: country_recovery）。

資料來源（不是新資料，是把指南已查核過的那張表畫成圖）：
  - 唯一讀取的檔：guide/index.html 的 #s4，裡面 data-card「單一市場可能等很久」那張表。
    表上三列的一手出處（查核紀錄在 research/supp-market-history.md）：
      美國：聯準會歷史頁（Federal Reserve History, "Stock Market Crash of 1929"），道瓊工業指數價格，
            1929-09（9/3 收 381.17）→ 1954-11（11/23 收回）。
      日本：日經官方，日經 225 價格指數，1989-12-29 → 2024-02-22；含息版 2021 年先過高點。
      台灣：證交所發行量加權股價指數逐日收盤，1990-02 → 2020-07；含息版沒有官方數字。
口徑：
  - 三條都是價格指數（不含股利）、名目、各自幣別；沒有扣物價、費用和稅。
  - 三個指數、幣別、日期精度不同（美國、台灣只到月，日本到日），不能直接比快慢。
  - 這三段是著名的挑出來的例子，不是平均，也不是所有市場跌下去都回得來的證據。
演算法：
  1. 從 #s4 的表抓三列（市場、「起 → 訖」、表上寫的「約多久」、查核說明）。
  2. 起訖日期只到月的，那一端的日當作 1 號；兩端都到日的，照實際日數。
  3. 經過月數 = 整月數 + 剩下天數 ÷ 一個月的天數（訖日的日 < 起日的日時借訖日前一個月的天數，否則用訖日那個月；只有兩端都到日才有小數）。
  4. 兩端都到日 → 顯示「X 年 Y 個月」（總月數 half-up 取整後拆年、月）；
     只到月 → 顯示「約 N 年」（月數 ÷ 12 後 half-up 取整）。
  5. 算出來的年（與月）必須和表上「約多久」那一欄的數字一模一樣，不一樣就 raise，不自己改數字。
  6. 長條位置用「年 + (月-1)/12 + (日-1)/當月天數/12」換算成小數年份。
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

# 表上沒寫、但圖上要標的指數名稱（出處與查核在 research/supp-market-history.md）
META = {
    "美國": dict(key="us", index="道瓊工業指數", source="聯準會歷史頁（Federal Reserve History）",
               url="https://www.federalreservehistory.org/essays/stock-market-crash-of-1929"),
    "日本": dict(key="jp", index="日經 225 指數", source="日經官方（Nikkei Inc.）", url=None),
    "台灣": dict(key="tw", index="加權股價指數", source="臺灣證券交易所逐日收盤", url=None),
}


def half_up(x, nd=0):
    q = Decimal(1).scaleb(-nd)
    return Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP)


def _plain(s):
    return unescape(re.sub(r"<[^>]+>", "", s)).strip()


def read_table():
    html = GUIDE.read_text(encoding="utf-8")
    i = html.find('id="s4"')
    if i < 0:
        raise RuntimeError("guide/index.html 找不到 #s4")
    j = html.find("<section", i + 10)
    sec = html[i:j if j > 0 else len(html)]
    m = re.search(r'<div class="data-card"><h3>(單一市場可能等很久.*?)</h3>.*?<table[^>]*>(.*?)</table>', sec, re.S)
    if not m:
        raise RuntimeError("#s4 找不到「單一市場可能等很久」那張表")
    heading, table = _plain(m.group(1)), m.group(2)
    head = [_plain(c) for c in re.findall(r"<th>(.*?)</th>", table, re.S)]
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", table.split("<tbody>", 1)[1], re.S):
        cells = [_plain(c) for c in re.findall(r"<td>(.*?)</td>", tr, re.S)]
        rows.append(cells)
    return heading, head, rows


def parse_date(s):
    p = [int(x) for x in s.split("-")]
    return dict(text=s, y=p[0], m=p[1], d=p[2] if len(p) == 3 else None)


def frac_year(dt):
    d = dt["d"] or 1
    return dt["y"] + (dt["m"] - 1) / 12 + (d - 1) / calendar.monthrange(dt["y"], dt["m"])[1] / 12


def months_between(a, b):
    whole = (b["y"] - a["y"]) * 12 + (b["m"] - a["m"])
    if a["d"] is None or b["d"] is None:
        return float(whole), "month"
    days = b["d"] - a["d"]
    if days < 0:
        whole -= 1
        py, pm = (b["y"], b["m"] - 1) if b["m"] > 1 else (b["y"] - 1, 12)
        dim = calendar.monthrange(py, pm)[1]
        days += dim
    else:
        dim = calendar.monthrange(b["y"], b["m"])[1]
    return whole + days / dim, "day"


def compute():
    heading, head, rows = read_table()
    out = []
    for cells in rows:
        market, span, dur, check = cells
        a_s, b_s = [x.strip() for x in span.split("→")]
        a, b = parse_date(a_s), parse_date(b_s)
        months, precision = months_between(a, b)
        table_nums = [int(x) for x in re.findall(r"\d+", dur)]
        if precision == "day":
            tot = int(half_up(months))
            yy, mm = divmod(tot, 12)
            label = "%d 年 %d 個月" % (yy, mm)
            computed = [yy, mm]
        else:
            yy = int(half_up(months / 12))
            label = "約 %d 年" % yy
            computed = [yy]
        if computed != table_nums:
            raise RuntimeError("%s：算出 %s，表上寫「%s」，不一致" % (market, computed, dur))
        tr = re.search(r"含息版\s*(\d{4})\s*年先過高點", check)
        meta = META[market]
        out.append(dict(
            key=meta["key"], market=market, index=meta["index"], source=meta["source"], url=meta["url"],
            peak=a_s, recover=b_s, date_precision=precision,
            peak_frac_year=round(frac_year(a), 4), recover_frac_year=round(frac_year(b), 4),
            months_exact=round(months, 4), years_exact=round(months / 12, 4),
            years_label=label, years_int=computed[0], months_rem=computed[1] if len(computed) > 1 else None,
            table_duration_text=dur, table_check_text=check,
            total_return_first_year=int(tr.group(1)) if tr else None,
        ))
    return dict(
        calc_key="country_recovery",
        source="guide/index.html #s4 表「%s」（一手出處見各列 source 與 research/supp-market-history.md）" % heading,
        table_heading=heading, table_columns=head,
        basis="價格指數（不含股利）、名目、各自幣別；沒有扣物價、費用和稅",
        selection="著名的挑出來的例子，不是平均",
        axis_from=AXIS_FROM, axis_to=AXIS_TO,
        rule=("經過月數＝整月數＋剩下天數÷當月天數（只有兩端都到日才有小數）；兩端到日顯示「X 年 Y 個月」"
              "（總月數 half-up），只到月顯示「約 N 年」（月數÷12 half-up）；必須等於表上的數字"),
        rows=out,
    )


# ======================================================================
def chart(res):
    import essay_charts as E

    rows = res["rows"]
    a0, a1 = res["axis_from"], res["axis_to"]
    jp = next(r for r in rows if r["key"] == "jp")

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
        out = [E.svg_open(lay, h, "美國、日本、台灣三個市場，價格指數從歷史高點到再創新高各花了多久")]
        out.append(E.hline(x0, x1, axis_y, E.INK, 1.1, None))
        for t in ticks:   # 只畫軸上的短刻度，不畫直向格線（設計系統：沒有直向軸線，也免得穿過日期字）
            out.append(E.poly([(px(t), axis_y), (px(t), axis_y + 4)], E.INK, 1.1))
            out.append(E.text(px(t), axis_y + (15 if mob else 17), str(t), lay.fs, "middle", E.MUTED))
        for i, r in enumerate(rows):
            y = top + i * rh
            xa, xb = px(r["peak_frac_year"]), px(r["recover_frac_year"])
            if mob:
                ly = y + 13
                out.append(E.text(x0, ly, "%s　%s" % (r["market"], r["years_label"]), lay.f, "start", E.INK, "800"))
                out.append(E.text(x1, ly, "%s → %s" % (r["peak"], r["recover"]), lay.fs, "end", E.MUTED))
                by = y + 20
                out.append(E.rect(xa, by, xb - xa, bh, E.TEAL, 3))
            else:
                out.append(E.text(4, y + 30, r["market"], lay.f, "start", E.INK, "800"))
                out.append(E.text(4, y + 45, r["index"], lay.fs, "start", E.MUTED))
                by = y + 20
                out.append(E.text((xa + xb) / 2, y + 14, r["years_label"], lay.fl, "middle", E.INK, "800"))
                out.append(E.rect(xa, by, xb - xa, bh, E.TEAL, 3))
                out.append(E.text(xa, by + bh + 13, r["peak"], lay.fs, "start", E.MUTED))
                out.append(E.text(xb, by + bh + 13, r["recover"], lay.fs, "end", E.MUTED))
        out.append("</svg>")
        return "\n".join(out)

    lg = E.legend([(E.TEAL, "價格指數從歷史高點，到收盤再回到那個高點")])
    nt = E.note(
        "三條都是價格指數（不含股利）、名目、各自幣別，沒有扣物價、費用和稅。"
        "美國：道瓊工業指數，聯準會歷史頁；日本：日經 225 指數，日經官方；台灣：加權股價指數，證交所逐日收盤。"
        "美國、台灣的日期只到月，日本到日。含息版會早一些：日本含息版 %d 年就先過了高點；台灣含息版沒有官方數字。"
        "三個指數、幣別不同，不能直接比快慢。這三段是挑出來的著名例子，不是平均；歷史不是保證。"
        % jp["total_return_first_year"])
    us, tw = (next(r for r in rows if r["key"] == k) for k in ("us", "tw"))
    return dict(
        title="單押一個市場，回到高點等了多久：三個著名例子",
        sub="美國、日本、台灣的價格指數（不含股利），從歷史高點到再創新高",
        svgs=[draw(E.L("d")), draw(E.L("m"))], extras=lg + nt,
        caption=("每一條是一個市場從當時的最高點，到價格指數再回到那裡的期間：美國%s、日本 %s、台灣%s。"
                 "在那個高點買進的人，照價格指數算，這整段期間都還沒回到買進時的點位。這是三個挑出來的例子，不是每次下跌都這麼久，也不代表下跌一定回得來。")
        % (us["years_label"], jp["years_label"], tw["years_label"]),
    )


if __name__ == "__main__":
    import json
    print(json.dumps(compute(), ensure_ascii=False, indent=2))
