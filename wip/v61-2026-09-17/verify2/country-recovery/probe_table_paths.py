#!/usr/bin/env python3
"""裁判第二輪：探 compute() 的「表還在才比對」各條路（這支才 import 模組；重算在 recompute2.py，沒有 import）。
只把改過的指南複本寫到本資料夾 guide-variants/，不動 guide/index.html、不動模組。"""
import re, sys, traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
FF = HERE.parents[3]
sys.path.insert(0, str(FF / "tools"))
import v61_g9_country_recovery as M  # noqa

REAL = M.GUIDE
g = REAL.read_text(encoding="utf-8")
VAR = HERE / "guide-variants"
VAR.mkdir(exist_ok=True)
i = g.find("<h3>單一市場可能等很久")
j = g.find("</table>", i) + len("</table>")
card_tbl = g[i:j]

variants = {
    "0 原樣": g,
    "1 選項B：h3＋表整塊拿掉": g[:i] + g[j:],
    "2 h3 留著、表換成 figure": g[:g.find("<div class=\"table-wrap\">", i)] + "<figure class=\"chart\"></figure>" + g[j:],
    "3 tr 加 class": g[:i] + card_tbl.replace("<tr>", "<tr class=\"r\">") + g[j:],
    "4 tbody 加屬性": g[:i] + card_tbl.replace("<tbody>", "<tbody class=\"b\">") + g[j:],
    "5 美國改成「約 25 年」": g[:i] + card_tbl.replace("<td>25 年</td>", "<td>約 25 年</td>") + g[j:],
    "6 日本改成「約 34 年」": g[:i] + card_tbl.replace("<td>34 年 2 個月</td>", "<td>約 34 年</td>") + g[j:],
    "7 標題改字「單一國家可能等很久」": g[:i] + card_tbl.replace("單一市場可能等很久", "單一國家可能等很久") + g[j:],
    "8 起訖箭頭改成「–」": g[:i] + card_tbl.replace("1929-09 → 1954-11", "1929-09–1954-11") + g[j:],
    "9 市場格加連結": g[:i] + card_tbl.replace("<td>美國</td>", "<td><a href=\"#x\">美國</a></td>") + g[j:],
    "10 台灣起訖改到日": g[:i] + card_tbl.replace("1990-02 → 2020-07", "1990-02-10 → 2020-07-27") + g[j:],
    "11 美國列改成 1929-10": g[:i] + card_tbl.replace("1929-09 → 1954-11", "1929-10 → 1954-11") + g[j:],
}
for name, text in variants.items():
    p = VAR / ("v%s.html" % name.split()[0])
    p.write_text(text, encoding="utf-8")
    M.GUIDE = p
    try:
        r = M.compute()
        print("%-28s → 不 raise；table_check=%s；labels=%s" % (name, r["table_check"], [x["years_label"] for x in r["rows"]]))
    except Exception as e:
        print("%-28s → %s: %s" % (name, type(e).__name__, e))
M.GUIDE = REAL
