# -*- coding: utf-8 -*-
"""v4.8 → v4.9：十歲讀者回饋。詞彙表擴到 38 個詞（分「先懂這十三個」與「遇到再查」）、節名改「先認識這些詞」；
名詞石板藍點狀底線連到詞彙表（每節第一次）；重點句淡藍底 mark.key；大人段落加「先跳過也可以」標籤；白話版與句子修正。一次性腳本。"""
import re, sys, html as H
P='/Users/linyenchu/Cladue Code/family-finance/guide/index.html'
h=open(P,encoding='utf-8').read()
X=lambda n:'<a class="xref" href="#s%d">%d</a>'%(n,n)
def rep(a,b,c=1):
    global h
    if h.count(a)!=c: print('MISMATCH',h.count(a),a[:60]); sys.exit(1)
    h=h.replace(a,b)

# ── 1. 節名 ──
rep('先認識十三個詞','先認識這些詞',5)
rep('<p class="decision">讀到看不懂的詞先回這裡；只要懂這十三個，後面全部讀得完。</p>','<p class="decision">讀到看不懂的詞先回這裡；前十三個懂了就能往下讀，後面的遇到再查。</p>')
rep('<p class="lede">前後各節都會用到，看不懂的時候回來查。</p>','<p class="lede">前後各節都會用到，看不懂的時候回來查。</p>\n<p class="explain"><span class="plain-title">白話版</span><br>像遊戲說明書前面的角色介紹：先認識名字，後面出場時才知道是誰。前十三個是主角，後面的是配角，出場再認就好。</p>')

# ── 2. 詞彙表：舊條目加 id，口徑獨立，加第二組 ──
ids={'股票、股東':'g-stock','債券':'g-bond','定存':'g-td','基金、ETF':'g-etf','指數、指數投資':'g-index','券商、複委託':'g-broker','年化、名目、實質、口徑':'g-annual','含息、配息':'g-div','波動':'g-vol','再平衡':'g-rebal','匯率':'g-fx','總報酬':'g-tr','內扣費用':'g-fee'}
for k,v in ids.items():
    rep('<dt>%s</dt>'%k,'<dt id="%s">%s</dt>'%(v,k))
rep('<dt id="g-annual">年化、名目、實質、口徑</dt><dd>年化是「平均一年長多少」；名目是帳面數字；實質是扣掉物價上漲之後真的多出來的部分。「口徑」就是一個數字的算法和範圍：哪段期間、哪種幣別、有沒有含息。</dd>',
    '<dt id="g-annual">年化、名目、實質</dt><dd>年化是「平均一年長多少」；名目是帳面數字；實質是扣掉物價上漲之後真的多出來的部分。</dd>\n<dt id="g-scope">口徑</dt><dd>一個數字的算法和範圍：哪段期間、哪種幣別、有沒有含息、有沒有扣費。兩個口徑不同的數字，不能直接比大小。</dd>')
