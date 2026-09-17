import re, sys, json
from html.parser import HTMLParser
VOID={'br','img','hr','meta','link','input','wbr','source','col','area','base'}
class N:
    def __init__(s,tag,attrs,parent):
        s.tag=tag;s.a=dict(attrs);s.p=parent;s.c=[]
    def cls(s): return s.a.get('class','') or ''
class P(HTMLParser):
    def __init__(s):
        super().__init__();s.root=N('root',[],None);s.cur=s.root
    def handle_starttag(s,t,a):
        n=N(t,a,s.cur);s.cur.c.append(n)
        if t not in VOID: s.cur=n
    def handle_endtag(s,t):
        x=s.cur
        while x is not None and x.tag!=t: x=x.p
        if x is not None and x.p is not None: s.cur=x.p
    def handle_data(s,d): s.cur.c.append(d)
html=open(sys.argv[1],encoding='utf-8').read()
p=P();p.feed(html)
def text(n):
    if isinstance(n,str): return n
    if n.tag in('style','script','svg'): return ''
    return ''.join(text(c) for c in n.c)
def cnt(t): return len(re.findall(r'[一-鿿㐀-䶿A-Za-z0-9]',t))
def find(n,pred,out):
    if isinstance(n,str):return out
    if pred(n): out.append(n)
    for c in n.c: find(c,pred,out)
    return out
secs=find(p.root,lambda n:n.tag=='section' and 'part' in n.cls(),[])
def title(s):
    h=find(s,lambda n:n.tag=='h2',[])
    return re.sub(r'\s+',' ',text(h[0])).strip() if h else ''
rows=[]
for s in secs:
    t=text(s); nfig=len(find(s,lambda n:n.tag=='figure',[])); ntab=len(find(s,lambda n:n.tag=='table',[]))
    # printed-closed details
    det=find(s,lambda n:n.tag=='details',[])
    dchars=sum(cnt(text(d)) for d in det if not any(dd is not d and d in [] for dd in det))
    rows.append((s.a['id'],title(s),cnt(t),nfig,ntab,len(det)))
print("== per section chars ==")
tot=sum(r[2] for r in rows)
for r in rows: print(f"{r[0]:18s} {r[2]:6d} fig{r[3]} tab{r[4]} det{r[5]}  {r[1][:40]}")
print('total',tot)
# runs: flatten blocks in doc order; break on figure/table
BLOCK={'p','li','h2','h3','h4','dt','dd','summary','figcaption','blockquote'}
seq=[]
def walk(n,sec,ctx):
    if isinstance(n,str): return
    if n.tag in('style','script','svg'): return
    if n.tag=='section' and 'part' in n.cls(): sec=n.a['id']
    if n.tag in ('figure','table'):
        seq.append(('VIS',sec,n.tag+'.'+n.cls(),0,'')); return
    if n.tag in('h2','h3'):
        seq.append(('H',sec,n.tag,cnt(text(n)),re.sub(r'\s+',' ',text(n)).strip()[:40]));return
    if n.tag in BLOCK and not any(isinstance(c,N) and c.tag in BLOCK|{'ul','ol','div','table','figure','details','dl'} for c in n.c):
        t=re.sub(r'\s+',' ',text(n)).strip()
        seq.append(('T',sec,n.tag+'.'+n.cls()+('/'+ctx if ctx else ''),cnt(t),t[:60]));return
    c2=ctx
    if n.tag=='div' and n.cls(): c2=n.cls().split()[0]
    if n.tag=='details': c2='details'
    for c in n.c: walk(c,sec,c2)
walk(p.root,None,'')
runs=[];cur=None
for it in seq:
    kind=it[0]
    if kind=='VIS' or (kind=='H' and it[2]=='h2'):
        if cur: runs.append(cur)
        cur=None;continue
    if cur is None: cur={'sec':it[1],'chars':0,'n':0,'start':it[4],'h3':[],'ctx':set()}
    if kind=='H': cur['h3'].append(it[4])
    cur['chars']+=it[3];cur['n']+=1;cur['ctx'].add(it[2].split('/')[-1] if '/' in it[2] else '')
if cur: runs.append(cur)
runs.sort(key=lambda r:-r['chars'])
print("== longest runs without figure/table (break at h2) ==")
for r in runs[:15]:
    print(r['sec'],r['chars'],'blocks',r['n'],'h3:',r['h3'][:6],'| start:',r['start'][:50],'| ctx',sorted(x for x in r['ctx'] if x)[:6])
# longest single paragraphs
ps=sorted([it for it in seq if it[0]=='T'],key=lambda x:-x[3])[:15]
print("== longest single blocks ==")
for it in ps: print(it[1],it[3],it[2],it[4])
