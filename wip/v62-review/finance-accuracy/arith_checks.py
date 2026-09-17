# 機械核對：表二、四個人、費用差、甜蜜點表、60萬表、物價倍數
import math
def fv_monthly(pmt, r, n):  # 月底投入、按月複利
    i=r/12; m=n*12
    return pmt*((1+i)**m-1)/i if i else pmt*m
print('表二 每月1000 (萬):')
for r in [0.02,0.03,0.036,0.04]:
    print(r,[round(fv_monthly(1000,r,n)/1e4,1) for n in [5,7,10,15,20,25,30]])
print('表二 10萬:')
for r in [0.02,0.036,0.04]:
    print(r,[round(1e5*(1+r/12)**(12*n)/1e4,1) for n in [5,7,10,15,20,25,30]])
print('物價倍數',[round(1.02**n,2) for n in [5,10,15,20,25,30,35,40]])
print('購買力',[round(100/1.02**n) for n in [10,20,30]])
print('四個人 6%:', round(fv_monthly(5000,.06,40)/1e4), round(fv_monthly(5000,.06,30)/1e4),
      round(fv_monthly(5000,.06,10)*(1+.005)**(360)/1e4), round(fv_monthly(5000,.017,40)/1e4))
print('費用差:', round(fv_monthly(5000,.06,30)/1e4), round(fv_monthly(5000,.05,30)/1e4))
for r in [.04,.06,.07]:
    print('滿足點',r,[round(math.log(1/s)/math.log(1+r),1) for s in [.5,1/3,.25]])
# 60 萬表：每年底 6 萬、7%
import itertools
bal=0;t=0;prev=0;target=60e4;out=[]
# continuous-time: FV = 6e4*((1.07^t)-1)/0.07 solve t
for k in range(1,11):
    tt=math.log(1+k*60e4*0.07/6e4)/math.log(1.07)
    out.append(round(tt-prev,2)); prev=tt
print('60萬格',out)
print('70/4',math.log(2)/math.log(1.04))
print('2%實質 存一半',round(math.log(2)/math.log(1.02),1),'1.5%',round(math.log(2)/math.log(1.015),1))
print('XIRR例', )
