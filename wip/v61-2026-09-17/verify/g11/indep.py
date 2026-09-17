# 獨立重算（不沿用 g11_us.py / g11_tw.py / v61_g11_ath_returns.py 的程式碼）
import csv, math, datetime as dt
D='/Users/linyenchu/Cladue Code/family-finance/research/data/'

def stats(xs):
    xs=sorted(xs); n=len(xs)
    med = xs[n//2] if n%2 else (xs[n//2-1]+xs[n//2])/2
    return dict(n=n, mean=round(100*sum(xs)/n,3), median=round(100*med,3),
                pos=round(100*sum(1 for x in xs if x>0)/n,3), mn=round(100*xs[0],2), mx=round(100*xs[-1],2))

# ---- US: Shiller, log-sum total return ----
rows=[r for r in csv.reader(open(D+'shiller_sp_monthly.csv'))][1:]
keep=[]
for r in rows:
    if float(r[2])==0: break
    keep.append((r[0][:7], float(r[1]), float(r[2])))
logs=[0.0]
for (m0,p0,_),(m1,p1,d1) in zip(keep, keep[1:]):
    logs.append(logs[-1]+math.log((p1+d1/12.0)/p0))
M=[k[0] for k in keep]; N=len(logs)
print('US months', N, M[0], M[-1])
def us(strict):
    rec=[None]
    for t in range(1,N):
        prior=max(logs[:t])
        rec.append(logs[t]>prior if strict else logs[t]>=prior)
    print(' strict' if strict else ' ties-in', 'record months', sum(rec[1:]))
    for Y in (1,5):
        k=12*Y; g={'ath':[], 'non':[], 'all':[]}
        for t in range(1,N-k):
            a=math.exp((logs[t+k]-logs[t])/Y)-1
            g['all'].append(a); g['ath' if rec[t] else 'non'].append(a)
        for kk in g: print('  US',Y,'y',kk,stats(g[kk]))
    # 1929-09 recovery
    t=M.index('1929-09'); back=next(s for s in range(t+1,N) if logs[s]>=logs[t])
    lo=min(range(t,back),key=lambda s:logs[s])
    print('  1929-09 back', M[back], back-t, 'months; low', M[lo], round(100*(math.exp(logs[lo]-logs[t])-1),1))
    return rec
us(False); us(True)

# ---- TW: daily, 1y calendar window via pointer walk ----
tw=[(dt.date.fromisoformat(a), float(b)) for a,b in list(csv.reader(open(D+'taiex_tr_monthly_raw.csv')))[1:]]
n=len(tw)
def same_day_next_year(d):
    try: return d.replace(year=d.year+1)
    except ValueError: return d.replace(year=d.year+1, day=28)
for strict in (False, True):
    hi=tw[0][1]; flag=[False]
    for i in range(1,n):
        v=tw[i][1]; f = v>hi if strict else v>=hi
        flag.append(f); hi=max(hi,v)
    g={'ath':[], 'non':[], 'all':[]}; j=0
    for i in range(1,n):   # 排除第一天（和模組同）；all 若含第一天 n 會 +1
        tgt=same_day_next_year(tw[i][0])
        if tgt>tw[-1][0]: break
        while j+1<n and tw[j+1][0]<=tgt: j+=1
        a=tw[j][1]/tw[i][1]-1
        g['all'].append(a); g['ath' if flag[i] else 'non'].append(a)
    print('TW', 'strict' if strict else 'ties-in', 'ATH days', sum(flag))
    for kk in g: print('  TW 1y', kk, stats(g[kk]))
    # 5y too
    g5={'ath':[], 'non':[]}; j=0
    for i in range(1,n):
        d=tw[i][0]
        try: tgt=d.replace(year=d.year+5)
        except ValueError: tgt=d.replace(year=d.year+5, day=28)
        if tgt>tw[-1][0]: break
        while j+1<n and tw[j+1][0]<=tgt: j+=1
        a=(tw[j][1]/tw[i][1])**(1/5)-1
        g5['ath' if flag[i] else 'non'].append(a)
    for kk in g5: print('  TW 5y', kk, stats(g5[kk]))

# ATH 叢集數：相鄰新高日間隔超過 60 個交易日才算新的一段
idx=[i for i in range(1,n) if flag[i]]
clusters=1+sum(1 for a,b in zip(idx,idx[1:]) if b-a>60)
print('TW ATH clusters (gap>60 trading days):', clusters)
starts=[tw[idx[0]][0]]+[tw[b][0] for a,b in zip(idx,idx[1:]) if b-a>60]
print(' cluster starts', [s.isoformat() for s in starts])
