import re, sys
from html.parser import HTMLParser
ROOT="/Users/linyenchu/Cladue Code/family-finance/"
OUT=ROOT+"wip/v61-2026-09-17/verify/jt/"
def section_html(s, sid):
    m=re.search(r'<section[^>]*id="%s"[^>]*>'%re.escape(sid), s)
    start=m.start(); depth=0
    for t in re.finditer(r'<(/?)section\b', s[start:]):
        if t.group(1)=='': depth+=1
        else:
            depth-=1
            if depth==0:
                return s[start:start+t.end()+1]
class T(HTMLParser):
    BLOCK={'p','li','h1','h2','h3','h4','tr','div','summary','details','br','table','ol','ul','section','figcaption'}
    def __init__(s): super().__init__(); s.out=[]
    def handle_starttag(s,tag,a):
        if tag in s.BLOCK: s.out.append('\n')
        if tag in ('td','th'): s.out.append(' | ')
        if tag=='a':
            d=dict(a)
            if d.get('href','').startswith('#'): s.out.append('[%s→%s]'%('term' if 'term' in (d.get('class') or '') else 'x', d['href']))
    def handle_endtag(s,tag):
        if tag in s.BLOCK: s.out.append('\n')
    def handle_data(s,d): s.out.append(d)
def text(h):
    t=T(); t.feed(h); x=''.join(t.out)
    return '\n'.join(l.strip() for l in x.split('\n') if l.strip())
old=open(ROOT+"guide/index.v61-pre-w1.backup.html",encoding='utf-8').read()
new=open(ROOT+"guide/index.html",encoding='utf-8').read()
for sid in sys.argv[1:]:
    for tag,s in (('old',old),('new',new)):
        h=section_html(s,sid)
        open(OUT+f"{sid}-{tag}.html","w").write(h)
        open(OUT+f"{sid}-{tag}.txt","w").write(text(h))
        print(sid,tag,len(h))
