# -*- coding: utf-8 -*-
"""structure 階段：產生 guidetools 補丁（S5、S7、D6 改節名、lifecycle 三題錨點、cases 指路句）。
所有 old 字串都從現行 guide/index.html 讀出來，不手打。"""
import json, re, sys
SRC = 'guide/index.html'
h = open(SRC, encoding='utf-8').read()
P = []
def add(sec, old, new, why):
    assert h.count(old) == 1, (sec, h.count(old), old[:80])
    P.append({'section': sec, 'old': old, 'new': new, 'why': why})

OLD_NAME = '用錢、退休與家庭交接'
NEW_NAME = '用錢前的準備與家庭交接'

# ---------- S5：搬移 firstmonth
fm_start = h.index('<section class="part" id="firstmonth">')
fm_end = h.index('</section>', fm_start) + len('</section>')
fm = h[fm_start:fm_end]
tail = h[fm_end:fm_end + 2]; assert tail == '\n\n'
add('firstmonth', fm + '\n\n', '', 'S5：從「開始前」移走')
fm_new = fm.replace('<p class="lede">動作散在後面各節，這一頁把它們排成順序。',
                    '<p class="lede">動作散在全書各節，這一頁把它們排成順序。')
assert fm_new != fm
steps_end = h.index('</section>', h.index('<section class="part" id="steps">')) + len('</section>')
anchor = h[steps_end - len('<a class="back" href="#toc">回目錄</a></section>'):steps_end] + '\n\n<section class="part" id="products">'
assert h[steps_end - len('<a class="back" href="#toc">回目錄</a></section>'):].startswith(anchor)
old = '<p class="decision">先以不影響生活的小金額完成一次入金、下單、交割與對帳，再設定固定投入。</p>' + anchor
add('steps', old, old.replace('\n\n<section class="part" id="products">', '\n\n' + fm_new + '\n\n<section class="part" id="products">'),
    'S5：放到七個步驟後面')

# 封面閱讀方式
old = '再讀「開始前」的其他四節（一眼看懂、投資前的安全順序、先認識這些詞、從第一週到第一年）加第'
add('cover', old, '再讀「開始前」的其他三節（一眼看懂、投資前的安全順序、先認識這些詞）加第', 'S5：開始前剩三節')
old = '要開戶、下單、對帳、每年檢查的時候，翻後面的實作附錄。'
add('cover', old, '要開戶、下單、對帳、每年檢查的時候，翻後面的實作附錄（從第一週到第一年的時間表也在那裡）。', 'S5：告訴讀者時間表搬到哪')

# 十分鐘看完的本節行動
old = '<p class="decision">讀完這一頁，照「<a class="xref" href="#steps">第一次投資的七個步驟</a>」用小金額開始；遇到問題，再翻對應的那一節。</p>'
add('ten', old, '<p class="decision">讀完這一頁，照「<a class="xref" href="#steps">第一次投資的七個步驟</a>」用小金額開始；第一週、第一個月、第一年各做什麼，排在「<a class="xref" href="#firstmonth">從第一週到第一年</a>」那一頁；遇到問題，再翻對應的那一節。</p>',
    'S5：本節行動連到時間表')

# ---------- S7：目錄
nav_s = h.index('<nav class="toc" id="toc"'); nav_e = h.index('</nav>', nav_s) + len('</nav>')
nav = h[nav_s:nav_e]
links = dict(re.findall(r'<li><a href="#([\w-]+)">(.*?)</a></li>', nav))
def ul(ids, tag='ul'):
    return '<%s>%s</%s>' % (tag, ''.join('<li><a href="#%s">%s</a></li>' % (i, links[i].replace(OLD_NAME, NEW_NAME)) for i in ids), tag)
core = re.findall(r'<li><a href="#([\w-]+)">', nav[nav.index('<ol>'):nav.index('</ol>')])
new_nav = ('<nav class="toc" id="toc" aria-label="目錄"><h2>目錄</h2>'
  '<h3>開始前</h3><p class="small">第一次讀先看這幾節：七件事、全書地圖、投資前的安全順序，和看不懂時回來查的詞。</p>'
  + ul(['ten', 'why', 'start', 'glossary']) +
  '<h3>先看懂，再決定</h3><p class="small">本書的主體：一節回答一個新手常問的問題，讀完會有一張自己的投資計畫。</p>'
  + ul(core, 'ol') +
  '<h3>實作附錄</h3><p class="small">要動手的時候翻這裡，不必從頭讀：做到哪一步，就翻哪一節。</p>'
  '<h4>開始做</h4>' + ul(['steps', 'firstmonth', 'products', 'costs']) +
  '<h4>人生階段</h4>' + ul(['withdraw', 'lifecycle']) +
  '<h4>維護</h4>' + ul(['sidepaths', 'annual']) +
  '<h4>查證</h4>' + ul(['toolbox', 'methods']) +
  '</nav>')
