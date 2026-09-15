# -*- coding: utf-8 -*-
"""指南 v2.1 → v3.0：專家內容意見＋研究代理來源＋八項補強。每個替換都斷言只命中一次。"""
import re, sys
P='/Users/linyenchu/Cladue Code/family-finance/guide/index.html'
h=open(P,encoding='utf-8').read()
n=0
def rep(old,new,count=1):
    global h,n
    c=h.count(old)
    assert c==count, (c, old[:70])
    h=h.replace(old,new); n+=1
def link(url,title,note):
    return f'<a class="source-link" href="{url}" target="_blank" rel="noopener"><span>{title}</span><span class="source-note">{note}</span></a>'

# ---------- 目錄 ----------
rep('<li><a href="#withdraw">用錢、退休與家庭交接</a></li>',
    '<li><a href="#withdraw">用錢、退休與家庭交接</a></li><li><a href="#lifecycle">槓桿、年齡與退休：三個常被問的問題</a></li><li><a href="#sidepaths">常見的岔路：為什麼不是核心</a></li><li><a href="#annual">每年一次的檢查表</a></li>')
rep('<li><a href="#methods">資料口徑與來源</a></li>',
    '<li><a href="#toolbox">去哪查：官方入口</a></li><li><a href="#methods">資料口徑與來源</a></li>')

# ---------- 開始前 ----------
rep('這筆錢重點是隨時拿得到，不是追求最高報酬。</li>',
    '這筆錢重點是隨時拿得到，不是追求最高報酬；放活存或定存，不放在證券戶裡等著投入。</li>')
rep('<li><strong>補上重大風險保障。</strong>先確認健保、醫療、意外、壽險或失能保障是否足以避免一次事故拖垮家庭。保險處理不能承受的大損失，投資處理長期成長；兩者工作不同。</li>',
    '<li><strong>補上重大風險保障。</strong>先確認健保、醫療、意外、壽險或失能保障是否足以避免一次事故拖垮家庭。保險處理不能承受的大損失，投資處理長期成長；兩者工作不同。三個防呆：保障用定期險買，先把保額買夠（看家裡的負債，加上家人幾年的生活費）；保費總額占收入太高，先停下來算；名字裡有「儲蓄」「還本」「投資型」的保單，先當投資商品比費用，不當保障。</li>')
rep('<span class="source-note">緊急預備金的官方說明</span></a></div>',
    '<span class="source-note">緊急預備金的官方說明</span></a>'+link('https://www.fsc.gov.tw/ch/home.jsp?id=96&amp;parentpath=0,2&amp;mcustomize=news_view.jsp&amp;dataserno=202409050002&amp;dtable=News','金管會：購買投資型保險商品注意事項（2024-09-05）','「投資相關風險是由保戶自行承擔、不保證獲利」')+'</div>'
    '<div class="story"><p><time datetime="2022-10-07">2022 年 10 月</time>，我解掉第一張儲蓄險：「趁著似乎還不錯的機會把它解掉了(好啦是有一點點擇時)」。錢從「現金備用」搬到「投資」，「雖然總資產不變，但因為投資資產增加，預期抵達可退休的年齡往前有 5 個月」。<time datetime="2023-04-02">2023 年 4 月</time>解掉最後一張，理由寫得很平：「不過我解掉儲蓄險跟這個無關，是計劃內的降低過高的備用金水位（剩一張）」。</p></div>')

# ---------- 十三個詞 ----------
rep('先認識十個詞','先認識十三個詞',3)
rep('只要懂這十個','只要懂這十三個')
rep('<dt>波動</dt><dd>價格上上下下的幅度，錢還在，只是現在賣掉會少。</dd>',
    '<dt>波動</dt><dd>價格上上下下的幅度，錢還在，只是現在賣掉會少。這句對一整群公司成立；單一家公司可能真的壞掉，第 5 節會分開講。</dd>')
rep('</dl>',
    '<dt>匯率</dt><dd>一塊美元換多少台幣。海外資產換回台幣算，會多一層漲跌；台幣升值時，帳面會縮水，市場本身沒有跌。</dd>\n'
    '<dt>總報酬</dt><dd>價格漲跌加上配息，一起算。比較任何兩檔商品都用它，不用配息率。</dd>\n'
    '<dt>內扣費用</dt><dd>基金每天從淨值裡扣掉的經理費、保管費和其他成本。你不會看到扣款，但報酬已經少了。</dd>\n</dl>')

# ---------- 第 1 節 ----------
rep('期間一換，答案就會換。</p></div>',
    '期間一換，答案就會換。</p></div>\n'
    '<div class="data-card"><h3>歷史報酬不是預期報酬</h3><p>上面的 9.8% 和 6.6% 是過去，不是預測。一群公司長期的報酬，大致等於配息率加上獲利成長，再加減「大家願意為每一塊獲利付的價格」的變化；前兩項可以估，第三項沒人知道。2025 年 12 月 Vanguard 對美國股票未來五到十年的估計，只有平均一年 4% 到 5%，比過去一百多年低。後面各節用 6% 或 7% 示範，是為了讓算術好讀，不是承諾。規劃時可以拿 4% 再算一次，看要多存多少；投入規則不因此改變，因為估得低不等於知道什麼時候跌。</p></div>')
rep('<span class="source-note">1900–2025 美國股票</span></a>',
    '<span class="source-note">1900–2025 美國股票</span></a>'+link('https://corporate.vanguard.com/content/corporatesite/us/en/corp/who-we-are/pressroom/press-release-vanguard-releases-2026-economic-and-market-outlook-121025.html','Vanguard 2026 Economic and Market Outlook 新聞稿（2025-12-10）','美股未來 5–10 年平均 4%–5%'))

# ---------- 第 2 節 ----------
rep('<p class="decision">先記下預計用錢年份與每年可投入金額。</p>',
    '<p>這一節的 7% 和 6% 都是教學假設；第 1 節說過，現在的估計更低。兩件事讓表成立：薪水漲了，投入跟著漲；每隔幾年用 4% 重算一次，看儲蓄率要不要調。</p>\n<p class="decision">先記下預計用錢年份與每年可投入金額。</p>')

