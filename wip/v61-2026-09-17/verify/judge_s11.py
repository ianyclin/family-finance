#!/usr/bin/env python3
"""裁判：第 11 節（id s11）第一批補丁核對。只讀，不改任何檔。"""
import re, html, collections, sys, json
from pathlib import Path

ROOT = Path("/Users/linyenchu/Cladue Code/family-finance")
OLD = (ROOT / "guide/index.v61-pre-w1.backup.html").read_text(encoding="utf-8")
NEW = (ROOT / "guide/index.html").read_text(encoding="utf-8")


def section(doc, sid):
    m = re.search(r'<section class="part" id="%s">' % re.escape(sid), doc)
    end = doc.find("</section>", m.start())
    return doc[m.start():end]


def text(fragment):
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", fragment, flags=re.S)
    t = re.sub(r"<svg.*?</svg>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "", t)
    return html.unescape(t)


def nums(t):
    return collections.Counter(re.findall(r"\d[\d,\.]*%?", t))


o11, n11 = section(OLD, "s11"), section(NEW, "s11")
to, tn = text(o11), text(n11)
print("s11 字數", len(to), "->", len(tn))
co, cn = nums(to), nums(tn)
print("少掉的數字次數:", dict((co - cn)))
print("多出的數字次數:", dict((cn - co)))

full_new = text(NEW)

# 1. 被刪或縮短的事實，逐字/片段在全書新版找得到嗎
checks = {
    "D2 回頭重想目標": "還不夠：回頭重想目標，不靠調高股票比例（三問第 3 題）",
    "D2 三問第3題 順序": "先照「多存 → 延後 → 降低目標」補，不靠調高股票比例",
    "D8 延後下一格": "延後要嘛直接延到表上的下一格年數，要嘛用複利計算機算，不要只在表二上比",
    "D8 投資圈0改填第5年": "投資圈還是 0 的人，改填第 5 年：拿 D 區扣完費用的「低」報酬率，查表二 5 年那一格，再乘上你每月投入是幾個一千元",
    "D8 目標那年定義": "目標那年（D 區補完缺口以後、低情境的到期金額）",
    "D8 現在那列用現在投資圈": "「現在」那一列用現在的投資圈",
    "D8 小安6500→214": "每月改投 6,500 元 → 低情境約 214 萬",
    "D8 表三除取少": "大跌少的錢換回今天（除）取年數少的那格",
    "D8 年數兩格中間": "年數在兩格中間，都往保守那邊取",
    "D3 start 底線": "放超過五年",
    "D3 教育金房款": "教育金",
    "D3 慢慢降低風險": "慢慢降低風險",
    "D1 row12 0.5% 暫估": "自己買指數 ETF（路徑 A、B）先用 0.5%",
    "D1 row12 路徑C兩層": "先向平台問出兩層合計的年費率",
    "D1 row12 不是上限": "0.5% 只是還沒挑產品時的暫估值，不是任何商品的費率，也不是上限",
    "D1 查表頁 取小一列": "就取比它小的那一列（錢算少一點）",
    "D1 查表頁 2.0%": "比 2.0% 還低就沒有可取的列，直接用複利計算機",
}
for k, v in checks.items():
    cnt_new_s11 = tn.count(v)
    cnt_new_all = full_new.count(v)
    print(f"[{'OK' if cnt_new_all else 'MISSING'}] {k}: s11={cnt_new_s11} 全書={cnt_new_all}")

# start 第 5 項
st = section(NEW, "start")
m = re.search(r"<ol[^>]*>(.*?)</ol>", st, flags=re.S)
items = re.findall(r"<li>(.*?)</li>", m.group(1), flags=re.S) if m else []
print("start ol 項數:", len(items))
for i, it in enumerate(items, 1):
    s = text(it)
    print(f"  第{i}項:", s[:400])

# 全書「不靠調高股票比例」出現處
print("\n'不靠調高股票比例' 新版出現次數（全書）:", full_new.count("不靠調高股票比例"))
print("s11 舊/新:", to.count("不靠調高股票比例"), tn.count("不靠調高股票比例"))

# facts.txt 每行是否在新版全文
facts = (ROOT / "lite/facts.txt").read_text(encoding="utf-8").splitlines()
miss = [f for f in facts if f.strip() and not f.startswith("#") and f.strip() not in full_new]
print("\nfacts.txt 行數", len(facts), "新版找不到:", len(miss))
for f in miss:
    print("  MISSING FACT:", f[:120])

# 受保護區塊 byte 一致
for alt in ["plan-blank", "lookup-tables", "ch4-drill"]:
    def blk(doc):
        i = doc.find(f'data-lite-alt="{alt}"')
        i = doc.rfind("<", 0, i)
        tag = re.match(r"<(\w+)", doc[i:]).group(1)
        # naive: find matching close by counting
        depth, j = 0, i
        pat = re.compile(r"<(/?)%s\b[^>]*>" % tag)
        for mm in pat.finditer(doc, i):
            depth += -1 if mm.group(1) else 1
            if depth == 0:
                return doc[i:mm.end()]
    print(alt, "unchanged:", blk(OLD) == blk(NEW))

# div.story / mark.key in s11 unchanged
for pat in [r'<div class="story">.*?</div>', r'<mark class="key">.*?</mark>']:
    print(pat[:20], re.findall(pat, o11, flags=re.S) == re.findall(pat, n11, flags=re.S))

# a.term 在 s11 前後一致
print("a.term s11 舊/新:", re.findall(r'<a class="term"[^>]*>(.*?)</a>', o11) == re.findall(r'<a class="term"[^>]*>(.*?)</a>', n11))
print("xref s11 舊:", re.findall(r'<a class="xref" href="([^"]+)">(.*?)</a>', o11).__len__(), "新:", re.findall(r'<a class="xref" href="([^"]+)">(.*?)</a>', n11).__len__())
for h, a in re.findall(r'<a class="xref" href="([^"]+)">(.*?)</a>', n11):
    pass
ids = set(re.findall(r'id="([^"]+)"', NEW))
bad = [(h, a) for h, a in re.findall(r'<a class="xref" href="#([^"]+)">(.*?)</a>', n11) if h not in ids]
print("s11 xref 指到不存在的 id:", bad)