rep('<h2>先認識這些詞</h2>','<h2>先認識這些詞</h2>')
h=h.replace('<dl class="glossary">','<h3>先懂這十三個</h3><dl class="glossary">',1)
NEW=[('g-nav','淨值','基金每一單位真正值多少錢：把基金持有的東西全部算成今天的價格，除以單位數。ETF 的市價會在淨值上下晃。'),
('g-hc','人力資本、財務資本','人力資本是你未來還能賺的薪水；財務資本是已經存下來、會自己生錢的資產。投資做的事，是把前者換成後者。'),
('g-exposure','曝險','會被某一件事影響的程度。薪水、房子、投資都押在台灣，就是對台灣的曝險很高。'),
('g-factor','因子、因子溢酬','因子是照某種特徵（例如公司小、價格便宜、最近在漲）挑股票的規則；溢酬是這樣挑在歷史上比市場多賺的那一段。多不多、以後還有沒有，沒有人保證。'),
('g-core','核心、衛星','核心是占大部分、照規則長期持有的那一塊；衛星是旁邊一小塊、有上限的嘗試。本文的核心是全球市值型。'),
('g-ratio','股債比、八二、六四','股票和防守資產（債券、定存）的比例。八二是八成股票、兩成防守；六四是六成對四成。'),
('g-card','規則卡','第 '+X(11)+' 節那張紙：寫下這筆錢的用途、多久投一次、跌了怎麼辦、什麼情況才賣。寫給平靜時的自己，也寫給家人。'),
('g-yield','殖利率','一年配的息除以現在的價格。它只講配多少，不講賺多少。'),
('g-ig','投資等級債','被信用評等公司評為還錢能力較好的債券；相對的是高收益債（也叫垃圾債），利息高，倒帳的機率也高。'),
('g-hedge','匯率避險','用額外的成本，把某一種貨幣的漲跌鎖住；先看它鎖的是哪一種貨幣，鎖成美元對台灣人沒有幫助。'),
('g-equal','收益平準金','拿新進場的人交進來的一部分本金去墊配息；配息裡的這一塊是投資人自己的錢繞一圈回來，不是賺到的。'),
('g-te','追蹤誤差','基金的報酬和它追蹤的指數之間的差距，差得越少越好。'),
('g-prem','折溢價','ETF 的市價和淨值的差。市價高於淨值叫溢價，等於用比裡面東西更貴的價格買；低於叫折價。'),
('g-dur','存續期間','債券價格對利率變動的敏感度；到期越久，利率一動價格晃得越大。'),
('g-domicile','註冊地、掛牌地','註冊地是基金設在哪個國家，決定扣稅和適用的法律；掛牌地是在哪個交易所買賣。'),
('g-stop','停利','漲了先賣掉一部分，把帳面獲利換成現金；賣了之後要不要買回，是另一個決定。'),
('g-daytrade','當沖','同一天買進又賣掉，賺當天的價差。'),
('g-settle','交割、T+2','成交後真正付錢、拿到股票的動作。台灣是成交日算起第二個營業日完成，所以叫 T+2；交割戶要先有錢。'),
('g-order','限價單、市價單','限價單是「最多用這個價買」；市價單是「照現在能成交的價馬上買」。定期定額由券商代下單，不用選。'),
('g-nhi','二代健保補充保費','健保在一般保費之外，對股利、利息、獎金這幾類收入另外收的一小筆保費，單次達門檻才扣。'),
('g-bracket','級距','所得稅把全年所得切成幾段，越高的那一段稅率越高；你落在哪一段，就叫級距。'),
('g-margin','融資、維持率','融資是向券商借錢買股票；維持率是股票市值除以借款，跌到門檻以下券商會要你補錢，不補就替你賣。'),
('g-xirr','XIRR','試算表的一個函式，把每一筆進出的金額和日期都算進去，算出「平均一年長多少」；本文說的「自己的年化」都用它。'),
('g-swr','提領率','退休後每年從資產拿出來花的比例；4% 的意思是資產一百萬，一年領四萬。')]
dl2='<h3>遇到再查</h3><dl class="glossary">\n'+'\n'.join('<dt id="%s">%s</dt><dd>%s</dd>'%(i,t,d) for i,t,d in NEW)+'\n</dl>\n'
rep('</dl>\n<p class="decision">讀到看不懂的詞先回這裡','</dl>\n'+dl2+'<p class="decision">讀到看不懂的詞先回這裡')