# ---------- 第 3 節 ----------
rep('<p class="decision">比較產品總費用率、交易成本與稅，並確認每筆支出換到的服務。</p>',
    '<div class="data-card"><h3>台灣自己的數字</h3><p>S&amp;P 的亞洲版報告（2024 年底；封面註明機構專用）裡，台灣大型股主動基金五年有 84% 落後指數；台灣中小型股基金五年只有 44% 落後，是少數主動比較有機會的分類。這份報告只到五年、樣本只有幾十檔，不能當長期定論；方向和美國一樣：市場越大越有效率，越難靠挑選贏。</p><p>費用的粗尺：台灣掛牌的市值型指數 ETF，經理費加保管費多在 0.5% 以下（0050、006208 的官方頁在第 12 節）；主動型基金的經理費通常高出好幾倍，公開說明書第一頁就有。差一個百分點以上，就要問對方憑什麼。</p></div>\n<p class="decision">比較產品總費用率、交易成本與稅，並確認每筆支出換到的服務。</p>')
rep('<span class="source-note">避開最差日的反方檢驗</span></a></div>',
    '<span class="source-note">避開最差日的反方檢驗</span></a></div>')  # no-op guard (s8 anchor kept)
# s3 source card: find SPIVA source card in s3 and append
m=re.search(r'(id="s3">.*?)(</div>\s*<div class="story">)',h,re.S)
assert m
h=h[:m.end(1)]+link('http://web.archive.org/web/20250707210638/https://www.spglobal.com/spdji/en/documents/spiva/spiva-asia-ex%20japan-year-end-2024.pdf','SPIVA Asia ex-Japan Year-End 2024（網路檔案館存檔）','台灣大型股 5 年 84%、中小型 44%；機構專用報告')+h[m.end(1):]; n+=1

# ---------- 第 4 節 ----------
rep('分散也有代價：它幾乎不會是當年第一名。',
    '分散是分散「市場」，不是分散「代號」。0050、0056、00878 三檔疊在一起，還是只押台灣。我股票裡的台股只占一到兩成，其餘是全球；<time datetime="2025-11-05">2025 年 11 月</time>我寫下把台股在股票裡的比例從一成慢慢調到 65 歲時兩成，理由是「較高機會在台灣退休」。這是我的比例，不是建議。</p>\n<p>分散也有代價：它幾乎不會是當年第一名。')

# ---------- 第 5 節 ----------
rep('波動會在兩種情況變成真的傷害',
    '對台灣人來說還有第三種：<strong>換回台幣的波動</strong>。全球股票用美元計價，台幣升值時，海外資產換算成台幣會縮水，即使市場本身沒跌。這不是資產壞掉，是尺換了。<time datetime="2022-09-14">2022 年 9 月</time>我寫「美元升值的影響不小」；<time datetime="2025-05-07">2025 年 5 月</time>台幣急升，我寫的是「匯率不可預期也不具備長期漲跌趨勢，對於長期分批買入分批提領的大多數人來說，都會減緩匯率造成的影響不論漲跌」。所以我投入時不看匯率、當天換。要不要買匯率避險的版本是另一個選擇：避險有成本，也把「台幣會不會一直升」變成另一個要猜的題目。</p>\n'
    '<div class="data-card"><h3>還有一種跌，幾十年才回來</h3><p>第 4 節那張表裡，美國、日本、台灣曾經 25 到 34 年才回到高點。這種情況不是波動，常被叫做<strong>深風險</strong>：通膨失控、戰爭、資產被沒收、貨幣崩壞。它們少見，但一發生就是一輩子的事。台灣讀者要平靜地面對一件事：薪水、房子、勞保、健保都在台灣，投資那一塊如果也全押台灣，等於把全部雞蛋放在同一個地緣風險裡。全球分散和海外註冊的 ETF 能保住投資那一塊，保不住薪水和房子；這是投資不該再押台灣的理由，不是要你搬家。</p></div>\n'
    '<p>波動會在兩種情況變成真的傷害')
rep('1950 年以前、其他國家、稅費與實際投資產品不在這張表裡',
    '1950 年以前、其他國家、匯率、稅費與實際投資產品不在這張表裡')

# ---------- 第 6、7 節 ----------
rep('<p class="decision">一次投入或分批除了比較平均結果，也要評估隔天若跌 20% 是否仍能照計畫執行。</p>',
    '<p>一次投入之前先問一句：這筆錢五年內會不會用到？會，就不是這一節的題目，回「投資前的安全順序」分桶。分批真正的對手是期限，不是後悔。</p>\n<p class="decision">一次投入或分批除了比較平均結果，也要評估隔天若跌 20% 是否仍能照計畫執行。</p>')
rep('<p class="decision">優先確認資金是否按計畫投入、總費用，以及下跌時的賣出規則。</p>',
    '<p>所以我的答案很短：發薪日就是投入日，扣掉預期支出後投入，不再多開一個「月初還是月底」的決定。</p>\n<p class="decision">優先確認資金是否按計畫投入、總費用，以及下跌時的賣出規則。</p>')

