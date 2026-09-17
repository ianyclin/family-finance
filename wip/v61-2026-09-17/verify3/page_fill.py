import fitz, re, sys
base='/Users/linyenchu/Cladue Code/family-finance/'
f=sys.argv[1] if len(sys.argv)>1 else base+'export/隔離人性-理財新手完整指南-v6.1.pdf'
d=fitz.open(f)
rows=[]
for i,p in enumerate(d):
    t=re.sub(r'\s+','',p.get_text())
    # vertical fill: max y of text/drawings/images
    ys=[b[3] for b in p.get_text('blocks')]
    try:
        ys+= [dr['rect'].y1 for dr in p.get_drawings()]
    except Exception: pass
    for img in p.get_image_info(): ys.append(img['bbox'][3])
    H=p.rect.height
    fill=(max(ys)/H) if ys else 0
    rows.append((i+1,len(t),round(fill,2)))
print('pages',len(rows))
for r in sorted(rows,key=lambda r:r[2])[:12]: print('lowfill',r)
for r in sorted(rows,key=lambda r:r[1])[:12]: print('lowchars',r)
