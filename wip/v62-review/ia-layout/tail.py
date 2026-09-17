import re,sys
sys.argv=['x','../guide-v62.html']
exec(open('density.py').read().split('secs=find')[0])
secs=find(p.root,lambda n:n.tag=='section' and 'part' in n.cls(),[])
for s in secs:
    if s.a['id'] in ('s6','s12','lifecycle','methods','firstmonth'):
        kids=[c for c in s.c if isinstance(c,N)]
        for c in kids[-5:]:
            print(s.a['id'],c.tag,c.cls(),re.sub(r'\s+',' ',text(c))[:160])
        print()
