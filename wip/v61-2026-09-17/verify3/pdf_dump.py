import fitz, json, sys
base='/Users/linyenchu/Cladue Code/family-finance/'
out=base+'wip/v61-2026-09-17/verify3/'
for name,f in [('full','export/隔離人性-理財新手完整指南-v6.1.pdf'),('work','export/隔離人性-可列印工作表-v6.1.pdf')]:
    d=fitz.open(base+f)
    pages=[p.get_text() for p in d]
    with open(out+name+'-pages.txt','w',encoding='utf-8') as w:
        for i,t in enumerate(pages,1):
            w.write('\n=====PAGE %d=====\n'%i); w.write(t)
    print(name,len(pages))
