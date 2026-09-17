import re,sys,difflib
a=open(sys.argv[1],encoding='utf-8').read(); b=open(sys.argv[2],encoding='utf-8').read()
def tok(s): return re.findall(r'<[^>]*>|[^<]+',s)
ta,tb=tok(a),tok(b)
sm=difflib.SequenceMatcher(None,ta,tb,autojunk=False)
n=0
for op,i1,i2,j1,j2 in sm.get_opcodes():
    if op=='equal': continue
    n+=1
    ctx=''.join(ta[max(0,i1-3):i1])[-200:]
    print(f'=== #{n} {op} (tok {i1})')
    print('CTX:',ctx.replace('\n','⏎'))
    print('-:',''.join(ta[i1:i2])[:3000].replace('\n','⏎'))
    print('+:',''.join(tb[j1:j2])[:3000].replace('\n','⏎'))