# ── 3. 白話版修正 ──
rep('複利像雪球。剛開始雪球很小，滾很久也不明顯；後來雪球變大，同樣滾一圈，就會多黏很多雪。但先想另一件事：你會滾雪球的那雙手，不會永遠有力氣。','複利像雪球。剛開始雪球很小，滾很久也不明顯；後來雪球變大，同樣滾一圈，就會多黏很多雪。但雪球要有人推：推雪球的是你的薪水，這雙手不會永遠有力氣，所以要趁有力氣的時候把雪球滾大。')
rep('你不只要猜「什麼時候開始跌」，還要猜「跌到哪裡會停」。等到大家都知道低點時，低點通常已經過了。','像在等公車，想等最空的那一班：你得猜下一班會不會更空，而等的時候車一班一班開走。等跌也一樣，你不只要猜「什麼時候開始跌」，還要猜「跌到哪裡會停」；等到大家都知道低點時，低點通常已經過了。')
rep('如果有一個人每月都買在最便宜的那天，另一個人每月都買在最貴的那天，二十三年後兩人的結果會有差，但差距比一般人想的小，而且現實中沒有人能永遠買在最便宜。','像去菜市場：有人每次都買到當月最便宜的那天，有人每次都買到最貴的那天，二十三年後兩人差得比想像中少；而且沒有人能永遠買到最便宜。')
rep('把球從左手換到右手，球不會變多。配息是把一部分價值發到你的帳戶，賣出是把一部分資產換成現金，錢只是換了位置；兩者都要把帳戶裡的現金和剩下的資產加起來一起看。','把球從左手換到右手，球不會變多。公司發錢給你（配息）或你自己賣掉一點（賣出），都只是把錢從一個口袋換到另一個口袋；要看的是兩個口袋加起來還有多少。')
rep('第 '+X(11)+' 節那張規則卡的工作，是讓保全先看說明書。</p>','第 '+X(11)+' 節那張規則卡，就是你事先寫給保全的說明書：先照上面做，不要臨時反應。</p>')
rep('前面十一節是零件，這一節是組裝順序。零件怎麼組，照 Vanguard 一份給一般投資人的原則文件：目標、平衡、成本、紀律，四樣都是你控制得了的事。','前面十一節是零件，這一節是組裝順序：先寫目標，再定比例，再壓低費用，最後照表做。四樣都是你控制得了的事。')
rep('<div class="data-card"><h3>四個原則，各對應前面的節</h3><ol class="checklist">','<div class="data-card"><h3>四個原則，各對應前面的節</h3><p>這四個原則出自 Vanguard 給一般投資人的原則文件（來源在本節末）。</p><ol class="checklist">')
rep('退休後同時遇到下跌與提領，也會讓資產比較難恢復。</p>','退休後同時遇到下跌與提領，也會讓資產比較難恢復。後半段的家庭一頁表，是給接手的人看的地圖：你不在時，家人照圖就找得到水桶在哪、怎麼拿。</p>')
rep('所以理論上年輕時可以多冒險一點；但「多冒險」和「借錢冒險」是兩件事。','所以理論上年輕時可以多冒險一點；但「多冒險」和「借錢冒險」（槓桿：借錢來投資，賺賠都放大）是兩件事。')
rep('<p class="lede">本文多處說「以公開說明書為準」「查官方公告」，這一頁就是那些地方；頁尾另有書單。</p>','<p class="lede">本文多處說「以公開說明書為準」「查官方公告」，這一頁就是那些地方；頁尾另有書單。</p>\n<p class="explain"><span class="plain-title">白話版</span><br>像電話簿：本文說「去查官方」的時候，號碼都在這一頁。</p>')

# ── 4. 句子修正 ──
rep('年底收正的剛好也是 18 年，這只是巧合，不是同一批年份。','年底收正的也有 18 年。意思是：中途跌一成很平常，也不代表那一年會虧。')
rep('（八二配置、股票漲五成，約是資產的 10%；六四、股票漲三成，約是 12%）','（八二配置（八成股票、兩成防守）、股票漲五成，約是資產的 10%；六四（六成股票）、股票漲三成，約是 12%）')
rep('兩個取比較小的那個，到了才動','先把四分之一換算成幾個百分點，再和五個百分點比，取比較小的那個，到了才動')
rep('（3.25 除以 27.44）','（台灣的 3.25% 是新興市場那一塊的 27.44%，所以整塊是 3.25 除以 0.2744，約 12%）')
rep('（這些是專業工具，一般人借不到那種利率；看不懂沒關係，重點在後面「台灣三種常見的借法」）','（這是他們用的工具，一般人用不到，也借不到那種利率；台灣人借得到的方式在下面）')
rep('叫資金加權報酬。','叫資金加權報酬。名字不用記，只要記得一個是基金的成績，一個是你的成績。')

