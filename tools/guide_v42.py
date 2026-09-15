# -*- coding: utf-8 -*-
"""v4.1 → v4.2：第 3 節加「最有名的主動投資人，替家人選的是指數」卡（巴菲特賭局、遺囑指示、Bogle 雕像、耶魯 Swensen）＋來源。一次性腳本。"""
import sys
P='/Users/linyenchu/Cladue Code/family-finance/guide/index.html'
h=open(P,encoding='utf-8').read()
i=h.find('<section class="part" id="s3">'); j=h.find('<section class="part" id="s4">'); assert 0<i<j
s=h[i:j]
X='<a class="xref" href="#s4">4</a>'
card=('<div class="data-card"><h3>最有名的主動投資人，替家人選的是指數</h3><ul>'
'<li><strong>十年賭局。</strong>巴菲特 2008 年起和避險基金業者 Protégé Partners 賭十年：他選一檔幾乎零成本的 S&amp;P 500 指數基金，對方選五檔「基金中的基金」，背後合計兩百多檔避險基金。2017 年底結算，指數基金十年累積 125.8%（平均一年 8.5%）；五檔對手各是 21.7%、42.3%、87.7%、2.8%、27.0%，平均一年 0.3% 到 6.5%，沒有一檔追上。賭金最後捐了 2,222,279 美元給奧馬哈的 Girls Inc.。</li>'
'<li><strong>給家人的遺囑指示。</strong>2013 年股東信裡，他寫給替太太管錢的受託人的指示只有一句：一成放短期公債，九成放一檔費用極低的 S&amp;P 500 指數基金（他建議 Vanguard 的）；他相信這樣的長期結果，會勝過多數請高費用經理人的退休基金、機構和個人。</li>'
'<li><strong>耶魯校務基金的 David Swensen。</strong>他從 1985 年替耶魯管錢到 2021 年過世，基金從 13 億美元長到 312 億美元，用的是主動、複雜、一般人做不到的方法；但他 2005 年寫給一般人的書《Unconventional Success》結論是：沒有把握贏過市場的人，該用低成本的指數基金與 ETF，並避開收高費用、有利益衝突的營利型基金公司。這本書沒有繁體中文版。</li>'
'</ul><p>兩個人自己都是主動投資人，說的是「不是他們的人」該怎麼做。注意他們講的 S&amp;P 500 只買美國；本指南的核心是全球市值型，理由在第 '+X+' 節。巴菲特 2016 年還寫：如果要替對美國投資人貢獻最大的人立一座雕像，人選毫無疑問是 Jack Bogle，指數基金的發明者。</p></div>\n')
tgt='<div class="source-card"><h3>直接來源</h3>'; assert s.count(tgt)==1
s=s.replace(tgt, card+tgt)
links=('<a class="source-link" href="https://www.berkshirehathaway.com/letters/2017ltr.pdf" target="_blank" rel="noopener"><span>Berkshire Hathaway 2017 年股東信（官方 PDF）第 11–12 頁「The Bet」</span><span class="source-note">十年賭局逐年成績表：指數基金 125.8%／8.5%，五檔基金中的基金 2.8% 到 87.7%；Girls Inc. of Omaha 收到 2,222,279 美元</span></a>'
'<a class="source-link" href="https://www.longbets.org/362/" target="_blank" rel="noopener"><span>Long Bets 第 362 號賭局頁</span><span class="source-note">賭局條款與雙方聲明；頁面寫的金額 2,222,278 美元與股東信差 1 美元，本文以股東信為準</span></a>'
'<a class="source-link" href="https://www.berkshirehathaway.com/letters/2013ltr.pdf" target="_blank" rel="noopener"><span>Berkshire Hathaway 2013 年股東信第 20 頁</span><span class="source-note">「Put 10% of the cash in short-term government bonds and 90% in a very low-cost S&amp;P 500 index fund. (I suggest Vanguard\'s.)」</span></a>'
'<a class="source-link" href="https://www.berkshirehathaway.com/letters/2016ltr.pdf" target="_blank" rel="noopener"><span>Berkshire Hathaway 2016 年股東信第 24 頁</span><span class="source-note">「If a statue is ever erected to honor the person who has done the most for American investors, the hands-down choice should be Jack Bogle.」</span></a>'
'<a class="source-link" href="https://www.simonandschuster.com/books/Unconventional-Success/David-F-Swensen/9780743228381" target="_blank" rel="noopener"><span>David F. Swensen, Unconventional Success（Free Press, 2005；出版社頁，對程式回 403、瀏覽器可開）</span><span class="source-note">耶魯任期與基金規模（13 億→312 億美元）取自紐約時報 2021-05-06 訃聞；書的建議（低成本指數基金與 ETF、避開營利型基金公司）取自書的內容摘要，本文沒有繁中譯本可逐字對照</span></a>')
s=s.replace(tgt, tgt+links)
h=h[:i]+s+h[j:]
open(P,'w',encoding='utf-8').write(h); print('ok',len(h))
