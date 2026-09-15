# -*- coding: utf-8 -*-
"""v3.9 → v4.0：家人推銷卡＋黃框；新興市場與中國段＋黃框；因子傾斜黃框補完整。"""
import re, html as H
P='/Users/linyenchu/Cladue Code/family-finance/guide/index.html'; h=open(P,encoding='utf-8').read(); n=0
def rep(a,b,c=1):
    global h,n
    k=h.count(a); assert k==c,(k,a[:60]); h=h.replace(a,b); n+=1
def link(url,title,note): return '<a class="source-link" href="%s" target="_blank" rel="noopener"><span>%s</span><span class="source-note">%s</span></a>'%(url,title,note)
EM='https://www.msci.com/documents/10199/c0db0a48-01f2-4ba9-ad01-226fd5678111'
rep('<li><strong>長輩或業務推保單、主動基金</strong>用第 1 節的問題問三次：誰付錢、最壞損失多少、能不能隨時拿回；答不出來就不買。<br><span class="tag">怕輸人・第 1、3 節</span></li>',
    '<li><strong>長輩、親友或業務推保單、個股、「停利入袋為安」</strong>用第 1 節的問題問三次：誰付錢、最壞損失多少、能不能隨時拿回；答不出來就不買。怎麼開口，看這一節最後那張卡。<br><span class="tag">怕輸人・第 1、3 節</span></li>')
rep('<div class="story"><p><time datetime="2022-08-07">2022 年 8 月 7 日</time>，我開粉專的理由',
    '<div class="data-card"><h3>家人推銷時，護住的是規則，不是說服對方</h3><ol class="checklist"><li><strong>不當場答應。</strong>任何商品都帶回家，用第 1 節的三個問題各寫一句；寫不出來就是答案。</li><li><strong>問數字，不爭觀點。</strong>推薦的人多半自己買了，或親友在賣：問「你買了多少、拿回多少、繳了幾年」，賺的會說、賠的多半不提，數字比說法誠實。</li><li><strong>留一個出口。</strong>真的推不掉的，用規則卡上「玩的錢」那一格處理：金額寫死、虧光不補，對方有面子，你的核心不動。</li><li><strong>保單另外算。</strong>保障用「投資前的安全順序」第 4 項的三個防呆看；名字裡有儲蓄、還本、投資型的，當投資商品比費用。</li></ol><p>這不是研究，是規則卡的延伸：對方改變不了你的卡，你也不必改變對方。</p></div>\n'
    '<div class="story"><p><time datetime="2022-08-12">2022 年 8 月</time>，粉專開站那週我寫：「生活中可能會遇到親戚朋友分享自己投資的某個操作賺了多少（賠錢當然絕口不提），或是有『停利』、『入袋為安』的說法。」我的回答是停利只是「暫時從市場挪到口袋裡」，錢只要還會投回去就還有機會虧。<time datetime="2025-02-06">2025 年 2 月</time>，我替不想開複委託的長輩想的是「退而求其次的方案」：台灣掛牌、分散到其他市場的 ETF，費用比美股同標的高很多，但一切從簡。<time datetime="2025-08-06">2025 年 8 月</time>，我聽到同事開始 0050 定期定額，寫「心裡滿高興的，這就是這個地方存在的意義」。</p></div>\n'
    '<div class="story"><p><time datetime="2022-08-07">2022 年 8 月 7 日</time>，我開粉專的理由')
rep('權重每個月都會變，數字看官方月報。</p></div>',
    '權重每個月都會變，數字看官方月報。</p><p><strong>新興市場和中國怎麼算。</strong>同一天的 MSCI 新興市場月報：台灣 27.44%、南韓 20.84%、中國 20.62%、印度 11.25%。用全球指數裡台灣 3.25% 反推，新興市場約占全球指數 12%，中國約 2.4%（兩份官方月報推算）。買全球市值型就含這一塊；市場上也有「不含中國」的版本，代價是費用和規模，而且挑掉一個國家就是一次主動決定，跟挑掉美國是同一件事。這是政治與個人立場，本文不替你決定：決定了就寫進規則卡，不因新聞反覆改。</p></div>\n'
    '<div class="story"><p>這件事我沒有在粉專寫過立場。我持有的全球型（VWRD、VT 這類）本身就含新興市場，我沒有另外挑掉任何國家。</p></div>')
rep('全球型含約一成新興市場，裡面有中國。','全球型含約 12% 新興市場，中國約 2.4%、台灣 3.25%（第 12 節那張卡）。')
rep('<span>MSCI ACWI Index 官方月報（2026-08-31）</span><span class="source-note">國家權重、前十大、產業權重；每月更新</span></a>',
    '<span>MSCI ACWI Index 官方月報（2026-08-31）</span><span class="source-note">國家權重、前十大、產業權重；每月更新</span></a>'+link(EM,'MSCI Emerging Markets Index 官方月報（2026-08-31）','台灣 27.44%、南韓 20.84%、中國 20.62%、印度 11.25%；新興市場占全球約 12% 由兩份月報推算'))
