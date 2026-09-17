import re,sys
exec(open(__file__.replace('h3.py','density.py')).read().split('secs=find')[0])
secs=find(p.root,lambda n:n.tag=='section' and 'part' in n.cls(),[])
want=sys.argv[2].split(',')
for s in secs:
    if s.a['id'] not in want: continue
    # walk doc order, split at h3
    cur='(top)';acc={};order=[];vis={}
    def w(n,inside_det=False):
        global cur
        if isinstance(n,str):
            acc[cur]=acc.get(cur,0)+cnt(n);return
        if n.tag in('style','script','svg'):return
        if n.tag=='h3':
            cur=re.sub(r'\s+',' ',text(n)).strip();order.append(cur);acc.setdefault(cur,0);return
        if n.tag in('figure','table'): vis.setdefault(cur,[]).append(n.tag+('('+n.a.get('data-chart','')+')' if n.tag=='figure' else ''))
        if n.tag=='details':
            sm=find(n,lambda x:x.tag=='summary',[])
            vis.setdefault(cur,[]).append('details['+(re.sub(r'\s+',' ',text(sm[0]))[:30] if sm else '')+'|print='+str('data-print' in n.a)+']')
        for c in n.c: w(c)
    w(s)
    print('###',s.a['id'])
    for k in ['(top)']+order: print(f'  {acc.get(k,0):5d} {k[:40]}  {vis.get(k,"")}')
