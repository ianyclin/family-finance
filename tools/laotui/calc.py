"""第七版工具（tools/laotui/laotui-tool.html）的對照用模型。
原為 scratchpad/laotui/calc6.py（第六版，2026-10-11 定版），2026-10-11 搬進 repo、改名，式子一字未改；
第七版只改頁面（補繳那段改帶狀圖），模型與第六版相同，所以熱圖、表格的數字用這支對照。
2026-10-11 自己投的報酬加 9% 一檔（GS），式子不變；掃組合的地方從六組變九組（nine_combos_max）。
tools/v7_g13_laotui.py 的 EXPECT_GRID／EXPECT_FLIP 就是這支的 values_default／flip_default。

以下為第六版原說明：
第六版（tool6，定版）模型：兩個開關（勞退報酬 × 自己投的報酬），稅固定「一次領、免稅額隨物價調」。
產生 tool6-data.json（寫在執行時的目前目錄，重跑覆蓋），並印驗證輸出與「要不要補繳稅，會差多少」那段的數字。"""
import json, itertools
KS=[5,12,20,30,40]
BR=[(610000,0.05,0),(1380000,0.12,42700),(2770000,0.20,153100),(5190000,0.30,430100),(float('inf'),0.40,949100)]
RLS=[0.017,0.021,0.0465]; GS=[0.06,0.075,0.09]
DEF=dict(rl=0.0465,gi=0.075)
CAREER,DY,NHI,EX1,EX2=35,0.03,0.0211,206000,414000
DED=101000+136000   # 退休那年的免稅額＋標準扣除額（115 年度，單身），乘 g
SALARY={5:45000,12:100000,20:150000,30:150000,40:150000}   # 各級距代表月薪（主線給定）
PK={k:round(v*0.06) for k,v in SALARY.items()}             # 雇主與自提都提 6%：2,700／6,000／9,000
FIXED=dict(monthly_by_bracket=PK,salary_by_bracket=SALARY,employer='同額（薪水的 6%）',career='25 歲開始工作、60 歲一次領，年資固定 35 年；已工作年數＝35−n',
           salary_at_retirement=0,path='台股 ETF 配息課稅（殖利率 3%、補充保費 2.11%、5% 級距允許負的配息稅）',tax='一次領，免稅額與級距隨物價每年 1.015^n')
def fv(p,r,n):
    if n<=0: return 0.0
    m=(1+r)**(1/12)-1; return p*((1+m)**(12*n)-1)/m
def tau(t): return 0.28 if t>=0.40 else t-0.085
def ri(t,gi): return gi-DY*(tau(t)+NHI)
def taxT(x,g):
    y=x/g
    for hi,r,d in BR:
        if y<=hi: return g*max(y*r-d,0)
def taxable(L,Y,g):
    lo,hi=EX1*Y*g,EX2*Y*g
    return 0.5*max(min(L,hi)-lo,0)+max(L-hi,0)
def cell(k,n,rl=0.0465,gi=0.075,tax='idx',P=None,nhi=NHI):
    t=k/100; Y=CAREER
    P=PK[k] if P is None else P; A=fv(P,rl,n); E=fv(P,rl,Y); B=fv(P*(1-t),gi-DY*(tau(t)+nhi),n)
    tx=0.0
    if tax!='none':
        g=1.015**n if tax=='idx' else 1.0
        tx=taxT(max(taxable(A+E,Y,g)-DED*g,0),g)-taxT(max(taxable(E,Y,g)-DED*g,0),g)
    return dict(v=(A-tx)/B-1,S=A,A_after=A-tx,E=E,B=B,tax_self=tx,Y=Y)
def val(k,n,**s): return cell(k,n,**s)['v']
def flip(vs):
    for i,v in enumerate(vs):
        if v<0: return i+1
    return None
def gaps(rl,gi):
    """回傳 (不用補 − 隨物價 的最大值與格子, 隨物價 − 凍結 的最大值與格子, 20%/15 年兩邊)"""
    bn=(0.0,None); bf=(0.0,None)
    for k in KS:
        for n in range(1,36):
            i=val(k,n,rl=rl,gi=gi); a=val(k,n,rl=rl,gi=gi,tax='none')-i; b=i-val(k,n,rl=rl,gi=gi,tax='frozen')
            if a>bn[0]+1e-12: bn=(a,(k,n))
            if b>bf[0]+1e-12: bf=(b,(k,n))
    i=val(20,15,rl=rl,gi=gi)
    return bn,bf,(val(20,15,rl=rl,gi=gi,tax='none')-i, i-val(20,15,rl=rl,gi=gi,tax='frozen'))
