import fitz, re
base='/Users/linyenchu/Cladue Code/family-finance/'
d=fitz.open(base+'export/隔離人性-理財新手完整指南-v6.1.pdf')
pages=[re.sub(r'\s+','',p.get_text()) for p in d]
h=open(base+'guide/index.html',encoding='utf-8').read()
toc=re.search(r'<nav class="toc".*?</nav>',h,re.S).group(0)
entries=re.findall(r'<a href="#([^"]+)">(.*?)</a>',toc)
# TOC text in PDF (pages 1-2)
toctext=''.join(pages[0:2])
# get h2 per id
ok=0
for sid,title in entries:
    t=re.sub(r'<[^>]+>','',title); tn=re.sub(r'\s+','',t)
    m=re.search(re.escape(tn)+r'(\d+)',toctext)
    pg=int(m.group(1)) if m else None
    # find first page (>=3) whose text contains title
    found=[i+1 for i,p in enumerate(pages) if i>=2 and tn in p]
    # section h2 appears; use first occurrence page not in toc
    first=found[0] if found else None
    status='OK' if pg==first else 'MISMATCH'
    if status=='OK': ok+=1
    print(status,sid,tn[:24],'toc=',pg,'firstfound=',first,'all=',found[:6])
print(ok,len(entries))
# order in TOC vs order of sections in body
body_ids=re.findall(r'<section class="part" id="([^"]+)"',h)
toc_ids=[e[0] for e in entries]
filtered=[i for i in body_ids if i in toc_ids]
print('order same:',filtered==toc_ids)
print('body ids:',body_ids)
