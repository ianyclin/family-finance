import csv, bisect, datetime as dt
D='/Users/linyenchu/Cladue Code/family-finance/research/data/'
tw=[(dt.date.fromisoformat(a), float(b)) for a,b in list(csv.reader(open(D+'taiex_tr_monthly_raw.csv')))[1:]]
ds=[d for d,_ in tw]; v=[x for _,x in tw]; n=len(v)
h=v[0]; fl=[False]
for i in range(1,n): fl.append(v[i]>=h); h=max(h,v[i])
for Y in (1,3,5,10):
    res=[]
    for i in range(0,n):
        d=ds[i]
        try: tg=d.replace(year=d.year+Y)
        except ValueError: tg=d.replace(year=d.year+Y, day=28)
        if tg>ds[-1]: break
        j=bisect.bisect_right(ds,tg)-1
        res.append(((v[j]/v[i])**(1/Y)-1, ds[i], fl[i]))
    res.sort()
    print('TW',Y,'worst5', [(round(100*a,2),str(d),f) for a,d,f in res[:5]])
    ath_share_bottom = sum(1 for a,d,f in res[:len(res)//20] if f)/(len(res)//20)
    print('   share of ATH starts in worst 5% of windows', round(100*ath_share_bottom,1), 'base ATH share', round(100*sum(f for _,_,f in res)/len(res),1))
