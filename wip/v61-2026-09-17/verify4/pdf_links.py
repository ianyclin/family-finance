import fitz, re
from collections import Counter
base='/Users/linyenchu/Cladue Code/family-finance/'
d=fitz.open(base+'export/隔離人性-理財新手完整指南-v6.1.pdf')
h=open(base+'guide/index.html',encoding='utf-8').read()
toc=re.search(r'<nav class="toc".*?</nav>',h,re.S).group(0)
ol=re.search(r'<ol>(.*?)</ol>',toc,re.S).group(1)
numbered=re.findall(r'href="#([^"]+)"',ol)
entries=[(sid,re.sub(r'<[^>]+>','',t)) for sid,t in re.findall(r'<a href="#([^"]+)">(.*?)</a>',toc)]
outline={}
for lvl,title,pg in d.get_toc():
    if lvl==2: outline[re.sub(r'\s+','',re.sub(r'^\d+\s','',title))]=pg
start={sid:outline[re.sub(r'\s+','',t)] for sid,t in entries}
num2start={i+1:start[sid] for i,sid in enumerate(numbered)}
name2start={re.sub(r'\s+','',t):start[sid] for sid,t in entries}
bad=[]; n=Counter()
for pi,p in enumerate(d):
    for l in p.get_links():
        if l.get('uri') or l.get('page') is None or l['page']<0: continue
        dest=l['page']+1
        txt=re.sub(r'\s+','',p.get_textbox(l['from']))
        if re.fullmatch(r'\d{1,2}',txt):
            n['num']+=1
            exp=num2start.get(int(txt))
            if exp!=dest: bad.append((pi+1,'num',txt,dest,exp))
        elif txt in name2start:
            n['name']+=1
            if name2start[txt]!=dest: bad.append((pi+1,'name',txt,dest,name2start[txt]))
        else:
            n['other']+=1
print(dict(n)); print('mismatches',len(bad))
for b in bad[:40]: print('  ',b)
# specific new links from this round
for pg in range(1,len(d)+1):
    t=re.sub(r'\s+','',d[pg-1].get_text())
    for key in ['「換匯成本」那一列','調得越勤越好嗎','第三題引用的','才需要賣掉一些來再平衡','照「從第一週到第一年」那一頁的順序做']:
        if key in t: print('found',key,'on page',pg)