# ---------- 第 8 節：高股息 ----------
rep('稅務口徑也不同。</p>',
    '稅務口徑也不同。</p>\n'
    '<div class="data-card"><h3>高股息 ETF：先看四件事</h3><ol class="checklist">'
    '<li><strong>它是一套挑股規則。</strong>用配息高低選公司，不是市場平均；報酬來源仍是那些公司賺的錢，只是名單不同。</li>'
    '<li><strong>收益平準金是什麼。</strong>證交所的說法：它「源自於投資人申購 ETF 時繳付之部分申購價款」，用來讓每次配息的金額穩定。金管會要求投信揭露每次配息裡股利、資本利得、收益平準金各占多少，也要標示「基金之配息來源可能為收益平準金」。看到這句，就知道有一部分是自己的本金繞一圈回來。</li>'
    '<li><strong>配息率不是報酬率。</strong>證交所寫「ETF 配息不代表完整報酬」，配出來的錢會從淨值扣掉。比較任何兩檔，用含息總報酬，不用配息率。</li>'
    '<li><strong>要現金流可以自己做。</strong>持有市值型、需要用錢時賣一小部分，效果和配息一樣，時間和金額由你決定，稅也比較好控制。</li>'
    '</ol><p>我對是否配息不太在意（<time datetime="2023-03-07">2023 年 3 月</time>）；小孩的台股部位我選不配息的版本，理由是省稅和方便小額。已經買了高股息的人不用急著賣：先算含息總報酬，新錢改買市值型，舊的照第 13 節的問題處理。</p></div>')
rep('<span class="source-note">Impact of being out of the market</span></a>',
    '<span class="source-note">Impact of being out of the market</span></a>'+link('https://www.twse.com.tw/zh/ETFortune/invest/8a8216d697fc438f019918a1dbdc04bb','臺灣證券交易所 ETF e添富：認識 ETF 收益分配（2025-08-29）','收益平準金的官方說明；「ETF 配息不代表完整報酬」'))

# ---------- 第 9 節：台灣散戶研究 ----------
rep('兩份樣本不同，不能混成同一組數字。</p>',
    '兩份樣本不同，不能混成同一組數字。</p>\n'
    '<p>台灣有自己的版本，而且樣本是全部台灣投資人。同一組作者加上兩位台灣學者，用 1995 到 1999 年台灣證交所的完整交易紀錄算出：個人投資人整體每年因為交易少賺 3.8 個百分點，損失金額相當於台灣 GDP 的 2.2%，幾乎全部來自主動追價的單子。他們再看 1992 到 2006 年的台灣當沖客：扣掉費用後能穩定賺錢的，不到 1%。兩份研究年代久遠，交易稅和工具都變了，但結論的方向沒有被推翻。</p>\n'
    '<p>要知道自己有沒有落差，每年年底把自己的年化報酬（用每筆金流和日期算）和 0050 或 VT 的含息報酬比一次；我自己就是用一張投資歷程表做這件事。</p>')
rep('<span class="source-note">較常賣贏家、留輸家</span></a></div>',
    '<span class="source-note">較常賣贏家、留輸家</span></a>'+link('https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/justhowmuchdoindividualinvestorslose_rfs_2009.pdf','Barber, Lee, Liu &amp; Odean (2009), Review of Financial Studies','台灣 1995–1999：每年少 3.8 個百分點、GDP 2.2%')+link('https://ideas.repec.org/a/eee/finmar/v18y2014icp1-24.html','Barber, Lee, Liu &amp; Odean (2014), Journal of Financial Markets','台灣當沖 1992–2006：穩定獲利者不到 1%')+'</div>')

# ---------- 第 10 節：冷卻期 ----------
rep('它們不是把人變理性，而是讓錯誤比較難發生。</p>',
    '它們不是把人變理性，而是讓錯誤比較難發生。</p>\n<p>再加兩個摩擦。一是<strong>冷卻期</strong>：任何規則的改動，寫下日期和理由之後，滿三十天才生效；想動手的念頭多半活不過三十天。二是<strong>關掉通知</strong>：券商 app 的漲跌推播、群組的即時行情都不需要，看盤的次數應該是你自己設的。</p>')

# ---------- 第 11 節 ----------
rep('五年不是自然定律，教育金、房款等不能延後的日期要更保守。</p>',
    '五年不是自然定律，教育金、房款等不能延後的日期要更保守。五年是能放股票的最短期限；十年是我自己的持有下限（第 12 節）。</p>')
rep('這是控制風險，不是預測市場。</p>',
    '這是控制風險，不是預測市場。門檻可以從「偏離設定比例五個百分點」開始；我用的是常見的 5/25 規則：偏離超過五個百分點，或超過該項比例的四分之一，才動。資產還小的時候不需要賣：只要一年投入的錢超過資產的一成，新錢就補得回來；大約到第 2 節那個「長出的錢追上投入」的年份，才需要真的賣。</p>')
rep('若用個股交易稅 0.3% 示範，稅是 240 元；ETF 稅率與其他費用另算。',
    '台灣 ETF 賣出時的交易稅是 0.1%，賣 8 萬的稅是 80 元；手續費另算。')
rep('理由只有「為求簡單」',
    '理由是「考量自己其實沒有確切的退休日期，投資心態和日常備用金也十分穩定，為求簡單將債券比例改為固定 10%」')

# ---------- 第 12 節 ----------
rep('這是給朋友的清單，不等於我全部的持股，也不是唯一答案。',
    '這是給朋友的清單，不等於我全部的持股，也不是唯一答案。清單裡我的核心是全球型；台股在我的股票裡只占一到兩成（第 4 節）。')
rep('我現在固定九比一，每個月投入時新錢先補落後的一邊，年底看一次、超過門檻才賣。代價：要賣掉漲得較多的一邊，並付交易成本。九比一只是我的比例。',
    '我現在固定九比一，每個月投入時新錢先補落後的一邊，年底看一次、超過門檻才賣。九比一的意思是：股票跌五成時，整體帳面約跌四成五，這是我接受的代價。我的一成債券是美國中期公債，不是長天期（原因在「ETF 與債券檢查表」）。代價：要賣掉漲得較多的一邊，並付交易成本。九比一只是我的比例，怎麼找自己的比例，看「槓桿、年齡與退休」那一節的兩把尺。')
rep('<li><strong>高股息 ETF</strong> 是用配息高低挑股票的規則，不是市場平均。</li>',
    '<li><strong>高股息 ETF</strong> 是用配息高低挑股票的規則，不是市場平均；第 8 節有先看的四件事。</li>')

