import fitz, re, json, difflib, os
R="/Users/linyenchu/Cladue Code/family-finance"
B="/private/tmp/claude-501/-Users-linyenchu-Cladue-Code/f330c746-4fb1-4319-8da3-61dfb142160e/scratchpad/ffbefore"
OUT=os.path.dirname(os.path.abspath(__file__))
def pages(p): 
    d=fitz.open(p); return d,[pg.get_text() for pg in d]
for kind,name in (('lite','隔離人性-可列印工作表-v6.2.pdf'),('full','隔離人性-理財新手完整指南-v6.2.pdf')):
    da,a=pages(os.path.join(R,'export',name)); db,b=pages(os.path.join(B,'export',name))
    print('==',kind,'after pages',len(a),'before pages',len(b))
    changed=[i+1 for i in range(max(len(a),len(b))) if (a[i] if i<len(a) else None)!=(b[i] if i<len(b) else None)]
    print('pages with text change:',changed)
    for i in changed:
        ta=a[i-1] if i<=len(a) else ''; tb=b[i-1] if i<=len(b) else ''
        sm=difflib.ndiff(tb.splitlines(),ta.splitlines())
        print('-- page',i); print('\n'.join(l for l in sm if l[:1] in '+-')[:3000])
    # blank-ish pages
    print('low-text pages after:',[(i+1,len(re.sub(r'\s','',t))) for i,t in enumerate(a) if len(re.sub(r'\s','',t))<250])
    print('low-text pages before:',[(i+1,len(re.sub(r'\s','',t))) for i,t in enumerate(b) if len(re.sub(r'\s','',t))<250])
    if kind=='lite':
        t=a[3]; print('P4 TEXT:\n'+t)
        print('第N章:',re.findall(r'第\s*[0-9０-９一二三四五六七八九十]+\s*章',''.join(a)),'附錄:',re.findall(r'附錄\s*\S',''.join(a)))
        pix=da[3].get_pixmap(dpi=110); pix.save(os.path.join(OUT,'v7-worksheet-p4.png'))
        # page 4 lowest text y
        blocks=da[3].get_text('blocks'); print('p4 last text bottom %.0f / page h %.0f' % (max(bl[3] for bl in blocks), da[3].rect.height))
        print('links on p4:',[l.get('uri') or l.get('page') for l in da[3].get_links()])
