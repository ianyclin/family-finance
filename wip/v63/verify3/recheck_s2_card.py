# 驗證員（judge）獨立重算：第 2 節「報酬率不等於報酬」四個數字，不 import calc_core
from decimal import Decimal, ROUND_HALF_UP
def fv(p0, rate, months, c):
    r = rate/100/12; v = p0
    for _ in range(months): v = v*(1+r)+c
    return v
def hu(x, q): return Decimal(str(x)).quantize(Decimal(q), rounding=ROUND_HALF_UP)
v = fv(0, 4, 120, 5000); put = 5000*120; gain = v-put
print('到期 %.2f 元 → %s 萬（書上 73.6）' % (v, hu(v/10000,'0.1')))
print('報酬 %.2f 元 → %s 萬（書上 13.6）' % (gain, hu(gain/10000,'0.1')))
print('報酬 ÷ 5,000 = %.4f → %s 倍（書上 27）' % (gain/5000, hu(gain/5000,'1')))
print('1 萬元個股要漲 %.4f%% → %s%%（書上 1,362）' % (gain/10000*100, hu(gain/10000*100,'1')))
