# 驗算 proposal-core-edition.md 的所有數字
# 規則：每月月底投入、年率/12 按月複利；報酬率一律用「印在查表上的一位小數」
from datetime import date

def fv(p0, rate, months, contrib):
    """contrib: function(month_index 1-based) -> amount"""
    r = rate / 100 / 12
    v = p0
    for m in range(1, months + 1):
        v = v * (1 + r) + contrib(m)
    return v

def w(x):  # 萬，四捨五入
    return round(x / 10000)

def w1(x):
    return round(x / 10000, 1)

print("== 查表：股票比例 -> 低/中/高（股票 4/6/7，防守 1.7）")
table = {}
for s in range(100, -1, -10):
    f = s / 100
    row = [round(f * k + (1 - f) * 1.7, 2) for k in (4, 6, 7)]
    table[s] = [round(x, 1) for x in row]
    print(s, row, table[s])

print("\n== 物價倍數 1.02^n")
for n in (5, 7, 10, 15, 20, 25, 30):
    print(n, round(1.02 ** n, 3))

print("\n== 倍數表（低那一列用的報酬率）：每月投 1,000 元 n 年後（萬）；現有 10 萬 n 年後（萬）")
for rate in (1.7, 2.2, 2.6, 3.1, 3.5, 4.0):
    a = [round(fv(0, rate, n * 12, lambda m: 1000) / 10000, 1) for n in (5, 7, 10, 15, 20, 25, 30)]
    b = [round(fv(100000, rate, n * 12, lambda m: 0) / 10000, 1) for n in (5, 7, 10, 15, 20, 25, 30)]
    print(rate, "月投1000:", a, " 現有10萬:", b)

print("\n== 壓力表 100 萬")
for s in (100, 80, 60, 40, 20):
    st = s / 100
    for d in (0, 10):
        print(s, "防守跌", d, [round(100 * st * x + 100 * (1 - st) * d / 100) for x in (0.4, 0.5, 0.6)])

print("\n== 小安：2026-10 起 240 個月；1-10 月 2,000，之後 5,000")
base = lambda m: 2000 if m <= 10 else 5000
for rt in table[80]:
    print("rate", rt, w(fv(0, rt, 240, base)), fv(0, rt, 240, base))
print("本金", sum(base(m) for m in range(1, 241)))
for x in (6000, 6500, 7000):
    c = lambda m, x=x: 2000 if m <= 10 else (5000 if m <= 26 else x)
    print("第27個月起", x, "低3.5:", fv(0, 3.5, 240, c), "中5.1:", w(fv(0, 5.1, 240, c)), "高5.9:", w(fv(0, 5.9, 240, c)), "本金", sum(c(m) for m in range(1, 241)))
c7 = lambda m: 2000 if m <= 10 else (5000 if m <= 26 else 7000)
for mm in (60, 84, 120):
    print("小安(7000案) 第", mm, "個月 低3.5:", w1(fv(0, 3.5, mm, c7)))
# 何時到 100 萬（低 3.5）
v = 0; r = 3.5 / 1200
for m in range(1, 241):
    v = v * (1 + r) + c7(m)
    if v >= 1_000_000:
        print("小安 7000 案 到 100 萬：第", m, "個月"); break