rep('全球指數的國家與公司權重：MSCI ACWI 官方月報 2026-08-31（第 12 節）。','全球指數的國家與公司權重、新興市場與中國：MSCI ACWI 與 MSCI Emerging Markets 官方月報 2026-08-31（第 12 節）。')
rep('<div class="story"><p>我股票裡的台股只占一到兩成，七成是全球市值型，剩下的一到兩成是因子傾斜（因子：照某種特徵挑股票的規則；第 3 節那次重算就是在檢查它值不值得）。<time datetime="2025-11-05">2025 年 11 月</time>我寫下把台股在股票裡的比例從一成慢慢調到 65 歲時兩成，理由是「降低退休提領匯率（較高機會在台灣退休）以及因子較大波動的影響」。這是我的比例，不是建議。</p></div>',
    '<div class="story"><p>我股票裡的台股只占一到兩成，七成是全球市值型，剩下的一到兩成是因子傾斜（因子：照某種特徵挑股票的規則）。<time datetime="2025-11-05">2025 年 11 月</time>我寫下把台股從一成慢慢調到 65 歲時兩成、因子從兩成降到一成，理由是「降低退休提領匯率（較高機會在台灣退休）以及因子較大波動的影響」。這是我的比例，不是建議。</p>'
    '<p>為什麼還留著因子，我自己的紀錄是三段。<time datetime="2025-11-08">2025 年 11 月</time>我把六年的投入全部改成「只買全球股票加全球債券」重算一次：13.79% 對上自己的 13.77%，「誒這不是根本沒差嗎？！」結論是「主動配置在我的這六年來的持倉期間，雖然目前沒有對我的績效造成拖累，但也沒有為我帶來超額報酬……但帶來額外的複雜性和波動性是肯定的」，所以簡介裡只建議「低成本且分散的全球市值型指數ETF」。同一篇我也寫了留著的條件：「如果相信長期因子溢酬的學術證據，就必須要維持近乎完美的『投資紀律』，並準備好面對未來數年甚至數十年可能的『持續落後』。『擇時因子』與『擇時市場』一樣困難。」<time datetime="2026-09-07">2026 年 9 月</time>我承認：「這其實是我自己找麻煩XD，真的是簡單就好了！」所以它是衛星、有上限、正在往下調，而且不會因為它落後就賣掉。</p></div>')
rep('要拿它當核心，你得在落後的那幾年不放棄，而且事前沒有人能保證那個特徵未來還會贏。</li>',
    '要拿它當核心，你得在落後的那幾年不放棄，而且事前沒有人能保證那個特徵未來還會贏。（一個真實的例子在下面的黃框：作者自己留了一小塊因子，六年下來沒有超額報酬，只多了複雜和波動。）</li>')
open(P,'w',encoding='utf-8').write(h); print('v40',n)
for t in ['div','section','ol','ul','li','p','table','a','details','figure','span']:
    o=len(re.findall(r'<%s\b'%t,h)); c=len(re.findall(r'</%s>'%t,h)); assert o==c,(t,o,c)
print('tags', len(re.findall(r'<span class="tag">', h)), 'chars',len(re.findall('[一-鿿]',h)))
a=re.sub(r"^\s*<!doctype[^>]*>\s*","",h,flags=re.I); a=re.sub(r"</?(html|head|body)\b[^>]*>\s*","",a,flags=re.I)
open('/Users/linyenchu/Cladue Code/family-finance/output/guide.html','w',encoding='utf-8').write(a)
open('/Users/linyenchu/Cladue Code/family-finance/output/guide-full.html','w',encoding='utf-8').write(h)
body=h[h.find('<header class="cover"'):]
body=re.sub(r'<svg.*?</svg>','',body,flags=re.S); body=re.sub(r'<details class="orig">.*?</details>','',body,flags=re.S)
body=re.sub(r'<div class="story">','\n【黃框】',body)
body=re.sub(r'<(section class="part" id="([^"]+)")>',r'\n\n═══ SECTION \2 ═══\n',body)
body=re.sub(r'<h2>(.*?)</h2>',lambda m:'\n## '+re.sub(r'<[^>]+>','',m.group(1))+'\n',body,flags=re.S)
body=re.sub(r'<h3>(.*?)</h3>',lambda m:'\n### '+re.sub(r'<[^>]+>','',m.group(1))+'\n',body,flags=re.S)
body=re.sub(r'<a class="source-link" href="[^"]+"[^>]*><span>(.*?)</span><span class="source-note">(.*?)</span></a>',lambda m:'\n  ・來源：'+re.sub(r'<[^>]+>','',m.group(1))+' ｜ '+re.sub(r'<[^>]+>','',m.group(2)),body,flags=re.S)
body=re.sub(r'<(li|dt|dd|tr)\b[^>]*>','\n- ',body); body=re.sub(r'</(td|th)>',' | ',body)
body=re.sub(r'<p class="decision">','\n【本節行動】',body); body=re.sub(r'<div class="warning">','\n【警告】',body); body=re.sub(r'<span class="plain-title">白話版</span><br>','【白話版】',body)
body=re.sub(r'<span class="chart-title">','\n[圖] ',body); body=re.sub(r'<figcaption>','\n[圖說] ',body)
body=re.sub(r'<(p|div|details|summary|ol|ul|table|thead|tbody|nav|header|figure)\b[^>]*>','\n',body)
body=re.sub(r'<[^>]+>','',body); body=H.unescape(body); body=re.sub(r'[ \t]+',' ',body); body=re.sub(r'\n\s*\n+','\n',body)
lines=[l.rstrip() for l in body.split('\n') if l.strip()]
open('/private/tmp/claude-501/-Users-linyenchu-Cladue-Code/74b71b1c-f70a-4f20-89ce-2952d977c51c/scratchpad/read_v40.txt','w',encoding='utf-8').write('\n'.join(lines)); print(len(lines),'lines')
for m in re.finditer(r'<section class="part" id="([^"]+)">(.*?)</section>',h,re.S):
    sec=m.group(2); t=re.sub(r'<svg.*?</svg>|<details.*?</details>','',sec,flags=re.S); t=re.sub(r'<[^>]+>','',t)
    zi=len(re.findall('[一-鿿]',t)); st=sec.count('class="story"'); ca=sec.count('class="data-card"'); fg=sec.count('<figure'); so=sec.count('source-link')
    print('%-11s 字=%5d 黃框=%d 卡=%d 圖=%d 來源=%d' % (m.group(1), zi, st, ca, fg, so))
