#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""要不要自提試算工具（tools/laotui/laotui-tool.html，第七版）的檢查。

    python3 tools/laotui/check_tool.py          通過 exit 0；有問題 exit 1；沒有 Chrome 印 SKIP、exit 0

做六件事：
  0. 原始檔逐字比規格：最上層那一行、「補繳的稅差多少」整個 details（a、b 兩段、#band、#flipnote、e 小字，
     順序與標籤都要一樣）、「回到書」那一行；字串寫在本檔 SPEC_* 常數。
  1. headless Chrome --dump-dom 載入工具，從表格（#tbl）抓 5 級距 × 35 年的百分比（一位小數）、
     從熱圖（#heat 的桌機版）翻盤年欄抓五個翻盤年，和 tools/v7_g13_laotui.py 比：
     35 年逐格比 vdef()（compute() 用的同一個式子），5、10、…、35 年那七欄另外比 compute()['grid']，
     翻盤年比 compute()['flip']；允許 0.05 個百分點（表格只印一位小數）。
     M 系列六個 span（M、Mside、Mrl、Mgi、Mk、Mn）比 calc.py 掃六組的最大值（calc.py main() 的 six_combos_max 同一個算法）。
  2. 版面結構：#band 內兩個 svg、每個 svg 4 條 polygon.band；#flipnote 非空；
     最上層（三個 <details> 以外）不再出現「參數：」「20% 級距、自提 15 年」；「怎麼算」內有「參數：」；
     「回到書」那行在最上層（details 外），href、target="_blank"、rel="noopener" 都對；全頁不再出現「20% 級距、自提 15 年」與 data-g="Za"／"Zb"；每個 data-g 的 span 都有字、不是 undefined／NaN。
  3. 用 iframe 包起來在 1024 與 375 寬量：六種報酬組合逐一點按鈕，
     X、Y、b12 與 #flipnote 要等於 tools/laotui/calc.py 算的值（跟著目前設定變）；
     帶狀圖右端四個級距標籤（text.el）兩兩不重疊；兩行註解（text.bn）的字框不和任何 polygon.band 相交
     （每 2px 取樣，用 polygon 在該 x 的上下緣內插，粗略）；四條帶的 polygon 每條 70 點逐點反推回百分點，
     和 calc.py 的 a、b 比（容差 0.05 個百分點），x 也要對上 X(n)；「0＝熱圖上的數字」不壓零線（在零線上方，或零線從字尾之後才開始），
     且字框左邊、字框高度內沒有零線或帶子邊線的線頭（看起來像「−0」）；帶狀圖裡所有字都在 svg 的寬度內；375 寬整頁不橫向溢出。
  4. （同 3，375 寬用手機版 svg 再做一次。）
  5. 截圖到 wip/v63-review/：laotui-tool7-1024.png、laotui-tool7-375.png、
     laotui-tool7-band-1024.png（?open=band，「補繳的稅差多少」展開）、
     laotui-tool7-band-375.png、laotui-tool7-band-1024-dark.png（--force-dark-mode）。截圖要人看，這支不判讀圖。
