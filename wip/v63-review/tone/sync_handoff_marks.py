#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""語氣批 B 類：把 docs/handoff-guide-2026-09-19.md 的重點句清單同步到指南現況。

只動被 B 類改到的那幾行（＋取消的那一行整條刪掉），改完再用指南實測核對一次。
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
DOC = ROOT / "docs" / "handoff-guide-2026-09-19.md"
GUIDE = ROOT / "guide" / "index.html"

# (舊清單文字, 新清單文字)；新文字 None＝整行刪掉
EDITS = [
    ("信用卡只繳最低應繳、餘額繼續滾利息的那種，一定先還。",
     "信用卡只繳最低應繳，剩下的餘額會一直滾利息，這種一定先還。"),
    ("它是一套寫得下來的步驟，不是一種本事。",
     "指數投資是一套寫得下來的步驟，不是一種本事。"),
    ("每年看看收支；有餘裕，再把投入跟著薪水或物價調高。",
     "每年看看收支，有餘裕就把投入跟著薪水或物價調高。"),
    ("消失的基金錢不會不見，但結束的時點由不得你。",
     "消失的基金錢不會不見，但什麼時候結束由不得你。"),
    ("這不是說高股息或策略型不能買：想要，就當成有上限的一小塊，寫進計畫；核心那一塊，用不需要猜的市值型。",
     "這不是說高股息或策略型不能買。想買就當成有上限的一小塊，寫進計畫。核心那一塊，用不需要猜的市值型。"),
    ("股票那一塊越大，平常的壞日子就越常等於一個月薪水——那是錢變多以後的日常，不是出事。",
     "股票那一塊越大，平常的壞日子就越常等於一個月薪水。那是錢變多以後的日常，不是出事。"),
    ("等匯率的代價通常也不是差那幾毛錢，是為了等，整筆錢晚了好幾個月才開始。",
     "等匯率的代價，通常不是差那幾毛錢，是整筆錢為了等，晚了好幾個月才開始。"),
    ("熱門時加碼、下跌時退出，會讓投資人的錢放在較差的時段。",
     "熱門時加碼、下跌時退出，錢就會放在比較差的時段。"),
    ("會怕、想動手都是正常的；要先準備好的，是那時候做什麼。",
     "會怕、想動手都是正常的；先想好那時候要做什麼。"),
    ("自動投入、預設選項、固定的查看頻率與事先寫好的賣出條件，都在減少需要臨場做的決定。",
     "自動投入、預設選項、固定的查看頻率、事先寫好的賣出條件，都在減少臨場要做的決定。"),
    ("關掉通知：券商 app 的漲跌推播、群組的即時行情都不需要，看盤的次數應該是你自己設的。",
     "關掉通知：券商 app 的漲跌推播、群組的即時行情都不需要，要看幾次由你自己定。"),
    ("買進前先讓交割帳戶有足夠資金，避免違約交割。",
     "買進前先讓交割帳戶裡的錢夠，才不會違約交割。"),
    ("大跌時先從預留現金或較穩定資產支應，並重新檢查支出；不要臨時把全部股票賣掉。",
     "大跌時先從預留現金或比較穩定的資產拿，同時重新檢查支出；不要臨時把全部股票賣掉。"),
    ("要現金流可以自己做。持有市值型，需要用錢的時候賣一小部分，拿到的現金跟配息一樣能花，時間和金額由你自己決定。",
     "要現金流可以自己做。"),
    ("已經買了高股息的人不用急著賣：先算含息總報酬，再決定新錢要不要改買市值型、舊的要不要換",
     "已經買了高股息的人不用急著賣。"),
    ("它們沒辦法把人變理性，只是讓錯誤比較難發生。", None),
    ("計畫表上任何一格要改（想賣、想加碼、換商品、調高股票比例都算），都先寫下日期和理由，隔一段固定時間再生效",
     "計畫表上任何一格要改，都先寫下日期和理由，隔一段固定時間再生效"),
    ("不追補錯過的那一段漲幅：一次補回來等於臨時加碼，又是一次時點判斷。",
     "不追補錯過的那一段漲幅：一次補回來等於臨時加碼，又是一次猜時機。"),
]

HEADER = ("**黃線 `mark.key`（106 句）**", "**黃線 `mark.key`（105 句）**")


def guide_marks():
    t = GUIDE.read_text(encoding="utf-8")
    key, top = [], []
    for m in re.finditer(r'<mark class="(key|key top)">(.*?)</mark>', t, re.S):
        txt = re.sub(r"<[^>]+>", "", m.group(2))
        (top if m.group(1) == "key top" else key).append(txt)
    return key, top


def main():
    lines = DOC.read_text(encoding="utf-8").split("\n")
    for old, new in EDITS:
        hits = [i for i, ln in enumerate(lines) if ln.startswith("- 第 ") and ln.endswith(old)]
        if not hits:
            print("（清單本來就沒收這一句，跳過）", old[:30])
            continue
        assert len(hits) == 1, (old, len(hits))
        i = hits[0]
        if new is None:
            lines.pop(i)
        else:
            lines[i] = lines[i][: -len(old)] + new
    body = "\n".join(lines)
    assert body.count(HEADER[0]) == 1
    body = body.replace(HEADER[0], HEADER[1], 1)
    DOC.write_text(body, encoding="utf-8")

    # 核對：清單每一行的句子都在指南裡找得到，數量也對得上
    key, top = guide_marks()
    listed = [ln for ln in body.split("\n") if ln.startswith("- 第 ") and "` " in ln]
    print("指南實測：黃線 %d、淡紅 %d" % (len(key), len(top)))
    miss = []
    for ln in listed:
        s = ln.split("` ", 1)[1]
        if s not in key and s not in top:
            miss.append(s)
    print("清單 %d 行，指南找不到的：%d" % (len(listed), len(miss)))
    for s in miss:
        print("   ✗", s)
    return 1 if miss else 0


if __name__ == "__main__":
    sys.exit(main())
