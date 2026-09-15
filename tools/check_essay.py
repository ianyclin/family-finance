#!/usr/bin/env python3
"""投資專篇哨兵：檢查 essay/sections/NN-slug.html 或組好的 essay/index.html。

用法：
    python3 tools/check_essay.py essay/sections/01-where-return-comes-from.html [--json]
    python3 tools/check_essay.py essay/index.html --full [--json]

規格出處：essay/outline.md §2（節、術語、字數）、§3（storyDates）、§5（禁數字）、§6（元件契約）。
錯誤 → exit 1；只有警告 → exit 0。
"""
import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTLINE = os.path.join(ROOT, "essay", "outline.md")
POSTS = os.path.join(ROOT, "research", "author-fb-posts-all.json")

HANDBOOK = "https://claude.ai/code/artifact/76934d5e-136e-42b8-8de1-14e623f8859c"

VOID = {"br", "img", "hr", "input", "meta", "link", "path", "circle", "rect",
        "line", "polyline", "polygon", "use", "stop", "ellipse", "source"}

# ---- §6.6 禁詞（錯誤）----
FORBIDDEN = ["歐印", "FIRE", "財富自由", "被動收入", "必定", "一定", "你應該",
             "保證", "穩賺", "必買", "最好的做法", "無風險", "零風險", "穩定高報酬",
             "翻身", "錯過就沒了", "最後機會"]

# ---- §5 不准出現的數字（錯誤）----
FORBIDDEN_NUM = [
    (r"13\.79", "作者績效 13.79"),
    (r"13\.77", "作者績效 13.77"),
    (r"0\.02\s*個百分點", "從作者績效推出的 0.02 個百分點"),
    (r"0\.006\s*%", "作者粗算 0.006%"),
    (r"0\.03\s*%", "商品層手續費 0.03%"),
    (r"4\.57\s*%", "作者再平衡門檻 4.57%"),
    (r"5\s*/\s*25\s*規則", "5/25 規則"),
    (r"368,?900", "摩根美元版四個人"),
    (r"192,?000", "摩根美元版四個人"),
    (r"176,?900", "摩根美元版四個人"),
    (r"121,?100", "摩根美元版四個人"),
    (r"7\s*個[^。]{0,8}兩週", "作者轉述版「7 個在兩週內」"),
    (r"6\s*個[^。]{0,6}隔天", "作者轉述版「6 個在隔天」"),
    (r"年化[^。，、]{0,6}\d+(\.\d+)?\s*%[^。]{0,10}(我|作者)", "疑似作者個人年化"),
    (r"(我|作者)[^。]{0,12}(報酬率|年化|含息報酬|月增率)[^。]{0,6}\d", "疑似作者個人績效"),
    (r"甜蜜點[^。]{0,10}\d+(\.\d+)?\s*%", "作者甜蜜點進度"),
]

# ---- 商品名與代號（錯誤）----
PRODUCT_RE = re.compile(
    r"\b(00\d{2,4}[A-Z]?|VT|VTI|VOO|VWRA|VWRD|VALU|VXUS|AVGS|AVUV|AVDV|CBU0|CBUO"
    r"|SPY|QQQ|BND|BNDW|IVV|SCHD|ARKK|IEI|BNDX)\b"
    r"|元大|富邦|國泰|中國信託|群益|復華|兆豐|第一金|統一投信"
    r"|台積電|鴻海|聯發科"
    r"|Firstrade|Interactive Brokers|嘉信|TD Ameritrade")

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⭕⌚-⏿]")