# ---------- ETF 與債券檢查表 ----------
rep('<li><strong>折溢價：</strong>',
    '<li><strong>名稱裡的字：</strong>「主動式」不是指數投資；「正 2」「反 1」只適合單日；「高股息」「月配」是挑股和發錢的規則，不是報酬。</li>\n<li><strong>折溢價：</strong>')
rep('它的角色不是保證賺錢，也不是單純追求最高利息。</p></div>',
    '它的角色不是保證賺錢，也不是單純追求最高利息。</p>'
    '<p>防守那一塊放什麼，比比例更重要。長天期美國公債 ETF 對利率最敏感：iShares 的 20 年期以上公債 ETF（TLT）從 2020 年高點到 2023 年 10 月跌了約 48%，這是進攻的波動，不是防守。<time datetime="2026-04-09">2026 年 4 月</time>我把債券全部換成美國中期公債，理由是「債券就必須在股災時真的有用，而不只是『看起來很分散』」「那少量的債券不是拿來賺錢的，而是用於穩定以及緩衝」。資產還不大的時候，台幣定存或高利活存就能當防守：沒有利率敏感度、沒有匯率、隨時可以拿去再平衡。</p></div>')
rep('<span class="source-note">台灣大型股 ETF</span></a></div></div>',
    '<span class="source-note">台灣大型股 ETF</span></a>'+link('https://finance.yahoo.com/news/record-drawdown-long-dated-bond-143100380.html','Investing.com（Yahoo Finance 轉載，2023-09-25）：TLT 創紀錄跌幅','「自 2020 年高點下跌 48%」')+link('https://www.twse.com.tw/zh/products/securities/etf/products/li.html','臺灣證券交易所：槓桿型及反向型 ETF','「僅限於單日……不宜長期持有」')+'</div></div>')

# ---------- 費用、稅務 ----------
rep('<li><strong>台灣掛牌 ETF 的配息：</strong>屬國內股利所得，報稅二選一：併入綜合所得、按股利的 8.5% 抵減稅額（每戶上限 8 萬元），或按 28% 分開計稅。單次配息達 2 萬元時，另扣 2.11% 二代健保補充保費（以健保署當年度公告為準）。</li>',
    '<li><strong>台灣掛牌 ETF 的配息：</strong>要看所得類別，配息通知書會列出每一塊錢是哪一種。持有台灣公司的 ETF（如 0050），配息裡的股利屬國內股利所得，報稅二選一：併入綜合所得、按股利的 8.5% 抵減稅額（每戶上限 8 萬元），或按 28% 分開計稅；股利部分單次達 2 萬元時，另扣 2.11% 二代健保補充保費（以健保署當年度公告為準）。持有海外股票的台灣 ETF（如 00646、009826），配息屬海外所得，走下一條的規則。配息裡來自資本利得或收益平準金的部分，不算所得，也不計補充保費。</li>')
rep('規則會調整，申報時要查當年度資料。</li>',
    '沒達到 100 萬的年份，不用計入基本所得額。規則會調整，申報時要查當年度資料。</li>')
rep('<h3>台灣投資人常遇到的三層稅務</h3>',
    '<p class="small">複委託每筆多有以美元計的最低手續費；小額定期投入前，先把最低收費除以每次投入金額，看比例。</p>\n<h3>台灣投資人常遇到的三層稅務</h3>')
rep('<span class="source-note">股利單次給付達 2 萬元、費率 2.11%</span></a></div></div>',
    '<span class="source-note">股利單次給付達 2 萬元、費率 2.11%</span></a>'+link('https://www.twse.com.tw/zh/ETFortune/invest/8a8216d697fc438f019918a1dbdc04bb','臺灣證券交易所 ETF e添富：認識 ETF 收益分配','配息組成揭露、收益平準金')+link('https://www.deloitte.com/tw/tc/services/tax/perspectives/internal-tax-update-2507-2.html','勤業眾信：ETF 收益分配的所得類別（2025-07）','54C 股利、海外所得、資本利得、收益平準金各自的規定；以國稅局為準')+'</div></div>')

# ---------- 用錢、退休 ----------
rep('第三層才是自己投資的這一桶。先查前兩層大概有多少，再算第三桶要補多少。</p>',
    '第三層才是自己投資的這一桶。先查前兩層大概有多少，再算第三桶要補多少；勞保、勞退怎麼算，還有「每年能領多少」的研究起點，在下一節。</p>')

# ---------- 六個步驟 ----------
rep('<li><strong>決定可以承受的跌幅。</strong>股票比例越高，短期可能跌得越深。若帳面跌 20% 就會影響睡眠或生活，應先降低風險比例，不靠意志力硬撐。</li>',
    '<li><strong>決定可以承受的跌幅。</strong>股票比例越高，短期可能跌得越深。粗尺：股票歷史上曾腰斬，所以「股票比例的一半」大約是最壞可能看到的帳面跌幅；只能忍 20%，股票就不超過四成。若帳面跌 20% 就會影響睡眠或生活，應先降低風險比例，不靠意志力硬撐。</li>')
rep('<li><strong>自動化並留紀錄。</strong>',
    '<li><strong>扣款日對齊發薪日。</strong>定期定額的扣款日設在發薪日後幾天內，交割戶先放好錢；錢不會在活存裡等，也不會扣款失敗。</li>\n<li><strong>自動化並留紀錄。</strong>')
h=h.replace('<h2>第一次投資的六個步驟</h2>','<h2>第一次投資的七個步驟</h2>'); h=h.replace('<a href="#steps">第一次投資的六個步驟</a>','<a href="#steps">第一次投資的七個步驟</a>'); n+=1
assert '六個步驟' not in h, 'still 六個步驟'

