import re, sys, json, html as H
from collections import Counter, defaultdict
base='/Users/linyenchu/Cladue Code/family-finance/'
old=open(base+'wip/v61-2026-09-17/fix2/before.html',encoding='utf-8').read()
new=open(base+'guide/index.html',encoding='utf-8').read()

def secmap(h):
    toc=re.search(r'<nav class="toc".*?</nav>',h,re.S).group(0)
    ol=re.search(r'<ol>(.*?)</ol>',toc,re.S).group(1)
    ids=re.findall(r'href="#([^"]+)"',ol)
    return {sid:i+1 for i,sid in enumerate(ids)}

def sections(h):
    """(id, start, end) for each <section ... id=...>"""
    out=[]
    for m in re.finditer(r'<section\b[^>]*\bid="([^"]+)"[^>]*>',h):
        out.append([m.group(1),m.start()])
    for i in range(len(out)):
        out[i].append(out[i+1][1] if i+1<len(out) else len(h))
    return out

def sec_of(secs,pos):
    for sid,a,b in secs:
        if a<=pos<b: return sid
    return None

def ids_in(h,start,end):
    return set(re.findall(r'(?<![\w-])id="([^"]+)"',h[start:end]))

for label,h in [('before',old),('after',new)]:
    sm=secmap(h); secs=sections(h)
    allids=set(re.findall(r'(?<![\w-])id="([^"]+)"',h))
    broken=[x for x in re.findall(r'href="#([^"]*)"',h) if x not in allids]
    # xref with number: 第 <a class="xref" href="#X">N</a> 節
    bad=[]
    for m in re.finditer(r'第\s*<a class="xref" href="#([^"]+)">(\d+)</a>\s*節',h):
        tgt,n=m.group(1),int(m.group(2))
        # anchor inside a section -> map to containing section id
        tsec=tgt if tgt in sm else sec_of(secs,h.find('id="%s"'%tgt))
        if sm.get(tsec)!=n: bad.append((sec_of(secs,m.start()),tgt,n,sm.get(tsec)))
    # xref where anchor text is a number but no 第..節 wrapper
    loose=[(sec_of(secs,m.start()),m.group(1),m.group(2),h[max(0,m.start()-15):m.start()]) for m in re.finditer(r'<a class="xref" href="#([^"]+)">(\d+)</a>',h) if not re.search(r'第\s*$',h[max(0,m.start()-4):m.start()])]
    # bare 第 N 節 in text without link
    text=re.sub(r'<a class="xref"[^>]*>\d+</a>','LINKNUM',h)
    bare=[(sec_of(secs,m.start()),m.group(0),re.sub(r'<[^>]+>','',h[max(0,m.start()-40):m.end()+20])) for m in re.finditer(r'第\s*(\d+)\s*節',text)]
    print('=====',label,'broken',broken,'num-xref mismatches',bad)
    print(' loose numeric xrefs',loose)
    print(' bare 第N節 (not linked):',len(bare))
    for b in bare: print('   ',b)

print('\n== every numeric xref: anchor number == TOC ordinal of target section ==')
for label,h in [('before',old),('after',new)]:
    sm=secmap(h); secs=sections(h); bad=[]; n=0
    for m in re.finditer(r'<a class="xref" href="#([^"]+)">(\d+)</a>',h):
        n+=1; tgt=m.group(1); num=int(m.group(2))
        tsec=tgt if tgt in sm else sec_of(secs,h.find('id="%s"'%tgt))
        if sm.get(tsec)!=num: bad.append((sec_of(secs,m.start()),tgt,num,sm.get(tsec)))
    print(label,'numeric xrefs',n,'bad',bad)
    # xref with text (named) : check text matches target title
    titles={}
    for sid,a,b in secs:
        mm=re.search(r'<h2[^>]*>(.*?)</h2>',h[a:b],re.S)
        if mm: titles[sid]=re.sub(r'<[^>]+>','',mm.group(1)).strip()
    named=[]
    for m in re.finditer(r'<a class="xref" href="#([^"]+)">([^<]*[^\d<][^<]*)</a>',h):
        tgt,t=m.group(1),H.unescape(m.group(2))
        tsec=tgt if tgt in titles else sec_of(secs,h.find('id="%s"'%tgt))
        tt=titles.get(tsec,'')
        if not tt.startswith(t) and t not in tt:
            named.append((sec_of(secs,m.start()),tgt,t,tt))
    print(label,'named xrefs not matching target h2:',len(named))
    for x in named: print('   ',x)