# ---- §5 允許的量級（只用來出警告，不擋）----
# 基礎清單＝§5「只准引的量級」逐條列出的（v0.9 用到但清單漏列的也補在這裡）；
# 另外會在 load_spec() 時，把 §5 那一段文字裡能機械抓到的數字併進來。
BASE_ALLOWED_NUMBERS = {
    "9.7%", "9.8%", "6.6%", "5.2%", "3.5%", "43.07%", "996萬", "502萬", "493萬", "343萬", "416萬",
    "86萬", "84.34%", "89.50%", "91.99%", "48.17%", "13.6%", "10.3%", "14.2%",
    "17.73%", "41.82%", "11.1%", "42.9%", "100%", "6%", "17%", "5%", "7%",
    "1.7%", "2%", "12.74%", "13.23%", "12.94%", "12.99%", "5.8%", "7.3%",
    "0.49個百分點", "0.1個百分點", "1.2個百分點", "66.7%", "8萬", "240元",
    "5個百分點", "5,000元", "1萬元", "276萬", "240萬", "180萬", "60萬",
    "100萬", "90萬", "80萬", "40萬", "100元", "82元", "67元", "55元",
    "10,000美元", "1萬美元", "2,000美元", "186,077", "170,555", "166,591",
    "151,343", "47,357", "80,619", "35,866", "13,826", "14,703,633",
    "15,780,598", "9%", "20%",
    # v0.9 用到、原清單漏列的（§5 補列）
    "10%", "30%", "50%", "100萬元", "1萬", "300元",
    # 行為金融補充（§5 新增來源）— 2026-09-11 主線補列
    "1.1個百分點", "1.1 個百分點", "7.3%", "6.3%", "2.6", "0.4", "8.48個百分點", "8.48 個百分點", "16.54%", "25.02%",
    "11.4%", "17.9%", "15%", "10%", "4.7%", "2.25", "2.25倍", "6%", "6.3%", "33%", "33.3%", "13%", "12.6%", "14.2%", "0.5%", "80%",

    "2.25%", "25%", "70%", "3%", "4%",
    # v1.1 股債區間表（手冊第 8 章）
    "39%", "47%", "15%", "33%", "5%", "14%", "−39%", "−15%",
    "0%", "1%", "16%", "19%", "21%", "28%", "40%",  # 同表 5、10 年列與圖表軸線
    "1,470萬", "1,578萬", "50萬", "70萬",  # v1.3 圖表
    "15,189,340元", "12.97%", "14,703,633元", "15,780,598元",
    # 2026-09-11 來源更新：SPIVA 2025 年底、JPM GTR 2026 區間表（含全部債券、現金兩欄）
    "85.59%", "89.93%", "92.89%", "50.55%", "37%", "52%", "29%", "18%", "13%", "11%", "9%", "8%", "2%", "1%", "0%", "200萬", "400萬", "22%", "49%", "60%", "62%", "75%", "79%", "81%", "83%", "85%", "86%", "250萬", "500萬", "750萬", "1000萬", "1500萬", "120萬", "300萬", "360萬", "420萬", "480萬", "540萬", "600萬",  # v1.4 圖表：平均收盤欄、座標軸、里程碑格
}
BASE_ALLOWED_NUMBERS |= {"2萬", "4萬", "6萬", "8萬", "5萬", "10萬", "15萬", "20萬", "85.6%", "89.9%", "92.9%", "1,519萬", "250美元", "7.25%", "6萬元"}  # 官方原圖出處說明  # v2.0 圖表：美元軸刻度、SPIVA 圓餅取一位小數
ALLOWED_NUMBERS = set(BASE_ALLOWED_NUMBERS)   # load_spec() 會用 §5 的內容再擴充
NUM_TOKEN_RE = re.compile(r"\d[\d,]*(?:\.\d+)?\s*(?:%|個百分點|萬元|萬|元|美元)")


class Node:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []
        self.parent = parent

    def classes(self):
        return set(self.attrs.get("class", "").split())

    def all_text(self):
        out = []
        for c in self.children:
            out.append(c if isinstance(c, str) else c.all_text())
        return "".join(out)

    def iter(self):
        yield self
        for c in self.children:
            if not isinstance(c, str):
                yield from c.iter()

    def kids(self):
        return [c for c in self.children if not isinstance(c, str)]


class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [], None)
        self.cur = self.root
        self.errors = []

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is None:
            self.errors.append("多餘的結束標籤 </%s>（第 %d 行）" % (tag, self.getpos()[0]))
            return
        if n is not self.cur:
            self.errors.append("標籤沒有正確關閉：在 </%s> 之前 <%s> 還沒關（第 %d 行）"
                               % (tag, self.cur.tag, self.getpos()[0]))
        self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def cjk_count(s):
    return len(re.findall(r"[一-鿿]", s))


# ---------------- outline 規格 ----------------