# ---------- 第 13 節：加四題（27 → 31） ----------
rep('<li><strong>讓家人能接手財務</strong>',
    '<li><strong>已經買了高股息 ETF</strong>不用急著賣。先算含息總報酬，新錢改買市值型；要不要換舊的，比較換的成本與稅。<br><span class="tag">怕賠・第 8 節</span></li>\n'
    '<li><strong>手上有儲蓄險，要不要解</strong>算兩個數：現在解約拿回多少、繼續繳到期拿回多少；再和同一筆錢改投指數的保守估計比。金管會的提醒在「常見的岔路」。<br><span class="tag">怕賠・開始前</span></li>\n'
    '<li><strong>台幣升值，海外資產帳面縮水</strong>市場沒跌，是尺換了。長期分批買、分批領，會平掉大部分匯率影響；不因匯率擇時。<br><span class="tag">怕賠・第 5 節</span></li>\n'
    '<li><strong>長輩或業務推保單、主動基金</strong>用第 1 節的問題問三次：誰付錢、最壞損失多少、能不能隨時拿回；答不出來就不買。<br><span class="tag">怕輸人・第 1、3 節</span></li>\n'
    '<li><strong>讓家人能接手財務</strong>')
rep('二十七種常見情境','三十一種常見情境',2)
rep('不在這 27 題中的問題','不在這 31 題中的問題')

