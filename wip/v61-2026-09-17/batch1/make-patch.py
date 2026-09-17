# 第 1 批：換骨架。讀 guide/index.html，產生 guidetools 補丁 patch-batch1.json（不直接寫原文）。
import re, json, html as H
ROOT = '/Users/linyenchu/Cladue Code/family-finance/'
h = open(ROOT + 'guide/index.html', encoding='utf-8').read()

def sec_block(sid):
    m = re.search(r'<section class="part" id="%s">.*?</section>' % re.escape(sid), h, re.S)
    assert m and '<section' not in m.group(0)[10:], sid
    return m.group(0)

def h2_name(sid):
    b = sec_block(sid)
    inner = re.search(r'<h2>(.*?)</h2>', b, re.S).group(1)
    return re.sub(r'<span class="num">.*?</span>', '', inner)

def num(sid):
    m = re.search(r'<h2><span class="num">(\d+)</span>', sec_block(sid))
    return m.group(1) if m else None

def lede(sid):
    return re.search(r'<p class="lede">(.*?)</p>', sec_block(sid), re.S).group(1)

def map_li(sid, extra=''):
    n = num(sid)
    ns = '<span class="map-num">%s</span>' % n if n else ''
    return '<li>%s<a class="xref" href="#%s">%s</a><span class="map-lede">%s</span>%s</li>' % (ns, sid, h2_name(sid), lede(sid), extra)

def group(gid, name, desc, ids, closing, pre='', extras=None):
    extras = extras or {}
    lis = '\n'.join(map_li(i, extras.get(i, '')) for i in ids)
    return ('<section class="part" id="%s"><h2>%s</h2><p class="lede">%s</p>\n%s<ol class="part-map">\n%s\n</ol>\n%s<a class="back" href="#toc">回目錄</a></section>'
            % (gid, name, desc, pre, lis, closing + '\n' if closing else ''))

D = {  # 組名與一行說明：recommended-structure.md 第一節樣張
 'core': ('先搞懂：為什麼這樣做', '十個新手最常問的問題，一節回答一個；計畫表每一格的理由都在這裡。'),
 'plan': ('寫下自己的計畫', '把理由填成一張紙：這筆錢什麼時候用、股票放幾成、跌了怎麼做；再看另外三個人怎麼填。'),
 'sit': ('遇到狀況時翻：怕跌、想賣、有人推銷', '心裡在怕、手癢想動、有人推薦東西的時候，先在這裡找該翻哪一頁。'),
 'howto': ('動手做：開戶、挑商品、第一年', '計畫寫好以後照順序做；做到哪一步，翻哪一節。'),
 'life': ('隨人生調整：每年檢查、年紀變了、快要用錢', '一年檢查一次；年紀、收入、用錢的日子改變時，回來重算。'),
 'ref': ('查資料', '官方網站、延伸閱讀，和全書數字怎麼算出來。'),
 'start': ('開始之前', '先抓重點，確認自己的錢能不能開始；看不懂的詞在這裡查。'),
}

g_core = group('group-core', *D['core'], ['s%d' % i for i in range(1, 11)],
  '<p class="small">可以照順序讀，也可以挑最想問的先讀；要寫計畫的人，至少先讀第 <a class="xref" href="#s5">5</a> 節和第 <a class="xref" href="#s10">10</a> 節。每一節的順序都一樣：先白話版，再數字和來源，最後一句「本節行動」。</p>')
g_plan = group('group-plan', *D['plan'], ['s11', 'cases', 's12'],
  '<p class="small">填 E 區（風險）和 F 區（跌了做什麼）以前，先讀第 <a class="xref" href="#s5">5</a> 節（壓力測試用的跌幅）和第 <a class="xref" href="#s10">10</a> 節（改計畫前的冷卻期）。要印出來手寫，另有《可列印工作表》。</p>')
g_sit = group('group-situations', *D['sit'], ['s13', 'sidepaths'], '',
  pre='<p>動手之前先看一遍也好：先知道自己可能會怕什麼，遇到時比較不慌。</p>\n')
g_howto = group('group-howto', *D['howto'], ['firstmonth', 'steps', 'products', 'costs'],
  '<p class="small">還沒寫計畫表的人，先回第 <a class="xref" href="#s11">11</a> 節。不必從頭讀：做到哪一步，就翻哪一節。</p>')
g_life = group('group-life', *D['life'], ['annual', 'lifecycle', 'withdraw'], '',
  extras={'lifecycle': '<span class="small"><a class="xref" href="#lifecycle-q1">第一題</a>　年齡該不該影響比例／<a class="xref" href="#lifecycle-q2">第二題</a>　年輕時借錢投資／<a class="xref" href="#lifecycle-q3">第三題</a>　退休要存多少</span>'})
