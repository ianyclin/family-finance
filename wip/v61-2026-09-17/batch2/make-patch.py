import json
P=[]
def add(sec,old,new,why): P.append(dict(section=sec,old=old,new=new,why=why))
# §8 anchors
add('ten','<div class="warning" data-lite="ch1"','<span id="ten-stop"></span><div class="warning" data-lite="ch1"','錨點：四個立即停止（span 插在警告框前）')
for sec,h3,i in [('s2','前幾年像沒在長：先有心理準備','s2-slow'),('s5','跌的時候、很久沒漲的時候，記得這幾句','s5-remember'),('s6','等匯率，和等股價是同一個問題','s6-fx'),('s6','現在是歷史新高，會不會太高了？','s6-ath'),('s8','高股息 ETF：先看四件事','s8-dividend'),('s11','把答案寫成一張紙：我的投資計畫','plan-table'),('cases','陳大哥：五年後退休','case-chen'),('s12','三條新手路徑：去哪裡買、各付什麼代價','s12-paths'),('s13','怕錯過（1 題）','s13-miss'),('s13','怕賠（14 題）','s13-loss'),('s13','怕輸人（4 題）','s13-envy'),('s13','無聊（1 題）','s13-bored'),('s13','想控制（7 題）','s13-control'),('s13','家人推銷時：守住自己的規則，不必說服對方','s13-family'),('costs','四種出事，哪一種會讓錢真的不見','costs-four')]:
    add(sec,'<h3>%s</h3>'%h3,'<h3 id="%s">%s</h3>'%(i,h3),'錨點 '+i)