# ---------- 新節 1：槓桿、年齡與退休 ----------
LIFE='''<section class="part" id="lifecycle"><h2>槓桿、年齡與退休：三個常被問的問題</h2><p class="lede">研究怎麼說、我怎麼做、你可以從哪裡開始算。</p>
<p class="explain"><span class="plain-title">白話版</span><br>年輕人有很多年的薪水還沒領到，那是一大筆看不見的資產。所以理論上年輕時可以多冒險一點；但「多冒險」和「借錢冒險」是兩件事。</p>

<h3>一、年齡真的該影響比例嗎？</h3>
<p>1992 年 Bodie、Merton、Samuelson 提出「人力資本」：未來幾十年的薪水像一張大債券，年輕人這張債券最大，而且還能靠多工作補回損失，所以年輕人「可以承擔比老年人更大的投資風險」。這是「隨年齡減少股票」最正式的來源。Vanguard 的目標日期基金照這個原則設計：25 歲股票 90%，65 歲 50%，72 歲左右降到 30%；40 歲以前維持 90%，理由是那時人力資本遠大於帳戶裡的錢。</p>
<p>但 Vanguard 自己也寫：人力資本理論沒有說股票該多快、減多少，「沒有普遍接受的最佳答案」。所以「100 減年齡」這類公式只是其中一種畫法，不是定律。</p>
<div class="data-card"><h3>我為什麼把滑翔改成固定</h3><p>我原本也隨年齡調：<time datetime="2025-11-05">2025 年 11 月</time>寫的是股票內部慢慢調到 65 歲時 7：1：2（全球：因子：台股），債券 11% 預計 55 歲調到 20%。<time datetime="2026-09-04">2026 年 9 月</time>改成固定：「考量自己其實沒有確切的退休日期，投資心態和日常備用金也十分穩定，為求簡單將債券比例改為固定 10%」。這不是說滑翔錯了；是說對一個預備金充足、沒有固定退休日、每個月照規則投入的人，多一條會動的線只是多一個要維護的東西。你如果有明確的退休年份，滑翔反而合理。</p></div>
<div class="data-card"><h3>兩把粗尺，只砍錯的數字</h3><ol class="checklist"><li><strong>天花板：</strong>股票在歷史上曾經腰斬（第 5 節：任一年最差 −37%，台股 2008 年 −43%）。所以「股票比例的一半」大約是你最壞可能看到的帳面跌幅。反過來算：只能忍 20%，股票就不超過四成；能忍 45%，才談九比一。</li><li><strong>地板：</strong>五年內要用的錢不放股票（「投資前的安全順序」第 5 項）。</li></ol><p>兩把尺之間都是可以的答案；退休之後的方向，看下面第三題。</p></div>

<h3>二、年輕時借錢投資，有沒有道理？</h3>
<p>有一派學者說有。Ayres 和 Nalebuff 2008 年的論文主張年輕時用 2:1 融資買股、年紀大了再降，用 1871 年起的美國資料回測，退休財富比目標日期基金高 90%。這個想法後來寫成一本書，你一定會聽到，所以我把它寫出來。</p>
<p>他們自己寫下的前提和代價，要一起看：</p>
<ul>
<li>「這套策略要有效，前提是能用低成本借到錢。」2006 年小額融資利率超過 9.5%，而他們自己寫，付 10% 的融資利率去買預期報酬 8% 的股票沒有道理。</li>
<li>1929 年 10 月，2:1 全槓桿的年輕人單月虧 53%；94 個世代裡有 22 個，一生中至少有一個月虧超過 40%。</li>
<li>股票溢酬只是一條歷史路徑，「投資人不該指望它維持在歷史水準」。</li>
</ul>
<p>反對的聲音也很清楚。Samuelson 2008 年說，讀到「年輕時大舉借錢買股」這種主張，「我的眉毛就往上挑」，他寫過 27 篇文章反駁。法學期刊的書評結論是：這套做法對一般投資人「太複雜」；「只要股票報酬低於借款成本，整個計畫就跟著失敗」；把未來薪水當債券去借錢，「在有相當違約機會時是危險的」。</p>
<div class="data-card"><h3>台灣三種常見的借法，代價各是什麼</h3><ul>
<li><strong>正 2 ETF：</strong>證交所的官方警語是「追求之正、反向倍數報酬率僅限於單日，每日複利計算下，長期報酬率會偏離原型指數之正、反向倍數表現，不宜長期持有」；投信投顧公會寫「僅適合短期交易，不適合長期持有」。它不是「兩倍的長期投資」。</li>
<li><strong>融資：</strong>整戶擔保維持率低於 130% 時，券商通知後兩個營業日內要補錢，沒補就從次一營業日起處分擔保品。跌到那個程度，是券商替你賣在低點，不是你決定。</li>
<li><strong>信貸：</strong>臺灣銀行無擔保個人信貸的總費用年百分率 6.69%（2026 年 8 月基準）；一家民營銀行公告的範圍是 4.13% 到 16.29%。第 1 節說過，美股未來的估計只有 4% 到 5%。借的錢有固定利息，投資報酬沒有。</li>
</ul></div>
<p>我的做法：房貸以外沒有槓桿（第 13 節）。理由不是研究說不行，是我的規則卡上寫著跌 30% 時照常投入，而槓桿會在那一天讓「照常」變成不可能。</p>

<h3>三、退休要存多少、每年能領多少？</h3>
<p>三個常被引用的起點，全部是美國資料、30 年退休期：</p>
<div class="table-wrap"><table class="compact"><thead><tr><th>來源</th><th>第一年提領率</th><th>前提</th></tr></thead><tbody>
<tr><td>Bengen 1994</td><td>4%（3% 是「絕對安全」）</td><td>股票 50%–75% 加中期公債；之後每年隨通膨調整；歷史上沒有一次在 33 年內用完</td></tr>
<tr><td>Trinity 1998</td><td>4%</td><td>75/25 股債、通膨調整，30 年成功率 98%；「多數退休者至少配 50% 股票」</td></tr>
<tr><td>Morningstar 2025</td><td>3.9%</td><td>股票 30%–50%、90% 成功率；改成彈性提領可到 5.7%</td></tr>
</tbody></table></div>
<p>把它翻成累積目標：一年花費除以 4% 是 25 倍，除以 3% 是 33 倍。我自己的目標用 2.5% 到 3%（<time datetime="2024-11-08">2024 年 11 月</time>「提領率 3 -&gt; 2.5%」），比研究保守，因為我不想每年重算。退休後的股債比，三份研究都落在股票三成到七成五之間，沒有一份是九比一：累積期和提領期是兩張不同的規則卡。</p>
<div class="data-card"><h3>為什麼提領期怕一開始就跌</h3><p>Vanguard 的例子：兩個人各帶 50 萬美元退休，都是 50/50，都每年領 2.5 萬再隨通膨調。1973 年退休的人，35 年平均實質報酬 5.23%，23 年就把錢花光；1974 年退休的人平均 5.1%，卻幾乎整段都還留著 30 萬。差別只在頭幾年的下跌發生在提領之前還是之後。「退休初期的下跌會把暫時損失變成永久損失，因為提領減少了能參與之後反彈的資產。」</p></div>
<div class="data-card"><h3>勞保和勞退先算，再算第三桶</h3><ul>
<li><strong>勞保老年年金：</strong>平均月投保薪資 × 年資 × 1.55%（另一式擇優）；平均月投保薪資是加保期間最高 60 個月的平均。2026 年起請領年齡 65 歲，年資要滿 15 年；提前領每年減 4%、最多減 20%，延後領每年加 4%、最多加 20%。</li>
<li><strong>勞退新制：</strong>雇主每月至少提工資的 6% 進你的專戶，專戶是你的；你可以再自提最多 6%，自提部分不計入當年薪資所得課稅。基金收益保證不低於兩年期定存利率，不足由國庫補。</li>
<li><strong>去算：</strong>勞保局有一頁整合試算，同時算勞保一次金、年金和勞退月退（連結在「去哪查」）。</li>
</ul></div>
<div class="source-card"><h3>直接來源</h3><div class="sources-grid">'''+''.join([
link('https://www.nber.org/papers/w3954','Bodie, Merton &amp; Samuelson (1992)','人力資本；年輕人可承擔較大投資風險'),
link('https://workplace.vanguard.com/content/dam/inst/iig-transformation/insights/pdf/2025/231657-02_TDF_PTDF_OTH-TRIGT-Research.pdf','Vanguard（2025-05）：目標日期基金滑翔軌道','25 歲 90%、65 歲 50%、72 歲 30%'),
link('https://workplace.vanguard.com/content/dam/inst/iig-transformation/insights/pdf/2022/Vanguards-approach-to-target-date-funds.pdf','Vanguard（2019）：目標日期基金設計','40 歲前 90%；「沒有普遍接受的最佳答案」'),
link('https://www.nber.org/papers/w14094','Ayres &amp; Nalebuff (2008), NBER WP 14094','生命週期槓桿；前提與 1929 年單月 −53%'),
link('https://lawreview.vermontlaw.edu/wp-content/uploads/2012/02/14-Vars-Book-2-Vol.-36.pdf','Vars (2011), Vermont Law Review 書評','「太複雜」「報酬低於借款成本就失敗」'),
link('https://rpc.cfainstitute.org/sites/default/files/-/media/documents/book/rf-publication/2009/rfv2009n4.pdf','CFA Institute Research Foundation (2009)','Samuelson 2008 開場：「眉毛往上挑」，第 2 頁'),
link('https://www.twse.com.tw/zh/products/securities/etf/products/li.html','臺灣證券交易所：槓桿型及反向型 ETF','官方警語'),
link('https://www.sitca.org.tw/ROC/SITCA_ETF/etf-hub-product.html','投信投顧公會 ETF 專區','「僅適合短期交易，不適合長期持有」'),
link('https://twse-regulation.twse.com.tw/m/LawContent.aspx?FID=FL007121','證券商辦理有價證券買賣融資融券業務操作辦法','第 54、55 條：130%、兩個營業日'),
link('https://www.bot.com.tw/Images/File/GetFileId/bc518e56-3341-4de4-ba88-65b0d74df77c','臺灣銀行：消費者貸款適用利率一覽表','無擔保個人信貸總費用年百分率 6.69%'),
link('https://www.ctbcbank.com/content/dam/minisite/long/loan/leader/loan1.html','中國信託：分期型信用貸款','總費用年百分率 4.13%～16.29%'),
link('https://robberger.com/wp-content/uploads/2024/01/retailinvestor.org_pdf_Bengen1.pdf','Bengen (1994), Journal of Financial Planning','4%、3%「絕對安全」、股票 50%–75%'),
link('https://www.aaii.com/journal/199802/feature.pdf','Cooley, Hubbard &amp; Walz (1998), AAII Journal（Trinity）','75/25、4%、30 年成功率 98%；PDF 可能需在瀏覽器開啟'),
link('https://static.twentyoverten.com/5b5730126af0247efe4f2066/zT8sbuFanVR/Morningstar-2025-State-of-Retirement-Income.pdf','Morningstar：State of Retirement Income 2025（鏡像）','3.9%、股票 30%–50%、彈性提領 5.7%'),
link('https://www.vanguard.co.uk/content/dam/intl/europe/documents/en/whitepapers/safeguarding-retirement-bear-market.pdf','Vanguard Research (2020)：Safeguarding retirement in a bear market','1973 與 1974 年退休的例子'),
link('https://corporate.vanguard.com/content/dam/corp/research/pdf/vanguard_principles_retirement_income.pdf','Vanguard (2026)：Principles for Retirement Income','報酬順序風險，第 10 頁'),
link('https://www.bli.gov.tw/0019825.html','勞保局：老年年金給付標準','1.55%、60 個月、±4%'),
link('https://www.bli.gov.tw/0004856.html','勞保局：老年給付請領資格','115 年起 65 歲、年資 15 年'),
link('https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=N0030020','勞工退休金條例','第 14 條 6%＋自提 6%；第 23 條保證收益'),
])+'''</div></div>
<p class="decision">先用勞保局試算查前兩層，再用 25 到 33 倍算第三桶；槓桿的答案先寫在規則卡上，不在行情好的那天決定。</p><a class="back" href="#toc">回目錄</a></section>

'''

