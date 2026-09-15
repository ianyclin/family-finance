#!/usr/bin/env python3
"""組裝 ELI5 版：essay/eli5/*.html → essay/eli5.html（artifact 版 output/eli5.html）。

跟大人版共用 outline §2 的順序、外殼 CSS／JS 與組裝邏輯（直接 import assemble_essay），
差別只有封面文字，以及把 ELI5 片段裡的 <figure class="chart" data-chart="ID"></figure>
空殼換成大人版 essay/sections 裡同 ID 的完整圖表。
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble_essay as A  # noqa: E402

ROOT = A.ROOT
SRC = os.path.join(ROOT, "essay", "eli5")
ADULT = os.path.join(ROOT, "essay", "sections")
BUILD = os.path.join(ROOT, "essay", "eli5-build")
OUT = os.path.join(ROOT, "essay", "eli5.html")
ARTIFACT = os.path.join(ROOT, "output", "eli5.html")

FIG_RE = re.compile(r'<figure class="chart" data-chart="([^"]+)">.*?</figure>', re.S)
ADULT_URL = "https://claude.ai/code/artifact/459f89ea-5a69-4326-b970-6aadb2615f86"

# 小朋友版的圖說：換掉大人版的 figcaption；SVG 本身不動
KID_CAPTIONS = {
    "three-circles": "三個圈圈：快、穩、賺得多。你最多只能挑兩個。三個都答應你的人，先問他錢從哪裡來。",
    "milestones": "一格是六十萬。第一格要快八年，最後一格一年多。下面那排是每一格裡，有多少是錢自己長出來的。",
    "four-people": "四個人每月都存五千。綠線存四十年最高。黃線只存十年就停，最後貼著紅線存三十年的那條。灰線是放銀行。",
    "spiva": "請人幫忙挑的基金，十年裡一大半輸給平均，二十年輸得更多。橘色是輸的。",
    "smooth-vs-jagged": "虛線是你以為的樣子，實線是真的走過的路。終點一樣，中間會上上下下。",
    "intra-year": "每根柱子是台灣那一年賺或賠多少，紅點是那一年中途最多跌掉多少。幾乎每年中途都跌過，年底多半是正的。",
    "ranges": "放越久，最好和最差越靠近。黃色是全放股票，綠色是一半放晃得小的地方：最差那年小很多，最好那年也小一點。",
    "five-people": "五個人拿到一樣多的錢。最會挑日子的只贏一點點，一直在等的那個最後少掉一大半。",
    "dca-high-low": "一個每月都買在最貴那天，一個都買在最便宜那天。兩條線幾乎疊在一起，差得很少。",
    "missing-days": "一直放著不動，和錯過漲最多的那幾天，差很多。最好的日子常常就在最壞的日子旁邊。",
    "buckets": "把錢照什麼時候要用分成三桶。越快要用的，越不能跌。第三桶留白，由你自己填。",
}


def kidify(cid, fig):
    if cid in KID_CAPTIONS:
        fig = re.sub(r"<figcaption>.*?</figcaption>", "<figcaption>%s</figcaption>" % KID_CAPTIONS[cid], fig, flags=re.S)
    if cid == "buckets":
        fig = fig.replace("看你第 8 章的答案", "由你自己填")
    return fig


def adult_figures():
    figs = {}
    for name in os.listdir(ADULT):
        if not name.endswith(".html") or name.startswith("_"):
            continue
        s = open(os.path.join(ADULT, name), encoding="utf-8").read()
        for m in FIG_RE.finditer(s):
            figs[m.group(1)] = m.group(0)
    return figs


def main():
    figs = adult_figures()
    if os.path.isdir(BUILD):
        shutil.rmtree(BUILD)
    os.makedirs(BUILD)
    missing = []
    for name in sorted(os.listdir(SRC)):
        if not name.endswith(".html") or name.startswith("_"):
            continue
        s = open(os.path.join(SRC, name), encoding="utf-8").read()

        def fill(m):
            cid = m.group(1)
            if cid not in figs:
                missing.append("%s：%s" % (name, cid))
                return ""
            return kidify(cid, figs[cid])
        s = FIG_RE.sub(fill, s)
        open(os.path.join(BUILD, name), "w", encoding="utf-8").write(s)
    for x in missing:
        print("✗ 找不到大人版的圖：", x)

    A.MAP = [
        ("第 1 到 5 節", "市場長什麼樣", "錢從哪來、時間、費用、分散、跌", "#01-where-return-comes-from", False),
        ("第 6 到 8 節", "人最常做的三個動作", "等便宜、挑日子、先賣一點", "#06-timing", False),
        ("第 9 到 10 節", "人為什麼會這樣", "差在按了幾次、十條會中的念頭", "#09-behavior-gap", False),
        ("第 11 節", "先寫一張卡", "怕的那天照卡做", "#11-rules", True),
        ("第 12 節", "作者的七條", "我怎麼做、為什麼、代價", "#12-seven-things", False),
        ("第 13 節", "十二題、六種害怕", "急著找答案先看這裡", "#13-questions", False),
    ]
    A.TITLE = "隔離人性・小朋友版"
    A.SUBTITLE = "十歲也看得懂的投資說明：錢從哪裡來，為什麼跌了不要慌，怎麼先把決定寫好"
    A.THESIS = ("這本只有一件事。買很多公司的一小塊，公司賺錢你就分到錢；"
                "但很多人拿不到那份錢，因為跌的時候害怕就賣掉。所以我在不害怕的時候先把決定寫好，"
                "害怕那天照著做就好。這就是「隔離人性」。")
    A.ABOUT = ("這是《隔離人性》的小朋友版，每一節都比大人版短、字也簡單，圖是同一批。"
               "看不懂的地方可以問大人，或去看大人版同一節。想直接找問題，跳到第十三節。")
    A.RULES = ("這一版的規矩：只把大人版的話講簡單，不加新的事、不加新的數字；"
               "作者做過的事，都有那一天的貼文可以查；每一節最後一句，把決定還給你。")
    css = os.path.join(ROOT, "essay", "shell", "style.css")
    js = os.path.join(ROOT, "essay", "shell", "app.js")
    r = A.build(BUILD, OUT, css, js)
    shutil.rmtree(BUILD)
    html = open(OUT, encoding="utf-8").read()
    html = html.replace(
        '每一節的證據都指回這本手冊：<a href="%s">家庭理財白話手冊</a>。' % A.HANDBOOK,
        '看不懂的地方，去看<a href="%s">大人版的同一節</a>；每個數字的出處都在<a href="%s">家庭理財白話手冊</a>。' % (ADULT_URL, A.HANDBOOK))
    open(OUT, "w", encoding="utf-8").write(html)
    html = re.sub(r"^\s*<!doctype[^>]*>\s*", "", html, flags=re.I)
    html = re.sub(r"</?(html|head|body)\b[^>]*>\s*", "", html, flags=re.I)
    open(ARTIFACT, "w", encoding="utf-8").write(html)
    print("輸出：%s；artifact 版：%s（%.1f KB）" % (OUT, ARTIFACT, len(html.encode("utf-8")) / 1024))
    return 1 if (missing or r.get("errors")) else 0


if __name__ == "__main__":
    sys.exit(main())
