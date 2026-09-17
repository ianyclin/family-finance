import json, re, html as H, difflib
base='/Users/linyenchu/Cladue Code/family-finance/'
new=open(base+'guide/index.html',encoding='utf-8').read()
def plain(s):
    s=re.sub(r'<svg.*?</svg>','',s,flags=re.S)
    return re.sub(r'\s+','',H.unescape(re.sub(r'<[^>]+>','',s)))
N=plain(new)
for g in ['front','mid','s11','back','s6']:
    for i,x in enumerate(json.load(open(base+f'wip/v61-2026-09-17/fix2/patch-{g}.json',encoding='utf-8'))):
        o=plain(x['old']); n=plain(x['new'])
        sm=difflib.SequenceMatcher(None,o,n,autojunk=False)
        for tag,i1,i2,j1,j2 in sm.get_opcodes():
            if tag in ('delete','replace') and i2-i1>=4:
                frag=o[i1:i2]
                # widen to clause
                a=max([o.rfind(c,0,i1) for c in '。；，：（）']+[-1])+1
                b=min([k for k in [o.find(c,i2) for c in '。；，：（）'] if k>=0]+[len(o)])
                clause=o[a:b]
                found=clause in N
                print(f'[{g}#{i}] removed:「{frag}」 clause:「{clause}」 clause-still-in-guide={found}')
