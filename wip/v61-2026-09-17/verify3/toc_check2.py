import fitz, re
base='/Users/linyenchu/Cladue Code/family-finance/'
d=fitz.open(base+'export/隔離人性-理財新手完整指南-v6.1.pdf')
h=open(base+'guide/index.html',encoding='utf-8').read()
toc=re.search(r'<nav class="toc".*?</nav>',h,re.S).group(0)
entries=[(i,re.sub(r'<[^>]+>','',t)) for i,t in re.findall(r'<a href="#([^"]+)">(.*?)</a>',toc)]
# TOC page numbers: collect toc text lines pages 1-2
lines=[]
for pn in (0,1):
    for l in d[pn].get_text().split('\n'): lines.append(l)
joined='\n'.join(lines)
flat=re.sub(r'\n','',joined)
tocnum={}
for sid,t in entries:
    tn=re.sub(r'\s+','',t)
    fl=re.sub(r'\s+','',joined)
    # number digits right after title; stop before next title's start (two-digit prefix for numbered) 
    m=re.search(re.escape(tn)+r'(\d+)',fl)
    s=m.group(1) if m else ''
    tocnum[sid]=s
# find heading spans: largest font on page
heads=[]
for pi,p in enumerate(d):
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            txt=''.join(s['text'] for s in l['spans']); sz=max(s['size'] for s in l['spans'])
            if sz>=17: heads.append((pi+1,round(sz,1),txt))
sizes={}
for pg,sz,t in heads: sizes.setdefault(sz,[]).append((pg,t))
for sz in sorted(sizes): print(sz,len(sizes[sz]),sizes[sz][:4])
# join consecutive heading lines per page
print('----')
h2=[]  # (page, text) merged
prev=None
for pg,sz,t in heads:
    if sz!=20.6: continue
    if h2 and h2[-1][0]==pg and not re.match(r'^\d',t) and prev_merge:
        pass
    h2.append([pg,t]); prev_merge=True
# merge wrapped lines: if next line on same page and previous title doesn't match any entry fully
titles={re.sub(r'\s+','',t):sid for sid,t in entries}
merged=[]
for pg,t in h2:
    t2=re.sub(r'\s+','',t)
    if merged and merged[-1][0]==pg and merged[-1][1] not in titles and not any(merged[-1][1].endswith(x) for x in ['']) :
        cand=merged[-1][1]+t2
        # accept merge if cand is prefix of some title or equals
        if any(k.startswith(cand) or re.sub(r'^\d+','',cand)==k or k in cand for k in titles):
            merged[-1][1]=cand; continue
    merged.append([pg,t2])
for pg,t in merged: print(pg,t)
print('----')
bad=0
for sid,t in entries:
    tn=re.sub(r'\s+','',t)
    pages=[pg for pg,x in merged if x==tn or re.sub(r'^\d{1,2}','',x)==tn]
    pgs=tocnum[sid]
    ok= pages and pgs.endswith(str(pages[0])) 
    print('OK ' if ok else 'BAD', sid, 'toc-digits',pgs,'h2 page',pages)
    if not ok: bad+=1
print('bad',bad)
