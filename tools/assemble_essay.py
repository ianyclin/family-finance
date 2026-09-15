#!/usr/bin/env python3
"""把 essay/sections/*.html 依 outline.md §2 的順序組成 essay/index.html。

用法：
    python3 tools/assemble_essay.py [--sections essay/sections] [--out essay/index.html]

輸出檔開頭放 <!doctype html> <meta charset> <title> <style>，結尾放 <script>，
可以直接用瀏覽器開；發佈端若自己包外層，重複的 doctype 會被忽略。

只用標準函式庫。缺節時照樣組裝並列出缺哪些。
底線開頭的檔案（例如 _sample.html）一律略過。
錨點缺失或 id 重複 → exit 1；只缺節 → exit 0。
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_essay import Parser, cjk_count, load_spec  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TITLE = "隔離人性"
SUBTITLE = "先弄對八件事，認得出自己的心魔，再把決定寫在平靜的時候"
HANDBOOK = "https://claude.ai/code/artifact/76934d5e-136e-42b8-8de1-14e623f8859c"
FB = "https://www.facebook.com/profile.php?id=100084000897269"
FONTS_URL = ("https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@600;700"
             "&family=Noto+Sans+TC:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap")

ABOUT = ("這篇是寫給零基礎朋友的投資專篇，主軸是知識，我自己的事只當例子。"
         "手冊是另一份文件，沒有它也讀得完這篇。不用照順序讀；想找自己的問題，直接跳第十三節。")

RULES = ("寫法上的四條規矩：我只講我做了什麼、為什麼、付了什麼代價，不寫我的報酬數字；"
         "每個觀念都指回手冊對應的那一章或原始研究；每一件我做過的事都對得到一篇貼文的日期；"
         "每一節的最後一句，把決定交還給你。")

THESIS = ("這篇只有一條線。報酬來自公司賺錢，長期看多數人卻拿不到市場給的那一份，差在人，不在挑了什麼。"
          "所以我把決定寫在平靜的時候，讓最難受的那一天沒有決定可做。"
          "書名是我 2026 年 5 月寫的一句話：隔離人性<q>不是沒有情緒，而是讓關鍵決策在情緒出現前就已完成</q>。")

MAP = [
    ("第 1 到 5 節", "市場長什麼樣", "報酬從哪來、時間、費用、分散、波動", "#01-where-return-comes-from", False),
    ("第 6 到 8 節", "人在市場裡最常做的三個動作", "等跌、挑日子、先賣一些", "#06-timing", False),
    ("第 9 到 10 節", "人為什麼會這樣", "行為落差、大腦與偏誤清單", "#09-behavior-gap", False),
    ("第 11 節", "規則卡", "把決定寫在平靜的時候", "#11-rules", True),
    ("第 12 節", "如果你問我怎麼做", "七條，含商品清單", "#12-seven-things", False),
    ("第 13 節", "二十七題、六種心魔", "急著找答案先看這裡", "#13-questions", False),
]

DISCLAIMER = ("這是一般說明，不是投資建議；數字有查證日期，會過期；"
              "作者的做法是一個人的做法，不是研究結論。")


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


# ---------------- 讀節 ----------------

class Section(object):
    def __init__(self, path, html, node):
        self.path = path
        self.html = html
        self.node = node
        self.id = node.attrs.get("id", "")

    def h2_text(self):
        h2 = next((n for n in self.node.iter() if n.tag == "h2"), None)
        if h2 is None:
            return self.id
        parts = []
        for c in h2.children:
            if isinstance(c, str):
                parts.append(c)
            elif "num" not in c.classes():
                parts.append(c.all_text())
        return re.sub(r"\s+", " ", "".join(parts)).strip()

    def dates(self):
        out = []
        for t in self.node.iter():
            if t.tag == "time":
                d = t.attrs.get("datetime", "")
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) and d not in out:
                    out.append(d)
        return sorted(out)

    def terms(self):
        """{dfn id: 白話解釋}。先用 title 屬性，沒有就抓 dfn 後面到句號為止的句子。"""
        out = {}
        for p in self.node.iter():
            if p.tag not in ("p", "li"):
                continue
            kids = p.children
            for i, c in enumerate(kids):
                if isinstance(c, str) or c.tag != "dfn":
                    continue
                key = c.attrs.get("id") or c.all_text().strip()
                title = (c.attrs.get("title") or "").strip()
                if title:
                    out[key] = title
                    continue
                tail = []
                for rest in kids[i + 1:]:
                    tail.append(rest if isinstance(rest, str) else rest.all_text())
                tail = "".join(tail)
                m = re.split(r"[。？?]", tail, 1)[0].strip()
                m = m.lstrip("，、：:；;")
                m = re.sub(r"^(就是|指的是|是指|是|指)", "", m).lstrip("，、")
                if m:
                    out[key] = re.sub(r"\s+", " ", m)
        return out

    def stats(self):
        total = cjk_count(self.node.all_text())
        story = next((n for n in self.node.iter()
                      if n.tag == "div" and "story" in n.classes()), None)
        st = cjk_count(story.all_text()) if story is not None else 0
        return total, st


def read_sections(sec_dir):
    """回傳 {id: Section}、解析錯誤清單。底線開頭的檔案略過。"""
    found, errors = {}, []
    if not os.path.isdir(sec_dir):
        return found, ["找不到節目錄 %s" % sec_dir]
    for name in sorted(os.listdir(sec_dir)):
        if not name.endswith(".html") or name.startswith("_"):
            continue
        path = os.path.join(sec_dir, name)
        html = open(path, encoding="utf-8").read()
        p = Parser()
        p.feed(html)
        p.close()
        for e in p.errors:
            errors.append("%s：%s" % (name, e))
        parts = [n for n in p.root.iter()
                 if n.tag == "section" and "part" in n.classes()]
        if len(parts) != 1:
            errors.append("%s：應該只有一個 <section class=\"part\">，實際 %d 個"
                          % (name, len(parts)))
            continue
        sec = Section(path, html.strip(), parts[0])
        if not sec.id:
            errors.append("%s：<section> 沒有 id" % name)
            continue
        if sec.id in found:
            errors.append("%s：節 id 重複（%s）" % (name, sec.id))
            continue
        found[sec.id] = sec
    return found, errors


# ---------------- 組頁 ----------------

def cover_html(sections, spec, order):
    toc = ['<nav class="toc" aria-label="目錄">', "<h2>目錄</h2>", "<ol>"]
    for sid in order:
        if sid in sections:
            toc.append('<li><a href="#%s">%s</a></li>'
                       % (esc(sid), esc(sections[sid].h2_text())))
        else:
            toc.append('<li><span class="pending">%s（還沒寫）</span></li>'
                       % esc(spec[sid]["title"]))
    toc += ["</ol>", "</nav>"]
    return "\n".join([
        '<header class="cover">',
        "<h1>%s</h1>" % esc(TITLE),
        '<p class="subtitle">%s</p>' % esc(SUBTITLE),
        '<p class="thesis">%s</p>' % THESIS,
        '<ol class="map">' + "".join(
            '<li%s><b>%s</b><a href="%s">%s</a><br>%s</li>'
            % (' class="is-hinge"' if hinge else "", esc(rng), href, esc(title), esc(sub))
            for rng, title, sub, href, hinge in MAP) + "</ol>",
        '<p class="about">%s</p>' % esc(ABOUT),
        '<p class="handbook-link">每一節的證據都指回這本手冊：'
        '<a href="%s">家庭理財白話手冊</a>。</p>' % HANDBOOK,
        "\n".join(toc),
        "</header>",
    ])


def footer_html(sections, spec, order):
    rows = []
    for sid in order:
        sec = sections.get(sid)
        if sec is None:
            continue
        ds = sec.dates()
        if not ds:
            continue
        links = "、".join('<a href="%s">%s</a>' % (FB, d) for d in ds)
        rows.append('<li><span class="sec-name">第 %d 節</span>'
                    '<span class="day-list">%s</span></li>' % (spec[sid]["num"], links))
    return "\n".join([
        '<footer class="page-foot">',
        '<p class="rules">%s</p>' % esc(RULES),
        '<p class="disclaimer">%s</p>' % esc(DISCLAIMER),
        '<section class="dates">',
        "<h2>作者貼文日期索引</h2>",
        "<ol>",
        "\n".join(rows) if rows else "<li>還沒有任何日期。</li>",
        "</ol>",
        '<p class="fb">每一則都在粉專上：<a href="%s">家庭財務規劃與指數投資</a>。</p>' % FB,
        "</section>",
        "</footer>",
    ])


def run_checks(html):
    """錨點與 id 重複。"""
    errors = []
    ids = re.findall(r'\sid="([^"]+)"', html)
    dup = sorted({i for i in ids if ids.count(i) > 1})
    for d in dup:
        errors.append("id 重複：%s" % d)
    idset = set(ids)
    hrefs = sorted(set(re.findall(r'href="#([^"]+)"', html)))
    for h in hrefs:
        if h not in idset:
            errors.append("內部連結 #%s 沒有對應的 id" % h)
    return errors, len(hrefs), len(idset)


def build(sec_dir, out_path, css_path, js_path):
    spec, order = load_spec()
    sections, errors = read_sections(sec_dir)

    unknown = [sid for sid in sections if sid not in spec]
    for sid in unknown:
        errors.append("節 %s 不在 outline §2 的節清單裡，已略過" % sid)
        sections.pop(sid)
    missing = [sid for sid in order if sid not in sections]

    css = open(css_path, encoding="utf-8").read()
    js = open(js_path, encoding="utf-8").read()

    terms = {}
    for sid in order:
        if sid in sections:
            terms.update(sections[sid].terms())

    body = [sections[sid].html for sid in order if sid in sections]
    if missing:
        body.append('<p class="missing-note">這一版還缺 %d 節：%s。</p>'
                    % (len(missing), esc("、".join(missing))))

    terms_json = json.dumps(terms, ensure_ascii=False).replace("<", "\\u003c")

    html = "\n".join([
        "<!doctype html>",
        '<meta charset="utf-8">',
        "<title>%s</title>" % esc(TITLE),
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="color-scheme" content="light dark">',
        '<meta name="description" content="%s">' % esc(SUBTITLE),
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link rel="stylesheet" href="%s">' % FONTS_URL,
        "<style>",
        css.rstrip(),
        "</style>",
        cover_html(sections, spec, order),
        '<main class="wrap" id="content">',
        "\n".join(body),
        "</main>",
        footer_html(sections, spec, order),
        '<script id="terms-json" type="application/json">%s</script>' % terms_json,
        "<script>",
        js.rstrip(),
        "</script>",
        "",
    ])

    anchor_errors, n_href, n_id = run_checks(html)
    errors += anchor_errors

    out_dir = os.path.dirname(os.path.abspath(out_path))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)

    return {
        "out": out_path,
        "sections": sections,
        "order": order,
        "spec": spec,
        "missing": missing,
        "errors": errors,
        "terms": terms,
        "hrefs": n_href,
        "ids": n_id,
        "bytes": len(html.encode("utf-8")),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sections", default=os.path.join(ROOT, "essay", "sections"))
    ap.add_argument("--out", default=os.path.join(ROOT, "essay", "index.html"))
    ap.add_argument("--css", default=os.path.join(ROOT, "essay", "shell", "style.css"))
    ap.add_argument("--js", default=os.path.join(ROOT, "essay", "shell", "app.js"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    r = build(args.sections, args.out, args.css, args.js)
    spec, sections = r["spec"], r["sections"]

    rows = []
    total = story_total = 0
    for sid in r["order"]:
        sec = sections.get(sid)
        if sec is None:
            rows.append({"id": sid, "num": spec[sid]["num"], "chars": None,
                         "target": spec[sid]["target"], "story_chars": None,
                         "story_ratio": None, "dates": []})
            continue
        c, s = sec.stats()
        total += c
        story_total += s
        rows.append({"id": sid, "num": spec[sid]["num"], "chars": c,
                     "target": spec[sid]["target"], "story_chars": s,
                     "story_ratio": round(s / c, 3) if c else 0,
                     "dates": sec.dates()})

    summary = {
        "out": r["out"], "bytes": r["bytes"], "sections": rows,
        "total_chars": total, "story_chars": story_total,
        "story_ratio": round(story_total / total, 3) if total else 0,
        "terms": len(r["terms"]), "missing": r["missing"],
        "anchors_checked": r["hrefs"], "ids": r["ids"], "errors": r["errors"],
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=1))
    else:
        print("輸出：%s（%.1f KB）" % (r["out"], r["bytes"] / 1024))
        want_terms = sum(len(spec[s]["terms"]) for s in r["order"] if s in spec)
        print("節：%d／%d　術語：%d／%d　錨點檢查：%d 個連結對 %d 個 id"
              % (len(sections), len(r["order"]), len(r["terms"]), want_terms,
                 r["hrefs"], r["ids"]))
        print("%-4s %-28s %6s %6s %6s %6s  %s" %
              ("節", "id", "字數", "目標", "故事", "占比", "日期"))
        for row in rows:
            if row["chars"] is None:
                print("%-4d %-28s %6s %6d %6s %6s  —"
                      % (row["num"], row["id"], "缺", row["target"], "—", "—"))
                continue
            flag = "  ←超過 30%" if row["story_ratio"] > 0.30 else ""
            print("%-4d %-28s %6d %6d %6d %5.1f%%  %s%s"
                  % (row["num"], row["id"], row["chars"], row["target"],
                     row["story_chars"], row["story_ratio"] * 100,
                     "、".join(row["dates"]), flag))
        print("合計：%d 字（故事 %d 字，占 %.1f%%）"
              % (total, story_total, summary["story_ratio"] * 100))
        if r["missing"]:
            print("還缺 %d 節：%s" % (len(r["missing"]), "、".join(r["missing"])))
        for e in r["errors"]:
            print("錯誤：%s" % e)
        print("結果：%d 個錯誤" % len(r["errors"]))

    sys.exit(1 if r["errors"] else 0)


if __name__ == "__main__":
    main()
