import re,sys
sys.argv=['x','../guide-v62.html']
exec(open('density.py').read().split('secs=find')[0])
secs=find(p.root,lambda n:n.tag=='section' and 'part' in n.cls(),[])
for s in secs:
    if s.a['id'].startswith('group'): continue
    L=[c for c in s.c if isinstance(c,N) and 'lede' in c.cls()]
    D=find(s,lambda n:'decision' in n.cls(),[])
    E=find(s,lambda n:'explain' in n.cls(),[])
    print(f"{s.a['id']:10s} lede{cnt(text(L[0])) if L else 0:4d} explain{cnt(text(E[0])) if E else 0:4d} decision{cnt(text(D[0])) if D else 0:4d}")