assert set(re.findall(r'href="#([\w-]+)"', new_nav)) == set(links), 'toc ids changed'
add('toc', nav, new_nav, 'S5＋S7：小標不帶數量、各組一行說明、實作附錄分四小群；時間表移到實作附錄；withdraw 新節名')

# group-core
old = '<section class="part" id="group-core"><h2>接下來的十四節：先看懂，再決定</h2><p class="lede">這十四節是本書的主體，一節回答一個新手常問的問題。</p>'
add('group-core', old, '<section class="part" id="group-core"><h2>本書的主體：先看懂，再決定</h2><p class="lede">接下來每一節回答一個新手常問的問題。</p>', 'S7：拿掉數量')
old = '第 <a class="xref" href="#cases">12</a> 節是另外三個人怎麼填同一張表，'
add('group-core', old, '第 <a class="xref" href="#cases">12</a> 節是另外三個人照同一套步驟想出不同的比例（陳大哥附填好的全表），', 'verify cases note：只有陳大哥有全表')

# group-howto
old = '<p class="lede">前面講為什麼，後面這九節講怎麼做。</p><p>開戶與第一次下單、挑 ETF 與債券、費用稅務與帳戶安全、用錢與退休交接、年齡與槓桿、'
add('group-howto', old, '<p class="lede">前面講為什麼，後面這幾節講怎麼做。</p><p>開戶與第一次下單、第一週到第一年的時間表、挑 ETF 與債券、費用稅務與帳戶安全、用錢前的準備與家庭交接、年齡與槓桿、',
    'S5＋S7＋D6：拿掉數量、補時間表、新節名')

# ---------- D6：withdraw
old = '<section class="part" id="withdraw"><h2>用錢、退休與家庭交接</h2><p class="lede">累積期怕沒有開始，提領期怕一開始就遇到大跌。</p>'
add('withdraw', old, '<section class="part" id="withdraw"><h2>' + NEW_NAME + '</h2><p class="lede">開始拿錢出來花以前，先把近幾年要用的錢備好；再留一張表，讓家人接得下去。</p>',
    'D6：新節名與 lede 對齊內容')
old = '同樣一桶水，一邊被拿去喝、一邊又在漏，見底的速度比只喝不漏快得多。退休後同時遇到下跌與提領，也會讓資產比較難恢復。後半段'
add('withdraw', old, '同樣一桶水，一邊被拿去喝、一邊又在漏，見底的速度比只喝不漏快得多。所以開始喝以前，先另外裝一壺夠喝幾天的水，桶子在漏的那幾天，先喝壺裡的。後半段',
    'D6：白話版改成比喻四項準備，不直接講答案')
old = '這兩件事的細節都在「<a class="xref" href="#lifecycle">年齡、槓桿與退休</a>」第三題，往下找'
add('withdraw', old, '這兩件事的細節都在「<a class="xref" href="#lifecycle-q3">年齡、槓桿與退休</a>」第三題，往下找', '第三題錨點')
old = '這一節講另外兩件事：接近用錢日要先準備什麼，和讓家人接得下去的家庭一頁表。'
add('withdraw', old, '這一節只講兩件要自己動手準備的事：接近用錢日要先準備什麼，和讓家人接得下去的家庭一頁表。', 'verify note：「另外兩件事」數不對')

# 全書錨文字
old = '帳戶清單寫在家庭一頁表（「<a class="xref" href="#withdraw">用錢、退休與家庭交接</a>」）'
add('s11', old, old.replace(OLD_NAME, NEW_NAME), 'D6 節名')
old = '<li>退休前五年，要把「<a class="xref" href="#withdraw">用錢、退休與家庭交接</a>」和「<a class="xref" href="#lifecycle">年齡、槓桿與退休</a>」第三題讀完。</li>'
add('cases', old, '<li>退休前五年，要讀「<a class="xref" href="#lifecycle-q3">年齡、槓桿與退休</a>」第三題（要存多少、為什麼一退休就跌最傷），和「<a class="xref" href="#withdraw">' + NEW_NAME + '</a>」的四項準備與家庭一頁表。</li>',
    'D6＋verify note：指路句寫出去那裡會看到什麼')