# ---------- 新節 2：常見的岔路 ----------
SIDE='''<section class="part" id="sidepaths"><h2>常見的岔路：為什麼不是核心</h2><p class="lede">每一條你都會遇到；每一條只講一句「為什麼不是核心」。</p>
<p class="explain"><span class="plain-title">白話版</span><br>去一個地方，主要的路只有一條；旁邊很多小路看起來近，走進去才發現通到別的地方。</p>
<ul>
<li><strong>個股：</strong>單一公司可能真的壞掉（第 5 節）；第 9 節的台灣研究裡，散戶整體因為交易每年少賺 3.8 個百分點。想買，先用第 1 節的問題問它一次。</li>
<li><strong>主題型 ETF（AI、半導體、電動車）：</strong>名字是主題，裡面常常是同一群公司；第 9 節的研究裡，產業型基金的行為落差最大。</li>
<li><strong>正 2、反 1：</strong>官方寫「不宜長期持有」；它是單日工具（上一節）。</li>
<li><strong>當沖：</strong>台灣 1992 到 2006 年的資料，扣掉費用後能穩定賺錢的當沖客不到 1%（第 9 節）。</li>
<li><strong>虛擬資產：</strong>金管會的說法是「屬新興且複雜性商品，無漲跌幅之限制容易暴漲暴跌，相關資訊較不透明交易風險高」。用第 1 節的問題問：誰付錢？答案是下一個人。</li>
<li><strong>投資型保單、儲蓄險：</strong>金管會提醒「投資相關風險是由保戶自行承擔、不保證獲利」「切勿僅因預期投資報酬率可能優於銀行存款利率就盲目決定投保」。保障用保險買，投資用投資買；混在一起的商品要拆開比費用。</li>
<li><strong>高股息、月配：</strong>第 8 節的四件事。</li>
<li><strong>單一國家、單一產業的 ETF：</strong>0050 也是其中一種。它分散的是台灣，不是分散那一家占 57% 的公司（第 12 節）。</li>
</ul>
<p>這些不是「不能碰」。規則卡上可以留一小格「玩的錢」，金額寫死、虧光不影響計畫；<time datetime="2025-11-02">2025 年 11 月</time>我回想賭日圓的群友，說的是「賭可以，但這就不在投資範疇了」。它不能是核心，也不能拿核心的錢補它。</p>
<div class="source-card"><h3>直接來源</h3><div class="sources-grid">'''+''.join([
link('https://www.fsc.gov.tw/ch/home.jsp?id=96&amp;parentpath=0,2&amp;mcustomize=news_view.jsp&amp;dataserno=202406250003&amp;dtable=News','金管會：虛擬資產交易風險（2024-06-25）','「無漲跌幅之限制容易暴漲暴跌」'),
link('https://www.fsc.gov.tw/ch/home.jsp?id=96&amp;parentpath=0,2&amp;mcustomize=news_view.jsp&amp;dataserno=202409050002&amp;dtable=News','金管會：購買投資型保險商品注意事項（2024-09-05）','「不保證獲利」「切勿盲目決定投保」'),
link('https://www.twse.com.tw/zh/products/securities/etf/products/li.html','臺灣證券交易所：槓桿型及反向型 ETF','「不宜長期持有」'),
link('https://ideas.repec.org/a/eee/finmar/v18y2014icp1-24.html','Barber, Lee, Liu &amp; Odean (2014)','台灣當沖：不到 1%'),
])+'''</div></div>
<p class="decision">遇到任何新商品，先問第 1 節的三個問題：誰付錢、最壞損失多少、能不能隨時拿回。</p><a class="back" href="#toc">回目錄</a></section>

'''