def load_spec(path=OUTLINE):
    """從 outline.md §2 的表與 §3 的 storyDates 讀出每節規格。"""
    src = open(path, encoding="utf-8").read()
    spec = {}
    order = []
    row = re.compile(r"^\|\s*(\d+)\s*\|\s*([0-9a-z-]+)\s*\|\s*([^|]+?)\s*\|"
                     r"\s*(\d+(?:[、/,]\s*\d+)*)\s*\|\s*([^|]+?)\s*\|\s*([\d,]+)\s*\|\s*$")
    for line in src.splitlines():
        m = row.match(line.strip())
        if not m:
            continue
        num, sid, title, chapter, terms, chars = m.groups()
        terms = terms.strip()
        term_list = [] if terms in ("—", "-", "無", "") else [
            t.strip() for t in terms.split("、") if t.strip()]
        spec[sid] = {
            "num": int(num),
            "id": sid,
            "title": title.strip(),
            # 章欄可列多章（例：08、07），第一個是主章，其餘是證據框也可指向的章
            "chapter": "%02d" % int(re.split(r"[、/,]", chapter)[0]),
            "chapters": ["%02d" % int(c) for c in re.split(r"[、/,]\s*", chapter)],
            "terms": term_list,
            "target": int(chars.replace(",", "")),
            "storyDates": [],
        }
        order.append(sid)

    # §3 每節的 storyDates
    cur = None
    for line in src.splitlines():
        s = line.strip()
        if s.startswith("## "):          # 離開 §3，後面的日期不算任何一節的
            cur = None
            continue
        h = re.match(r"^###\s+([0-9a-z-]+)", s)
        if h:
            cur = h.group(1) if h.group(1) in spec else None
            continue
        if cur and "storyDates" in line and not spec[cur]["storyDates"]:
            spec[cur]["storyDates"] = re.findall(r"\d{4}-\d{2}-\d{2}", line)

    # §5「只准引的量級」：把能機械抓到的數字併進允許清單（漏抓的仍留在 BASE）
    for line in src.splitlines():
        if "只准引的量級" in line:
            for m in NUM_TOKEN_RE.finditer(line):
                ALLOWED_NUMBERS.add(re.sub(r"\s+", "", m.group(0)))
    return spec, order


def term_quota(spec):
    """術語總數上限：§2 表各節術語加總；表讀不到就退回 14（§6 的上限）。"""
    total = sum(len(v["terms"]) for v in spec.values())
    return total if total else 14


def load_post_dates(path=POSTS):
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception:
        return None
    out = set()
    for p in data:
        iso = (p.get("published_iso") or "")[:10]
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", iso):
            out.add(iso)
    return out


# ---------------- 單節檢查 ----------------

def text_without_q(node):
    """回傳（純文字, 含引句標記的文字）：<q> 內容換成 \x01 佔位，供句長豁免用。"""
    out = []
    for c in node.children:
        if isinstance(c, str):
            out.append(c)
        elif c.tag == "q":
            out.append("\x01" + c.all_text() + "\x01")
        else:
            out.append(text_without_q(c))
    return "".join(out)


def split_sentences(t):
    return [s for s in re.split(r"[。？?！!]", t) if s.strip()]


