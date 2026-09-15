#!/usr/bin/env python3
"""章節片段哨兵：檢查 chapters/NN-slug.html 是否符合 components.md 的契約。

用法：python3 tools/check_fragment.py chapters/04-emergency-fund.html [--json] [--loose]
--loose 給附錄（17）用：不要求章首章尾結構、來源交叉引用只算警告。
錯誤 → exit 1；只有警告 → exit 0。
"""
import json
import re
import sys
from html.parser import HTMLParser

VOID = {"br", "img", "hr", "input", "meta", "link", "path", "circle", "rect", "line",
        "polyline", "polygon", "use", "stop", "ellipse"}

ALLOWED_TAGS = {"section", "header", "footer", "h2", "h3", "h4", "p", "ul", "ol", "li",
                "strong", "span", "dfn", "sup", "a", "details", "summary", "div", "table",
                "thead", "tbody", "tr", "th", "td", "article", "dl", "dt", "dd", "aside",
                "pre", "figure", "figcaption", "svg"}
SVG_TAGS = {"svg", "g", "path", "circle", "rect", "line", "polyline", "polygon", "text", "tspan",
            "title", "desc", "defs", "use", "linearGradient", "stop", "ellipse", "clipPath"}

ALLOWED_CLASSES = {"chapter", "ch-head", "eyebrow", "lede", "ch-meta", "meta-block", "checks", "time",
                   "num", "badge", "cite", "table-wrap", "cards", "card", "steps", "chart",
                   "box", "fact", "formula", "tradeoff", "warning", "myth", "action",
                   "box-label", "how", "caveat", "cols", "col", "bottom", "ws-date", "worksheet", "blank",
                   "ch-foot", "gain", "today", "do", "crit", "est", "later", "sources-wrap", "sources",
                   "lvl", "official", "academic", "industry", "inference", "foot-note",
                   # 導讀與附錄的額外元素（design-brief.md）
                   "checkup-table", "q-index", "triage", "routes", "manifesto", "glossary",
                   "wide", "swipe-hint", "expiry", "revisions", "master-list", "pair", "version-line",
                   "author", "keypoints", "author-route", "route-intro", "route-note"}
WIDE_TABLES = {"checkup-table", "expiry"}

FORBIDDEN_ERR = ["推薦", "建議你", "你應該", "最好的做法", "必買", "必賺", "穩賺", "穩定高報酬",
                 "無風險", "零風險", "長期必勝", "財富自由", "被動收入", "翻身", "錯過就沒了",
                 "最後機會", "不理財財不理你", "有錢人都這樣做", "別擔心", "很簡單", "末日",
                 "等回檔", "先觀望", "現在太高"]
FORBIDDEN_WARN = ["保證", "保本", "一定", "建議", "應該", "老公", "老婆", "你還在"]

PRODUCT_RE = re.compile(
    r"\b(00\d{2,4}[A-Z]?|VT|VTI|VOO|VWRA|VWRD|VALU|AVGS|AVUV|AVDV|CBUO|SPY|QQQ|BND|BNDW|IVV|SCHD|ARKK)\b"
    r"|元大|富邦|國泰|中信|中國信託|玉山|台新|永豐|凱基|統一投信|群益|復華|兆豐|第一金|華南|彰銀|合庫|台銀|土銀"
    r"|台積電|鴻海|聯發科|長榮|陽明"
    r"|Firstrade|Interactive Brokers|嘉信|Schwab|TD Ameritrade|eToro|Robinhood"
    r"|南山|新光|遠雄|全球人壽|三商美邦|安聯|保誠|法巴|台灣人壽|富邦人壽|國泰人壽|中國人壽|凱基人壽"
    r"|Moneybook|CWMoney|記帳城市|麻布記帳|Richart|LINE Bank|將來銀行|樂天銀行"
)

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⭕⌚-⏿]")


