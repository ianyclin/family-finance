# -*- coding: utf-8 -*-
"""裁判獨立重算：只借用 tools/calc_core.py 的 fv() 約定（年率/12 按月複利、月底投入），
不 import lite/calc-results.json 的任何現成結果。half-up。"""
from decimal import Decimal, ROUND_HALF_UP

def fv(p0, rate, months, contrib):
    f = contrib if callable(contrib) else (lambda m: contrib)
    r = rate / 100 / 12; v = p0
    for m in range(1, months + 1):
        v = v * (1 + r) + f(m)
    return v

def h1(x): return float(Decimal(str(x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
def h0(x): return int(Decimal(str(x)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
def wan(x): return h0(x/10000)
def wan1(x): return h1(x/10000)
CPI = {5:1.10,10:1.22,15:1.35,20:1.49,25:1.64,30:1.81,35:2.00,40:2.21}
def cpi(y):
    for k in sorted(CPI):
        if y <= k: return CPI[k]
    raise ValueError(y)
def look(stock_pct):
    f = stock_pct/100
    return tuple(h1(f*v + (1-f)*2) for v in (4,6,7))
def m_of(year, month):  # 第 1 個月 = 2026-10
    return (year-2026)*12 + (month-10) + 1

OK=[];BAD=[]
def chk(label, got, want):
    (OK if got==want else BAD).append((label, got, want))

print('=== 查表（股票比例 → 低/中/高，以及減 0.5%）===')
for s in (0,20,40,60,70,80):
    lo,mi,hi = look(s)
    print(f'  股票{s}%: {lo}/{mi}/{hi}  減0.5 → {h1(lo-0.5)}/{h1(mi-0.5)}/{h1(hi-0.5)}')
chk('查表 80% 低', look(80)[0], 3.6); chk('查表 80% 中', look(80)[1], 5.2); chk('查表 80% 高', look(80)[2], 6.0)
chk('查表 60% 低', look(60)[0], 3.2); chk('查表 60% 中', look(60)[1], 4.4); chk('查表 60% 高', look(60)[2], 5.0)
chk('查表 40% 低', look(40)[0], 2.8); chk('查表 40% 中', look(40)[1], 3.6); chk('查表 40% 高', look(40)[2], 4.0)
chk('查表 70% 低', look(70)[0], 3.4); chk('查表 70% 中', look(70)[1], 4.8); chk('查表 70% 高', look(70)[2], 5.5)
chk('查表 20% 低', look(20)[0], 2.4)

print()
print('=== 小安（第 11 節）===')
N = m_of(2046,9); print('  期數 2026-10→2046-09 =', N)
chk('小安期數', N, 240)
chk('小安目標 134×1.49', h0(134*1.49), 200)
print('  134 × 1.49 =', round(134*1.49,2))
base = lambda m: 2000 if m<=10 else 5000
for rate,label,want in ((3.1,'低',160),(4.7,'中',191),(5.5,'高',209)):
    v = fv(0, rate, 240, base); print(f'  {label} {rate}%: {v:,.0f} 元 = {wan1(v)} 萬 → 印 {wan(v)} 萬 (書:{want})')
    chk(f'小安 {label}', wan(v), want)
principal = 10*2000 + 230*5000
print('  本金:', principal, '=', principal/10000, '萬 (書:117 萬)'); chk('小安本金', wan1(principal), 117.0)
m27 = m_of(2028,12); print('  2028-12 = 第', m27, '個月')
sched65 = lambda m: 2000 if m<=10 else (5000 if m<m27 else 6500)
v = fv(0,3.1,240,sched65); print(f'  ①多存 6,500: {v:,.0f} = {wan1(v)} 萬 → 印 {wan(v)} (書:203)'); chk('小安多存6500', wan(v), 203)
p2 = 10*2000 + (m27-11)*5000 + (240-m27+1)*6500
print('  多存後本金:', p2, '=', p2/10000, '萬 (書:149.1 萬)'); chk('小安多存本金', wan1(p2), 149.1)
sched60 = lambda m: 2000 if m<=10 else (5000 if m<m27 else 6000)
v = fv(0,3.1,240,sched60); print(f'  每月 6,000: {wan1(v)} 萬 → 印 {wan(v)} (書:189)'); chk('小安6000', wan(v), 189)
# ②延後
found=None
for m in range(241, 600):
    yrs = m/12; t = 134*cpi(yrs)*10000
    if fv(0,3.1,m,base) >= t: found=(m,yrs,cpi(yrs),t); break
m,yrs,c,t = found
yy = 2026 + (9 + m - 1)//12; mm = (9 + m - 1)%12 + 1
print(f'  ②延後: 第 {m} 個月 = {yy}-{mm:02d}, 年數 {yrs:.2f}, 物價倍數 {c}, 目標 {t/10000:.2f} 萬 → 印 {h0(t/10000)} 萬')
print(f'     多出 {(m-240)/12:.2f} 年 → 一位小數 {h1((m-240)/12)} (書:2053 年 6 月左右、多約 6.8 年、243 萬)')
chk('小安延後目標萬', h0(t/10000), 243); chk('小安延後年月', (yy,mm), (2053,6)); chk('小安延後多幾年', h1((m-240)/12), 6.8)
print('     判斷: 多出年數 %.2f > 最多能延 5 年 → 走不通 %s' % ((m-240)/12, (m-240)/12 > 5))
# E 區壓力測試
v5 = fv(0,3.1,60,base); print(f'  第 5 年: {v5:,.0f} = {wan1(v5)} 萬 → 印 {wan(v5)} (書:34)'); chk('小安第5年', wan(v5), 34)
for amt,want in ((34,(11,14,16)),(203,(65,81,97))):
    got = tuple(h0(amt*0.8*d) for d in (0.4,0.5,0.6))
    print(f'  壓力 {amt} 萬 80%: {got} (書:{want})'); chk(f'小安壓力{amt}', got, want)
print('  第5年少14萬÷1.10 =', round(14/1.10,2), '→', h0(14/1.10), '萬；÷3.8 =', round(h0(14/1.10)/3.8,2), '→', h1(h0(14/1.10)/3.8), '(書:13 萬、3.4 個月)')
chk('小安第5年換月薪', (h0(14/1.10), h1(h0(14/1.10)/3.8)), (13, 3.4))
print('  2046少81萬÷1.49 =', round(81/1.49,2), '→', h0(81/1.49), '萬；÷3.8 =', round(h0(81/1.49)/3.8,2), '→', h0(h0(81/1.49)/3.8), '(書:54 萬、約 14 個月)')
chk('小安2046換月薪', (h0(81/1.49), h0(h0(81/1.49)/3.8)), (54, 14))