def check_section(sec, spec, post_dates, errors, warns, stats, seen_dfn_ids):
    sid = sec.attrs.get("id", "")
    label = "節 %s" % (sid or "（沒有 id）")
    sp = spec.get(sid)
    if sp is None:
        errors.append("%s：id 不在 outline §2 的十節清單裡" % label)
    text = sec.all_text()

    # --- 五元件齊全且順序正確 ---
    kids = sec.kids()
    want = [("h2", None), ("p", "lede"), ("div", "concept"), ("div", "story"), ("p", "handback")]
    got = [(k.tag, sorted(k.classes())) for k in kids]
    if len(kids) != 5 or any(
            kids[i].tag != w[0] or (w[1] and w[1] not in kids[i].classes())
            for i, w in enumerate(want) if i < len(kids)):
        errors.append("%s：五元件必須依序是 h2 → p.lede → div.concept → div.story → p.handback，"
                      "實際是 %s" % (label, got))
    h2 = kids[0] if kids and kids[0].tag == "h2" else None
    lede = next((k for k in kids if k.tag == "p" and "lede" in k.classes()), None)
    concept = next((k for k in kids if "concept" in k.classes()), None)
    story = next((k for k in kids if "story" in k.classes()), None)
    handback = next((k for k in kids if "handback" in k.classes()), None)

    if h2 is not None and not any(n.tag == "span" and "num" in n.classes() for n in h2.iter()):
        errors.append("%s：<h2> 缺 <span class=\"num\">" % label)

    # --- lede ---
    if lede is not None:
        n = cjk_count(lede.all_text())
        if n > 30:
            errors.append("%s：lede 超過 30 字（%d 字）" % (label, n))
        if len(split_sentences(lede.all_text())) > 1:
            warns.append("%s：lede 不只一句" % label)

    # --- concept 段數與證據框 ---
    if concept is not None:
        ps = [k for k in concept.kids() if k.tag == "p"]
        if not 2 <= len(ps) <= 5:
            warns.append("%s：concept 應有 2 到 5 個 <p>，實際 %d 個" % (label, len(ps)))
        # 證據框（指回手冊）與來源框（指外部論文）都算一個「證據」
        ev = [n for n in concept.iter()
              if n.tag == "aside" and "box" in n.classes()
              and n.classes() & {"evidence", "source"}]
        if not 1 <= len(ev) <= 2:
            errors.append("%s：證據框應有 1 到 2 個，實際 %d 個" % (label, len(ev)))
        for b in ev:
            is_src_box = "source" in b.classes()
            kind = "來源框" if is_src_box else "證據框"
            if not is_src_box and not any("magnitude" in n.classes() for n in b.iter()):
                errors.append("%s：證據框缺 <p class=\"magnitude\">" % label)
            if is_src_box and not any(
                    n.tag == "p" and "src" in n.classes() for n in b.iter()):
                errors.append("%s：來源框缺 <p class=\"src\">" % label)
            a = next((n for n in b.iter() if n.tag == "a"), None)
            href = a.attrs.get("href", "") if a is not None else ""
            if not href:
                errors.append("%s：%s缺 <a href>" % (label, kind))
            elif is_src_box:
                # 來源框可以連外部論文，不強制 #ch-
                if not re.match(r"https?://", href):
                    errors.append("%s：來源框的連結不是網址：%s" % (label, href))
            elif "#ch-" not in href:
                errors.append("%s：證據框連結沒有 #ch- 錨點：%s" % (label, href))
            elif not href.startswith(HANDBOOK):
                warns.append("%s：證據框連結不是手冊網址：%s" % (label, href))
            elif sp and "#ch-" in href and not any(
                    ("#ch-%s" % c) in href for c in sp.get("chapters", [sp["chapter"]])):
                warns.append("%s：證據框指向 %s，outline 標的是第 %s 章"
                             % (label, href.split("#")[-1],
                                "、".join(sp.get("chapters", [sp["chapter"]]))))
        outside = [n for n in sec.iter()
                   if n.tag == "aside" and n.classes() & {"evidence", "source"}
                   and n not in list(concept.iter())]
        if outside:
            errors.append("%s：有 %d 個證據框不在 concept 裡" % (label, len(outside)))
    else:
        errors.append("%s：缺 div.concept" % label)

    # --- dfn ---
    dfns = [n for n in sec.iter() if n.tag == "dfn"]
    if sp is not None and len(dfns) != len(sp["terms"]):
        errors.append("%s：<dfn> 應有 %d 個（%s），實際 %d 個"
                      % (label, len(sp["terms"]), "、".join(sp["terms"]) or "無", len(dfns)))
    for d in dfns:
        did = d.attrs.get("id", "")
        if not did.startswith("term-"):
            errors.append("%s：<dfn> 的 id 必須是 term-…，實際 %r" % (label, did))
        elif did in seen_dfn_ids:
            errors.append("%s：<dfn> id 重複：%s" % (label, did))
        else:
            seen_dfn_ids.add(did)
        if concept is not None and d not in list(concept.iter()):
            warns.append("%s：<dfn> %s 不在 concept 裡" % (label, did or d.all_text()))

    # --- story ---
    story_chars = cjk_count(story.all_text()) if story is not None else 0
    sec_chars = cjk_count(text)
    ratio = (story_chars / sec_chars) if sec_chars else 0.0
    if ratio > 0.30:
        errors.append("%s：story 占比 %.1f%%（%d／%d 字）超過 30%%"
                      % (label, ratio * 100, story_chars, sec_chars))

    # --- time ---
    times = [n for n in sec.iter() if n.tag == "time"]
    if story is not None and not times:
        errors.append("%s：story 沒有任何 <time datetime>" % label)
    used = set()
    for t in times:
        dt = t.attrs.get("datetime", "")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", dt):
            errors.append("%s：<time> 的 datetime 不是 YYYY-MM-DD：%r" % (label, dt))
            continue
        used.add(dt)
        if post_dates is not None and dt not in post_dates:
            errors.append("%s：<time datetime=\"%s\"> 在貼文檔裡找不到這一天" % (label, dt))
        if sp is not None and dt not in sp["storyDates"]:
            errors.append("%s：%s 不在 outline 的 storyDates（%s）"
                          % (label, dt, "、".join(sp["storyDates"])))
    if sp is not None:
        unused = [d for d in sp["storyDates"] if d not in used]
        if unused:
            warns.append("%s：storyDates 有 %s 沒有用到" % (label, "、".join(unused)))

    # --- handback ---
    if handback is not None:
        if len(split_sentences(handback.all_text())) > 1:
            warns.append("%s：交還句不只一句" % label)
        if "你應該" in handback.all_text():
            errors.append("%s：交還句出現指令語氣" % label)

    # --- 句長與段落句數 ---
    for p in (n for n in sec.iter() if n.tag in ("p", "li")
              and not (n.classes() & {"src", "magnitude"})):
        raw = text_without_q(p).strip()
        parts = re.split(r"([。？?！!])", raw)
        sents = []
        buf = ""
        for seg in parts:
            buf += seg
            if seg in "。？?！!":
                sents.append(buf)
                buf = ""
        if buf.strip():
            sents.append(buf)
        sents = [s for s in sents if s.strip()]
        if len(sents) > 3:
            warns.append("%s：一段 %d 句（>3）：%s…" % (label, len(sents), raw[:24]))
        for s in sents:
            if "\x01" in s:
                continue  # 引句豁免
            n = cjk_count(s)
            if n > 30:
                warns.append("%s：一句 %d 字（>30）：%s…" % (label, n, s.strip()[:30]))

    stats.setdefault("sections", []).append({
        "id": sid,
        "chars": sec_chars,
        "target": sp["target"] if sp else None,
        "story_chars": story_chars,
        "story_ratio": round(ratio, 3),
        "dfn": len(dfns),
        "evidence": len([n for n in sec.iter()
                         if n.tag == "aside" and n.classes() & {"evidence", "source"}]),
        "dates": sorted(used),
    })
    return sec_chars, story_chars