class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "text")

    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []
        self.parent = parent
        self.text = []

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

    def has_ancestor(self, pred):
        p = self.parent
        while p is not None:
            if pred(p):
                return True
            p = p.parent
        return False


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
        node = Node(tag, attrs, self.cur)
        self.cur.children.append(node)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is None:
            self.errors.append(f"多餘的結束標籤 </{tag}>（第 {self.getpos()[0]} 行）")
            return
        if n is not self.cur:
            self.errors.append(f"標籤沒有正確關閉：在 </{tag}> 之前 <{self.cur.tag}> 還沒關（第 {self.getpos()[0]} 行）")
        self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def cjk_count(s):
    return len(re.findall(r"[一-鿿]", s))


def check(path, loose=False):
    src = open(path, encoding="utf-8").read()
    p = Parser()
    p.feed(src)
    p.close()
    errors = list(p.errors)
    warns = []
    if p.cur is not p.root:
        errors.append(f"檔案結束時 <{p.cur.tag}> 還沒關閉")

    roots = [c for c in p.root.children if not isinstance(c, str)]
    if len(roots) != 1 or roots[0].tag != "section" or "chapter" not in roots[0].classes():
        errors.append("根元素必須是唯一一個 <section class=\"chapter\">")
        return errors, warns, {}
    sec = roots[0]
    for k in ("id", "data-num", "data-stage"):
        if k not in sec.attrs:
            errors.append(f"<section> 缺 {k}")
    chnum = sec.attrs.get("data-num", "?")

    for n in sec.iter():
        in_svg = n.tag in SVG_TAGS and n.has_ancestor(lambda a: a.tag == "svg") or n.tag == "svg"
        if in_svg:
            if n.tag not in SVG_TAGS:
                errors.append(f"svg 內不允許的標籤 <{n.tag}>")
            continue
        if n.tag not in ALLOWED_TAGS:
            errors.append(f"不允許的標籤 <{n.tag}>")
        if "style" in n.attrs:
            errors.append(f"<{n.tag}> 用了 style 屬性")
        bad = n.classes() - ALLOWED_CLASSES
        if bad:
            errors.append(f"<{n.tag}> 自創 class：{sorted(bad)}")

    # 章首
    head = next((n for n in sec.iter() if n.tag == "header" and "ch-head" in n.classes()), None)
    if loose:
        pass
    elif head is None:
        errors.append("缺 <header class=\"ch-head\">")
    else:
        for cls in ("eyebrow", "lede", "ch-meta", "time"):
            if not any(cls in n.classes() for n in head.iter()):
                errors.append(f"章首缺 .{cls}")
        if not any(n.tag == "h2" for n in head.iter()):
            errors.append("章首缺 <h2>")
        blocks = [n for n in head.iter() if "meta-block" in n.classes()]
        if len(blocks) != 3:
            errors.append(f"章首 meta-block 應有 3 個，實際 {len(blocks)}")
        lede = next((n for n in head.iter() if "lede" in n.classes()), None)
        if lede is not None and cjk_count(lede.all_text()) > 30:
            errors.append(f"一句話超過 30 字（{cjk_count(lede.all_text())} 字）")

    # 章尾
    foot = next((n for n in sec.iter() if n.tag == "footer" and "ch-foot" in n.classes()), None)
    if loose:
        pass
    elif foot is None:
        errors.append("缺 <footer class=\"ch-foot\">")
    else:
        for cls in ("gain", "today", "later", "sources-wrap", "foot-note"):
            if not any(cls in n.classes() for n in foot.iter()):
                errors.append(f"章尾缺 .{cls}")
        today = next((n for n in foot.iter() if "today" in n.classes()), None)
        if today is not None:
            for cls in ("do", "crit", "est"):
                if not any(cls in n.classes() for n in today.iter()):
                    errors.append(f"今天的一件事缺 .{cls}")

    # 框
    boxes = [n for n in sec.iter() if n.tag == "aside" and "box" in n.classes()]
    if len(boxes) > 7:
        errors.append(f"框超過 7 個（{len(boxes)}）")
    actions = [b for b in boxes if "action" in b.classes()]
    if len(actions) > 2:
        errors.append(f"動手框超過 2 張（{len(actions)}）")
    kinds = {"fact", "formula", "tradeoff", "warning", "myth", "action"}
    for b in boxes:
        k = b.classes() & kinds
        if len(k) != 1:
            errors.append(f"框的種類不明確：{sorted(b.classes())}")
        if not any("box-label" in n.classes() for n in b.iter()):
            errors.append(f"框缺 .box-label：{sorted(b.classes())}")
        if "tradeoff" in b.classes():
            bottom = next((n for n in b.iter() if "bottom" in n.classes()), None)
            if bottom is None or "只有你知道" not in bottom.all_text():
                errors.append("取捨框缺固定底句「這一題沒有標準答案，只有你知道＿＿＿」")
            elif "＿＿＿" in bottom.all_text() and bottom.all_text().strip().endswith(("＿＿＿。", "＿＿＿")):
                warns.append("取捨框底句的＿＿＿還沒填成具體內容")
        if "formula" in b.classes():
            if not any(n.tag == "pre" for n in b.iter()):
                errors.append("算式框缺 <pre>")
            if not any("caveat" in n.classes() for n in b.iter()):
                errors.append("算式框缺 .caveat（這只是算術，不是預測）")
        if "myth" in b.classes():
            t = b.all_text()
            for need in ("很多人以為", "實際上", "為什麼會這樣誤會"):
                if need not in t:
                    errors.append(f"誤解框缺「{need}」")

    # 對照卡
    for card in (n for n in sec.iter() if n.tag == "article" and "card" in n.classes()):
        dts = [d.all_text().strip() for d in card.iter() if d.tag == "dt"]
        want = ["怎麼運作", "最好的情況", "最差的情況", "成本", "適合誰", "不適合誰"]
        if dts != want:
            errors.append(f"對照卡六欄不符：{dts}")

    # 表格欄數
    for t in (n for n in sec.iter() if n.tag == "table"):
        if t.classes() & WIDE_TABLES:
            continue
        rows = [r for r in t.iter() if r.tag == "tr"]
        if rows:
            cells = [c for c in rows[0].children if not isinstance(c, str) and c.tag in ("th", "td")]
            if len(cells) > 3:
                errors.append(f"表格超過 3 欄（{len(cells)}）")

    # 引用與來源
    cites = [n for n in sec.iter() if n.tag == "sup" and "cite" in n.classes()]
    cite_targets = set()
    for c in cites:
        a = next((x for x in c.iter() if x.tag == "a"), None)
        if a is None or not a.attrs.get("href", "").startswith("#src-"):
            errors.append("cite 上標缺 <a href=\"#src-…\">")
        else:
            cite_targets.add(a.attrs["href"][1:])
    src_list = next((n for n in sec.iter() if n.tag == "ol" and "sources" in n.classes()), None)
    src_ids = set()
    if src_list is None:
        if not loose:
            errors.append("缺 <ol class=\"sources\">")
    else:
        for li in (n for n in src_list.children if not isinstance(n, str) and n.tag == "li"):
            sid = li.attrs.get("id", "")
            if not sid.startswith("src-"):
                errors.append("來源 li 缺 id=\"src-…\"")
            src_ids.add(sid)
            lvl = next((x for x in li.iter() if "lvl" in x.classes()), None)
            if lvl is None or not (lvl.classes() & {"official", "academic", "industry", "inference"}):
                errors.append(f"來源 {sid} 缺等級（official/academic/industry/inference）")
            elif "inference" not in lvl.classes() and not any(x.tag == "a" for x in li.iter()):
                errors.append(f"來源 {sid} 不是本文推論卻沒有網址")
            if "查證" not in li.all_text() and (lvl is None or "inference" not in lvl.classes()):
                warns.append(f"來源 {sid} 缺查證日期")
    for t in sorted(cite_targets - src_ids):
        (warns if loose else errors).append(f"正文引用了不存在的來源 {t}")
    for s in sorted(src_ids - cite_targets):
        (warns if loose else errors).append(f"來源 {s} 沒有被正文引用")
    for s in src_ids:
        if not re.fullmatch(rf"src-{int(chnum):02d}-\d+", s) if chnum.isdigit() else False:
            warns.append(f"來源編號格式不是 src-{int(chnum):02d}-N：{s}")

    # dfn
    seen = {}
    for d in (n for n in sec.iter() if n.tag == "dfn"):
        term = d.attrs.get("data-term", "")
        if not term or d.attrs.get("id") != f"def-{term}":
            errors.append(f"dfn 的 id 必須是 def-＋data-term：{d.attrs}")
        if term in seen:
            warns.append(f"術語「{term}」在本章出現兩次 dfn")
        seen[term] = True

    # 文字層檢查（排除來源清單與 svg）
    def visible_text(node, skip):
        out = []
        for c in node.children:
            if isinstance(c, str):
                out.append(c)
            elif skip(c):
                continue
            else:
                out.append(visible_text(c, skip))
        return "".join(out)

    body_text = visible_text(sec, lambda n: n.tag in ("svg",) or n.classes() & {"sources", "foot-note"})
    for w in FORBIDDEN_ERR:
        for m in re.finditer(re.escape(w), body_text):
            ctx = body_text[max(0, m.start() - 15): m.end() + 15].replace("\n", " ")
            errors.append(f"禁用字眼「{w}」：…{ctx}…")
    for w in FORBIDDEN_WARN:
        n = len(re.findall(re.escape(w), body_text))
        if n:
            warns.append(f"需人工判斷的字眼「{w}」出現 {n} 次（保證收益、法定用語可留；作為結論不可）")
    product_text = visible_text(sec, lambda n: n.tag in ("svg",) or n.classes() & {"sources", "foot-note", "author"})
    for m in PRODUCT_RE.finditer(product_text):
        ctx = product_text[max(0, m.start() - 15): m.end() + 15].replace("\n", " ")
        errors.append(f"疑似商品／公司名「{m.group(0)}」：…{ctx}…")

    # 驚嘆號、表情符號（框標籤與時間列除外）
    def text_outside_labels(node):
        out = []
        for c in node.children:
            if isinstance(c, str):
                out.append(c)
            elif c.tag == "svg" or c.classes() & {"box-label", "time", "est", "sources", "pair"}:
                continue
            else:
                out.append(text_outside_labels(c))
        return "".join(out)

    plain = text_outside_labels(sec)
    if "！" in plain or "!" in plain:
        errors.append(f"正文有驚嘆號（{plain.count('！') + plain.count('!')} 處）")
    em = EMOJI_RE.findall(plain)
    if em:
        errors.append(f"正文有表情符號：{''.join(em)[:20]}")

    # 段落句數與句長
    long_paras = 0
    long_sents = 0
    for pnode in (n for n in sec.iter() if n.tag == "p" and not (n.classes() & {"box-label", "time", "est", "foot-note", "eyebrow"})):
        t = pnode.all_text().strip()
        sents = [s for s in re.split(r"[。！？]", t) if s.strip()]
        if len(sents) > 4:
            long_paras += 1
        long_sents += sum(1 for s in sents if cjk_count(s) > 40)
    if long_paras:
        warns.append(f"{long_paras} 段超過 4 句")
    if long_sents:
        warns.append(f"{long_sents} 句超過 40 字")

    # 假設聲明
    if re.search(r"年化|報酬率|成長率", body_text) and not re.search(r"不是承諾|不是預測", body_text):
        errors.append("出現報酬率／年化／成長率，但沒有「這是假設，不是承諾」或「這只是算術，不是預測」")

    stats = {
        "chars": cjk_count(body_text),
        "boxes": len(boxes),
        "action_boxes": len(actions),
        "sources": len(src_ids),
        "cites": len(cites),
        "dfn": len(seen),
        "h3": sum(1 for n in sec.iter() if n.tag == "h3" and not n.has_ancestor(lambda a: a.tag in ("header", "footer"))),
        "cards": sum(1 for n in sec.iter() if "card" in n.classes()),
        "figures": sum(1 for n in sec.iter() if n.tag == "figure"),
    }
    return errors, warns, stats


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    errors, warns, stats = check(path, loose="--loose" in sys.argv)
    if "--json" in sys.argv:
        print(json.dumps({"file": path, "errors": errors, "warnings": warns, "stats": stats}, ensure_ascii=False, indent=1))
    else:
        print(f"檔案：{path}")
        print(f"統計：{json.dumps(stats, ensure_ascii=False)}")
        for e in errors:
            print(f"錯誤：{e}")
        for w in warns:
            print(f"警告：{w}")
        print(f"結果：{len(errors)} 個錯誤，{len(warns)} 個警告")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