# ── 5. 「先跳過也可以」標籤 ──
L=lambda t:'<span class="later">%s</span>'%t
rep('<strong>用小金額完成第一次。</strong>',L('先跳過也可以，第一次下單前再回來看')+'<strong>用小金額完成第一次。</strong>')
rep('<h3>成交不等於交割完成</h3>','<h3>成交不等於交割完成</h3>'+L('先跳過也可以，第一次下單前再回來看'))
rep('<h3>台灣投資人常遇到的四層稅務</h3>','<h3>台灣投資人常遇到的四層稅務</h3>'+L('先跳過也可以，第一次報稅前再回來看'))
rep('<h3>選 ETF 時逐項查看</h3>','<h3>選 ETF 時逐項查看</h3>'+L('先跳過也可以，挑產品那天再逐項看'))
rep('<h3>二、年輕時借錢投資，有沒有道理？</h3>','<h3>二、年輕時借錢投資，有沒有道理？</h3>'+L('先跳過也可以，想借錢投資那天再回來看'))

# ── 6. 重點句 mark.key ──
KEY=['它是一套寫得下來的步驟，不是一種本事。','上面的 9.8% 和 6.6% 是過去，不是預測。','越早換，交叉點越早。','簡單不是妥協，是把所有會扣分的動作拿掉以後剩下的東西。','核心放全球市值型，台股大盤可以是裡面的一塊。','波動會在兩種情況變成真的傷害：第一，錢很快要用，被迫低價賣；第二，比例超過心理承受度，自己在低點賣。','有錢可投、計畫也允許的時候，就照規則投進去。','挑一個固定的日子就好。','配不配息本身不是重點，總報酬才是','熱門時加碼、下跌時退出，會讓投資人的錢放在較差的時段。','它們不是把人變理性，而是讓錯誤比較難發生。','最不用臨場判斷的答案是三格都寫「照常投入，新錢照規則補落後的那一邊」。','表裡故意不放商品代號：代號會變，原則不會。','對方改變不了你的卡，你也不必改變對方。','買進前先讓交割帳戶有足夠資金，避免違約交割','防守那一塊放什麼，比放多少更重要。','市值型配置加一張規則卡，是最容易交接的組合','借的錢有固定利息，投資報酬沒有。','這一格不能變成核心，也不能拿核心的錢去補。','差很多，先找原因，不先換商品。']
for k in KEY: rep(k,'<mark class="key">'+k+'</mark>')

# ── 7. 名詞連結（每節第一次；跳過連結、標題、黃框、標籤、svg、strong、time、mark）──
TERMS=[('市值型','g-index'),('內扣費用','g-fee'),('淨值','g-nav'),('口徑','g-scope'),('含息','g-div'),('除息','g-div'),('配息','g-div'),('複委託','g-broker'),('名目','g-annual'),('實質','g-annual'),('年化','g-annual'),('人力資本','g-hc'),('財務資本','g-hc'),('曝險','g-exposure'),('因子','g-factor'),('衛星','g-core'),('股債比','g-ratio'),('八二','g-ratio'),('六四','g-ratio'),('規則卡','g-card'),('殖利率','g-yield'),('投資等級','g-ig'),('匯率避險','g-hedge'),('收益平準金','g-equal'),('追蹤誤差','g-te'),('折溢價','g-prem'),('存續期間','g-dur'),('註冊地','g-domicile'),('掛牌','g-domicile'),('停利','g-stop'),('當沖','g-daytrade'),('交割','g-settle'),('限價單','g-order'),('市價單','g-order'),('補充保費','g-nhi'),('級距','g-bracket'),('融資','g-margin'),('維持率','g-margin'),('XIRR','g-xirr'),('提領率','g-swr'),('再平衡','g-rebal'),('總報酬','g-tr')]
# 短解釋：取詞彙表 dd 第一句
TIP={}
for gid in set(g for _,g in TERMS):
    m=re.search(r'<dt id="%s">[^<]*</dt><dd>(.*?)</dd>'%gid,h,re.S)
    t=re.sub(r'<[^>]+>','',m.group(1)); TIP[gid]=re.split(r'[。；]',t)[0]+'。'
