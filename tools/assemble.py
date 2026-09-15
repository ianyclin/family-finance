#!/usr/bin/env python3
"""把 shell/ 與 chapters/ 組裝成單檔 output/index.html。

用法：
    python3 tools/assemble.py [--chapters-dir chapters] [--out output/index.html]

輸出檔不含 <html> <head> <body>（發佈端會包外層），
但開頭放 <!doctype html> <meta charset> <title> <style>，結尾放 <script>，
可以直接用瀏覽器開（有 doctype 才不會落進怪異模式；發佈端若自己包外層，
重複的 doctype 會被忽略）。

只用標準函式庫。缺章時照樣組裝，並在終端列出缺哪些。
錨點缺失或 id 重複 → exit 1；只缺章 → exit 0。
"""
import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TITLE = "家庭理財白話手冊"
FONTS_URL = ("https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@600;700"
             "&family=Noto+Sans+TC:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap")

# ---- 階段設定表（區隔頁文字，出自 design-brief.md）----
STAGES = [
    (0, "", "導讀", "先花三分鐘決定從哪裡開始。"),
    (1, "第一區", "看清楚",
     "這一區做完，你會有一張家庭資產負債表、一張現金流表，和一個寫了金額與年份的目標。"),
    (2, "第二區", "止血與撐住",
     "這一區做完，你會知道自己撐得過幾個月、哪筆債先還、哪些保障已經有了、哪些賠不起。"),
    (3, "第三區", "長大",
     "這一區做完，你會看懂報酬從哪裡來、費用怎麼吃掉它，並且把投資寫成一張自己的規則卡。"),
    (4, "第四區", "制度",
     "這一區做完，你會查出自己退休時已經有的、看懂稅怎麼算，並把租與買兩邊的帳攤開。"),
    (5, "第五區", "家庭與交棒",
     "這一區做完，你會有一張全家一頁資訊表，受益人與文件位置都填好。"),
    (6, "第六區", "守住", "這一區做完，你會有三個問題，先把多數陷阱篩掉。"),
    (7, "第七區", "例行化", "這一區做完，你會有一份一年的節奏表，知道每年幾月要重查什麼。"),
]
STAGE_NAME = {s[0]: s[2] for s in STAGES}
STAGE_KICKER = {s[0]: s[1] for s in STAGES}
STAGE_GAIN = {s[0]: s[3] for s in STAGES}
STAGE_NAME[8] = "附錄"
STAGE_KICKER[8] = ""
BAR_COUNT = 8  # 進度條八段：0 導讀 … 7 例行化；data-stage=8（附錄）全滿

# 預期章節（依 outline.md §3 的檔名）
EXPECTED = [
    "00-how-to-use", "01-why-and-order", "02-balance-sheet", "03-cash-flow",
    "04-emergency-fund", "05-debt", "06-insurance", "07-time-inflation-compounding",
    "08-risk-diversification-cost", "09-rules-card", "10-retirement", "11-tax",
    "12-housing", "13-family", "14-legacy", "15-scams", "16-action-list",
    "17-glossary-sources",
]

VOID = {"br", "img", "hr", "input", "meta", "link", "path", "circle", "rect", "line",
        "polyline", "polygon", "use", "stop", "ellipse"}
SKIP_TEXT_TAGS = {"svg"}
SKIP_TEXT_CLASSES = {"sources", "foot-note"}


def cjk_count(s):
    return len(re.findall(r"[一-鿿]", s))


