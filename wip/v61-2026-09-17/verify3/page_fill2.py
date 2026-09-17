import fitz, re, sys
base='/Users/linyenchu/Cladue Code/family-finance/'
f=sys.argv[1] if len(sys.argv)>1 else base+'export/隔離人性-理財新手完整指南-v6.1.pdf'
d=fitz.open(f)
rows=[]
for i,p in enumerate(d):
    pix=p.get_pixmap(dpi=30, colorspace=fitz.csGRAY)
    w,h=pix.width,pix.height; s=pix.samples
    content=[y for y in range(h) if min(s[y*w:(y+1)*w])<200]
    # ignore top/bottom 7% (header/footer)
    body=[y for y in content if 0.07*h<y<0.93*h]
    last=max(body)/h if body else 0
    ink=len(body)/h
    txt=[b for b in p.get_text('blocks') if b[1]>0.05*p.rect.height and b[3]<0.95*p.rect.height]
    rows.append((i+1,round(last,2),round(ink,2)))
print('pages',len(rows))
for r in sorted(rows,key=lambda r:r[1])[:14]: print('lastrow',r)