print("月份換算：第1個月=2026-10；第27個月=", (2026*12+9+26)//12, (2026*12+9+26)%12+1, "；第240個月=", (2026*12+9+239)//12, (2026*12+9+239)%12+1)

print("\n== 阿凱：現有 30 萬，每月 1 萬，240 個月")
for lab, s in (("六四", 60), ("八二", 80)):
    print(lab, [w1(fv(300000, rt, 240, lambda m: 10000)) for rt in table[s]])
print("六四 每月 1.2 萬 低3.1:", w1(fv(300000, 3.1, 240, lambda m: 12000)))
print("六四 每月 1.15 萬 低3.1:", w1(fv(300000, 3.1, 240, lambda m: 11500)))
v = 300000; r = 3.1 / 1200; m = 0
while v < 4_500_000:
    m += 1; v = v * (1 + r) + 10000
print("六四 每月1萬 到450萬要", m, "個月 =", round(m / 12, 1), "年")
print("阿凱 20 年後六四低情境", w1(fv(300000, 3.1, 240, lambda m: 10000)), "股票60% 跌40/50/60:", [w1(fv(300000, 3.1, 240, lambda m: 10000) * 0.6 * x) for x in (.4, .5, .6)])

print("\n== 小芸與阿哲 頭期款桶：現有 120 萬，1.7%")
for x in (25000, 30000):
    print(x, "84 月:", w1(fv(1_200_000, 1.7, 84, lambda m, x=x: x)), "72 月:", w1(fv(1_200_000, 1.7, 72, lambda m, x=x: x)))
v = 1_200_000; r = 1.7 / 1200; m = 0
while v < 4_000_000:
    m += 1; v = v * (1 + r) + 25000
print("2.5 萬 到 400 萬要", m, "個月，比 84 多", m - 84)
v72 = fv(1_200_000, 1.7, 72, lambda m: 25000)
print("第72個月(2032-09) 若六成股票跌50% 少", w1(v72 * 0.6 * 0.5))
print("長期桶 現有 40 萬 每月 1 萬 360 月 八二:", [w1(fv(400000, rt, 360, lambda m: 10000)) for rt in table[80]])

print("\n== 陳大哥")
lab = 45800 * 30 * 0.0155
print("勞保", lab)
gap = 50000 - lab - 7000
print("缺口/月", gap, "取 2.2 萬 -> 年", 22000 * 12)
for k in (25, 33, 40):
    print(k, "倍", 264000 * k / 10000, "x1.104=", round(264000 * k * 1.02 ** 5 / 10000, 1))
for lab2, s in (("四六", 40), ("七三", 70)):
    print(lab2, table[s], [w1(fv(8_000_000, rt, 60, lambda m: 30000)) for rt in table[s]])
low46 = fv(8_000_000, 2.6, 60, lambda m: 30000)
print("第一年提領 26.4萬x1.104=", round(264000 * 1.02 ** 5 / 10000, 1), "占四六低情境", round(264000 * 1.02 ** 5 / low46 * 100, 2), "%")
for s, d in ((70, 0), (40, 0), (40, 10)):
    print(s, d, [round(800 * s / 100 * x + 800 * (1 - s / 100) * d / 100) for x in (.4, .5, .6)])
print("五年缺口 今天:", 26.4 * 5, "2031:", round(26.4 * 5 * 1.02 ** 5, 1))
print("換倉稅 個股200萬x0.3%=", 2_000_000 * 0.003, " ETF280萬x0.1%=", 2_800_000 * 0.001)

print("\n== XIRR")
def xirr(flows):
    d0 = flows[0][0]
    f = lambda r: sum(a / (1 + r) ** ((d - d0).days / 365) for d, a in flows)
    lo, hi = -0.9, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > 0: lo = mid
        else: hi = mid
    return mid
print(xirr([(date(2027, 1, 1), -100000), (date(2027, 7, 1), -20000), (date(2027, 12, 31), 128000)]))

print("\n== 補充")
c65 = lambda m: 2000 if m <= 10 else (5000 if m <= 26 else 6500)
print("小安 6500 案", [w1(fv(0, rt, 240, c65)) for rt in (3.5, 5.1, 5.9)], "本金", sum(c65(m) for m in range(1, 241)))
for mm in (60, 120):
    print(" 第", mm, "月 低3.5", w1(fv(0, 3.5, mm, c65)))
v = 0; r = 3.5/1200
for m in range(1, 241):
    v = v*(1+r)+c65(m)
    if v >= 500000 and 'h50' not in dir(): h50 = m; print(" 到50萬 第", m, "月")
    if v >= 1000000: print(" 到100萬 第", m, "月"); break
mo = lambda k: ((2026*12+9+k-1)//12, (2026*12+9+k-1)%12+1)
print(" 月份", mo(27), mo(h50), mo(m), "阿凱271月", mo(271))
print("陳大哥 二八 2.2", w1(fv(8_000_000, 2.2, 60, lambda m: 30000)), " 全定存 1.7", w1(fv(8_000_000, 1.7, 60, lambda m: 30000)))
print("小安 壓力 36.4萬(第60月)?", w1(fv(0,3.5,60,c65)*0.8*0.5), "200萬x.8x.5=80 ; 80/3.8=", round(80/3.8,1), "；第5年少/3.8", round(fv(0,3.5,60,c65)*0.8*0.5/38000,1))
print("阿凱 116萬/平均月收入5萬=", round(116.3/5,1), " 30萬x.6x.5=9 ; 9/5=", 9/5)
print("50 列 half-up: 4.35->4.4")