class Frag(HTMLParser):
    """從一個章節片段抓出組裝與檢查需要的東西。"""

    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.stack = []          # [(tag, classes)]
        self.skip_depth = 0      # >0 表示目前文字不計入字數
        self.ids = []            # [(id, tag)]
        self.links = []          # ['#ch-01', ...]
        self.terms = []          # dfn 的 data-term
        self.text = []           # 計入字數的文字
        self.section = None      # 根 section 的屬性
        self.h2 = None
        self.eyebrow = None
        self._grab = None        # 'h2' / 'eyebrow'
        self._grab_start = -1    # 開始抓的時候堆疊有多深
        self._buf = []
        # 名詞表
        self.glossary = []       # [(term, word, definition)]
        self._gl_depth = 0
        self._gl_cur = None      # [term, word, [def parts]]
        self._gl_mode = None     # 'dt' / 'dd'

    # -- 工具 --
    def _classes(self, attrs):
        return set(attrs.get("class", "").split())

    def _flush_grab(self):
        if self._grab:
            value = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if self._grab == "h2" and self.h2 is None:
                self.h2 = value
            elif self._grab == "eyebrow" and self.eyebrow is None:
                self.eyebrow = value
            self._grab = None
            self._buf = []

    # -- HTMLParser --
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = self._classes(a)

        if "id" in a:
            self.ids.append((a["id"], tag))
        href = a.get("href", "")
        if href.startswith("#"):
            self.links.append(href)
        if tag == "dfn" and a.get("data-term"):
            self.terms.append(a["data-term"])
        if tag == "section" and "chapter" in cls and self.section is None:
            self.section = a

        if tag == "h2" and self.h2 is None and self._gl_depth == 0:
            self._grab, self._buf, self._grab_start = "h2", [], len(self.stack)
        elif "eyebrow" in cls and self.eyebrow is None:
            self._grab, self._buf, self._grab_start = "eyebrow", [], len(self.stack)

        # 名詞表
        if tag == "dl" and "glossary" in cls:
            self._gl_depth += 1
        elif self._gl_depth:
            if tag == "dt":
                self._close_gl_entry()
                self._gl_cur = [a.get("id", ""), [], []]
                self._gl_mode = "dt"
            elif tag == "dd" and self._gl_cur:
                self._gl_mode = "dd"

        # 只有會進堆疊的標籤才動 skip_depth，否則 svg 裡的 <path> 這種空元素
        # 會有進無出，之後整份文件都不算字數。
        if tag not in VOID:
            if self.skip_depth or tag in SKIP_TEXT_TAGS or (cls & SKIP_TEXT_CLASSES):
                self.skip_depth += 1
            self.stack.append((tag, cls))

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append((a["id"], tag))
        if a.get("href", "").startswith("#"):
            self.links.append(a["href"])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        idx = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                idx = i
                break
        if idx is None:
            return
        if self._grab is not None and idx <= self._grab_start:
            self._flush_grab()
        if self._gl_depth:
            if tag == "dl":
                self._close_gl_entry()
                self._gl_depth -= 1
            elif tag in ("dt", "dd"):
                self._gl_mode = None
        popped = self.stack[idx:]
        del self.stack[idx:]
        for _ in popped:
            if self.skip_depth:
                self.skip_depth -= 1

    def handle_data(self, data):
        if self._grab:
            self._buf.append(data)
        if self._gl_depth and self._gl_cur:
            if self._gl_mode == "dt":
                self._gl_cur[1].append(data)
            elif self._gl_mode == "dd":
                self._gl_cur[2].append(data)
        if not self.skip_depth:
            self.text.append(data)

    def _close_gl_entry(self):
        if not self._gl_cur:
            return
        raw_id, word, definition = self._gl_cur
        word = re.sub(r"\s+", " ", "".join(word)).strip()
        definition = re.sub(r"\s+", " ", "".join(definition)).strip()
        term = raw_id[5:] if raw_id.startswith("term-") else word
        if term and definition:
            self.glossary.append((term, word or term, definition))
        self._gl_cur = None
        self._gl_mode = None


class Chapter(object):
    def __init__(self, path, src, frag):
        self.path = path
        self.src = src
        self.frag = frag
        attrs = frag.section or {}
        self.id = attrs.get("id", "")
        try:
            self.num = int(attrs.get("data-num", "-1"))
        except ValueError:
            self.num = -1
        try:
            self.stage = int(attrs.get("data-stage", "-1"))
        except ValueError:
            self.stage = -1
        self.title = frag.h2 or self.id or os.path.basename(path)
        self.eyebrow = frag.eyebrow or ""
        self.chars = cjk_count("".join(frag.text))


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def num_of(name):
    m = re.match(r"(\d+)", name)
    return int(m.group(1)) if m else 999


def load_chapters(chapters_dir):
    out = []
    if not os.path.isdir(chapters_dir):
        return out
    names = [n for n in os.listdir(chapters_dir) if n.endswith(".html")]
    for name in sorted(names, key=lambda n: (num_of(n), n)):
        path = os.path.join(chapters_dir, name)
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        frag = Frag()
        frag.feed(src)
        frag.close()
        ch = Chapter(path, src, frag)
        if ch.num < 0:
            ch.num = num_of(name)
        out.append(ch)
    return sorted(out, key=lambda c: c.num)


# ---------- 產生外殼片段 ----------

def progress_html(stage):
    label = STAGE_NAME.get(stage, "")
    aria = "閱讀進度：%s（共八區）" % (label or "未標示")
    parts = ['<div class="progress" role="img" aria-label="%s">' % esc(aria)]
    for i in range(BAR_COUNT):
        cls = ["seg"]
        if stage >= i:
            cls.append("is-done")
        if stage == i:
            cls.append("is-current")
        parts.append(
            '<span class="%s"><span class="bar"></span>'
            '<span class="seg-label">%s</span></span>' % (" ".join(cls), esc(STAGE_NAME.get(i, "")))
        )
    parts.append("</div>")
    return "".join(parts)


