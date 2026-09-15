# -*- coding: utf-8 -*-
"""v4.9 → v4.9.1：十歲讀者第二輪。先拆掉所有名詞連結、改文字、再用縮減後的詞表重標（白話版不標）。一次性腳本。"""
import re, sys, html as H
P='/Users/linyenchu/Cladue Code/family-finance/guide/index.html'
h=open(P,encoding='utf-8').read()
h=re.sub(r'<a class="term"[^>]*>([^<]*)</a>',r'\1',h)
def rep(a,b,c=1):
    global h
    if h.count(a)!=c: print('MISMATCH',h.count(a),a[:60]); sys.exit(1)
    h=h.replace(a,b)
L=lambda t:'<span class="later">%s</span>'%t
# 十四個
rep('<h3>先懂這十三個</h3>','<h3>先懂這十四個</h3>'); rep('前十三個是主角','前十四個是主角'); rep('前十三個懂了就能往下讀','前十四個懂了就能往下讀')
# 詞彙表小修
rep('基金每一單位真正值多少錢：把基金持有的東西全部算成今天的價格，除以單位數。ETF 的市價會在淨值上下晃。','基金每一份真正值多少錢：把基金持有的東西全部算成今天的價格，除以總共切成幾份。ETF 的市價會在淨值上下晃。')
rep('溢酬是這樣挑在歷史上比市場多賺的那一段。多不多、以後還有沒有，沒有人保證。','溢酬是這樣挑在歷史上比市場多賺的部分。多不多、以後還有沒有，沒有人保證。')
rep('一年配的息除以現在的價格。它只講配多少，不講賺多少。','一年配的息除以現在的價格。它只講配多少，不講賺多少：配出來的錢會從價格裡扣掉（第 <a class="xref" href="#s8">8</a> 節）。')
rep('用額外的成本，把某一種貨幣的漲跌鎖住；先看它鎖的是哪一種貨幣，鎖成美元對台灣人沒有幫助。','用合約先約定好未來換匯的價格，讓某一種貨幣的漲跌影響不到你，代價是要付費用。先看它鎖的是哪一種貨幣：鎖成美元只是把其他貨幣換美元的風險擋掉，美元換台幣的風險還在。')
rep('債券價格對利率變動的敏感度；到期越久，利率一動價格晃得越大。','利率每動一點，債券價格會跟著動多少；到期越久，利率一動價格晃得越大。')
rep('對股利、利息、獎金這幾類收入另外收的一小筆保費，單次達門檻才扣。','對股利、利息、獎金這幾類收入另外收的一小筆保費，單次達 2 萬元才扣（以健保署公告為準）。')
rep('維持率是股票市值除以借款','維持率是股票現在的總值除以借款')
rep('試算表的一個函式，把每一筆進出的金額和日期都算進去','試算表裡的一個內建算式（像加總的 SUM 一樣，輸入就會算），把每一筆進出的金額和日期都算進去')
# 白話版：槓桿
rep('但「多冒險」和「借錢冒險」（槓桿：借錢來投資，賺賠都放大）是兩件事。','但「多冒險」和「借錢冒險」（槓桿：借錢來投資，賺賠都放大）是兩件事：借的錢要付利息，跌太多還會被強迫賣掉。')
# 標籤：第五步移到限價單那段；補五處
rep(L('先跳過也可以，第一次下單前再回來看')+'<strong>用小金額完成第一次。</strong>','<strong>用小金額完成第一次。</strong>')
rep('自己下單時，限價單是','下面這段'+L('先跳過也可以，第一次自己下單前再回來看')+'自己下單時，限價單是')
rep('<p>再平衡是把跑掉的比例調回原本設定。','<p>'+L('先跳過也可以，資產大到要賣的時候再回來看')+'再平衡是把跑掉的比例調回原本設定。')
rep('<strong>自己的報酬：</strong>','<strong>自己的報酬：</strong>'+L('先跳過也可以，年底要算的時候再回來看'))
rep('要注意台灣和美國目前沒有租稅協定','（'+L('先跳過也可以，選台灣掛牌還是海外的時候再看')+'）要注意台灣和美國目前沒有租稅協定')
rep('有些基金和 ETF 名字裡有「避險」，意思是','（'+L('先跳過也可以，看到「避險」兩個字再回來')+'）有些基金和 ETF 名字裡有「避險」，意思是')
rep('<h3>三、退休要存多少、每年能領多少？</h3>','<h3>三、退休要存多少、每年能領多少？</h3>'+L('先跳過也可以，接近退休再回來看'))
rep('<section class="part" id="methods"><h2>資料口徑與來源</h2><p class="lede">','<section class="part" id="methods"><h2>資料口徑與來源</h2>'+L('這一節是給想核對數字的人')+'<p class="lede">')
# 重點句：拿掉五句
for k in ['越早換，交叉點越早。','配不配息本身不是重點，總報酬才是','它們不是把人變理性，而是讓錯誤比較難發生。','防守那一塊放什麼，比放多少更重要。','這一格不能變成核心，也不能拿核心的錢去補。']:
    rep('<mark class="key">'+k+'</mark>',k)