g_ref = group('group-ref', *D['ref'], ['toolbox', 'methods'],
  '<p class="small">看不懂的詞，在最前面的「<a class="xref" href="#glossary">先認識這些詞</a>」；正文裡點詞也會跳過去。</p>')

P = []
def patch(section, old, new, why):
    assert h.count(old) == 1, (section, old[:80], h.count(old))
    P.append({'section': section, 'old': old, 'new': new, 'why': why})

# §6.1 group-core 原地改寫
patch('group-core', sec_block('group-core'), g_core, '§6.1 改寫成組地圖')
# §6.2 group-plan 插在 s11 前
patch('group-plan', '<section class="part" id="s11">', g_plan + '\n\n<section class="part" id="s11">', '§6.2 新增分組節')
# §6.3 group-situations 插在 s13 前（第 1 批：不放狀況索引表）
patch('group-situations', '<section class="part" id="s13">', g_sit + '\n\n<section class="part" id="s13">', '§6.3 新增分組節（第 1 批版）')

# §1 搬節＋§6.4／6.5／6.6：group-howto 到 annual 整段重排
order_old = ['group-howto', 'steps', 'firstmonth', 'products', 'costs', 'withdraw', 'lifecycle', 'sidepaths', 'annual']
start = h.index('<section class="part" id="group-howto">')
end = h.index('<section class="part" id="toolbox">')
region = h[start:end]
assert region == '\n\n'.join(sec_block(s) for s in order_old) + '\n\n', 'region 不是九節以空行相接'
side_old = '<li><strong>正 2、反 1：</strong>官方寫「不宜長期持有」；它是單日工具（上一節）。</li>'
side_new = '<li><strong>正 2、反 1：</strong>官方寫「不宜長期持有」；它是單日工具（「<a class="xref" href="#lifecycle-q2">年齡、槓桿與退休</a>」第二題）。</li>'
side = sec_block('sidepaths'); assert side.count(side_old) == 1
side = side.replace(side_old, side_new)
new_region = '\n\n'.join([side, g_howto, sec_block('firstmonth'), sec_block('steps'), sec_block('products'), sec_block('costs'),
                          g_life, sec_block('annual'), sec_block('lifecycle'), sec_block('withdraw'), g_ref]) + '\n\n'
patch('restructure', region, new_region, '§1 搬節（sidepaths 前移、firstmonth↔steps、annual→lifecycle→withdraw）＋§9.1＋§6.4–6.6')

# §5.1 目錄
toc_old = re.search(r'<nav class="toc" id="toc" aria-label="目錄">.*?</nav>', h, re.S).group(0)
def ul(ids): return '<ul>' + ''.join('<li><a href="#%s">%s</a></li>' % (i, h2_name(i)) for i in ids) + '</ul>'
def ol(ids, cls): return '<ol class="%s">' % cls + ''.join('<li><a href="#%s">%s</a></li>' % (i, h2_name(i)) for i in ids) + '</ol>'
def part(name, desc, body, group=None, rng=None, is_open=False):
    return ('<details class="toc-part" data-print="open"%s%s><summary><span class="toc-part-name">%s</span>%s<span class="toc-part-desc">%s</span></summary>\n%s</details>'
            % (' data-group="%s"' % group if group else '', ' open' if is_open else '', name,
               '<span class="toc-part-range">%s</span>' % rng if rng else '', desc, body))
toc_new = ('<nav class="toc" id="toc" aria-label="目錄"><h2>目錄</h2>\n'
  '<p class="small toc-hint">點組名展開；想從頭讀，從「開始之前」往下。</p>\n'
  + '\n'.join([
    part(*D['start'], ul(['ten', 'why', 'start', 'glossary']), is_open=True),
    part(*D['core'], ol(['s%d' % i for i in range(1, 11)], 'toc-from-1'), 'group-core', '第 1–10 節'),
    part(*D['plan'], ol(['s11', 'cases', 's12'], 'toc-from-11'), 'group-plan', '第 11–13 節'),
    part(*D['sit'], ol(['s13'], 'toc-from-14') + ul(['sidepaths']), 'group-situations'),
    part(*D['howto'], ul(['firstmonth', 'steps', 'products', 'costs']), 'group-howto'),
    part(*D['life'], ul(['annual', 'lifecycle', 'withdraw']), 'group-life'),
    part(*D['ref'], ul(['toolbox', 'methods']), 'group-ref'),
  ]) + '\n</nav>\n'
  '<script>\n(function(){if(!window.matchMedia||!window.matchMedia(\'(min-width: 760px)\').matches)return;\n'
  'document.querySelectorAll(\'#toc details.toc-part, details.read-how\').forEach(function(d){d.open=true;});})();\n</script>')
patch('toc', toc_old, toc_new, '§5.1 目錄七組＋§5.3 寬螢幕展開')