def divider_html(stage):
    kicker = STAGE_KICKER.get(stage, "")
    name = STAGE_NAME.get(stage, "")
    gain = STAGE_GAIN.get(stage, "")
    parts = ['<div class="stage-divider" id="stage-%d" data-stage="%d">' % (stage, stage)]
    if kicker:
        parts.append('<p class="stage-kicker">%s</p>' % esc(kicker))
    parts.append('<p class="stage-name" role="heading" aria-level="2">%s</p>' % esc(name))
    if gain:
        parts.append('<p class="stage-gain">%s</p>' % esc(gain))
    parts.append("</div>")
    return "".join(parts)


def nav_html(chapters):
    out = ['<nav class="sitenav" id="sitenav" aria-label="章節導覽">',
           '<div class="nav-head"><p class="nav-title">%s</p>'
           '<button type="button" class="nav-close">關閉</button></div>' % esc(TITLE)]
    last_stage = None
    open_list = False
    for ch in chapters:
        if ch.stage != last_stage:
            if open_list:
                out.append("</ul>")
            kicker = STAGE_KICKER.get(ch.stage, "")
            name = STAGE_NAME.get(ch.stage, "第 %s 區" % ch.stage)
            out.append('<p class="nav-stage">%s</p>' % esc((kicker + " " + name).strip()))
            out.append("<ul>")
            open_list = True
            last_stage = ch.stage
        num = "導" if ch.num == 0 else ("附" if ch.num == 17 else str(ch.num))
        aria = ch.eyebrow or ch.title
        out.append(
            '<li class="nav-item" data-ch="%s">'
            '<span class="nav-num">%s</span>'
            '<a href="#%s">%s</a>'
            '<span class="nav-done"><input type="checkbox" data-ch="%s" aria-label="%s 完成"></span>'
            "</li>" % (esc(ch.id), esc(num), esc(ch.id), esc(ch.title), esc(ch.id), esc(aria))
        )
    if open_list:
        out.append("</ul>")
    out.append("</nav>")
    return "\n".join(out)


def topbar_html(total):
    return ("<header class=\"topbar\">"
            "<p class=\"book-title\">%s</p>"
            "<p class=\"where\">共 %d 章</p>"
            "<button type=\"button\" class=\"toc-btn\" aria-controls=\"sitenav\" "
            "aria-expanded=\"false\">目錄</button>"
            "</header>" % (esc(TITLE), total))


SECTION_RE = re.compile(r"<section\b[^>]*>")


def inject_progress(ch):
    m = SECTION_RE.search(ch.src)
    if not m:
        return ch.src
    return ch.src[:m.end()] + "\n" + progress_html(ch.stage) + ch.src[m.end():]


# ---------- 檢查 ----------

def run_checks(chapters, extra_ids):
    errors, warnings = [], []
    seen = {}
    for ch in chapters:
        for i, tag in ch.frag.ids:
            if i in seen:
                errors.append("id 重複：%s（%s 與 %s）" % (i, seen[i], os.path.basename(ch.path)))
            else:
                seen[i] = os.path.basename(ch.path)
    for i in extra_ids:
        if i in seen:
            errors.append("id 重複：%s（外殼產生的 id 與 %s 撞名）" % (i, seen[i]))
        else:
            seen[i] = "外殼"

    present_nums = set(c.num for c in chapters)
    checked = 0
    for ch in chapters:
        for href in ch.frag.links:
            target = href[1:]
            if not target:
                continue
            prefix = target.split("-")[0] + "-"
            if prefix not in ("src-", "ch-", "ws-", "term-", "def-"):
                continue
            checked += 1
            if target in seen:
                continue
            missing_chapter = None
            m = re.match(r"(?:ch|src)-(\d+)", target)
            if m and int(m.group(1)) not in present_nums:
                missing_chapter = int(m.group(1))
            msg = "%s 指向不存在的錨點 #%s" % (os.path.basename(ch.path), target)
            if missing_chapter is not None:
                warnings.append(msg + "（第 %02d 章還沒交，先不算錯）" % missing_chapter)
            else:
                errors.append(msg)
    return errors, warnings, checked, len(seen)


# ---------- 主流程 ----------

