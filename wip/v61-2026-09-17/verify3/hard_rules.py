import re, sys, difflib, html as H
base='/Users/linyenchu/Cladue Code/family-finance/'
old=open(base+'wip/v61-2026-09-17/stages/structure-before.html',encoding='utf-8').read()
new=open(base+(sys.argv[1] if len(sys.argv)>1 else 'guide/index.html'),encoding='utf-8').read()
VOID={'br','img','hr','input','meta','link','source','col','wbr'}
def outer(h,pos):
    m=re.match(r'<([a-zA-Z0-9]+)',h[pos:]); tag=m.group(1).lower()
    depth=0
    for t in re.finditer(r'<(/?)(%s)\b[^>]*>'%tag,h[pos:],re.I):
        if t.group(1)=='': depth+=1
        else: depth-=1
        if depth==0: return h[pos:pos+t.end()]
def find_all(h,pattern):
    return [outer(h,m.start()) for m in re.finditer(pattern,h)]
def txt(s): return re.sub(r'\s+',' ',H.unescape(re.sub(r'<[^>]+>','',s))).strip()
# stories
so=find_all(old,r'<div class="story"'); sn=find_all(new,r'<div class="story"')
print('stories',len(so),len(sn),'identical html:',so==sn)
ko=[txt(x) for x in find_all(old,r'<mark class="key"')]; kn=[txt(x) for x in find_all(new,r'<mark class="key"')]
print('mark.key',len(ko),len(kn),'same order+text:',ko==kn)
if ko!=kn:
    print(' removed',[k for k in ko if k not in kn]); print(' added',[k for k in kn if k not in ko])
# facts
facts=[l.rstrip('\n') for l in open(base+'lite/facts.txt',encoding='utf-8') if l.strip() and not l.startswith('#')]
plainN=re.sub(r'\s+','',txt(new)); lite=open(base+'lite/index.html',encoding='utf-8').read(); plainL=re.sub(r'\s+','',txt(lite))
miss=0
for f in facts:
    fo=f.startswith('full-only:'); s=f.split(':',1)[1] if fo else f
    s2=re.sub(r'\s+','',s)
    if s2 not in plainN or (not fo and s2 not in plainL): miss+=1; print(' FACT MISSING',f)
print('facts',len(facts),'missing',miss)
def strip_print(h): return re.sub(r'\sdata-print="[^"]*"','',h)
for name,pat in [('plan-blank',r'<details data-lite-alt="plan-blank"'),('lookup-tables',r'<details data-lite-alt="lookup-tables"'),('ch4-drill',r'<[a-z]+ [^>]*data-lite-alt="ch4-drill"'),('app-a-checklist',r'<[a-z]+ [^>]*data-lite-alt="app-a-checklist"')]:
    a=find_all(old,pat); b=find_all(new,pat)
    same=[strip_print(x) for x in a]==[strip_print(x) for x in b]
    print('block',name,len(a),len(b),'same ignoring data-print:',same, 'raw same:',a==b)
    if not same:
        for x,y in zip(a,b):
            X,Y=strip_print(x),strip_print(y)
            for tag,i1,i2,j1,j2 in difflib.SequenceMatcher(None,X,Y,autojunk=False).get_opcodes():
                if tag!='equal': print('   ',tag,repr(X[max(0,i1-60):i2+20]),'=>',repr(Y[max(0,j1-60):j2+20]))
# ten warning
def ten_warn(h):
    s=h.index('<section class="part" id="ten"'); return outer(h,h.index('<div class="warning"',s))
print('ten warning same:',ten_warn(old)==ten_warn(new))
# lite-alt attributes inventory
print('data-lite-alt old',sorted(set(re.findall(r'data-lite-alt="([^"]+)"',old)))==sorted(set(re.findall(r'data-lite-alt="([^"]+)"',new))))
print('data-lite old/new same:',re.findall(r'data-lite="([^"]+)"',old)==re.findall(r'data-lite="([^"]+)"',new))
