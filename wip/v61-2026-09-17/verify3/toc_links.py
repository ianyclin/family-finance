import fitz,re
base='/Users/linyenchu/Cladue Code/family-finance/'
d=fitz.open(base+'export/隔離人性-理財新手完整指南-v6.1.pdf')
# heading page map from h2 font 20.6
heads={}
for pi,p in enumerate(d):
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            sz=max(s['size'] for s in l['spans'])
            if abs(sz-20.6)<0.3:
                heads.setdefault(pi+1,[]).append(''.join(s['text'] for s in l['spans']))
n=0;bad=0
for pn in (0,1):
    p=d[pn]
    for lk in p.get_links():
        if lk.get('kind')!=fitz.LINK_GOTO: continue
        r=lk['from']; words=p.get_textbox(r+(-2,-2,60,2)).replace('\n','')
        dest=lk['page']+1
        m=re.search(r'(\d+)\s*$',p.get_textbox(fitz.Rect(r.x0,r.y0,p.rect.width-30,r.y1+1)).replace('\n',''))
        printed=int(m.group(1)) if m else None
        n+=1
        ok = printed==dest
        if not ok: bad+=1
        print('OK ' if ok else 'BAD', 'printed',printed,'dest',dest, words[:30], '| h2 on dest:', (heads.get(dest) or [''])[0][:20])
print(n,'links',bad,'bad')
