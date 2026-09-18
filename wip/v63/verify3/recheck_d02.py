from decimal import Decimal, ROUND_HALF_UP
def fv(p0, rate, months, c):
    r = rate/100/12; v=p0
    for m in range(months): v = v*(1+r)+c
    return v
def wan(x): return int(Decimal(str(x/10000)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
def wan1(x): return float(Decimal(str(x/10000)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
print("== 小芸阿哲 頭期款桶 120萬 + 84期, 目標400萬")
for c in (25000,28000,28500,29000,29500,30000,30500):
    v=fv(1_200_000,1.7,84,c)
    print(f"  每月{c}: {wan1(v)}萬 / 整數{wan(v)}萬  夠不夠={v>=4_000_000}")
print("  2% 對照 25k:", wan1(fv(1_200_000,2,84,25000)), " 30k:", wan(fv(1_200_000,2,84,30000)))
# 延後
r=1.7/100/12; v=1_200_000; m=0
while v<4_000_000:
    v=v*(1+r)+25000; m+=1
print(f"  25k 要 {m} 個月, 比84多{m-84}; 起始2026-10 → 第{m}月=", end="")
t=2026*12+(10-1)+(m-1); print('%d-%02d'%(t//12,t%12+1))
print("== 陳大哥 全放定存 800萬 + 每月3萬 60期")
v=fv(8_000_000,1.7,60,30000); print("  1.7%:", wan(v), "萬  wan1=",wan1(v))
v2=fv(8_000_000,2,60,30000); print("  2.0%:", wan(v2),"萬")
v3=fv(8_000_000,1.9,60,30000); print("  股票兩成扣費1.9%:", wan(v3),"萬")