# ---------- 新節 3：每年一次的檢查表 ----------
ANNUAL='''<section class="part" id="annual"><h2>每年一次的檢查表</h2><p class="lede">一年一次，一小時，其他時間不用看。</p>
<p class="explain"><span class="plain-title">白話版</span><br>像車子的年度保養：不是每天檢查引擎，而是一年一次把該看的看完。</p>
<ol class="checklist">
<li><strong>儲蓄率：</strong>今年投入的錢除以收入，和去年比。薪水漲了，投入有沒有跟著漲？</li>
<li><strong>預備金：</strong>還夠不夠必要支出的三到六個月？家裡狀況變了（多一個小孩、換工作、變單薪），要重算。</li>
<li><strong>股債比例：</strong>和規則卡上的設定差多少？超過門檻才動，新錢先補少的那邊（第 11 節）。</li>
<li><strong>費用：</strong>持有的每一檔，今年的總費用率是多少？有沒有同一個指數、更便宜的選擇？要換，先算換的成本（第 13 節）。</li>
<li><strong>保單：</strong>保額還夠不夠負債加家人幾年的生活費？名字裡帶「儲蓄」「還本」的保單，要不要重新算？</li>
<li><strong>自己的報酬：</strong>用金流和日期算今年的年化，和 0050 或 VT 的含息報酬比一次（第 9 節）。差很多，先找原因，不先換商品。</li>
<li><strong>家庭一頁表：</strong>帳戶、保單、貸款、聯絡人、文件位置有沒有變（「用錢、退休與家庭交接」）。</li>
<li><strong>規則卡：</strong>有沒有哪一格今年被證明寫錯了？要改，寫日期和理由，滿三十天生效（第 10 節）。</li>
<li><strong>稅：</strong>今年配息的所得類別、海外所得有沒有接近 100 萬（「費用、稅務與帳戶安全」）。</li>
<li><strong>帳戶安全：</strong>密碼、多因素驗證、聯絡資料，順便核對一次持股與現金。</li>
</ol>
<p>我自己的固定動作：每個月投入時順便補落後的那一邊，年底看一次再平衡；改規則一律記下來，<time datetime="2025-11-05">2025 年 11 月</time>寫的是「為了避免隨意變動策略，有任何變更我都會記錄在投資歷程（XIRR）表格上」。</p>
<p class="decision">把這十項印出來，訂一個日期（例如每年一月的發薪日），做完打勾。</p><a class="back" href="#toc">回目錄</a></section>

'''

# ---------- 新節 4：去哪查 ----------
def box(title, items):
    return '<div class="source-card"><h3>'+title+'</h3><div class="sources-grid">'+''.join(link(*i) for i in items)+'</div></div>\n'
TOOL='''<section class="part" id="toolbox"><h2>去哪查：官方入口</h2><p class="lede">本文多處說「以公開說明書為準」「查官方公告」，這一頁就是那些地方。</p>
'''+box('商品與市場',[
('https://www.twse.com.tw/zh/products/securities/etf/overview.html','臺灣證券交易所：ETF 專區','上市 ETF 名單、規模、折溢價'),
('https://www.twse.com.tw/zh/ETFortune/','證交所 ETF e添富','收益平準金等投資觀念'),
('https://www.sitca.org.tw/ROC/SITCA_ETF/etf-hub-product.html','投信投顧公會：ETF 專區','各類 ETF 說明與警語'),
('https://www.fundclear.com.tw/','基金資訊觀測站','公開說明書、費用率'),
('https://mops.twse.com.tw/','公開資訊觀測站','基金與公司的法定公告'),
('https://www.tdcc.com.tw/','集保結算所','集保 e 存摺、股權查詢'),
])+box('退休與保險',[
('https://www.bli.gov.tw/0109187.html','勞保局：勞保老年給付及勞退試算整合','一頁算勞保一次金、年金、勞退月退'),
('https://www.bli.gov.tw/0012942.html','勞保局：勞退個人專戶查詢及試算','看自己專戶累積多少'),
('https://www.bli.gov.tw/0019825.html','勞保局：老年年金給付標準','公式與加減成'),
('https://www.ib.gov.tw/','金管會保險局','保險商品規範與申訴'),
])+box('稅與健保',[
('https://www.etax.nat.gov.tw/','財政部稅務入口網','綜所稅、股利二選一、海外所得'),
('https://www.mof.gov.tw/singlehtml/384fb3077bb349ea973e7fc6f13b6974?cntId=2066d90cd88547e9954a79490776c88b','財政部：海外所得與最低稅負','100 萬、750 萬、20%'),
('https://www.nhi.gov.tw/ch/cp-1719-0d5e5-2540-1.html','健保署：補充保險費扣取項目','股利單次 2 萬、2.11%'),
])+box('安全、申訴與利率',[
('https://www.fsc.gov.tw/','金管會','合法業者查詢、新聞稿'),
('https://www.sfb.gov.tw/','金管會證期局','投資詐騙提醒'),
('https://165.npa.gov.tw/','165 全民防騙網','查詐騙、報案'),
('https://www.cbc.gov.tw/tw/np-371-1.html','中央銀行：五大銀行平均存款利率','定存利率的官方數字'),
])+'''<p class="small">連結檢查日期：2026-09-11。政府網站會改版，找不到時用該站的搜尋，或搜尋「機構名稱＋頁面名稱」。</p>
<p class="decision">看到本文說「查官方」的地方，回這一頁點進去；不從群組或私訊的連結進入。</p><a class="back" href="#toc">回目錄</a></section>

'''

rep('<section class="part" id="s13">', LIFE+SIDE+ANNUAL+'<section class="part" id="s13">')
rep('<section class="part" id="methods">', TOOL+'<section class="part" id="methods">')

# ---------- 資料口徑 ----------
rep('每一則都有那一天的粉專貼文可以查。</li></ul>',
    '每一則都有那一天的粉專貼文可以查。</li>\n<li>本文所有試算都是名目數字、以台幣或美元各自計算，不含匯率變動；換回台幣的結果會不同。</li>\n<li>「槓桿、年齡與退休」引用的提領率研究全部是美國資料與 30 年期；勞保、勞退依 2026 年 9 月的法規與勞保局公告。</li></ul>')
rep('主動基金比較取自 SPIVA U.S. Year-End 2025；結果只代表報告中的美國基金分類與期間。</li>',
    '主動基金比較取自 SPIVA U.S. Year-End 2025；台灣數字取自 SPIVA Asia ex-Japan Year-End 2024（機構專用報告，只到五年）。結果只代表報告中的分類與期間。</li>')

open(P,'w',encoding='utf-8').write(h)
print('replacements:',n,'bytes:',len(h.encode()))