# 就地解釋
rep('和避險基金業者 Protégé Partners 賭十年','和避險基金（收費很高的私人基金）業者 Protégé Partners 賭十年')
rep('校務基金','校務基金（學校自己的一大筆錢）')
rep('退休財富的標準差少四分之一以上','退休財富的標準差（上下起伏的大小）少四分之一以上')
rep('（另一式擇優）','（另一式擇優：勞保局有兩個公式，取高的）')
rep('用程式去抓會被擋下來、回 403，用瀏覽器打得開','用程式去抓會被擋下來（回 403，就是網站擋下程式的代號），用瀏覽器打得開')
rep('SHA-256 為','SHA-256（檔案的指紋）為')
rep('多輪對抗性檢查','多輪對抗性檢查（專門找錯的檢查）')
rep('用前瞻報酬假設模擬的結果','用對未來報酬的假設跑模擬得到的結果')
rep('利息通常按實際存期的牌告利率八折計','利息通常按實際存了多久、用銀行公告的牌告利率打八折計')
rep('可能把正常現金流時點也算成','可能把正常的現金流時點（錢進出的時間）也算成')
rep('（8 萬元抵減上限除以 2% 稅差）','（8 萬元抵減上限除以 2% 稅差；2% 是 30% 級距和 28% 的差）')
rep('（另一套用來算最低稅負的所得總數）','（政府另外算一次的所得總數，用來確定高所得的人至少繳一點稅）')
rep('仍高於全股票策略的中位數','仍高於全股票策略的中位數（排在正中間的那個結果）')
rep('樂金 2021。寫給大人看的：','樂金 2021。別被書名騙了，是寫給大人看的：')
rep('取比較小的那個，到了才動（','取比較小的那個，到了才動；取小的是為了讓占比小的資產也管得到，債券只占 10% 時，偏五個百分點等於跑了一半（')
rep('六四（六成股票）、股票漲三成，約是 12%）。','六四（六成股票）、股票漲三成，約是 12%）。為什麼剛好是這個數：股票漲了以後總資產變大，防守那一塊要跟著長到同樣的比例，差的那一塊就是防守比例乘漲幅乘總資產。')
rep('這張表只算 1 月到 12 月這一種起點，從高點起算的那種一年不在裡面，所以任一天起算的最差值只會更差。','這張表每一段都是從 1 月 1 日算到 12 月 31 日；如果從某個高點那一天起算，一年後會比表上最差的那格更差，所以表上的最差值是偏好看的。')
rep('海外 ETF 名字裡的「USD Hedged」，意思是基金把裡面各國貨幣的漲跌都鎖成美元；對你來說那還是一筆美元資產，美元對台幣的漲跌一樣跑不掉；','基金裡有歐元、日圓等各國貨幣，海外 ETF 名字裡的「USD Hedged」是把這些貨幣對美元的漲跌抵掉，讓它像純美元資產；但美元對台幣的漲跌沒有被抵掉；')
# 重標名詞（縮減詞表；白話版不標）
TERMS=[('內扣費用','g-fee'),('淨值','g-nav'),('口徑','g-scope'),('複委託','g-broker'),('人力資本','g-hc'),('財務資本','g-hc'),('曝險','g-exposure'),('因子','g-factor'),('衛星','g-core'),('股債比','g-ratio'),('八二','g-ratio'),('六四','g-ratio'),('殖利率','g-yield'),('投資等級','g-ig'),('匯率避險','g-hedge'),('收益平準金','g-equal'),('追蹤誤差','g-te'),('折溢價','g-prem'),('存續期間','g-dur'),('註冊地','g-domicile'),('掛牌','g-domicile'),('停利','g-stop'),('當沖','g-daytrade'),('交割','g-settle'),('限價單','g-order'),('市價單','g-order'),('補充保費','g-nhi'),('級距','g-bracket'),('融資','g-margin'),('維持率','g-margin'),('XIRR','g-xirr'),('提領率','g-swr'),('波動','g-vol')]
TIP={}
for gid in set(g for _,g in TERMS):
    m=re.search(r'<dt id="%s">[^<]*</dt><dd>(.*?)</dd>'%gid,h,re.S); t=re.sub(r'<[^>]+>','',m.group(1)); TIP[gid]=re.split(r'[。；]',t)[0]+'。'