add('s10','<ul class="checklist"><li><strong>冷卻期</strong>','<ul class="checklist"><li id="s10-cooling"><strong>冷卻期</strong>','錨點：冷卻期 li（只加屬性）')
add('s11','<div class="data-card" data-lite-alt="ch4-drill">','<span id="drill"></span><div class="data-card" data-lite-alt="ch4-drill">','錨點：大跌演練（span 插在受保護區塊前）')
# §6.3 situations table + closing sentence
table='''<div class="table-wrap"><table class="compact text situations"><thead><tr><th>遇到的狀況</th><th>先翻這裡</th></tr></thead><tbody>
<tr><td>帳面跌了一兩成、新聞說要崩盤，很想賣</td><td>先打開自己<a class="xref" href="#plan-table">計畫表</a>的 F 區照做；再看第 <a class="xref" href="#s5-remember">5</a> 節「跌的時候、很久沒漲的時候，記得這幾句」、第 <a class="xref" href="#drill">11</a> 節「大跌演練」、第 <a class="xref" href="#s13-loss">14</a> 節「怕賠」</td></tr>
<tr><td>投了好幾年，好像都沒在長</td><td>第 <a class="xref" href="#s2-slow">2</a> 節「前幾年像沒在長」、第 <a class="xref" href="#s5-remember">5</a> 節同一張卡、第 <a class="xref" href="#s13-bored">14</a> 節「無聊」</td></tr>
<tr><td>漲很多，想先賣掉一些</td><td>第 <a class="xref" href="#s8">8</a> 節、第 <a class="xref" href="#s13-miss">14</a> 節「怕錯過」</td></tr>
<tr><td>手上有錢，想等跌下來，或覺得現在太高</td><td>第 <a class="xref" href="#s6">6</a> 節（含「<a class="xref" href="#s6-ath">現在是歷史新高，會不會太高了？</a>」）、第 <a class="xref" href="#s13-loss">14</a> 節「怕賠」</td></tr>
<tr><td>台幣升值，海外資產縮水</td><td>第 <a class="xref" href="#s6-fx">6</a> 節「等匯率，和等股價是同一個問題」、第 <a class="xref" href="#s13-loss">14</a> 節「怕賠」最後一題</td></tr>
<tr><td>想改計畫、想調高股票比例、想加碼攤平</td><td>第 <a class="xref" href="#s10-cooling">10</a> 節「冷卻期」、第 <a class="xref" href="#s13-control">14</a> 節「想控制」</td></tr>
<tr><td>朋友集中一檔賺很多，覺得自己輸了</td><td>第 <a class="xref" href="#s13-envy">14</a> 節「怕輸人」</td></tr>
<tr><td>有人推薦高股息、月配、儲蓄險、正 2、主題型，或家人一直推銷</td><td>「<a class="xref" href="#sidepaths">常見的岔路</a>」、第 <a class="xref" href="#s8-dividend">8</a> 節「高股息 ETF：先看四件事」、第 <a class="xref" href="#s13-family">14</a> 節「家人推銷時」</td></tr>
<tr><td>想借錢投資（信貸、質押、融資）</td><td>「<a class="xref" href="#lifecycle-q2">年齡、槓桿與退休</a>」第二題、「<a class="xref" href="#sidepaths">常見的岔路</a>」</td></tr>
<tr><td>LINE 老師、保證獲利、要你匯款或給驗證碼</td><td>「<a class="xref" href="#ten-stop">十分鐘看完</a>」的四個立即停止（已經匯了，打 165）、「<a class="xref" href="#costs-four">費用、稅務與帳戶安全</a>」的「四種出事」</td></tr>
</tbody></table></div>
'''
old_sit='<p>動手之前先看一遍也好：先知道自己可能會怕什麼，遇到時比較不慌。</p>\n<ol class="part-map">\n<li><span class="map-num">14</span>'
add('group-situations',old_sit,old_sit.replace('<ol class="part-map">\n',table+'<ol class="part-map">\n'),'§6.3 狀況索引表')
old_end='這裡只回答一件事：為什麼它不是核心。</span></li>\n</ol>\n<a class="back" href="#toc">回目錄</a></section>'
add('group-situations',old_end,old_end.replace('</ol>\n','</ol>\n<p class="small">表上找不到，就往下翻第 <a class="xref" href="#s13">14</a> 節，31 題照六種感受分組。</p>\n'),'§6.3 收尾句')
# §6.5
old_life='讓家人接得下去。</span></li>\n</ol>\n<a class="back" href="#toc">回目錄</a></section>'
add('group-life',old_life,old_life.replace('</ol>\n','</ol>\n<p class="small">離退休只剩幾年的人，可以對照第 <a class="xref" href="#case-chen">12</a> 節的陳大哥（五年後退休，附填好的全表）。</p>\n'),'§6.5 陳大哥句')
# §9.3
old_prod='ETF 也要打開成分表，不能只看名稱、價格或配息。</p>\n<div class="data-card" data-lite-alt="ch6-pick"><h3>選 ETF 時逐項查看</h3>'
add('products',old_prod,old_prod.replace('</p>\n','</p>\n<p>還沒決定去哪裡買，先看第 <a class="xref" href="#s12-paths">13</a> 節「三條新手路徑：去哪裡買、各付什麼代價」。</p>\n',1),'§9.3 products 指路句（第 2 題 A）')
# 新 1 → #plan-table
add('cover','第 <a class="xref" href="#s11">11</a> 節的計畫表（白話版、兩把尺、壓力測試、三問）','第 <a class="xref" href="#plan-table">11</a> 節的計畫表（白話版、兩把尺、壓力測試、三問）','新 1 改回 #plan-table')
# §7.1 tasks
tasks='''<nav class="tasks" aria-label="我現在想"><p class="tasks-title"><strong>我現在想……</strong></p>
<ul>
<li><a href="#ten">只有十分鐘，先抓重點</a></li>
<li><a href="#start">先確認能不能開始投資（預備金、卡債、保單）</a></li>
<li><a href="#group-plan">寫下自己的比例和規則</a></li>
<li><a href="#group-howto">開戶、挑商品、下第一單</a></li>
<li><a href="#group-situations">大跌很慌、想賣，或有人推銷</a></li>
<li><a href="#annual">年底了，做一年一次的檢查</a></li>
<li><a href="#group-life">自己或爸媽快退休、快要用錢</a></li>
</ul>
<p class="small">看不懂的詞，翻「<a class="xref" href="#glossary">先認識這些詞</a>」；想從頭讀，往下看<a href="#toc">目錄</a>。</p></nav>
'''
add('cover','</p>\n<details class="promise read-how" data-print="open">','</p>\n'+tasks+'<details class="promise read-how" data-print="open">','§7.1 封面入口')
add('css','.part-map .map-lede+.small{display:block;padding-left:1.9em}\n','.part-map .map-lede+.small{display:block;padding-left:1.9em}\n.tasks ul{list-style:none;margin:.4em 0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}\n.tasks li a{display:block;height:100%;padding:.6em .8em;border:1px solid var(--line);border-radius:12px;background:var(--surface);text-decoration:none;line-height:1.4}\n@media print{.tasks{display:none}}\n','§7.1 CSS')
json.dump(P,open(__file__.replace('make-patch.py','patch-batch2.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(P))
