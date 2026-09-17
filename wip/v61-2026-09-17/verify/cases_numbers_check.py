import sys, re
sys.path.insert(0,'tools')
import guidetools as g
from collections import Counter
base='wip/v61-2026-09-17/verify/'
a=g.to_text(base+'cases-old.html'); b=g.to_text(base+'cases-new.html')
num=lambda s: Counter(re.findall(r'\d+(?:[.,]\d+)*', s))
ca,cb=num(a),num(b)
lost=ca-cb
for k,v in lost.items():
    print(k, 'old',ca[k],'new',cb[k], 'ZERO!' if cb[k]==0 else '')
