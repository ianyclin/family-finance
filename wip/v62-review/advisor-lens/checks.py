import math
def fv_monthly(pv, pmt_fn, r, n):
    i=r/12; v=pv
    for m in range(1,n+1):
        v=v*(1+i)+pmt_fn(m)
    return v
# 小芸阿哲 頭期款: 120萬 + 3萬/月, 84 months
for r in (0.02,0.017,0.015):
    for p in (2.5,2.9,3.0):
        print('down', r, p, round(fv_monthly(120, lambda m:p, r, 84),1))
# 甜蜜點 with 2% growth in contributions, annual
def sweet(r,g):
    fv=0;c=1
    for n in range(1,80):
        fv=fv*(1+r)+c
        if fv*r>=c*(1+g): return n
        c*=1+g
for r in (0.04,0.06,0.07):
    print('sweet',r,sweet(r,0),sweet(r,0.02))
# 80/20 threshold breach one-year gain
x=(0.85*20)/(80*0.15); print('gain needed',x)
# 小安 year5 value with schedule
def pmt(m):
    if m<=10: return 0.2
    if m<27: return 0.5
    return 0.65
print('xiaoan y5',fv_monthly(0,pmt,0.036,60), 'y20', fv_monthly(0,pmt,0.036,240))
print('xiaoan y20 base',fv_monthly(0,lambda m:0.2 if m<=10 else 0.5,0.036,240))
# annualized vs cumulative spread 20y
print((1.06**20),(1.18**20))
print('10y -1%', 0.99**10)
# crash rebalance for 80/20
s,d=80*0.5,20; tot=s+d; print('ratio after crash',s/tot, 'move',0.8*tot-s)
# retiree 60/40 with 40 = 5y buffer
s,d=60*0.5,40; tot=s+d; print('ret ratio',s/tot,'move',0.6*tot-s,'def left',d-(0.6*tot-s))
# chen
s,d=445.2*0.5,667.8; tot=s+d; print('chen',s/tot, 0.4*tot-s, d-(0.4*tot-s))
