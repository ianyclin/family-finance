import re, html
base="/Users/linyenchu/Cladue Code/family-finance/"
new=open(base+"guide/index.html",encoding="utf-8").read()
def sec(h,sid):
    m=re.search(r'<section class="part" id="%s">'%re.escape(sid),h); n=h.find('<section class="part"',m.end()); return h[m.start():n]
def plain(s):
    s=re.sub(r'<a class="xref" href="#([^"]+)">(.*?)</a>',r'⟦\2→\1⟧',s)
    s=re.sub(r'<[^>]+>','',s); return html.unescape(s)
changed={"annual","cases","firstmonth","s1","s10","s11","s12","s13","s3","s5","s7","s8","steps","ten","why","withdraw","lifecycle","start","products","costs"}
for sid in ["s2","s6","s9","s10","s12","s13","steps"]:
    t=plain(sec(new,sid))
    for m in re.finditer(r'⟦([^⟧]*)→([^⟧]+)⟧',t):
        if m.group(2) in changed:
            print(sid,"|",m.group(2),"|",t[max(0,m.start()-70):m.end()+50].replace("\n"," "))
