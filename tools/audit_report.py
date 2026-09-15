#!/usr/bin/env python3
"""把兩份稽核 JSON（作者補充素材 32 條、粉專整合項目）組成一頁 HTML 稽核表。"""
import html
import json
import sys
from collections import Counter

ROOT = "/Users/linyenchu/Cladue Code/family-finance"
SUPP = f"{ROOT}/tools/state/audit-supplement.json"
FB = f"{ROOT}/tools/state/audit-fb.json"
OUT = f"{ROOT}/output/audit.html"

STATUS_ZH = {
    "present": "在手冊裡", "partial": "部分在", "missing": "找不到", "dropped-by-design": "裁定不放",
    "not-applicable": "確認未誤入",
}
FAITH_ZH = {"ok": "與原文一致", "date-mismatch": "日期不符", "quote-mismatch": "引句不符", "number-mismatch": "數字不符", "tone-violation": "語氣走樣", "n/a": "—"}


def esc(s):
    return html.escape(str(s or ""))


def table(rows, cols):
    out = ['<div class="table-wrap"><table>', "<thead><tr>" + "".join(f"<th>{esc(c[1])}</th>" for c in cols) + "</tr></thead><tbody>"]
    for r in rows:
        cells = []
        for key, _label in cols:
            v = r.get(key, "")
            if key == "status":
                v = f'<span class="st st-{esc(v)}">{esc(STATUS_ZH.get(v, v))}</span>'
            elif key == "faithful":
                v = f'<span class="ft ft-{esc(v).replace("/", "-")}">{esc(FAITH_ZH.get(v, v))}</span>'
            else:
                v = esc(v)
            cells.append(f"<td>{v}</td>")
        out.append("<tr>" + "".join(cells) + "</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def main():
    supp = json.load(open(SUPP, encoding="utf-8"))
    fb = json.load(open(FB, encoding="utf-8")) if len(sys.argv) < 2 or sys.argv[1] != "--supp-only" else []
    cs = Counter(r["status"] for r in supp)
    cf = Counter(r["status"] for r in fb)
    ff = Counter(r.get("faithful") for r in fb)

    def stat_line(c, keys):
        return " · ".join(f"{STATUS_ZH.get(k, k)} {c.get(k, 0)}" for k in keys if c.get(k))

    page = f"""<title>素材稽核表</title>
<meta charset="utf-8">
<style>
:root{{--paper:#F4F6F8;--surface:#fff;--ink:#1B2733;--muted:#5C6B78;--line:#CBD3DA;--fill:#E8EDF1;--accent:#B33A2E;--teal:#1E7B6C;--amber:#9A6B12;--amber-soft:#F5EBD3;--teal-soft:#DDEFEA;--accent-soft:#F6E4E1}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--paper:#121820;--surface:#1A222B;--ink:#E6EAEE;--muted:#9AA7B2;--line:#33404B;--fill:#222C36;--accent:#E2685A;--teal:#4FB8A5;--amber:#D9A441;--amber-soft:#3A2E12;--teal-soft:#173129;--accent-soft:#3A2320}}}}
:root[data-theme="dark"]{{--paper:#121820;--surface:#1A222B;--ink:#E6EAEE;--muted:#9AA7B2;--line:#33404B;--fill:#222C36;--accent:#E2685A;--teal:#4FB8A5;--amber:#D9A441;--amber-soft:#3A2E12;--teal-soft:#173129;--accent-soft:#3A2320}}
body{{background:var(--paper);color:var(--ink);font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif;font-size:15px;line-height:1.7;margin:0;padding:1.5rem 1rem 4rem}}
main{{max-width:72rem;margin:0 auto}}
h1{{font-family:"Noto Serif TC","Songti TC",serif;font-size:1.7rem;margin:.2rem 0 .3rem}}
h2{{font-family:"Noto Serif TC","Songti TC",serif;font-size:1.25rem;margin:2rem 0 .5rem;border-top:3px solid var(--ink);padding-top:.6rem}}
p.lede{{color:var(--muted);margin:0 0 1rem}}
.sum{{display:flex;flex-wrap:wrap;gap:.5rem 1.2rem;margin:.4rem 0 1rem;font-family:"IBM Plex Mono",Menlo,monospace;font-size:.85rem;color:var(--muted)}}
.table-wrap{{overflow-x:auto;background:var(--surface);border:1px solid var(--line)}}
table{{border-collapse:collapse;width:100%;min-width:64rem;font-size:.86rem}}
th,td{{border-bottom:1px solid var(--line);padding:.5rem .6rem;vertical-align:top;text-align:left}}
th{{color:var(--muted);font-weight:500;background:var(--fill);position:sticky;top:0}}
td:nth-child(1){{min-width:11rem;font-weight:700}}
td{{max-width:22rem}}
.st,.ft{{display:inline-block;padding:.05em .5em;border-radius:3px;font-size:.8rem;white-space:nowrap;font-family:"IBM Plex Mono",Menlo,monospace}}
.st-present,.ft-ok{{background:var(--teal-soft);color:var(--teal)}}
.st-partial{{background:var(--amber-soft);color:var(--amber)}}
.st-missing,.ft-date-mismatch,.ft-quote-mismatch,.ft-number-mismatch,.ft-tone-violation{{background:var(--accent-soft);color:var(--accent)}}
.st-dropped-by-design,.st-not-applicable,.ft-n-a{{background:var(--fill);color:var(--muted)}}
.legend{{font-size:.85rem;color:var(--muted);margin:.5rem 0 1rem}}
</style>
<main>
<h1>素材稽核表</h1>
<p class="lede">作者補充的 32 條圖與主張，以及粉專 154 篇的整合項目，逐條對照：裁定、查證結果、現在手冊裡在不在、在哪一句、與原文是否一致。稽核日 2026-09-08。</p>
<p class="legend">狀態：「在手冊裡」＝裁定要放的內容現在確實在；「部分在」＝只放了一部分，備註說明缺哪半；「找不到」＝裁定要放但現在沒有；「裁定不放」＝查證後決定不放（附理由）。</p>

<h2>一、作者補充的 32 條圖與主張</h2>
<div class="sum"><span>{stat_line(cs, ["present", "partial", "missing", "dropped-by-design"])}</span></div>
{table(supp, [("claim", "素材"), ("ruling", "裁定與理由"), ("verified", "查證結果"), ("factError", "素材本身的錯"), ("status", "現況"), ("where", "在哪裡"), ("quote", "手冊原句"), ("note", "備註")])}

<h2>二、粉專 154 篇的整合項目</h2>
<div class="sum"><span>{stat_line(cf, ["present", "partial", "missing", "not-applicable"])}</span><span>忠實度：{" · ".join(f"{FAITH_ZH.get(k, k)} {v}" for k, v in ff.items() if k)}</span></div>
{table(fb, [("item", "項目"), ("ruling", "裁定"), ("status", "現況"), ("where", "在哪裡"), ("quote", "手冊原句"), ("faithful", "與原文對照"), ("note", "備註")]) if fb else "<p>（粉專稽核尚未完成）</p>"}
</main>
"""
    open(OUT, "w", encoding="utf-8").write(page)
    print(f"寫出 {OUT}；補充素材 {len(supp)} 列 {dict(cs)}；粉專 {len(fb)} 列 {dict(cf)} 忠實度 {dict(ff)}")


if __name__ == "__main__":
    main()