"""
import importlib.util
import itertools
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
TOOL = os.path.join(HERE, 'laotui-tool.html')
SHOTS = os.path.join(ROOT, 'wip', 'v63-review')
sys.path.insert(0, TOOLS)

from build_lite import find_chrome  # noqa: E402
import v7_g13_laotui as G13  # noqa: E402

_spec = importlib.util.spec_from_file_location('laotui_calc', os.path.join(HERE, 'calc.py'))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

TOL = 0.05          # 百分點

# 規格字串（2026-10-11 主線派工單，逐字）
SPEC_TOP = '<p>圖上已經把 60 歲一次領要補的稅算進去；誰要補、會差多少，見下面「補繳的稅差多少」。</p>'
SPEC_A = ('要補繳的只有同時符合這幾點的人：60 歲一次領、年資長、月薪到上限所以雇主也提到頂、帳戶總額超過免稅額。'
          '年資 35 年時，一次領 <span data-g="ex1"></span> 萬以內免稅，<span data-g="ex1"></span> 萬到 <span data-g="ex2"></span> 萬之間一半計入所得，'
          '超過的全數計入（115 年度數字）。年資滿 15 年改按月領，每年 89.4 萬以內免稅，多數人零稅。')
SPEC_B = ('圖上已經把補繳算進去，而且假設免稅額和級距每年隨物價調 1.5%。下面這張圖是：熱圖每一格的數字，往上最多再加多少（完全不用補的人），'
          '往下最多再減多少（免稅額和級距一直不調）。5% 級距是零；12% 級距最多差 <span data-g="b12"></span> 個百分點；'
          '20% 以上的人，不用補最多再加 <span data-g="X"></span> 個百分點，免稅額和級距若都不調，存越久差越多，最多再減 <span data-g="Y"></span> 個百分點。')
SPEC_E = ('以上百分點是目前設定的數字；六種報酬組合裡差最多的是 <span data-g="M"></span> 個百分點（<span data-g="Mside"></span>，'
          '勞退 <span data-g="Mrl"></span>、自己投 <span data-g="Mgi"></span>，<span data-g="Mk"></span>% 級距、自提 <span data-g="Mn"></span> 年）。')
SPEC_GAPD = ('<details class="tv pad" id="gapd"><summary>補繳的稅差多少</summary>\n<p>' + SPEC_A + '</p>\n<p>' + SPEC_B + '</p>\n'
             '<div class="box" id="band"></div>\n<p id="flipnote"></p>\n<p class="small">' + SPEC_E + '</p>\n</details>')
BACK_HREF = 'https://claude.ai/artifact/9WawELoGewi9ecKK32YcfU#pension'
SPEC_BACK = ('<p class="small pad" id="backlink">這是《隔離人性》第 24 節的附屬工具；回到書：<a href="' + BACK_HREF +
             '" target="_blank" rel="noopener">第 24 節「勞保和勞退先算」</a>。</p>')
# 帶狀圖幾何（和 bandSVG 同一組數）
BAND_GEOM = {'d': dict(l=46, r=70, t=14, b=40, W=640, H=300), 'm': dict(l=40, r=50, t=14, b=40, W=360, H=280)}
PMIN, PMAX = -30, 10


def check_source(problems, lines):
    src = open(TOOL, encoding='utf-8').read()
    for name, spec in (('最上層那一行', SPEC_TOP), ('「補繳的稅差多少」details', SPEC_GAPD), ('回到書那一行', SPEC_BACK)):
        n = src.count(spec)
        lines.append('原始檔逐字比規格：%s 出現 %d 次' % (name, n))
        if n != 1:
            problems.append('原始檔裡「%s」和規格逐字對不上（出現 %d 次，應 1 次）' % (name, n))
    i_top, i_gapd, i_how = src.find(SPEC_TOP), src.find(SPEC_GAPD), src.find('<summary>怎麼算</summary>')
    if not (0 <= i_top < i_gapd < i_how):
        problems.append('順序不對：最上層那一行 → 補繳的稅差多少 → 怎麼算')
    i_yby, i_back, i_fig = src.find('<details class="tv" id="yby">'), src.find(SPEC_BACK), src.find('</figure>')
    if not (0 <= i_yby < i_back < i_fig) or src.find('</details>', i_yby) > i_back:
        problems.append('「回到書」應在逐年細看 details 之後、</figure> 之前')


def expect_m():
    """calc.py main() 的 six_combos_max：六組 gaps() 的兩種差裡最大的那個。"""
    allg = []
    for rl, gi in itertools.product(C.RLS, C.GS):
        n_, f_, _ = C.gaps(rl, gi)
        if n_[1]:
            allg.append((n_[0], '不用補', rl, gi) + n_[1])
        if f_[1]:
            allg.append((f_[0], '免稅額和級距不調', rl, gi) + f_[1])
    M = max(allg)
    RN = {0.017: '1.7%', 0.021: '2.1%', 0.0465: '4.65%'}
    GN = {0.06: '6%', 0.075: '7.5%'}
    return {'M': '%.1f' % (M[0] * 100), 'Mside': '完全不用補' if M[1] == '不用補' else M[1],
            'Mrl': RN[M[2]], 'Mgi': GN[M[3]], 'Mk': str(M[4]), 'Mn': str(M[5])}
MINUS = '−'
COMBOS = [(rl, gi) for rl, gi in itertools.product(['0.017', '0.021', '0.0465'], ['0.06', '0.075'])]


def chrome_run(chrome, args, timeout=180):
    # 不加 --user-data-dir：這台機器上 headless 會卡住（build_lite.py 同一條註解）
    cmd = [chrome, '--headless=new', '--disable-gpu', '--allow-file-access-from-files', '--hide-scrollbars'] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def unesc(s):
    return s.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&amp;', '&')


def strip_tags(s):
    return unesc(re.sub(r'<[^>]+>', '', s))


def parse_pct(s):
    s = s.strip().rstrip('%').replace(MINUS, '-').replace('+', '')
    return float(s)


# ---------------------------------------------------------------------------
# 1＋2：dump-dom
def check_dom(chrome, problems, lines):
    p = chrome_run(chrome, ['--virtual-time-budget=5000', '--dump-dom', 'file://' + TOOL])
    dom = p.stdout
    if '<main>' not in dom:
        problems.append('dump-dom 沒有內容（stderr 前 300 字：%s）' % p.stderr[:300])
        return
    # 表格
    m = re.search(r'id="tbl"><table>.*?<tbody>(.*?)</tbody>', dom, flags=re.S)
    if not m:
        problems.append('找不到 #tbl 的表格')
        return
    rows = re.findall(r'<tr><th scope="row">(\d+)</th>(.*?)</tr>', m.group(1), flags=re.S)
    if len(rows) != 35:
        problems.append('#tbl 應有 35 列，抓到 %d 列' % len(rows))
    res = G13.compute()
    worst, nbad = 0.0, 0
    for n_s, tds in rows:
        n = int(n_s)
        vals = [parse_pct(x) for x in re.findall(r'<td>(.*?)</td>', tds)]
        if len(vals) != len(G13.KS):
            problems.append('#tbl 第 %d 列應有 %d 格，抓到 %d' % (n, len(G13.KS), len(vals)))
            continue
        for k, shown in zip(G13.KS, vals):
            exp = G13.vdef(k, n) * 100
            d = abs(shown - exp)
            worst = max(worst, d)
            if d > TOL + 1e-9:
                nbad += 1
                problems.append('表格 級距 %d%% 第 %d 年：頁面 %.1f，v7_g13 %.4f' % (k, n, shown, exp))
            if n in G13.COLS:
                g = res['grid'][str(k)][G13.COLS.index(n)] * 100
                if abs(shown - g) > TOL + 1e-9:
                    problems.append('表格 級距 %d%% 第 %d 年：頁面 %.1f，compute() grid %.4f' % (k, n, shown, g))
    lines.append('表格 %d×%d 格對 v7_g13：最大差 %.4f 個百分點，超過 %.2f 的 %d 格' % (len(rows), len(G13.KS), worst, TOL, nbad))
    # 翻盤年（桌機版熱圖）
    heat = re.search(r'id="heat">(.*?)</svg>', dom, flags=re.S)
    fl = re.findall(r'<text class="fl"[^>]*>(.*?)</text>', heat.group(1)) if heat else []
    got = [None if x.strip() == '—' else int(x.replace('年', '')) for x in fl]
    exp = [res['flip'][str(k)] for k in G13.KS]
    lines.append('翻盤年 頁面 %s；compute() %s' % (got, exp))
    if got != exp:
        problems.append('翻盤年不同：頁面 %r，compute() %r' % (got, exp))
    # 帶狀圖
    band = re.search(r'id="band">(.*?)</div>', dom, flags=re.S)
    svgs = re.findall(r'<svg\b.*?</svg>', band.group(1), flags=re.S) if band else []
    npoly = [len(re.findall(r'<polygon class="band\b', s)) for s in svgs]
    lines.append('#band：svg %d 個，每個 polygon.band %s 條' % (len(svgs), npoly))
    if len(svgs) != 2 or npoly != [4, 4]:
        problems.append('#band 應有 2 個 svg、各 4 條帶：%d 個 svg，%r' % (len(svgs), npoly))
    fn = re.search(r'<p id="flipnote">(.*?)</p>', dom, flags=re.S)
    fnt = strip_tags(fn.group(1)).strip() if fn else ''
    lines.append('#flipnote：%s' % (fnt or '（空）'))
    if not fnt:
        problems.append('#flipnote 是空的')
    # 最上層 vs 收合
    main = re.search(r'<main>(.*?)</main>', dom, flags=re.S).group(1)
    details = re.findall(r'<details\b.*?</details>', main, flags=re.S)
    top = strip_tags(re.sub(r'<details\b.*?</details>', '', main, flags=re.S))
    for bad in ('參數：', '20% 級距、自提 15 年'):
        if bad in top:
            problems.append('最上層（details 外）還有「%s」' % bad)
    howto = [d for d in details if re.search(r'<summary[^>]*>怎麼算</summary>', d)]
    if not howto or '參數：' not in strip_tags(howto[0]):
        problems.append('「怎麼算」裡找不到「參數：」')
    if '回到書' not in top:
        problems.append('「回到書」那行不在最上層（收合時看不到）')
    if '20% 級距、自提 15 年' in strip_tags(dom):
        problems.append('全頁還有「20% 級距、自提 15 年」')
    if re.search(r'data-g="Z[ab]"', dom):
        problems.append('還有 data-g="Za"／"Zb"')
    spans = re.findall(r'<span data-g="(\w+)">(.*?)</span>', dom)
    empty = sorted({k for k, v in spans if not v.strip() or v in ('undefined', 'NaN')})
    lines.append('data-g span %d 個，空的或 undefined／NaN：%s' % (len(spans), empty or '無'))
    if empty:
        problems.append('data-g 沒填好：%s' % empty)
    got_m = {k: unesc(v) for k, v in spans if k.startswith('M')}
    exp_m = expect_m()
    lines.append('M 系列 頁面 %s；calc.py six_combos_max %s' % (got_m, exp_m))
    if got_m != exp_m:
        problems.append('M 系列不同：頁面 %r，calc.py %r' % (got_m, exp_m))
    bl = re.search(r'<p class="small pad" id="backlink">(.*?)</p>', dom, flags=re.S)
    a = re.search(r'<a ([^>]*)>', bl.group(1)) if bl else None
    attrs = dict(re.findall(r'(\w+)="([^"]*)"', a.group(1))) if a else {}
    lines.append('回到書：href=%s target=%s rel=%s' % (unesc(attrs.get('href', '')), attrs.get('target'), attrs.get('rel')))
    if unesc(attrs.get('href', '')) != BACK_HREF or attrs.get('target') != '_blank' or attrs.get('rel') != 'noopener':
        problems.append('回到書連結不對：%r' % attrs)
    lines.append('details %d 個：%s' % (len(details), [strip_tags(re.search(r'<summary[^>]*>(.*?)</summary>', d).group(1)) for d in details]))


# ---------------------------------------------------------------------------
# 3：iframe 量測（六組報酬逐一點）
MEASURE_JS = r"""
function go(){var out=document.getElementById('out'),res={};
 try{var w=document.getElementById('f').contentWindow,doc=w.document;res.innerWidth=w.innerWidth;
  var kind=w.innerWidth<=640?'m':'d';res.kind=kind;
  function ph(){return Math.ceil(doc.querySelector('main').getBoundingClientRect().bottom+w.scrollY+60);}
  res.scrollHclosed=ph();
  doc.getElementById('gapd').open=true;res.combos=[];
  var CB=%(combos)s;
  CB.forEach(function(c){doc.querySelector('#ctl button[data-k="rl"][data-v="'+c[0]+'"]').click();doc.querySelector('#ctl button[data-k="gi"][data-v="'+c[1]+'"]').click();
   var svg=doc.querySelector('#band svg.'+kind),vb=svg.viewBox.baseVal;
   var el=[].slice.call(svg.querySelectorAll('text.el')).map(function(t){var b=t.getBBox();return [t.textContent,b.x,b.y,b.width,b.height];});
   var tx=[].slice.call(svg.querySelectorAll('text')).map(function(t){var b=t.getBBox();return [t.textContent,b.x,b.x+b.width];});
   var hitA=[],ann=[];[].slice.call(svg.querySelectorAll('text.bn')).forEach(function(t){var b=t.getBBox();ann.push([t.textContent.slice(0,1),Math.round(b.x),Math.round(b.y)]);
    [].slice.call(svg.querySelectorAll('polygon.band')).forEach(function(pg){var P=pg.getAttribute('points').trim().split(' ').map(function(q){return q.split(',').map(Number);}),N=P.length/2,U=P.slice(0,N),L=P.slice(N).reverse();
     function at(E,x){for(var i=0;i<E.length-1;i++)if(x>=E[i][0]&&x<=E[i+1][0]){var f=(x-E[i][0])/((E[i+1][0]-E[i][0])||1);return E[i][1]+f*(E[i+1][1]-E[i][1]);}return null;}
     for(var x=b.x;x<=b.x+b.width;x+=2){var u=at(U,x),lo=at(L,x);if(u===null||lo===null)continue;if(u<=b.y+b.height&&lo>=b.y){hitA.push([t.textContent.slice(0,1),pg.dataset.k,Math.round(x)]);break;}}});});
   var g={};['X','Y','b12'].forEach(function(k){g[k]=doc.querySelector('[data-g="'+k+'"]').textContent;});
   var poly=[].slice.call(svg.querySelectorAll('polygon.band')).map(function(pg){return [pg.dataset.k,pg.getAttribute('points')];});
   var bz=svg.querySelector('text.bz').getBBox(),zl=svg.querySelector('line.zero'),ex=svg.querySelectorAll('polyline.be');
   /* 零線標籤左邊有沒有線頭：零線或任一條邊線在標籤字框左緣之前、字框高度內有點 */
   var stub=[];[zl].concat([].slice.call(ex)).forEach(function(L){var P=L.tagName==='line'?[[+L.getAttribute('x1'),+L.getAttribute('y1')],[+L.getAttribute('x2'),+L.getAttribute('y2')]]:L.getAttribute('points').trim().split(' ').map(function(q){return q.split(',').map(Number);});
     for(var i=0;i<P.length-1;i++){var x0=P[i][0],x1=P[i+1][0];if(x0>=bz.x)break;for(var x=x0;x<=Math.min(x1,bz.x-0.5);x+=0.5){var f=(x-x0)/((x1-x0)||1),y=P[i][1]+f*(P[i+1][1]-P[i][1]);if(y>=bz.y&&y<=bz.y+bz.height){stub.push([L.getAttribute('class'),Math.round(x)]);return;}}}});
   res.combos.push({rl:c[0],gi:c[1],el:el,tx:tx,hitA:hitA,ann:ann,poly:poly,bzRight:bz.x+bz.width,bzBottom:bz.y+bz.height,zeroY:+zl.getAttribute('y1'),zeroX1:+zl.getAttribute('x1'),stub:stub,W:vb.width,g:g,flipnote:doc.getElementById('flipnote').textContent,
     svgW:svg.getBoundingClientRect().width,svgRight:svg.getBoundingClientRect().right});});
  doc.querySelector('#ctl button[data-k="rl"][data-v="0.0465"]').click();doc.querySelector('#ctl button[data-k="gi"][data-v="0.075"]').click();
  res.scrollW=doc.documentElement.scrollWidth;res.scrollHopen=ph();
 }catch(e){res.error=String(e)+' '+(e.stack||'');}
 out.textContent=JSON.stringify(res);}
