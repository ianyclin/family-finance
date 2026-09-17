import csv, math, datetime as dt, statistics as st
D='/Users/linyenchu/Cladue Code/family-finance/research/data/'
rows=list(csv.reader(open(D+'shiller_sp_monthly.csv')))[1:]
k=[]
for r in rows:
    if float(r[2])==0: break
    k.append((r[0][:7], float(r[1]), float(r[2])))
tr=[1.0]
for a,b in zip(k,k[1:]): tr.append(tr[-1]*(b[1]+b[2]/12)/a[1])
M=[x[0] for x in k]; N=len(tr)
hi=tr[0]; ath=[False]
for v in tr[1:]:
    ath.append(v>=hi); hi=max(hi,v)
def grp(Y, lo='0000', hi_='9999'):
    kk=12*Y; A=[];B=[]
    for t in range(1,N-kk):
        if not (lo<=M[t]<=hi_): continue
        x=(tr[t+kk]/tr[t])**(1/Y)-1
        (A if ath[t] else B).append(x)
    f=lambda xs: (len(xs), round(100*st.fmean(xs),1), round(100*st.median(xs),1), round(100*sum(x>0 for x in xs)/len(xs),1))
    return f(A), f(B)
for lab,lo,hi_ in (('US 1950+','1950-01','9999'),('US <1950','0000','1949-12'),('US 1871-1928','0000','1928-12')):
    for Y in (1,5,10):
        print(lab,Y,'ATH',*grp(Y,lo,hi_)[0:1],'nonATH',grp(Y,lo,hi_)[1])
idx=[t for t in range(1,N) if ath[t]]
print('US ATH clusters gap>12m:', 1+sum(1 for a,b in zip(idx,idx[1:]) if b-a>12))
# TW excluding 2007 starts (sensitivity only)
tw=[(dt.date.fromisoformat(a), float(b)) for a,b in list(csv.reader(open(D+'taiex_tr_monthly_raw.csv')))[1:]]
n=len(tw); h=tw[0][1]; fl=[False]
for i in range(1,n):
    fl.append(tw[i][1]>=h); h=max(h,tw[i][1])
import bisect
ds=[d for d,_ in tw]
def tw_grp(Y, excl=None):
    A=[];B=[]
    for i in range(1,n):
        d=ds[i]
        try: tg=d.replace(year=d.year+Y)
        except ValueError: tg=d.replace(year=d.year+Y, day=28)
        if tg>ds[-1]: break
        if excl and excl[0]<=d<=excl[1]: continue
        j=bisect.bisect_right(ds,tg)-1
        x=(tw[j][1]/tw[i][1])**(1/Y)-1
        (A if fl[i] else B).append(x)
    f=lambda xs: (len(xs), round(100*st.fmean(xs),1), round(100*st.median(xs),1), round(100*sum(x>0 for x in xs)/len(xs),1))
    return f(A), f(B)
for Y in (1,3,5):
    print('TW all',Y,tw_grp(Y))
    print('TW excl 2006-07..2007-12 starts',Y,tw_grp(Y,(dt.date(2006,7,1),dt.date(2007,12,31))))
