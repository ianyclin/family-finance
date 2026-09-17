import re, sys
from collections import Counter
def block(h, m, tag):
    d=0
    for t in re.finditer(r'<%s\b[^>]*>|</%s>'%(tag,tag), h[m.start():]):
        d += -1 if t.group(0).startswith('</') else 1
        if d==0: return h[m.start():m.start()+t.end()]
def blocks(h, tag, attr_re):
    return [block(h,m,tag) for m in re.finditer(r'<%s\b[^>]*%s[^>]*>'%(tag,attr_re), h)]
old, new = (open(p,encoding='utf-8').read() for p in sys.argv[1:3])
specs=[('div',r'class="[^"]*\bstory\b[^"]*"','story'),('mark',r'class="[^"]*\bkey\b[^"]*"','mark.key'),('div',r'class="[^"]*\bwarning\b[^"]*"','warning'),
 ('details',r'data-lite-alt="plan-blank"','plan-blank'),('details',r'data-lite-alt="lookup-tables"','lookup-tables'),('div',r'data-lite-alt="ch4-drill"','ch4-drill'),
 ('ol',r'class="checklist"','ol.checklist (all)'),('div',r'data-lite-alt="[^"]+"','div[data-lite-alt]'),('details',r'data-lite-alt="[^"]+"','details[data-lite-alt]'),('div',r'data-lite="[^"]+"','div[data-lite]')]
for tag,a,name in specs:
    A,B=Counter(blocks(old,tag,a)),Counter(blocks(new,tag,a))
    print(f'{name:24s} old {sum(A.values()):3d} new {sum(B.values()):3d} raw-identical: {A==B}')
    if A!=B:
        for x in (A-B): print('   LOST  ', re.sub(r'\s+',' ',re.sub('<[^>]+>','',x))[:200])
        for x in (B-A): print('   ADDED ', re.sub(r'\s+',' ',re.sub('<[^>]+>','',x))[:200])
# annual checklist
def annual_ck(h):
    m=re.search(r'<section class="part" id="annual">(.*?)</section>',h,re.S).group(1)
    return re.findall(r'<ol class="checklist".*?</ol>', m, re.S)
print('annual ol.checklist identical:', annual_ck(old)==annual_ck(new), len(annual_ck(new)))