SKIP_OPEN=re.compile(r'<(a|h2|h3|h4|nav|svg|strong|time|mark|span class="tag"|span class="chart-title"|div class="story"|details class="orig"|title|figure)\b')
def linkify(sec):
    used=set(); out=[]; pos=0; depth={}; stack=[]
    tok=re.compile(r'<[^>]+>')
    for m in tok.finditer(sec):
        text=sec[pos:m.start()]
        if text and not stack:
            spans=[]
            for term,gid in TERMS:
                if term in used or gid in used: continue
                k=text.find(term)
                if k<0: continue
                if any(not (k+len(term)<=a or k>=b) for a,b,_,_ in spans): continue
                spans.append((k,k+len(term),term,gid)); used.add(term); used.add(gid)
            if spans:
                spans.sort(); out2=[]; last=0
                for a,b,term,gid in spans:
                    out2.append(text[last:a]); out2.append('<a class="term" href="#%s" title="%s">%s</a>'%(gid,H.escape(TIP[gid],quote=True),term)); last=b
                out2.append(text[last:]); text=''.join(out2)
        out.append(text)
        tag=m.group(0)
        if tag.startswith('</'):
            name=re.match(r'</(\w+)',tag).group(1)
            if stack and stack[-1][0]==name: stack.pop()
            elif stack and name in [s[0] for s in stack]:
                # 巢狀同名（例如 div.story 內的 div）：以計數處理
                idx=len(stack)-1-[s[0] for s in stack][::-1].index(name); stack.pop(idx) if False else None
        else:
            mm=SKIP_OPEN.match(tag)
            if mm and not tag.endswith('/>'):
                name=re.match(r'<(\w+)',tag).group(1); stack.append((name,tag))
            elif stack:
                # 在跳過區域內的其他標籤：若是同名開標，push 以配對
                name=re.match(r'<(\w+)',tag).group(1)
                if name in [s[0] for s in stack] and not tag.endswith('/>') and name not in ('br','img','path','circle','line','rect','text','polyline','polygon','g','defs','clipPath','use','input'):
                    stack.append((name,tag))
        out.append(tag); pos=m.end()
    out.append(sec[pos:])
    return ''.join(out)
parts=re.split(r'(<section class="part" id="[^"]+">)',h)
for k in range(1,len(parts),2):
    sid=re.search(r'id="([^"]+)"',parts[k]).group(1)
    if sid=='glossary': continue
    body=parts[k+1]; endi=body.find('</section>')
    parts[k+1]=linkify(body[:endi])+body[endi:]
h=''.join(parts)
print('term links',h.count('class="term"'))

# ── 8. CSS ──
css_add=('a.term{color:var(--blue);text-decoration:none;border-bottom:1px dotted var(--blue)}'
'mark.key{background:#e3ebf4;color:inherit;padding:0 .2em;border-radius:4px;-webkit-box-decoration-break:clone;box-decoration-break:clone}'
'.later{display:inline-block;margin:0 0 .4em;padding:2px 9px;background:var(--amber2);color:var(--amber);border-radius:999px;font-size:.84rem}'
'.glossary+h3,section h3+dl.glossary{margin-top:.6em}')
rep('</style>',css_add+'</style>')
rep('.data-card{background:#19251f;border-color:#35483f}','.data-card{background:#19251f;border-color:#35483f}mark.key{background:#22344a}')
rep('@media print{.xref{border-bottom:0}}','@media print{.xref{border-bottom:0}a.term{color:#345f88;border-bottom:1px dotted #345f88}mark.key{background:#e3ebf4;-webkit-print-color-adjust:exact;print-color-adjust:exact}}')
open(P,'w',encoding='utf-8').write(h); print('written',len(h))
