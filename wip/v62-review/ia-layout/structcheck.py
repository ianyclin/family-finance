import re,sys
sys.argv=[sys.argv[0],sys.argv[1]]
exec(open(__file__.replace('struct.py','density.py')).read().split('secs=find')[0])
secs=find(p.root,lambda n:n.tag=='section' and 'part' in n.cls(),[])
def T(n): return re.sub(r'\s+',' ',text(n)).strip()
for s in secs:
    kids=[c for c in s.c if isinstance(c,N)]
    seq=[]
    for c in kids:
        k=c.tag+('.'+c.cls().split()[0] if c.cls() else '')
        seq.append(k)
    lede=[c for c in kids if 'lede' in c.cls()]
    dec=find(s,lambda n:'decision' in n.cls(),[])
    exp=find(s,lambda n:'explain' in n.cls(),[])
    h2=find(s,lambda n:n.tag=='h2',[])
    print(s.a['id'],'|H2:',T(h2[0]) if h2 else '-','|lede:',T(lede[0])[:50] if lede else 'NONE','|explain',len(exp),'|decision',len(dec), ('last:'+seq[-1]) )
    for d in dec: print('   DEC:',T(d)[:90])
    # order summary: compress
    comp=[]
    for k in seq:
        if not comp or comp[-1][0]!=k: comp.append([k,1])
        else: comp[-1][1]+=1
    print('   ',' > '.join(f"{k}x{n}" if n>1 else k for k,n in comp)[:400])
# toc
toc=find(p.root,lambda n:n.tag=='nav' and n.a.get('id')=='toc',[])[0]
print('TOC:',T(toc)[:3000])
tasks=find(p.root,lambda n:n.tag=='nav' and 'tasks' in n.cls(),[])[0]
print('TASKS:',T(tasks))
