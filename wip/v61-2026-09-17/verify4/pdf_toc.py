import fitz, re
base='/Users/linyenchu/Cladue Code/family-finance/'
d=fitz.open(base+'export/隔離人性-理財新手完整指南-v6.1.pdf')
w=fitz.open(base+'export/隔離人性-可列印工作表-v6.1.pdf')
h=open(base+'guide/index.html',encoding='utf-8').read()
print('full pages',len(d),'worksheet pages',len(w))

toc=re.search(r'<nav class="toc".*?</nav>',h,re.S).group(0)
ol=re.search(r'<ol>(.*?)</ol>',toc,re.S).group(1)
numbered=re.findall(r'href="#([^"]+)"',ol)
entries=[(sid,re.sub(r'<[^>]+>','',t)) for sid,t in re.findall(r'<a href="#([^"]+)">(.*?)</a>',toc)]
print('toc entries in guide nav:',len(entries))

# printed page labels: first line of each page should be its number
lab_bad=[(i+1,p.get_text().split('\n',1)[0]) for i,p in enumerate(d) if p.get_text().split('\n',1)[0].strip()!=str(i+1)]
print('pages whose first text line != physical page number:',lab_bad[:10])

# TOC text (pages 1-2), whitespace-stripped
tt=re.sub(r'\s+','',d[0].get_text().split('\n',1)[1]+d[1].get_text().split('\n',1)[1])
tt=tt[tt.find('目錄'):]
# links on toc pages in reading order
links=[]
for pn in (0,1):
    p=d[pn]
    ls=[l for l in p.get_links() if l.get('page') is not None and l.get('page')>=0 and not l.get('uri')]
    # only those in TOC area: page 1 below '目錄' heading
    if pn==0:
        y=[b for b in p.get_text('blocks') if b[4].strip().startswith('目錄')]
        ymin=y[0][1] if y else 0
        ls=[l for l in ls if l['from'].y0>=ymin]
    ls.sort(key=lambda l:(l['from'].y0,l['from'].x0))
    links+= [(pn,l) for l in ls]
# merge links with same dest that are line-wrapped continuations
merged=[]
for pn,l in links:
    if merged and merged[-1][1]['page']==l['page'] and merged[-1][0]==pn and abs(l['from'].y0-merged[-1][1]['from'].y1)<4:
        continue
    merged.append((pn,l))
print('toc links (after merging wrapped lines):',len(merged))

outline={}
for lvl,title,pg in d.get_toc():
    if lvl==2: outline[re.sub(r'\s+','',re.sub(r'^\d+\s','',title))]=pg

bad=0; pos=0
for k,(sid,title) in enumerate(entries):
    t=re.sub(r'\s+','',title)
    pre='%02d'%(numbered.index(sid)+1) if sid in numbered else ''
    i=tt.find(pre+t,pos)
    if k+1<len(entries):
        nsid,nt=entries[k+1]; npre='%02d'%(numbered.index(nsid)+1) if nsid in numbered else ''
        j=tt.find(npre+re.sub(r'\s+','',nt),i+1)
        seg=tt[i+len(pre+t):j]
    else:
        seg=tt[i+len(pre+t):]
    m=re.match(r'(\d+)',seg) if i>=0 else None
    printed=int(m.group(1)) if m else None
    if i>=0: pos=i+len(pre+t)
    cands=[]
    for pn,l in links:
        bt=re.sub(r'\s+','',d[pn].get_textbox(l['from']))
        if len(bt)>=4 and (bt in pre+t+str(printed) or t.startswith(re.sub(r'^\d{2}','',bt)[:6])):
            cands.append(l['page']+1)
    dest=sorted(set(cands))
    dest=dest[0] if len(dest)==1 else dest
    ol_pg=outline.get(t)
    # h2 text actually on printed page?
    page_txt=re.sub(r'\s+','',d[printed-1].get_text()) if printed else ''
    on_page=(t in page_txt) or (t[:12] in page_txt)
    # and not on previous page as h2 (heading must start on this page): check outline agrees
    ok= printed is not None and printed==dest==ol_pg and on_page
    if not ok: bad+=1
    print('OK ' if ok else 'BAD', sid.ljust(10), 'printed',printed,'link->',dest,'outline',ol_pg,'title-on-page',on_page,'|',title[:22])
print('TOC entries',len(entries),'bad',bad)
