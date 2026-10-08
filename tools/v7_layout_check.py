#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""版面哨兵（v7 批 AY）：用 headless Chrome 在 375 與 1024 實量指南的版式。

為什麼要有這一支：`tools/v7_check.py` 只看內容（主線字數、數字保全、planstep、錨點），
CSS 改動在這之前是裸奔的。這一支量的是版式稽核（`wip/v63-review/layout-audit-visual.md`）
點名的五件事：

  (a) 每張 figure.chart 的左右緣和所在 section.part 的 padding box 對不對齊（手機出血）
  (b) 每張表在手機上要不要橫向捲（.table-wrap 的 is-scrollable）
  (c) section.part 底下 p 的左緣有幾種（容器內距不一致的量化指標）
  (d) 換行的 summary，續行有沒有比首行往左突出（外置 marker 造成的鋸齒）
  (e) 整份文件有沒有橫向溢出
  (f) 第 28 節製作說明那句「全書 N 張表…N 張圖也在手機寬和電腦寬各量一次」對不對得上
      這一支自己量到的 .table-wrap 與 figure.chart 張數（批 BS 加。批 BJ 新增一張圖以後
      那句話從 29 變成 30，沒有任何哨兵抓得到，是裁判用眼睛看出來的）

macOS 的 Chrome 視窗最小寬是 500px，直接 `--window-size=375` 量到的是 500，
所以照版式審的做法：用一個 file:// 的外框頁把指南放進 width=375 的 iframe 裡量
（需要 `--allow-file-access-from-files` 才能跨 file:// 讀 iframe 的 DOM）。

量測前會把所有 <details> 打開（否則摺疊裡的表與圖沒有幾何），再觸發一次 resize
讓指南自己的 JS 重算 .table-wrap 的 is-scrollable／no-scroll。

用法：
    python3 tools/v7_layout_check.py [guide/index.html] [--json] [--chrome PATH]