# ---------------- 全文層檢查 ----------------

def is_advice_section(sec):
    """§6：第 13 節（<section class="part advice" data-allow-products="true">）"""
    return (sec.attrs.get("data-allow-products", "") == "true"
            or "advice" in sec.classes())


def check_text_level(text, errors, warns, where="", allow_products=False):
    pre = (where + "：") if where else ""
    if "！" in text or "!" in text:
        errors.append("%s正文有驚嘆號（%d 處）" % (pre, text.count("！") + text.count("!")))
    for w in FORBIDDEN:
        for m in re.finditer(re.escape(w), text):
            ctx = text[max(0, m.start() - 12): m.end() + 12].replace("\n", " ")
            errors.append("%s禁詞「%s」：…%s…" % (pre, w, ctx))
    for pat, why in FORBIDDEN_NUM:
        for m in re.finditer(pat, text):
            ctx = text[max(0, m.start() - 12): m.end() + 12].replace("\n", " ")
            errors.append("%s禁數字（%s）：…%s…" % (pre, why, ctx))
    if not allow_products:
        for m in PRODUCT_RE.finditer(text):
            ctx = text[max(0, m.start() - 12): m.end() + 12].replace("\n", " ")
            errors.append("%s商品名或代號「%s」：…%s…" % (pre, m.group(0), ctx))
        for m in re.finditer("我建議", text):
            ctx = text[max(0, m.start() - 12): m.end() + 12].replace("\n", " ")
            errors.append("%s「我建議」只准出現在第 13 節：…%s…" % (pre, ctx))
    em = EMOJI_RE.findall(text)
    if em:
        warns.append("%s正文有表情符號：%s（只准留在引句裡）" % (pre, "".join(em)[:20]))
    unknown = set()
    for m in NUM_TOKEN_RE.finditer(text):
        tok = re.sub(r"\s+", "", m.group(0))
        if tok not in ALLOWED_NUMBERS:
            unknown.add(tok)
    if unknown:
        warns.append("%s有 %d 個數字不在 §5 清單裡，要人工核對：%s"
                     % (pre, len(unknown), "、".join(sorted(unknown))))