def build(chapters_dir, out_path):
    with open(os.path.join(ROOT, "shell", "style.css"), encoding="utf-8") as fh:
        css = fh.read()
    with open(os.path.join(ROOT, "shell", "app.js"), encoding="utf-8") as fh:
        js = fh.read()
    if "</style" in css.lower():
        raise SystemExit("style.css 內含 </style，無法內嵌")
    if "</script" in js.lower():
        raise SystemExit("app.js 內含 </script，無法內嵌")

    chapters = load_chapters(chapters_dir)
    found_nums = set(c.num for c in chapters)
    missing = [n for n in EXPECTED if num_of(n) not in found_nums]

    # 名詞表 → JSON
    glossary = {}
    dup_terms = []
    for ch in chapters:
        for term, word, definition in ch.frag.glossary:
            if term in glossary:
                dup_terms.append(term)
            glossary[term] = definition

    # 章節本體：區隔頁 + 進度條
    body = []
    seen_stages = set()
    extra_ids = []
    for ch in chapters:
        if ch.stage in STAGE_GAIN and ch.stage not in seen_stages:
            body.append(divider_html(ch.stage))
            extra_ids.append("stage-%d" % ch.stage)
        seen_stages.add(ch.stage)
        body.append(inject_progress(ch))
    if missing:
        body.append('<p class="missing-note">這一版還缺 %d 章：%s。</p>'
                    % (len(missing), esc("、".join(missing))))

    errors, warnings, checked, id_count = run_checks(chapters, extra_ids)

    # dfn 對不上名詞表
    orphan_terms = []
    for ch in chapters:
        for term in ch.frag.terms:
            if term not in glossary:
                orphan_terms.append((os.path.basename(ch.path), term))

    gl_json = json.dumps(glossary, ensure_ascii=False).replace("<", "\\u003c")

    html = "\n".join([
        "<!doctype html>",
        '<meta charset="utf-8">',
        "<title>%s</title>" % esc(TITLE),
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="color-scheme" content="light dark">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link rel="stylesheet" href="%s">' % FONTS_URL,
        "<style>",
        css.rstrip(),
        "</style>",
        topbar_html(len(chapters)),
        '<div class="scrim"></div>',
        nav_html(chapters),
        '<main class="page" id="content" data-total-chapters="%d">' % len(chapters),
        "\n".join(body),
        "</main>",
        '<script id="glossary-json" type="application/json">%s</script>' % gl_json,
        "<script>",
        js.rstrip(),
        "</script>",
        "",
    ])

    out_dir = os.path.dirname(os.path.abspath(out_path))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)

    report = {
        "chapters": chapters,
        "missing": missing,
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
        "id_count": id_count,
        "glossary": glossary,
        "dup_terms": dup_terms,
        "orphan_terms": orphan_terms,
        "bytes": len(html.encode("utf-8")),
        "out": out_path,
    }
    return report


def print_report(r):
    print("章節：找到 %d／預期 %d" % (len(r["chapters"]), len(EXPECTED)))
    if r["missing"]:
        print("缺章（%d）：%s" % (len(r["missing"]), "、".join(r["missing"])))
    print("")
    print("每章字數（中文字，不含來源清單與免責句）：")
    total = 0
    for ch in r["chapters"]:
        total += ch.chars
        print("  %-5s stage %-2s %6d 字  %s" % (ch.id or "?", ch.stage, ch.chars, ch.title))
    print("  合計 %d 字" % total)
    print("")
    print("id：%d 個" % r["id_count"])
    print("錨點：檢查 %d 個 #src-／#ch-／#ws-／#term-／#def- 連結" % r["checked"])
    print("名詞表：%d 條；dfn 對不上的 %d 個" % (len(r["glossary"]), len(r["orphan_terms"])))
    for name, term in r["orphan_terms"]:
        print("  警告：%s 的 dfn「%s」在名詞表找不到條目，浮層不會啟動" % (name, term))
    for term in r["dup_terms"]:
        print("  警告：名詞「%s」在名詞表出現一次以上，後者覆蓋前者" % term)
    for w in r["warnings"]:
        print("  警告：%s" % w)
    for e in r["errors"]:
        print("  錯誤：%s" % e)
    print("")
    print("輸出：%s（%.1f KB）" % (r["out"], r["bytes"] / 1024.0))
    print("結果：%d 個錯誤，%d 個警告"
          % (len(r["errors"]), len(r["warnings"]) + len(r["orphan_terms"]) + len(r["dup_terms"])))


def main():
    ap = argparse.ArgumentParser(description="組裝家庭理財白話手冊單檔輸出")
    ap.add_argument("--chapters-dir", default=os.path.join(ROOT, "chapters"))
    ap.add_argument("--out", default=os.path.join(ROOT, "output", "index.html"))
    args = ap.parse_args()
    r = build(args.chapters_dir, args.out)
    print_report(r)
    sys.exit(1 if r["errors"] else 0)


if __name__ == "__main__":
    main()
