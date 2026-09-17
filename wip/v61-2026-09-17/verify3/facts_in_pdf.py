import fitz,re
base='/Users/linyenchu/Cladue Code/family-finance/'
d=fitz.open(base+'export/隔離人性-理財新手完整指南-v6.1.pdf')
P=re.sub(r'\s+','',''.join(p.get_text() for p in d))
for l in open(base+'lite/facts.txt',encoding='utf-8'):
    l=l.rstrip('\n')
    if not l.strip() or l.startswith('#'): continue
    s=l.split(':',1)[1] if l.startswith('full-only:') else l
    s2=re.sub(r'\s+','',s)
    print('PDF' if s2 in P else 'NOT-IN-PDF', l[:80])
