import re, html as H
from collections import Counter
base='/Users/linyenchu/Cladue Code/family-finance/'
old=open(base+'wip/v61-2026-09-17/fix2/before.html',encoding='utf-8').read()
new=open(base+'guide/index.html',encoding='utf-8').read()

def sections(h):
    out=[]
    for m in re.finditer(r'<section\b[^>]*\bid="([^"]+)"[^>]*>',h):
        out.append([m.group(1),m.start()])
    for i in range(len(out)):
        out[i].append(out[i+1][1] if i+1<len(out) else len(h))
    return out

def blank_blocks(s, pat, tag):
    """replace blocks (story div, explain p, h2/h3, strong, svg, style, source-card) with spaces of equal length"""
    res=list(s)
    for m in re.finditer(pat,s):
        depth=0; j=m.start(); k=len(s)
        for t in re.finditer(r'<%s\b[^>]*>|</%s>'%(tag,tag),s[j:]):
            depth+= -1 if t.group(0).startswith('</') else 1
            if depth==0: k=j+t.end(); break
        for i in range(j,k): res[i]=' '
    return ''.join(res)

def terms(h):
    info={}
    secs=sections(h)
    for sid,a,b in secs:
        s=h[a:b]
        links=[(m.start(),m.group(1),H.unescape(m.group(2))) for m in re.finditer(r'<a class="term" href="#([^"]+)"[^>]*>(.*?)</a>',s)]
        info[sid]=links
    return info

ti_old=terms(old); ti_new=terms(new)
print('term links total before',sum(len(v) for v in ti_old.values()),'after',sum(len(v) for v in ti_new.values()))
for sid in ti_new:
    c=Counter(x[1] for x in ti_new[sid]); d=[k for k,v in c.items() if v>1]
    co=Counter(x[1] for x in ti_old.get(sid,[])); do=[k for k,v in co.items() if v>1]
    if d or do: print('DUP term href in section',sid,'after',d,'before',do)
    if [x[1:] for x in ti_new[sid]]!=[x[1:] for x in ti_old.get(sid,[])]:
        print('changed term list in',sid)
        print('   before',[x[1:] for x in ti_old.get(sid,[])])
        print('   after ',[x[1:] for x in ti_new[sid]])

# first-occurrence check: for each term link, does its anchor word appear earlier in the section's eligible text?
def visible(s):
    s=re.sub(r'<style.*?</style>',lambda m:' '*len(m.group(0)),s,flags=re.S)
    s=re.sub(r'<svg.*?</svg>',lambda m:' '*len(m.group(0)),s,flags=re.S)
    s=re.sub(r'\stitle="[^"]*"',lambda m:' '*len(m.group(0)),s)
    s=re.sub(r'\saria-label="[^"]*"',lambda m:' '*len(m.group(0)),s)
    s=re.sub(r'\salt="[^"]*"',lambda m:' '*len(m.group(0)),s)
    return s

def first_occ(h,label):
    out=[]
    for sid,a,b in sections(h):
        s=visible(h[a:b])
        # eligible text: exclude h2/h3, explain box, story, strong, other links(non-term), source-card
        e=s
        e=blank_blocks(e,r'<div\b[^>]*class="story"','div')
        e=blank_blocks(e,r'<div\b[^>]*class="source-card"','div')
        e=blank_blocks(e,r'<p\b[^>]*class="explain"','p')
        e=re.sub(r'<h[1-4][^>]*>.*?</h[1-4]>',lambda m:' '*len(m.group(0)),e,flags=re.S)
        e=re.sub(r'<strong\b[^>]*>.*?</strong>',lambda m:' '*len(m.group(0)),e,flags=re.S)
        e=re.sub(r'<a (?![^>]*class="term")[^>]*>.*?</a>',lambda m:' '*len(m.group(0)),e,flags=re.S)
        e=re.sub(r'<mark\b[^>]*>.*?</mark>',lambda m:' '*len(m.group(0)),e,flags=re.S)
        seen=set()
        for m in re.finditer(r'<a class="term" href="#([^"]+)"[^>]*>(.*?)</a>',s):
            word=H.unescape(re.sub(r'<[^>]+>','',m.group(2)))
            prior=re.sub(r'<[^>]+>',lambda x:' '*len(x.group(0)),e[:m.start()])
            if word in prior:
                i=prior.rfind(word)
                out.append((sid,m.group(1),word,re.sub(r'\s+','',prior[max(0,prior.find(word)-30):prior.find(word)+len(word)+10])))
    return out
fo=first_occ(old,'before'); fn=first_occ(new,'after')
print('\nterm link not at first eligible occurrence: before',len(fo),'after',len(fn))
for x in fn:
    print('  ', 'NEW ' if x not in fo else 'old ', x)