# ---------------- 主流程 ----------------

def check(path, full=False):
    src = open(path, encoding="utf-8").read()
    spec, order = load_spec()
    post_dates = load_post_dates()
    p = Parser()
    p.feed(src)
    p.close()
    errors = list(p.errors)
    warns = []
    if post_dates is None:
        warns.append("讀不到 research/author-fb-posts-all.json，日期只檢查格式")
    if p.cur is not p.root:
        errors.append("檔案結束時 <%s> 還沒關閉" % p.cur.tag)

    parts = [n for n in p.root.iter() if n.tag == "section" and "part" in n.classes()]
    stats = {}
    if not parts:
        errors.append("找不到任何 <section class=\"part\">")
        return errors, warns, stats

    expected = [sid for sid in order if sid in spec]
    if full:
        ids = [n.attrs.get("id", "") for n in parts]
        # 順序要跟 §2 表一致；還沒寫的節只列出來，不算錯
        pos = -1
        out_of_order = False
        for sid in ids:
            if sid not in expected:
                continue                      # id 不在表裡，前面已經報過錯
            i = expected.index(sid)
            if i <= pos:
                out_of_order = True
            pos = i
        if out_of_order:
            errors.append("節的順序與 outline §2 不符：%s" % ids)
        missing = [s for s in expected if s not in ids]
        if missing:
            warns.append("outline §2 有 %d 節還沒寫（不算錯）：%s"
                         % (len(missing), "、".join(missing)))
        if len(parts) > len(expected):
            errors.append("全篇最多 %d 節，實際 %d 節" % (len(expected), len(parts)))
    else:
        if len(parts) != 1:
            errors.append("片段檔應該只有一個 <section class=\"part\">，實際 %d 個" % len(parts))

    seen_dfn_ids = set()
    total_chars = total_story = 0
    for sec in parts:
        c, s = check_section(sec, spec, post_dates, errors, warns, stats, seen_dfn_ids)
        total_chars += c
        total_story += s

    # 文字層：第 13 節（advice／data-allow-products）豁免商品代號與「我建議」
    advice = [n for n in parts if is_advice_section(n)]
    plain_text = "".join(n.all_text() for n in parts if n not in advice)
    if plain_text:
        check_text_level(plain_text, errors, warns)
    for sec in advice:
        check_text_level(sec.all_text(), errors, warns,
                         where="節 %s" % sec.attrs.get("id", ""),
                         allow_products=True)

    if full:
        quota = term_quota(spec)
        want_dfn = sum(len(spec[s]["terms"]) for s in expected if s in spec) or quota
        if len(parts) == len(expected) and len(seen_dfn_ids) != want_dfn:
            errors.append("全篇 <dfn> 應恰好 %d 個，實際 %d 個" % (want_dfn, len(seen_dfn_ids)))
        if len(seen_dfn_ids) > quota:
            errors.append("全篇 <dfn> 超過術語上限 %d 個，實際 %d 個"
                          % (quota, len(seen_dfn_ids)))
        if total_chars and total_story / total_chars > 0.30:
            errors.append("全篇 story 占比 %.1f%% 超過 30%%" % (total_story / total_chars * 100))
        anchors = set(re.findall(r'\sid="([^"]+)"', src))
        for href in set(re.findall(r'href="#([^"]+)"', src)):
            if href not in anchors:
                errors.append("內部連結 #%s 沒有對應的 id" % href)

    stats["chars"] = total_chars
    stats["story_chars"] = total_story
    stats["story_ratio"] = round(total_story / total_chars, 3) if total_chars else 0
    stats["dfn"] = len(seen_dfn_ids)
    stats["parts"] = len(parts)
    return errors, warns, stats


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("path")
    ap.add_argument("--full", action="store_true", help="檢查組好的整篇 index.html")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    errors, warns, stats = check(args.path, full=args.full)
    if args.json:
        print(json.dumps({"file": args.path, "errors": errors, "warnings": warns,
                          "stats": stats}, ensure_ascii=False, indent=1))
    else:
        print("檔案：%s" % args.path)
        print("統計：%s" % json.dumps(stats, ensure_ascii=False))
        for e in errors:
            print("錯誤：%s" % e)
        for w in warns:
            print("警告：%s" % w)
        print("結果：%d 個錯誤，%d 個警告" % (len(errors), len(warns)))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