old = '欄位、密碼處理與更新時機在「<a class="xref" href="#withdraw">用錢、退休與家庭交接</a>」的〈家庭一頁表〉。</span><br><span class="tag">第 <a class="xref" href="#s11">11</a> 節、「<a class="xref" href="#withdraw">用錢、退休與家庭交接</a>」</span>'
add('s13', old, old.replace(OLD_NAME, NEW_NAME), 'D6 節名')
old = '「<a class="xref" href="#withdraw">用錢、退休與家庭交接</a>」的四項準備，就是那五到十年要做的事。'
add('lifecycle', old, old.replace(OLD_NAME, NEW_NAME), 'D6 節名')
old = '文件位置有沒有變（「<a class="xref" href="#withdraw">用錢、退休與家庭交接</a>」）？'
add('annual', old, old.replace(OLD_NAME, NEW_NAME), 'D6 節名（app-a-checklist 指紋會變，工作表不引這段連結）')
old = '<li>五年內要開始從投資圈拿生活費：「<a class="xref" href="#withdraw">用錢、退休與家庭交接</a>」、「<a class="xref" href="#lifecycle">年齡、槓桿與退休</a>」第三題；'
add('annual', old, '<li>五年內要開始從投資圈拿生活費：「<a class="xref" href="#lifecycle-q3">年齡、槓桿與退休</a>」第三題（要存多少、為什麼一退休就跌最傷）、「<a class="xref" href="#withdraw">' + NEW_NAME + '</a>」的四項準備；',
    'D6：提領講解改指第三題，四項準備留在 withdraw')
old = '<li>家人需要能接手：「<a class="xref" href="#withdraw">用錢、退休與家庭交接</a>」。</li>'
add('annual', old, old.replace(OLD_NAME, NEW_NAME), 'D6 節名')

# ---------- lifecycle 三題 id
for n, t in (('1', '一、年齡真的該影響比例嗎？'), ('2', '二、年輕時借錢投資，有沒有道理？'), ('3', '三、退休要存多少、每年能領多少？')):
    add('lifecycle', '<h3>%s</h3>' % t, '<h3 id="lifecycle-q%s">%s</h3>' % (n, t), '三題錨點')

# ---------- cases note：第 11 節小安
old = '其他三種人怎麼填，看「<a class="xref" href="#cases">另外三個人</a>」。'
add('s11', old, '其他三種人怎麼想、陳大哥填好的全表，看「<a class="xref" href="#cases">另外三個人</a>」。', 'verify cases note')

# ---------- D10：兩個 details 加 data-print="open"
old = '<details><summary>展開 24 格怎麼填（欄位表，和各區的補充說明）</summary>'
add('s11', old, '<details data-print="open"><summary>展開 24 格怎麼填（欄位表，和各區的補充說明）</summary>', 'D10：紙本展開')
old = '<details data-lite-alt="lookup-tables"><summary>'
add('s11', old, '<details data-lite-alt="lookup-tables" data-print="open"><summary>', 'D10：紙本展開（lookup-tables 指紋會變，內容不變）')

# ---------- 所有「年齡、槓桿與退休」第N題 xref 指到題目 id（避開上面已處理的片段）
done = [(h.index(x['old']), h.index(x['old']) + len(x['old'])) for x in P]
q = {'一': '1', '二': '2', '三': '3'}
pat = re.compile(r'<a class="xref" href="#lifecycle">年齡、槓桿與退休</a>」第([一二三])題')
for m in pat.finditer(h):
    if any(a <= m.start() < b for a, b in done): continue
    # 擴張 old 到唯一
    L = 0
    while True:
        old = h[m.start() - L:m.end()]
        if h.count(old) == 1: break
        L += 10
    new = old[:L] + m.group(0).replace('href="#lifecycle"', 'href="#lifecycle-q%s"' % q[m.group(1)])
    s = m.start() - L
    if any(not (m.end() <= a or s >= b) for a, b in done):
        # 和既有補丁重疊：縮到不重疊
        raise SystemExit('overlap at %d' % m.start())
    done.append((s, m.end()))
    add('xref-lifecycle', old, new, '第%s題錨點' % m.group(1))

json.dump(P, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(P), 'patches; lifecycle xrefs:', sum(1 for x in P if x['section'] == 'xref-lifecycle'))
