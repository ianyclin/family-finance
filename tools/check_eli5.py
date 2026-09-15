#!/usr/bin/env python3
"""ELI5 版哨兵：檢查 essay/eli5/*.html 片段。

規則（給小學五年級讀的版本）：
  只有一個 <section class="part">，id 要在 outline §2 的節清單裡
  五個元素都在：h2（含 span.num）、p.lede、div.concept、div.story、p.handback
  每句 ≤22 個中文字（以 。？！； 切句，不含標點與引號）
  禁詞：一定、必定、保證、穩賺、你應該、財富自由、被動收入、驚嘆號，以及術語
        （損失趨避、行動偏誤、沈沒成本、心理帳戶、再平衡、過度自信、行為落差、市值、年化、擇時）
  商品代號一律不准（連第 12 節也不准）
  正文阿拉伯數字（不含節次與 <time datetime>）≤2 個
  <figure class="chart" data-chart="ID"> 必須是空殼，且 ID 在大人版 essay/sections 存在
  story 段裡的 <time datetime> 必須在大人版同一節出現過（不可新增作者經歷）
用法：python3 tools/check_eli5.py [檔案…]（不給檔名就掃整個 essay/eli5/）
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_essay import Parser, cjk_count, load_spec, PRODUCT_RE  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ELI5 = os.path.join(ROOT, "essay", "eli5")
ADULT = os.path.join(ROOT, "essay", "sections")

FORBIDDEN = ["一定", "必定", "保證", "穩賺", "你應該", "財富自由", "被動收入", "！", "!",
             "損失趨避", "行動偏誤", "沈沒成本", "心理帳戶", "再平衡", "過度自信", "行為落差", "市值", "年化", "擇時"]
MAX_SENT = 22
MAX_NUMBERS = 2


def adult_info():
    figs, dates = set(), {}
    for name in os.listdir(ADULT):
        if not name.endswith(".html") or name.startswith("_"):
            continue
        s = open(os.path.join(ADULT, name), encoding="utf-8").read()
        figs |= set(re.findall(r'data-chart="([^"]+)"', s))
        m = re.search(r'<section[^>]*id="([^"]+)"', s)
        if m:
            dates[m.group(1)] = set(re.findall(r'datetime="(\d{4}-\d{2}-\d{2})"', s))
    return figs, dates


def check_file(path, spec, figs, dates):
    errors, warns = [], []
    html = open(path, encoding="utf-8").read()
    p = Parser()
    p.feed(html)
    p.close()
    errors += p.errors
    parts = [n for n in p.root.iter() if n.tag == "section" and "part" in n.classes()]
    if len(parts) != 1:
        return ["應該只有一個 <section class=\"part\">，實際 %d" % len(parts)], warns, {}
    sec = parts[0]
    sid = sec.attrs.get("id", "")
    if sid not in spec:
        errors.append("id %s 不在 outline §2 的節清單裡" % sid)
    kids = sec.kids()
    if not (kids and kids[0].tag == "h2" and any(n.tag == "span" and "num" in n.classes() for n in kids[0].iter())):
        errors.append("缺 h2 或 h2 裡沒有 span.num")
    for tag, cls in (("p", "lede"), ("div", "concept"), ("div", "story"), ("p", "handback")):
        if not any(k.tag == tag and cls in k.classes() for k in kids):
            errors.append("缺 %s.%s" % (tag, cls))
    text_all = sec.all_text()
    # 句長：逐元素切，h2／lede／每段各自算
    for el in (n for n in sec.iter() if n.tag in ("h2", "p", "li", "figcaption")):
        body = re.sub(r"[「」『』（）()《》〈〉、，,：:；;\s]", "", el.all_text())
        for sent in re.split(r"[。？?！!；;]", body):
            n = cjk_count(sent)
            if n > MAX_SENT:
                warns.append("句長 %d 字：%s" % (n, sent[:30]))
    # 禁詞
    for w in FORBIDDEN:
        if w in text_all:
            errors.append("禁詞「%s」" % w)
    if PRODUCT_RE.search(text_all):
        errors.append("出現商品代號或公司名：%s" % PRODUCT_RE.search(text_all).group(0))
    # 數字
    body_no_time = re.sub(r'<time[^>]*>.*?</time>', "", html, flags=re.S)
    body_no_time = re.sub(r'<span class="num">\d+</span>', "", body_no_time)
    body_no_time = re.sub(r'<figure[^>]*>.*?</figure>', "", body_no_time, flags=re.S)
    body_no_time = re.sub(r"<[^>]+>", "", body_no_time)
    body_no_time = re.sub(r"第\s*\d+\s*(節|題|章)", "", body_no_time)   # 節次、題號不算數字
    nums = re.findall(r"\d[\d,\.]*", body_no_time)
    if len(nums) > MAX_NUMBERS:
        errors.append("阿拉伯數字 %d 個（上限 %d）：%s" % (len(nums), MAX_NUMBERS, "、".join(nums)))
    # 圖表空殼
    for m in re.finditer(r'<figure class="chart" data-chart="([^"]+)">(.*?)</figure>', html, re.S):
        if m.group(2).strip():
            errors.append("圖表 %s 不是空殼" % m.group(1))
        if m.group(1) not in figs:
            errors.append("圖表 %s 在大人版找不到" % m.group(1))
    # 日期
    for d in re.findall(r'datetime="(\d{4}-\d{2}-\d{2})"', html):
        if d not in dates.get(sid, set()):
            errors.append("日期 %s 不在大人版第 %s 節" % (d, sid))
    stats = {"id": sid, "chars": cjk_count(text_all), "numbers": len(nums)}
    return errors, warns, stats


def main():
    spec, _ = load_spec()
    figs, dates = adult_info()
    files = sys.argv[1:] or sorted(os.path.join(ELI5, f) for f in os.listdir(ELI5) if f.endswith(".html") and not f.startswith("_"))
    bad = 0
    for f in files:
        errors, warns, stats = check_file(f, spec, figs, dates)
        flag = "✗" if errors else "✓"
        print("%s %s  字數 %s  數字 %s" % (flag, os.path.basename(f), stats.get("chars"), stats.get("numbers")))
        for e in errors:
            print("   錯誤：" + e)
        for w in warns[:8]:
            print("   警告：" + w)
        bad += bool(errors)
    print("結果：%d 個檔有錯誤" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
