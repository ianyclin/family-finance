# -*- coding: utf-8 -*-
"""v4.2 → v4.3：「去哪查」加「再往下讀：書與人」卡（作者 2026-09-12 拍板的書單與台灣作者）。一次性腳本。"""
P='/Users/linyenchu/Cladue Code/family-finance/guide/index.html'
h=open(P,encoding='utf-8').read()
i=h.find('<section class="part" id="toolbox">'); j=h.find('<section class="part" id="methods">'); assert 0<i<j
s=h[i:j]
def L(u,t): return '<a href="%s" target="_blank" rel="noopener">%s</a>'%(u,t)
card=('<div class="data-card"><h3>再往下讀：書與人</h3>'
'<p>本文只講到能開始；想追根究柢，下面的書照難易度排。書名後面是出版社與繁中版年份，內容以你手上那一版為準。</p>'
'<h4>入門：不需要背景，讀完就能開始</h4><ul>'
'<li>《約翰柏格投資常識》John Bogle，寰宇 2019。指數基金的發明人，用最簡單的算術講為什麼買整個市場、放很久、少付費。</li>'
'<li>《持續買進》Nick Maggiulli，商業周刊 2023。用資料回答「該不該等」「一次投還是分批」；作者的部落格 '+L('https://ofdollarsanddata.com/','Of Dollars and Data')+'（英文）仍每週更新。同一位作者 2026 年的《財富階梯》談各個財富階段的策略，後半有集中持股與創業，不是指數化的書，當延伸。</li>'
'<li>《我8歲，我會自己賺錢！》Allan Roth，樂金 2021。寫給大人看的：一位理財規劃師教兒子用三檔指數基金，說明為什麼這樣就贏過多數專業經理人。</li>'
'<li>《不看盤，我才賺到大錢》Bill Schultheis，大是 2026 第四版。前證券營業員的「買幾檔指數基金放著不管」。</li>'
'<li>《不在意，才能賺最多》Bill Schultheis，樂金 2023。上一本的精簡版：儲蓄、投資、規劃三步。</li>'
'<li>《一年投資5分鐘》陳逸朴（小資YP），遠流 2021。台灣本土，從觀念到開戶一路寫完；券商操作那章已經舊了，看他網站的新版。</li>'
'<li>《通膨時代，我選擇穩定致富》理財館長（陳震奇）、狂徒，遠流 2022。台灣本土；前三章和實務章是給新手的，第 4 章的回測與槓桿可以先跳過。</li>'
'<li>《綠角的基金8堂課》2016 補課增修版，綠角，經濟日報 2016。從風險講起的入門書；作者的部落格與粉專持續更新到現在。</li>'
'<li>《致富心態》Morgan Housel，天下文化 2020（2026 有增訂版）。講錢和心理，不講方法。</li>'
'<li>《金錢超思考》Jonathan Clements，遠流 2026 新裝版。25 篇短文談錢、快樂和人生的關係；不教操作。</li>'
'<li>《If You Can》William Bernstein，2014。免費英文小冊，作者官網有 PDF，一個下午讀得完；沒有中文版。</li>'
'</ul><h4>進階：看得懂報酬、波動、配置之後</h4><ul>'
'<li>《漫步華爾街》Burton Malkiel，天下文化 2023 五十週年增訂版。效率市場與歷史資料，講清楚為什麼選股和擇時長期難贏。</li>'
'<li>《投資終極戰》Charles Ellis，大牌 2020。「輸家的遊戲」：少犯錯的人贏。</li>'
'<li>《鄉民的提早退休計畫》觀念版，Bogleheads 三位作者，樂金 2021。從儲蓄到退休、遺產的百科式整理。</li>'
'<li>《投資金律》新版，William Bernstein，臉譜 2024。理論、歷史、心理、產業四根柱子；裡面談因子是中性討論，不是叫你加。</li>'
'<li>《長期買進》周冠男，天下文化 2024。財金教授從行為面談自制力，加上自己持有 0050 二十年的紀錄。</li>'
'<li>《夠了》John Bogle，早安財經 2019。Vanguard 創辦人談金融業與「多少才夠」；繁中版已絕版，圖書館或二手書找得到。</li>'
'</ul><h4>深入</h4><ul>'
'<li>《快思慢想》Daniel Kahneman，天下文化。不是投資書，是第 '+'<a class="xref" href="#s10">10</a>'+' 節那些偏誤的根。</li>'
'</ul><h4>台灣寫指數化投資的人</h4>'
'<p>下面幾位的立場和本文一致：低成本、分散、市值型、長期、不擇時。先看他們的觀念文，再看逐檔分析。</p><ul>'
'<li><strong>綠角</strong>：'+L('https://greenhornfinancefootnote.blogspot.com/','綠角財經筆記')+'，2007 年寫到現在，粉專與實體課也持續；書見上。</li>'
'<li><strong>ffaarr（張遠）</strong>：'+L('https://finance.ffaarr.com.tw/','ffaarr 的投資理財記事')+'。沒有出書；海外 ETF 逐檔比較與債券指數拆解是招牌，新手先讀他的觀念文。</li>'
'<li><strong>小資YP（陳逸朴）</strong>：'+L('https://yp-finance.com/','小資YP 投資理財筆記')+'；書見上，另有付費的回測工具。</li>'
'<li><strong>周冠男</strong>：政大財管系教授，主要在臉書與媒體專訪；書見上。</li>'
'<li><strong>理財館長（陳震奇）</strong>：'+L('https://portaly.cc/musclemoney','IG 與 Podcast')+' 為主，短、口語；他本人是證券營業員；書見上。</li>'
'</ul><p>上面這些人多半也開課、賣工具或放開戶推薦連結，那是他們的收入，不是問題；但要分開看：觀念可以學，課程、工具、要去哪家開戶，另外用第 '+'<a class="xref" href="#s1">1</a>'+' 節的三個問題判斷。</p>'
'<p class="small">書目資料 2026-09-12 查自三民、博客來與出版社頁面；版次與價格會變，以書店當下為準。本段是書單，不是對任何人的評價。</p></div>\n')
tgt='<p class="small">連結檢查日期：2026-09-12'; assert s.count(tgt)==1
s=s.replace(tgt, card+tgt)
h=h[:i]+s+h[j:]
# 目錄與 lede 補一句
old='<li><a href="#toolbox">去哪查：官方入口</a></li>'; assert h.count(old)==1
h=h.replace(old,'<li><a href="#toolbox">去哪查：官方入口與延伸閱讀</a></li>')
old2='<section class="part" id="toolbox"><h2>去哪查：官方入口</h2>'; assert h.count(old2)==1
h=h.replace(old2,'<section class="part" id="toolbox"><h2>去哪查：官方入口與延伸閱讀</h2>')
old3='本文多處說「以公開說明書為準」「查官方公告」，這一頁就是那些地方。'; assert h.count(old3)==1
h=h.replace(old3,'本文多處說「以公開說明書為準」「查官方公告」，這一頁就是那些地方；頁尾另有書單。')
open(P,'w',encoding='utf-8').write(h); print('ok',len(h))