# §7.2 閱讀方式框
pm = re.search(r'<div class="promise">(.*?)</div>\n<div class="audit-stamp">', h, re.S)
inner = pm.group(1)
old1 = '只有十分鐘的人，先讀「<a class="xref" href="#ten">十分鐘看完</a>」；多一點時間，再讀「開始前」的其他三節（一眼看懂、投資前的安全順序、先認識這些詞）加第 <a class="xref" href="#s11">11</a>、<a class="xref" href="#s12">13</a> 節，大約四十分鐘。'
new1 = '只有十分鐘的人，先讀「<a class="xref" href="#ten">十分鐘看完</a>」和「<a class="xref" href="#start">投資前的安全順序</a>」；多一點時間，再讀「<a class="xref" href="#why">一眼看懂</a>」、第 <a class="xref" href="#s11">11</a> 節的計畫表（白話版、兩把尺、壓力測試、三問）、第 <a class="xref" href="#s12">13</a> 節的四個原則和七個問題，最後看「<a class="xref" href="#firstmonth">從第一週到第一年</a>」，大約四十分鐘，讀完就知道這個星期做什麼。'
old2 = '心裡正在怕某一件事的時候，直接翻第 <a class="xref" href="#s13">14</a> 節；要開戶、下單、對帳、每年檢查的時候，翻後面的實作附錄（從第一週到第一年的時間表也在那裡）。'
new2 = '心裡正在怕某一件事的時候，翻「<a class="xref" href="#group-situations">遇到狀況時翻</a>」；要開戶、下單、對帳的時候，翻「<a class="xref" href="#group-howto">動手做</a>」；每年檢查、年紀變了、快要用錢的時候，翻「<a class="xref" href="#group-life">隨人生調整</a>」。'
assert inner.count(old1) == 1 and inner.count(old2) == 1
inner2 = inner.replace(old1, new1).replace(old2, new2)
patch('cover', '<div class="promise">' + inner + '</div>',
      '<details class="promise read-how" data-print="open"><summary><strong>怎麼讀這本書</strong>：綠框、黃框、標籤、四十分鐘讀法</summary>' + inner2 + '</details>',
      '§7.2 閱讀方式框兩句＋details 外殼')

# §5.2＋§6.0 CSS：接在現有 .toc 規則後面（插在 .toc h4 那條後面）
css_anchor = '.toc h4{font-size:.84rem;margin:.8em 0 .1em}'
assert h.count(css_anchor) == 1
css_new = ('\n.toc .toc-hint{margin:.2em 0 .6em}\n'
 '.toc details.toc-part{border-top:1px solid var(--line);padding:.15em 0}\n'
 '.toc details.toc-part>summary{list-style:none;cursor:pointer;display:flex;flex-wrap:wrap;align-items:baseline;gap:.1em .6em;padding:.55em 0}\n'
 '.toc details.toc-part>summary::-webkit-details-marker{display:none}\n'
 '.toc details.toc-part>summary::before{content:"▸";color:var(--muted);width:1em}\n'
 '.toc details.toc-part[open]>summary::before{content:"▾"}\n'
 '.toc .toc-part-name{font-weight:700}\n'
 '.toc .toc-part-range{font-size:.8em;color:var(--muted)}\n'
 '.toc .toc-part-desc{flex-basis:100%;font-size:.84em;color:var(--muted);padding-left:1.6em}\n'
 '.toc ol.toc-from-11{counter-reset:toc 10}\n'
 '.toc ol.toc-from-14{counter-reset:toc 13}\n'
 '.toc .toc-tag{margin-left:.5em;font-size:.75em;color:var(--muted);border:1px solid var(--line);border-radius:6px;padding:0 .35em}\n'
 '@media print{.toc details.toc-part>summary::before{content:none}.toc .toc-part-desc{padding-left:0}.toc .toc-hint{display:none}}\n'
 '.part-map{list-style:none;margin:.6em 0;padding:0}\n'
 '.part-map li{padding:.45em 0;border-top:1px solid var(--line)}\n'
 '.part-map .map-num{display:inline-block;min-width:1.9em;color:var(--muted);font-variant-numeric:tabular-nums}\n'
 '.part-map .map-lede{display:block;font-size:.88em;color:var(--muted);padding-left:1.9em}\n'
 '.part-map .map-lede+.small{display:block;padding-left:1.9em}\n')
i = h.index(css_anchor)
# 找這條規則所在那一行的行尾，接在行尾後面
line_end = h.index('\n', i)
anchor_line = h[h.rfind('\n', 0, i) + 1:line_end]
assert h.count(anchor_line) == 1
patch('css', anchor_line, anchor_line + css_new.rstrip('\n'), '§5.2 目錄 CSS＋§6.0 組地圖 CSS')

json.dump(P, open(ROOT + 'wip/v61-2026-09-17/batch1/patch-batch1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('patches', len(P))
