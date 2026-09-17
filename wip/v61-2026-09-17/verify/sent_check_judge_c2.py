import re, html
ROOT="/Users/linyenchu/Cladue Code/family-finance/"
def plain(s):
    s=re.sub(r'<img[^>]*>','',s)
    s=re.sub(r'<[^>]+>','',s); s=html.unescape(s)
    return re.sub(r'\s+','',s)
newfull=plain(open(ROOT+"guide/index.html",encoding='utf-8').read())
for sid in ['annual','withdraw','lifecycle','costs','products','glossary']:
    o=open(f'jc-{sid}-old.txt').read(); n=plain(open(f'jc-{sid}-new.html').read())
    parts=[p for p in re.split(r'(?<=[。？！；：])|\n',o) if p and len(re.sub(r'\s','',p))>3]
    miss_sec=[]; miss_all=[]
    for p in parts:
        q=re.sub(r'\[→#[^\]]+\]','',p); q=re.sub(r'\s+','',q).replace('|','')
        if not q: continue
        if q not in n: miss_sec.append(q)
        if q not in newfull: miss_all.append(q)
    print('=====',sid,'not in new section:',len(miss_sec),' not anywhere:',len(miss_all))
    for q in miss_sec: print('  [sec]', ('ANYWHERE-MISSING ' if q in miss_all else '(elsewhere) '), q[:160])