def main():
    bn,bf,c=gaps(**DEF)
    allg=[]
    for rl,gi in itertools.product(RLS,GS):
        n_,f_,_=gaps(rl,gi)
        if n_[1]: allg.append((n_[0],'不用補',rl,gi)+n_[1])
        if f_[1]: allg.append((f_[0],'免稅額和級距不調',rl,gi)+f_[1])
    M=max(allg)
    out={'note':'第六版（定版）。退休那年扣免稅額＋標準扣除額 237,000×g。60 歲一次領；值＝(A−因自提多繳的稅)/B−1。每月提繳跟著級距走（5%→2,700、12%→6,000、20% 以上→9,000，雇主同額）。兩個開關：勞退報酬（1.7% 保證下限／2.1% 2006–2015 最差十年／4.65% 2006–2025，皆出自勞動基金運用局表 2）、自己投的毛報酬（6%／7.5%／9%，台股 ETF 配息稅另扣）。稅固定為一次領、免稅額隨物價調。',
         'fixed':FIXED,'default':DEF,'options':{'rl':RLS,'gi':GS},'brackets':KS,'years':list(range(1,36)),
         'bracket_table_115':[[hi if hi!=float('inf') else None,r,d] for hi,r,d in BR],
         'exempt_35y':{'tax_free_upto':EX1*CAREER,'half_upto':EX2*CAREER},
         'values_default':{str(k):[round(val(k,n,**DEF),6) for n in range(1,36)] for k in KS},
         'flip_default':{str(k):flip([val(k,n,**DEF) for n in range(1,36)]) for k in KS},
         'detail_default':{str(k):[{x:(round(y,6) if x=='v' else round(y)) for x,y in cell(k,n,**DEF).items()} for n in range(1,36)] for k in KS},
         'all_combos':{f'rl={rl},gi={gi}':{str(k):[round(val(k,n,rl=rl,gi=gi),6) for n in range(1,36)] for k in KS} for rl,gi in itertools.product(RLS,GS)},
         'flip_all_combos':{f'rl={rl},gi={gi}':{str(k):flip([val(k,n,rl=rl,gi=gi) for n in range(1,36)]) for k in KS} for rl,gi in itertools.product(RLS,GS)},
         'tax_gap':{'default_no_tax_max':{'pp':round(bn[0]*100,4),'bracket':bn[1][0],'years':bn[1][1]},
                    'default_frozen_max':{'pp':round(bf[0]*100,4),'bracket':bf[1][0],'years':bf[1][1]},
                    'default_20pct_15y':{'no_tax_pp':round(c[0]*100,4),'frozen_pp':round(c[1]*100,4)},
                    'nine_combos_max':{'pp':round(M[0]*100,4),'side':M[1],'rl':M[2],'gi':M[3],'bracket':M[4],'years':M[5]}}}
    # 12% 級距月薪敏感度：月薪 10 萬～15.4 萬（提繳上限 15 萬），每 1,000 元
    sens=[]
    for sal in range(100000,153001,1000):   # 154,000 已屬 20% 級距
        p=min(sal,150000)*0.06; f=flip([val(12,n,P=p,**DEF) for n in range(1,36)]); sens.append((sal,f))
    base=sens[0][1]; first=next((s for s,f in sens if f is not None and f<base),None)
    fl=[f for s,f in sens if first and s>=first]
    out['sens_12pct']={'flip_by_salary':{str(s):f for s,f in sens},'earlier_from_salary':first,'flip_range_from_there':[min(fl),max(fl)] if fl else None}
    nh=max(cell(k,n,nhi=0,**DEF)['B']/cell(k,n,**DEF)['B']-1 for k in KS for n in range(1,36))   # 自己投那條路被低估的比例
    nhv=max(val(k,n,**DEF)-val(k,n,nhi=0,**DEF) for k in KS for n in range(1,36))                   # 對圖上數字的影響
    cr=max(cell(k,n,rl=rl,gi=gi)['B']*DY*0.085 for k in (5,12,20,30) for n in range(1,36) for rl,gi in itertools.product(RLS,GS))   # 40% 用分開計稅、沒有抵減
    out['checks']={'no_nhi_index_path_underestimated_pct':round(nh*100,4),'no_nhi_chart_value_max_pp':round(nhv*100,4),'max_dividend_credit_5to30pct_9combos':round(cr)}
    json.dump(out,open('tool6-data.json','w'),ensure_ascii=False,indent=1)
    print('== 預設 5x7（%）與翻盤年')
    print('     '+' '.join(f'{n:>6}' for n in (5,10,15,20,25,30,35))+'  翻盤年')
    for k in KS:
        vs=[val(k,n,**DEF) for n in range(1,36)]; f=flip(vs)
        print(f'{k:>3}% '+' '.join(f'{vs[n-1]*100:+6.1f}' for n in (5,10,15,20,25,30,35))+f'  {f if f else "—"}')
    print('== 要不要補繳稅，會差多少（預設 4.65%／7.5%）')
    print(f' X 不用補 vs 隨物價 最大 {bn[0]*100:.4f}pp @ {bn[1][0]}% 自提 {bn[1][1]} 年')
    print(f' Y 隨物價 vs 凍結 最大 {bf[0]*100:.4f}pp @ {bf[1][0]}% 自提 {bf[1][1]} 年')
    print(f' Z 20% 自提 15 年：不用補 +{c[0]*100:.4f}pp，凍結 −{c[1]*100:.4f}pp')
    print(f' 九組最大 {M[0]*100:.4f}pp（{M[1]}，勞退 {M[2]}，自己投 {M[3]}，{M[4]}% 自提 {M[5]} 年）')
    print(f' 年資 35 年免稅線 {EX1*CAREER:,}、半數到 {EX2*CAREER:,}')
    print(f"== 12% 敏感度：月薪 {first} 起翻盤年早於 {base}，範圍 {out['sens_12pct']['flip_range_from_there']}")
    print(' '+' '.join(f'{s//1000}k:{f}' for s,f in sens[::2]))
    print(f"== 檢查：不扣補充保費時自己投那條路最多被低估 {nh*100:.4f}%、圖上數字最多差 {nhv*100:.4f}pp；5–30% 級距、9 組股利抵減最大 {cr:,.0f} 元（上限 80,000）")
    print('== 翻盤年（9 組；5/12/20/30/40%）')
    for key,f in out['flip_all_combos'].items(): print(f' {key:<20} '+' '.join(str(f[str(k)] or '—') for k in KS))
    print('== selftest refs')
    for rl,gi in itertools.product(RLS,GS):
        print(f' rl={rl} gi={gi} '+' '.join(f'{k}:'+'/'.join(f'{val(k,n,rl=rl,gi=gi)*100:.4f}' for n in (5,20,35)) for k in KS))
if __name__=='__main__': main()