document.getElementById('f').addEventListener('load',function(){setTimeout(go,200);});
"""

WRAP = """<!doctype html><meta charset="utf-8">
<style>html,body{margin:0;padding:0}iframe{border:0;display:block}</style>
<iframe id="f" src="%(src)s" width="%(w)d" height="%(h)d"></iframe>
<pre id="out">PENDING</pre>
<script>%(js)s</script>
"""


def measure(chrome, width, td):
    wrap = os.path.join(td, 'm%d.html' % width)
    with open(wrap, 'w', encoding='utf-8') as fh:
        fh.write(WRAP % {'src': 'file://' + TOOL, 'w': width, 'h': 1600,
                         'js': MEASURE_JS % {'combos': json.dumps([list(c) for c in COMBOS])}})
    p = chrome_run(chrome, ['--window-size=%d,1700' % max(width + 40, 900), '--virtual-time-budget=15000',
                            '--dump-dom', 'file://' + wrap])
    m = re.search(r'<pre id="out">(.*?)</pre>', p.stdout, flags=re.S)
    raw = unesc(m.group(1).strip()) if m else ''
    if not raw or raw == 'PENDING':
        raise SystemExit('量不到（%dpx）：%s' % (width, p.stderr[:300]))
    return json.loads(raw)


def expect_band(rl, gi):
    """calc.py 的式子：X、Y＝20% 以上的人 a、b 的最大值；b12＝12% 的 b 最大值；flipnote 照頁面的寫法。"""
    def a(k, n):
        return C.val(k, n, rl=rl, gi=gi, tax='none') - C.val(k, n, rl=rl, gi=gi)

    def b(k, n):
        return C.val(k, n, rl=rl, gi=gi) - C.val(k, n, rl=rl, gi=gi, tax='frozen')

    def pp1(x):
        v = x * 100
        return '%.1f' % (0 if abs(v) < 0.05 else v)
    X = max([0.0] + [a(k, n) for k in (20, 30, 40) for n in range(1, 36)])
    Y = max([0.0] + [b(k, n) for k in (20, 30, 40) for n in range(1, 36)])
    B12 = max([0.0] + [b(12, n) for n in range(1, 36)])
    parts = []
    for k in C.KS:
        ys = []
        for n in (5, 10, 15, 20, 25, 30, 35):
            v = C.val(k, n, rl=rl, gi=gi)
            vn = C.val(k, n, rl=rl, gi=gi, tax='none')
            vf = C.val(k, n, rl=rl, gi=gi, tax='frozen')
            if (v < 0) != (vn < 0) or (v < 0) != (vf < 0):
                ys.append(str(n))
        if ys:
            parts.append('級距 %d%% 第 %s 年' % (k, '、'.join(ys)))
    note = ('目前設定下，會因此從贏變輸或從輸變贏的格子：' + '、'.join(parts) + '。') if parts \
        else '目前設定下，沒有任何一格會因此改變輸贏。'
    return {'X': pp1(X), 'Y': pp1(Y), 'b12': pp1(B12)}, note


EL_FONT = 12        # text.el 的字級；垂直方向用字身（12px）比，不用行框（15px，上下各多出一點空白）


def check_poly(kind, c, rl, gi):
    """polygon 點反推百分點：前 35 點是上緣 a(n)（n=1..35），後 35 點是下緣 −b(n)（n=35..1）。"""
    g = BAND_GEOM[kind]
    pw, ph = g['W'] - g['l'] - g['r'], g['H'] - g['t'] - g['b']
    bad, worst = [], 0.0
    ks = [p[0] for p in c['poly']]
    if ks != ['40', '30', '20', '12']:
        bad.append('帶的順序 %r，應為 40、30、20、12' % ks)
    for k_s, pts in c['poly']:
        k = int(k_s)
        P = [tuple(map(float, q.split(','))) for q in pts.split()]
        if len(P) != 70:
            bad.append('級距 %d%% 有 %d 點' % (k, len(P)))
            continue
        for j, (x, y) in enumerate(P):
            n = j + 1 if j < 35 else 70 - j
            v = C.val(k, n, rl=rl, gi=gi)
            exp = (C.val(k, n, rl=rl, gi=gi, tax='none') - v) * 100 if j < 35 else -(v - C.val(k, n, rl=rl, gi=gi, tax='frozen')) * 100
            got = PMAX - (y - g['t']) / ph * (PMAX - PMIN)
            ex = g['l'] + (n - 1) / 34 * pw
            d = abs(got - exp)
            worst = max(worst, d)
            if d > TOL + 1e-9 or abs(x - ex) > 0.06:
                bad.append('級距 %d%% 第 %d 點（n=%d）：%.3f vs %.3f、x %.1f vs %.2f' % (k, j + 1, n, got, exp, x, ex))
    return worst, bad


def overlap(r1, r2):
    """兩個 [字, x, y, w, h] 的 bbox：水平看 bbox，垂直看行框中間 12px 的字身。
    排開法照折線圖（間距 14），行框 15 會互相壓 1px，但字身之間還有 2px，字不會疊。"""
    def em(r):
        top = r[2] + (r[4] - EL_FONT) / 2
        return top, top + EL_FONT
    a0, a1 = em(r1)
    b0, b1 = em(r2)
    return not (r1[1] + r1[3] <= r2[1] or r2[1] + r2[3] <= r1[1] or a1 <= b0 + 1e-6 or b1 <= a0 + 1e-6)


def check_measure(chrome, problems, lines):
    heights = {}
    with tempfile.TemporaryDirectory() as td:
        for width in (1024, 375):
            r = measure(chrome, width, td)
            if r.get('error'):
                problems.append('%dpx 量測出錯：%s' % (width, r['error']))
                continue
            heights[width] = (r['scrollHclosed'], r['scrollHopen'])
            lines.append('%dpx：innerWidth %d，用 %s 版帶狀圖，頁高 %d（收合）／%d（補繳展開），scrollWidth %d'
                         % (width, r['innerWidth'], r['kind'], r['scrollHclosed'], r['scrollHopen'], r['scrollW']))
            if r['innerWidth'] != width:
                problems.append('%dpx：iframe innerWidth=%d' % (width, r['innerWidth']))
            if r['scrollW'] > width:
                problems.append('%dpx：整頁橫向溢出（scrollWidth %d）' % (width, r['scrollW']))
            for c in r['combos']:
                exp_g, exp_note = expect_band(float(c['rl']), float(c['gi']))
                tag = '%dpx 勞退 %s／自己投 %s' % (width, c['rl'], c['gi'])
                if c['g'] != exp_g:
                    problems.append('%s：X／Y／b12 頁面 %r，calc.py %r' % (tag, c['g'], exp_g))
                if c['flipnote'] != exp_note:
                    problems.append('%s：flipnote 頁面「%s」，calc.py「%s」' % (tag, c['flipnote'], exp_note))
                el = c['el']
                ov = [(p[0], q[0]) for i, p in enumerate(el) for q in el[i + 1:] if overlap(p, q)]
                if len(el) != 4 or ov:
                    problems.append('%s：右端標籤 %d 個，重疊 %r' % (tag, len(el), ov))
                worst, bad = check_poly(r['kind'], c, float(c['rl']), float(c['gi']))
                c['polyWorst'] = worst
                if bad:
                    problems.append('%s：帶狀圖 polygon 和模型對不上：%s' % (tag, '；'.join(bad[:5])))
                if c['zeroX1'] < c['bzRight'] + 1 and c['bzBottom'] > c['zeroY'] - 1:
                    problems.append('%s：零線標籤壓在零線上（字框底 %.1f、零線 y %.1f、零線起點 %.1f）' % (tag, c['bzBottom'], c['zeroY'], c['zeroX1']))
                if c['stub']:
                    problems.append('%s：零線標籤左邊、字框高度內有線頭 %r' % (tag, c['stub']))
                if len(c['ann']) != 2 or c['hitA']:
                    problems.append('%s：兩行註解 %d 個，和帶子相交 %r（[箭頭, 級距, x]）' % (tag, len(c['ann']), c['hitA']))
                out = [t[0] for t in c['tx'] if t[1] < -0.5 or t[2] > c['W'] + 0.5]
                if out:
                    problems.append('%s：帶狀圖的字超出 svg 寬度：%r' % (tag, out))
                if c['svgRight'] > width + 0.5:
                    problems.append('%s：帶狀圖右緣 %.1f 超出視窗' % (tag, c['svgRight']))
                if width == 1024:
                    lines.append('  %s：X %s、Y %s、b12 %s；標籤 y %s；註解 [箭頭, x, y] %s；%s'
                                 % (tag.split('：')[0][7:], c['g']['X'], c['g']['Y'], c['g']['b12'],
                                    [round(e[2], 1) for e in el], c['ann'], c['flipnote']))
            lines.append('%dpx：六組 X／Y／b12／flipnote 對 calc.py、標籤重疊、字超出 svg、註解與帶子相交、零線標籤與線頭都查過；'
                         'polygon 4×70 點對模型最大差 %.4f 個百分點' % (width, max(c.get('polyWorst', 0) for c in r['combos'])))
    return heights


# ---------------------------------------------------------------------------
# 4：截圖
def shots(chrome, heights, lines, problems):
    os.makedirs(SHOTS, exist_ok=True)
    url = 'file://' + TOOL
    h1024c, h1024o = heights.get(1024, (2400, 3200))
    h375c, h375o = heights.get(375, (3200, 4200))
    with tempfile.TemporaryDirectory() as td:
        def wrap375(name, q):
            pth = os.path.join(td, name)
            with open(pth, 'w', encoding='utf-8') as fh:
                fh.write('<!doctype html><meta charset="utf-8"><style>html,body{margin:0}iframe{border:0;display:block}</style>'
                         '<iframe src="%s%s" width="375" height="%d"></iframe>' % (url, q, h375o + 40))
            return 'file://' + pth
        jobs = [
            ('laotui-tool7-1024.png', 1024, h1024c + 20, url, []),
            ('laotui-tool7-375.png', 375, h375c + 20, wrap375('w1.html', ''), []),
            ('laotui-tool7-band-1024.png', 1024, h1024o + 20, url + '?open=band', []),
            ('laotui-tool7-band-375.png', 375, h375o + 20, wrap375('w2.html', '?open=band'), []),
            ('laotui-tool7-band-1024-dark.png', 1024, h1024o + 20, url + '?open=band', ['--force-dark-mode']),
        ]
        for name, w, h, u, extra in jobs:
            out = os.path.join(SHOTS, name)
            if os.path.exists(out):
                os.remove(out)
            chrome_run(chrome, extra + ['--window-size=%d,%d' % (w, h), '--run-all-compositor-stages-before-draw',
                                        '--virtual-time-budget=5000', '--screenshot=' + out, u])
            if os.path.exists(out):
                lines.append('截圖 %s（%d×%d）' % (os.path.relpath(out, ROOT), w, h))
            else:
                problems.append('截圖失敗：%s' % name)


def main():
    chrome = find_chrome()
    if not chrome:
        print('SKIP：找不到 Chrome（check_tool.py 需要 headless Chrome）')
        return 0
    problems, lines = [], []
    check_source(problems, lines)
    check_dom(chrome, problems, lines)
    heights = check_measure(chrome, problems, lines)
    if '--no-shots' not in sys.argv:
        shots(chrome, heights, lines, problems)
    print('\n'.join(lines))
    if problems:
        print('\nFAIL（%d 項）' % len(problems))
        print('\n'.join('  ' + p for p in problems))
        return 1
    print('\nOK：laotui-tool.html 第七版檢查通過')
    return 0


if __name__ == '__main__':
    sys.exit(main())