SKIP_OPEN=re.compile(r'<(a|h2|h3|h4|nav|svg|strong|time|mark|span class="tag"|span class="later"|span class="chart-title"|p class="explain"|div class="story"|details class="orig"|title|figure)\b')
VOID={'br','img','path','circle','line','rect','text','polyline','polygon','g','defs','clipPath','use','input'}
def linkify(sec):
    used=set(); out=[]; pos=0; stack=[]
    for m in re.finditer(r'<[^>]+>',sec):
        text=sec[pos:m.start()]
        if text and not stack:
            spans=[]
            for term,gid in TERMS:
                if term in used or gid in used: continue
                k=text.find(term)
                if k<0 or any(not (k+len(term)<=a or k>=b) for a,b,_,_ in spans): continue
                spans.append((k,k+len(term),term,gid)); used.add(term); used.add(gid)
            if spans:
                spans.sort(); o2=[]; last=0
                for a,b,term,gid in spans:
                    o2.append(text[last:a]); o2.append('<a class="term" href="#%s" title="%s">%s</a>'%(gid,H.escape(TIP[gid],quote=True),term)); last=b
                o2.append(text[last:]); text=''.join(o2)
        out.append(text); tag=m.group(0)
        if tag.startswith('</'):
            name=re.match(r'</(\w+)',tag).group(1)
            if stack and stack[-1]==name: stack.pop()
        else:
            name=re.match(r'<(\w+)',tag).group(1)
            if SKIP_OPEN.match(tag) and not tag.endswith('/>'): stack.append(name)
            elif stack and name in stack and name not in VOID and not tag.endswith('/>'): stack.append(name)
        out.append(tag); pos=m.end()
    out.append(sec[pos:]); return ''.join(out)
parts=re.split(r'(<section class="part" id="[^"]+">)',h)
for k in range(1,len(parts),2):
    if 'id="glossary"' in parts[k]: continue
    body=parts[k+1]; e=body.find('</section>'); parts[k+1]=linkify(body[:e])+body[e:]
h=''.join(parts)
open(P,'w',encoding='utf-8').write(h); print('terms',h.count('class="term"'),'keys',h.count('mark class="key"'),'later',h.count('class="later"'))