綠燈印一行 LAYOUT OK；紅燈逐條列出違規，exit 1。
沒給 --chrome 時用 build_lite.find_chrome() 找；找不到（雲端容器）印 LAYOUT SKIPPED（沒有 Chrome），exit 0。
"""
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_lite import find_chrome  # CHROME_BIN → Mac 路徑 → PATH；找不到回 None

# 門檻。(c) 的目標是 ≤8（版式審 3-A「容器收成四種」做完才到得了）；
# 用「不准比現況更糟」的棘輪：批 BE 把 ol.qa 的縮排收成和其他清單一樣的 40px 以後，
# 375 實測 7 種（已到 ≤8 的目標）、1024 實測 9 種，棘輪就收到這兩個數字。
LIMITS = {
    375: {"p_left_kinds": 7, "scrollable_tables": 1, "summary_outdent": 0, "figure_misaligned": 0},
    1024: {"p_left_kinds": 9, "scrollable_tables": 0, "summary_outdent": 0, "figure_misaligned": 0},
}
P_LEFT_KINDS_GOAL = 8

# (f) 第 28 節製作說明的自我宣告。三個數字依序是：全書表數、哨兵逐張量過的表數、圖數。
# 句子改寫時這支會找不到而判紅——那是刻意的，改了句子就要回來對一次。
# 兩件已知的界線（批 BT 記，裁判 judge-br-bs 次要-3）：
#   (a) 整句字面比對，連「全書 51」→「全書共 51」、全形（375 像素）→ 半形、句中插一個
#       <a class="xref">、「；」改「，」都會變成「找不到」而判紅，不是判黃。那句話在第 28 節
#       製作說明的散文裡，未來的語氣批很容易碰到。
#   (b) 只查傳進來的那一個檔。output/guide.html 與 output/full-v60-out.html 裡同一句不在
#       這支的範圍內（它們由 build_lite.py 從 guide/index.html 產生，來源同一份）。
CLAIM_RE = re.compile(
    r'全書 (\d+) 張表，其中 (\d+) 張由版面哨兵在手機寬度（375 像素）逐張量過，'
    r'另一張隨它所在的圖一起量；(\d+) 張圖也在手機寬和電腦寬各量一次')
# 批 CE：宣告句的殘跡。CLAIM_RE 對不上、但書上還有這些字，就是句子被改寫了（判紅）；兩個都沒有，才是整句已刪。
CLAIM_TRACE_RE = re.compile(r'全書\s*\d+\s*張表|版面哨兵')

MEASURE_JS = r"""
function measure(){
  var w = document.getElementById('f').contentWindow;
  var d = w.document;
  var res = {innerWidth: w.innerWidth, figures: [], tables: [], pLefts: {},
             summaryOutdent: [], summaryLines: 0, docOverflow: 0, overflowers: []};

  function partOf(el){ var p = el.closest('section.part'); return p; }
  // padding box＝扣掉框線、含內距的那個盒子。L104 的註解說圖要出血到這裡。
  function padBox(el){
    var r = el.getBoundingClientRect(), cs = w.getComputedStyle(el);
    return {left: r.left + parseFloat(cs.borderLeftWidth),
            right: r.right - parseFloat(cs.borderRightWidth)};
  }
  // (a) 圖
  Array.prototype.forEach.call(d.querySelectorAll('figure.chart'), function(f, i){
    var part = partOf(f); if(!part) return;
    var pb = padBox(part), r = f.getBoundingClientRect();
    res.figures.push({i: i, id: part.id, cls: f.className,
                      left: +(r.left - pb.left).toFixed(1), right: +(pb.right - r.right).toFixed(1),
                      w: +r.width.toFixed(1)});
  });
  // (b) 表
  Array.prototype.forEach.call(d.querySelectorAll('.table-wrap'), function(tw, i){
    var tb = tw.querySelector('table');
    var need = tb ? tb.offsetWidth : tw.scrollWidth;
    var part = partOf(tw);
    res.tables.push({i: i, id: part ? part.id : '', cls: (tb ? tb.className : ''),
                     over: +(need - tw.clientWidth).toFixed(1),
                     scrollable: tw.classList.contains('is-scrollable'),
                     appx: !!tw.closest('#worksheet'),
                     hint: w.getComputedStyle(tw, '::before').content});
  });
  // (c) 正文左緣
  Array.prototype.forEach.call(d.querySelectorAll('section.part p'), function(p){
    var r = p.getBoundingClientRect();
    if(r.width === 0 && r.height === 0) return;
    var k = Math.round(r.left);
    res.pLefts[k] = (res.pLefts[k] || 0) + 1;
  });
  // (d) summary 續行左突
  Array.prototype.forEach.call(d.querySelectorAll('summary'), function(s, i){
    var rg = d.createRange(); rg.selectNodeContents(s);
    var rects = rg.getClientRects(); if(!rects.length) return;
    var lines = [];
    for(var j = 0; j < rects.length; j++){
      var rc = rects[j]; if(rc.width === 0 && rc.height === 0) continue;
      var hit = null;
      for(var k = 0; k < lines.length; k++){ if(Math.abs(lines[k].top - rc.top) < 4){ hit = lines[k]; break; } }
      if(hit){ hit.left = Math.min(hit.left, rc.left); }
      else { lines.push({top: rc.top, left: rc.left}); }
    }
    if(lines.length < 2) return;
    res.summaryLines++;
    var first = lines[0].left, worst = 0;
    for(var k = 1; k < lines.length; k++){ worst = Math.max(worst, first - lines[k].left); }
    if(worst > 0.5){
      var det = s.parentElement;
      res.summaryOutdent.push({cls: det ? det.className : '', out: +worst.toFixed(1),
                               text: (s.textContent || '').slice(0, 30)});
    }
  });
  return res;
}
// 橫向溢出要量讀者看到的那個狀態（摺疊預設收合），所以在打開摺疊之前先量。
function overflow(){
  var w = document.getElementById('f').contentWindow, d = w.document;
  var out = {docOverflow: Math.max(0, d.documentElement.scrollWidth - w.innerWidth), overflowers: []};
  if(out.docOverflow > 1){
    Array.prototype.forEach.call(d.querySelectorAll('body *'), function(el){
      var r = el.getBoundingClientRect();
      if(r.width === 0 && r.height === 0) return;
      if(r.right > w.innerWidth + 1){
        var par = el.parentElement;
        var pr = par ? par.getBoundingClientRect() : null;
        if(pr && pr.right > w.innerWidth + 1) return;  // 只報最外層那一個
        out.overflowers.push({tag: el.tagName.toLowerCase(),
                              cls: typeof el.className === 'string' ? el.className : '',
                              id: el.id, right: +r.right.toFixed(1), w: +r.width.toFixed(1)});
      }
    });
  }
  return out;
}
function go(){
  var w = document.getElementById('f').contentWindow, d = w.document;
  var ov = overflow();
  // 摺疊裡的圖與表收合時沒有幾何，所以量它們之前要全部打開，再觸發一次 resize
  // 讓指南自己的 JS 重算 .table-wrap 的 is-scrollable／no-scroll。
  Array.prototype.forEach.call(d.querySelectorAll('details'), function(x){ x.open = true; });
  w.dispatchEvent(new w.Event('resize'));
  setTimeout(function(){
    var out;
    try { var m = measure(); m.docOverflow = ov.docOverflow; m.overflowers = ov.overflowers;
          out = JSON.stringify(m); }
    catch(e){ out = JSON.stringify({error: String(e)}); }
    document.getElementById('out').textContent = out;
  }, 400);
}
document.getElementById('f').addEventListener('load', function(){ setTimeout(go, 300); });
"""

WRAPPER = """<!doctype html><meta charset="utf-8">
<style>html,body{margin:0;padding:0}iframe{border:0;display:block}#out{white-space:pre-wrap}</style>
<iframe id="f" src="%(src)s" width="%(w)d" height="%(h)d"></iframe>
<pre id="out">PENDING</pre>
<script>%(js)s</script>
"""


def run_width(chrome, guide_abspath, width, height=1200, budget=25000):
    with tempfile.TemporaryDirectory() as td:
        wrapper = os.path.join(td, "wrap.html")
        with open(wrapper, "w", encoding="utf-8") as fh:
            fh.write(WRAPPER % {"src": "file://" + guide_abspath, "w": width,
                                "h": height, "js": MEASURE_JS})
        # 不要加 --user-data-dir：這台機器上 headless 會卡住不出東西
        # （build_lite.py:839 有同一條註解，2026-09-16 實測）。
        cmd = [chrome, "--headless=new", "--disable-gpu",
               "--allow-file-access-from-files", "--hide-scrollbars",
               "--window-size=%d,%d" % (max(width + 40, 900), height),
               "--virtual-time-budget=%d" % budget,
               "--dump-dom", "file://" + wrapper]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        dom = p.stdout
    m = re.search(r'<pre id="out">(.*?)</pre>', dom, flags=re.S)
    if not m:
        raise SystemExit("量不到：Chrome 沒有吐出 #out（stderr 前 500 字）\n" + p.stderr[:500])
    raw = m.group(1).strip()
    if raw == "PENDING" or not raw:
        raise SystemExit("量不到：iframe 還沒量完就被 dump（試著把 --virtual-time-budget 調大）")
    raw = raw.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    return json.loads(raw)


def check(width, res, problems, lines):
    lim = LIMITS[width]
    if res.get("error"):
        problems.append("%dpx 量測失敗：%s" % (width, res["error"]))
        return
    if res["innerWidth"] != width:
        problems.append("%dpx：iframe 實際 innerWidth=%s，量到的不是目標寬度" % (width, res["innerWidth"]))

    # (a)
    if width <= 660:
        bad = [f for f in res["figures"] if abs(f["left"]) > 1.5 or abs(f["right"]) > 1.5]
        note = "圖應出血到 section.part 的 padding box（左右各 0）"
    else:
        bad = [f for f in res["figures"] if f["left"] < -1.5 or f["right"] < -1.5]
        note = "圖不得超出 section.part 的 padding box"
    lines.append("%dpx  figure.chart %d 張，左右緣不對的 %d 張（%s）" % (width, len(res["figures"]), len(bad), note))
    for f in bad[:20]:
        lines.append("        #%s %s  左差 %s  右差 %s" % (f["id"], f["cls"], f["left"], f["right"]))
    if len(bad) > lim["figure_misaligned"]:
        problems.append("%dpx：%d 張 figure.chart 左右緣不對（上限 %d）" % (width, len(bad), lim["figure_misaligned"]))

    # (b)
    scroll = [t for t in res["tables"] if t["over"] > 2]
    hinted = [t for t in res["tables"] if t["scrollable"]]
    nohint = [t for t in scroll if "滑動" not in (t["hint"] or "")]
    ghost = [t for t in hinted if t["over"] <= 2]
    lines.append("%dpx  .table-wrap %d 個，需要橫向捲的 %d 個，顯示提示字的 %d 個"
                 % (width, len(res["tables"]), len(scroll), len([t for t in res["tables"] if "滑動" in (t["hint"] or "")])))
    for t in scroll[:20]:
        lines.append("        #%s table.%s 超出 %spx  提示=%s" % (t["id"], t["cls"], t["over"], t["hint"]))
    # 批 CX（主線拍板）：書末附錄（#worksheet）是可列印工作表，表格照紙本排，手機上要橫捲是預期的；
    # 它們不算進「需要橫向捲」的上限，但一樣要有提示字（下面的 nohint 照樣查附錄的表），整份文件橫向溢出也照樣要是 0。
    scroll_main = [t for t in scroll if not t.get("appx")]
    if len(scroll) != len(scroll_main):
        lines.append("%dpx  其中書末附錄（#worksheet）的表 %d 個，不計入上限、只查提示字" % (width, len(scroll) - len(scroll_main)))
    if len(scroll_main) > lim["scrollable_tables"]:
        problems.append("%dpx：%d 張表需要橫向捲（上限 %d）" % (width, len(scroll_main), lim["scrollable_tables"]))
    if nohint:
        problems.append("%dpx：%d 張表要橫捲卻沒有提示字（%s）"
                        % (width, len(nohint), "、".join("#" + t["id"] for t in nohint[:5])))
    if ghost:
        problems.append("%dpx：%d 張表不用捲卻被標成 is-scrollable" % (width, len(ghost)))

    # (c)
    kinds = sorted(int(k) for k in res["pLefts"])
    lines.append("%dpx  section.part 底下 p 的左緣 %d 種：%s（目標 ≤%d）"
                 % (width, len(kinds), " ".join("%s(%d)" % (k, res["pLefts"][str(k)]) for k in kinds), P_LEFT_KINDS_GOAL))
    if len(kinds) > lim["p_left_kinds"]:
        problems.append("%dpx：正文左緣 %d 種，比棘輪 %d 還多" % (width, len(kinds), lim["p_left_kinds"]))

    # (d)
    lines.append("%dpx  換行的 summary %d 個，續行往左突出的 %d 個"
                 % (width, res["summaryLines"], len(res["summaryOutdent"])))
    for s in res["summaryOutdent"][:10]:
        lines.append("        details.%s 突出 %spx：%s…" % (s["cls"], s["out"], s["text"]))
    if len(res["summaryOutdent"]) > lim["summary_outdent"]:
        problems.append("%dpx：%d 個 summary 續行左突（上限 %d）"
                        % (width, len(res["summaryOutdent"]), lim["summary_outdent"]))

    # (e)
    lines.append("%dpx  文件橫向溢出 %spx" % (width, res["docOverflow"]))
    for o in (res.get("overflowers") or [])[:10]:
        lines.append("        %s.%s#%s 右緣 %s 寬 %s" % (o["tag"], o["cls"], o["id"], o["right"], o["w"]))
    if res["docOverflow"] > 1:
        problems.append("%dpx：文件橫向溢出 %spx" % (width, res["docOverflow"]))


def check_claims(guide, raw, problems, lines):
    """(f) 書上寫的張數 vs 這一支量到的張數。"""
    with open(guide, encoding="utf-8") as f:
        src = f.read()
    m = CLAIM_RE.search(src)
    if not m and not CLAIM_TRACE_RE.search(src):
        # 批 CE（外部複審 C4，作者 2026-09-26 拍板）把第 28 節「想深入：這本書做過哪些檢查」整個摺疊刪了，
        # 張數宣告句跟著不在書上：書上沒有宣告，就沒有東西要對。只要書上還留著任何一點宣告的痕跡
        # （「全書 N 張表」或「版面哨兵」），仍照下面判紅——句子改寫過就要回來對一次的規則不變。
        lines.append("宣告  書上已經沒有「全書 N 張表…N 張圖…」宣告句（批 CE 刪了第 28 節那個摺疊），不比對")
        return
    if not m:
        lines.append("宣告  找不到第 28 節製作說明那句「全書 N 張表…N 張圖…」")
        problems.append("找不到第 28 節製作說明的張數宣告句（句子改寫過就要回來對一次，"
                        "樣板在 tools/v7_layout_check.py 的 CLAIM_RE）")
        return
    tables_all, tables_measured, figs = (int(x) for x in m.groups())
    got_tables = sorted({len(raw[w]["tables"]) for w in raw if not raw[w].get("error")})
    got_figs = sorted({len(raw[w]["figures"]) for w in raw if not raw[w].get("error")})
    lines.append("宣告  書上寫「全書 %d 張表，其中 %d 張由版面哨兵逐張量過；%d 張圖」；"
                 "實量 .table-wrap %s 個、figure.chart %s 張"
                 % (tables_all, tables_measured, figs,
                    "／".join(str(n) for n in got_tables),
                    "／".join(str(n) for n in got_figs)))
    if len(got_tables) != 1 or got_tables[0] != tables_measured:
        problems.append("書上寫版面哨兵量過 %d 張表，實量 .table-wrap %s 個"
                        % (tables_measured, "／".join(str(n) for n in got_tables)))
    if len(got_figs) != 1 or got_figs[0] != figs:
        problems.append("書上寫 %d 張圖，實量 figure.chart %s 張"
                        % (figs, "／".join(str(n) for n in got_figs)))
    if tables_all != tables_measured + 1:
        problems.append("書上寫全書 %d 張表、哨兵量過 %d 張，兩者差的不是句子裡說的那 1 張"
                        % (tables_all, tables_measured))


def main(argv):
    chrome = None
    as_json = False
    args = []
    i = 0
    while i < len(argv):
        if argv[i] == "--chrome":
            chrome = argv[i + 1]; i += 2; continue
        if argv[i] == "--json":
            as_json = True; i += 1; continue
        args.append(argv[i]); i += 1
    guide = args[0] if args else "guide/index.html"
    guide = os.path.abspath(guide)
    if not os.path.exists(guide):
        raise SystemExit("找不到 " + guide)
    if chrome is None:
        chrome = find_chrome()
        if chrome is None:
            print("LAYOUT SKIPPED（沒有 Chrome）")
            return 0
    if not os.path.exists(chrome):
        raise SystemExit("找不到 Chrome：%s（用 --chrome 指定）" % chrome)

    problems, lines, raw = [], [], {}
    for width in (375, 1024):
        res = run_width(chrome, guide, width)
        raw[width] = res
        check(width, res, problems, lines)
    check_claims(guide, raw, problems, lines)

    if as_json:
        print(json.dumps(raw, ensure_ascii=False, indent=1))
        return 0
    print("\n".join(lines))
    if problems:
        for p in problems:
            print("FAIL [layout] " + p)
        return 1
    print("LAYOUT OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
