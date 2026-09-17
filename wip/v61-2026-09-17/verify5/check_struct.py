import re, sys
from struct_lib import *
h=load(sys.argv[1] if len(sys.argv)>1 else '../../../guide/index.html')
secs=sections(h); byid={s['id']:s for s in secs}
body_order=[s['id'] for s in secs if not s['id'].startswith('group-')]
toc=re.search(r'<nav class="toc".*?</nav>', h, re.S).group(0)
toc_links=re.findall(r'<a href="#([\w-]+)">(.*?)</a>', toc)
problems=[]
# 1 order
if [i for i,_ in toc_links]!=body_order: problems.append(('order', [i for i,_ in toc_links], body_order))
for i,t in toc_links:
    if text(t)!=byid[i]['name']: problems.append(('tocname',i,text(t),byid[i]['name']))
# groups
groups=re.findall(r'<details class="toc-part"([^>]*)><summary>(.*?)</summary>(.*?)</details>', toc, re.S)
full_order=[s['id'] for s in secs]
print('toc groups', len(groups))
for attrs, summ, inner in groups:
    g=re.search(r'data-group="([^"]+)"', attrs)
    name=text(re.search(r'toc-part-name">(.*?)</span>', summ).group(1))
    rng=re.search(r'toc-part-range">(.*?)</span>', summ)
    desc=text(re.search(r'toc-part-desc">(.*?)</span>', summ).group(1))
    links=re.findall(r'<a href="#([\w-]+)">', inner)
    print('  ', attrs.strip(), '|', name, '|', rng.group(1) if rng else '-', '|', links)
    if 'data-print' not in attrs: problems.append(('noprint', name))
    if g:
        gid=g.group(1); gs=byid[gid]
        if gs['name']!=name: problems.append(('groupname',gid,name,gs['name']))
        if gs['lede']!=desc: problems.append(('groupdesc',gid,desc,gs['lede']))
        idx=full_order.index(gid)
        if full_order[idx+1]!=links[0]: problems.append(('groupfirst',gid,full_order[idx+1],links[0]))
        # group section contiguous covering exactly these links
        nxt=[x for x in full_order[idx+1:idx+1+len(links)]]
        if nxt!=links: problems.append(('groupspan',gid,nxt,links))
        # map
        m=re.search(r'<ol class="part-map">(.*?)</ol>', gs['body'], re.S)
        lis=re.findall(r'<li>(.*?)</li>', m.group(1), re.S)
        mlinks=[]
        for li in lis:
            a=re.search(r'<a class="xref" href="#([\w-]+)">(.*?)</a>', li)
            mn=re.search(r'<span class="map-num">(\d+)</span>', li)
            ml=re.search(r'<span class="map-lede">(.*?)</span>', li)
            tid=a.group(1); mlinks.append(tid); t=byid[tid]
            if text(a.group(2))!=t['name']: problems.append(('mapname',gid,tid,text(a.group(2)),t['name']))
            if text(ml.group(1))!=t['lede']: problems.append(('maplede',gid,tid,text(ml.group(1)),t['lede']))
            if (mn.group(1) if mn else None)!=t['num']: problems.append(('mapnum',gid,tid))
        if mlinks!=links: problems.append(('maplinks',gid,mlinks,links))
        if rng:
            nums=[byid[l]['num'] for l in links]
            r=re.findall(r'\d+', rng.group(1))
            if [str(x) for x in (min(map(int,nums)),max(map(int,nums)))]!=r: problems.append(('range',gid,r,nums))
    else:
        # first group: must start the book
        if links!=full_order[:len(links)]: problems.append(('firstgroup',links))
# counter start
for m in re.finditer(r'<ol class="(toc-from-(\d+))">(.*?)</ol>', toc, re.S):
    first=re.search(r'href="#([\w-]+)"', m.group(3)).group(1)
    if byid[first]['num']!=m.group(2): problems.append(('counter',m.group(1),first,byid[first]['num']))
    css=re.search(r'\.toc ol\.%s\{counter-reset:toc (\d+)\}'%m.group(1), h)
    base = int(css.group(1)) if css else 0
    if base+1!=int(m.group(2)): problems.append(('countercss',m.group(1),base))
    # each item consecutive num
    ids=re.findall(r'href="#([\w-]+)"', m.group(3))
    for k,i in enumerate(ids):
        if byid[i]['num']!=str(int(m.group(2))+k): problems.append(('counterseq',i))
# group sections all have map
for s in secs:
    if s['id'].startswith('group-') and s['id'] not in [re.search(r'data-group="([^"]+)"',a).group(1) for a,_,_ in groups if 'data-group' in a]:
        problems.append(('group-not-in-toc',s['id']))
# xref numbers
anc=anchor_sec(h)
n=0
for m in re.finditer(r'<a class="xref" href="#([\w-]+)">(\d+)</a>', h):
    n+=1
    t=anc.get(m.group(1))
    if t is None or t['num']!=m.group(2):
        problems.append(('xref',m.group(1),m.group(2), t['id'] if t else None, t['num'] if t else None))
print('xref numeric', n)
# numeric xref inside which section: print context of each "第 ... 節"
print('PROBLEMS', len(problems))
for p in problems: print(p)
