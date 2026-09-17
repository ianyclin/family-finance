import re, sys
from struct_lib import *
h=load(sys.argv[1])
hb=re.sub(r'<(style|script)\b.*?</\1>',lambda m:' '*len(m.group(0)),h,flags=re.S)
secs=sections(h); order=[s['id'] for s in secs]
def sec_at(i):
    cur=None
    for s in secs:
        if s['start']<=i: cur=s['id']
    return cur
anc=anchor_sec(h)
# A) links with directional words in 40 chars before or 15 after
DIR=r'(前面|後面|上面|下面|上方|下方|下一節|上一節|前一節|後一節|往下|往回|往前|往後|最前面|最後面|書末|接著|稍後|剛才|讀過|前幾節|後幾節|本附錄|附錄|回頭|先回|再回|回到)'
print('=== A: links with directional context (cross-section only)')
for m in re.finditer(r'<a\b[^>]*href="#([\w-]+)"[^>]*>(.*?)</a>', hb, re.S):
    tgt=m.group(1); src=sec_at(m.start())
    if tgt not in anc or src is None: continue
    tsec=anc[tgt]['id']
    if tsec==src: continue
    before=text(hb[max(0,m.start()-160):m.start()])[-40:]
    after=text(hb[m.end():m.end()+80])[:15]
    ctx=before+'【'+text(m.group(2))+'】'+after
    if re.search(DIR, before[-25:]+'|'+after):
        rel='FWD' if order.index(tsec)>order.index(src) else 'BACK'
        print(src,'->',tsec,rel,'|',ctx)
print('=== B: section-level directional words (no link needed)')
t_all=[]
for s in secs:
    body=re.sub(r'<(style|script)\b.*?</\1>','',s['body'],flags=re.S)
    tx=text(body)
    for m in re.finditer(r'(上一節|下一節|前一節|後一節|前面幾節|後面幾節|前幾節|後幾節|前面各節|後面各節|前面的章節|後面的章節|前面的節|後面的節|本附錄|附錄|書末|全書最後|最後一節|前面十|後面這幾節|前面講|後面講|接下來幾節|下面幾節|上面幾節|往下翻|往回翻|往前翻|往後翻|開始前」|「開始前|先看懂，再決定|實作附錄|本書的主體|維護」|人生階段|查證」|開始做」|最前面)', tx):
        print(s['id'],'|',tx[max(0,m.start()-40):m.end()+30])
