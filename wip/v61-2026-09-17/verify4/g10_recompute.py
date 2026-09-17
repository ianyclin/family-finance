# 獨立重算 G10 圖下 note／圖說／lead 裡的數字（不 import 模組的計算函式），half-up 一位
import re, html, xlrd
from decimal import Decimal, ROUND_HALF_UP
def hu(x): return Decimal(repr(x*100)).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP)
sh=xlrd.open_workbook('research/data/damodaran_histret.xls').sheet_by_name('Returns by year')
hdr=next(r for r in range(sh.nrows) if str(sh.cell_value(r,0)).strip()=='Year')
names=[str(sh.cell_value(hdr,c)).strip() for c in range(sh.ncols)]
cs=[i for i,n in enumerate(names) if n.startswith('S&P 500 (includes dividends)')][0]
cb=[i for i,n in enumerate(names) if n.startswith('3-month T.Bill')][0]
cd=[i for i,n in enumerate(names) if n.startswith('US T. Bond')][0]
D={}
for r in range(hdr+1,sh.nrows):
    y=sh.cell_value(r,0)
    if isinstance(y,float) and 1900<y<2100: D[int(y)]=(sh.cell_value(r,cs),sh.cell_value(r,cb),sh.cell_value(r,cd))
last=max(D); print('columns',names[cs],'|',names[cb],'|',names[cd],'last',last)
def path(start,idx=1):
    s,b=0.8,0.2; out=[]
    for y in range(start,last+1):
        s*=1+D[y][0]; b*=1+D[y][idx]; out.append((y,s/(s+b)))
    return out
out_strict=lambda w: abs(w-0.8)>0.05
out_round=lambda w: abs(hu(w)-80)>=5
p=path(1990)
fb=next(x for x in p if out_strict(x[1]))
print('1990 first breach',fb[0],'year#',fb[0]-1990+1,hu(fb[1]))
print('back inside after breach',[y for y,w in p if y>fb[0] and not out_strict(w)])
print('2008',hu(dict(p)[2008]),'end',last,hu(p[-1][1]))
pb=path(1990,2); print('bond 2008',hu(dict(pb)[2008]), 'bond 2002 inside?', not out_strict(dict(pb)[2002]), 'bond 2008 inside?', not out_strict(dict(pb)[2008]))
print('bond path 1995-2010',[(y,str(hu(w))) for y,w in pb if 1995<=y<=2010])
p2=path(2000); fb2=next(x for x in p2 if out_strict(x[1])); print('2000 start first breach',fb2[0],hu(fb2[1]),'dir','below' if fb2[1]<0.8 else 'above')
for rule,f in (('strict',out_strict),('rounded',out_round)):
    yrs=[]
    for s in range(1928,2022):
        pp=path(s); b=next((y for y,w in pp if f(w)),None); yrs.append(None if b is None else b-s+1)
    v=[y for y in yrs if y is not None]
    n=len(yrs)
    print(rule,'n',n,'never',n-len(v),'min',min(v),'<=4',sum(1 for y in v if y<=4),sum(1 for y in v if y<=4)/n,'<=10',sum(1 for y in v if y<=10),sum(1 for y in v if y<=10)/n,
          '<=3',sum(1 for y in v if y<=3)/n,'<=9',sum(1 for y in v if y<=9)/n)
# bills never negative
print('min bill',min((D[y][1],y) for y in D))
# compare with guide
g=open('guide/index.html',encoding='utf-8').read()
i=g.find('不管它，比例會自己跑掉'); seg=g[i-3000:i+60000]
j=seg.find('class="note"'); note=html.unescape(re.sub('<[^>]+>','',seg[j:seg.find('</p>',j)]))
print('NOTE in guide:\n',note)
# money not in chart: rebalanced vs not final multiple (not printed)
s,b=0.8,0.2
for y in range(1990,last+1): s*=1+D[y][0]; b*=1+D[y][1]
v=1.0
for y in range(1990,last+1): v=v*0.8*(1+D[y][0])+v*0.2*(1+D[y][1])
print('growth multiple no-reb',round(s+b,2),'annual reb',round(v,2))
