# -*- coding: utf-8 -*-
"""M01 獨立查證：主計總處 cpispl.xls（CPI 2021=100）＋央行 a13rate.xls（五大銀行存放款利率歷史）"""
import openpyxl, xlrd, os
from decimal import Decimal, ROUND_HALF_UP
D=os.path.dirname(os.path.abspath(__file__))
SCR='/private/tmp/claude-501/-Users-linyenchu-Cladue-Code/f330c746-4fb1-4319-8da3-61dfb142160e/scratchpad'
def h(x,n='0.01'): return float(Decimal(str(x)).quantize(Decimal(n),rounding=ROUND_HALF_UP))

# ---- CPI ----
b=xlrd.open_workbook(os.path.join(SCR,'cpispl.xls')); s=b.sheet_by_name('CPI')
cpi_jan={}; cpi_avg={}
for r in range(s.nrows):
    try: y=int(float(str(s.cell_value(r,0)).strip()))+1911
    except: continue
    try: cpi_jan[y]=float(s.cell_value(r,1))
    except: pass
    try: cpi_avg[y]=float(s.cell_value(r,13))
    except: pass
print('CPI 2005 平均 %.2f / 1月 %.2f' % (cpi_avg[2005], cpi_jan[2005]))
print('CPI 2025 平均 %.2f / 1月 %.2f' % (cpi_avg[2025], cpi_jan[2025]))
print('CPI 2021 平均 %.2f （確認基期 2021=100）' % cpi_avg[2021])
print('物價 20 年（1月→1月）：%.4f 倍 → 漲 %.1f%%' % (cpi_jan[2025]/cpi_jan[2005], (cpi_jan[2025]/cpi_jan[2005]-1)*100))
print('物價 20 年（年平均）：%.4f 倍 → 漲 %.1f%%' % (cpi_avg[2025]/cpi_avg[2005], (cpi_avg[2025]/cpi_avg[2005]-1)*100))
s2=b.sheet_by_name('年增率'); yoy={}
for r in range(s2.nrows):
    try: y=int(float(str(s2.cell_value(r,0)).strip()))+1911
    except: continue
    try: yoy[y]=float(s2.cell_value(r,13))
    except: pass
print('年增率 2022/2023/2024/2025 =', [yoy.get(y) for y in (2022,2023,2024,2025)])

# ---- 五大銀行一年期定存（固定），每年 1 月 ----
wb=openpyxl.load_workbook(os.path.join(SCR,'a13rate.xlsx'), data_only=True)
FIVE=['台銀','合庫','一銀','華銀','彰銀']   # 央行「五大銀行」
ALL=wb.sheetnames
def series(sheet):
    ws=wb[sheet]; out={}
    for r in range(6, ws.max_row+1):
        k=str(ws.cell(r,1).value)
        if len(k)!=5 or not k.isdigit(): continue
        y=int(k[:3])+1911; m=int(k[3:])
        v=ws.cell(r,14).value            # 定存 一年期 固定
        try: out[(y,m)]=float(v)
        except: pass
    return out
S={n:series(n) for n in ALL}
print('\n工作表:', ALL)
print('年 | ' + ' | '.join(ALL) + ' | 五大平均 | 六家平均')
jan5={}; jan6={}
for y in range(2005,2026):
    row=[S[n].get((y,1)) for n in ALL]
    f=[S[n][(y,1)] for n in FIVE if (y,1) in S[n]]
    a=[v for v in row if v is not None]
    jan5[y]=sum(f)/len(f); jan6[y]=sum(a)/len(a)
    print(y, ' | '.join('%.4f'%v if v is not None else '  -  ' for v in row), '| %.4f | %.4f'%(jan5[y],jan6[y]))
print('\n書上：2005 年 1 月 1.59%、2022 年 1 月 0.77%、2024 年 1 月 1.58%、2025 年起 1.70%')
for y in (2005,2022,2024,2025):
    print('  %d：五大平均 %.4f → 兩位 %.2f；台銀 %.3f' % (y, jan5[y], h(jan5[y]), S['台銀'][(y,1)]))
# 逐年續存 20 年（2005-01 存入，每年 1 月續存，到 2025-01）
for name,jan in (('五大平均',jan5),('六家平均',jan6),('台銀',{y:S['台銀'][(y,1)] for y in range(2005,2026)})):
    v=1.0
    for y in range(2005,2025): v*= (1+jan[y]/100)
    print('%s：20 年逐年續存 = %.4f 倍（100 元 → %.1f 元）' % (name, v, v*100))
# 用書上印出來的 4 個數字無法還原全部，改用四捨五入到兩位的五大平均
v=1.0
for y in range(2005,2025): v*= (1+h(jan5[y])/100)
print('五大平均(先四捨五入兩位)：%.4f 倍' % v)

# ---- 追加：年平均口徑（裁判加驗，書上用的是每年 1 月）----
print('\n=== 追加：一年期定存「年平均」 vs 書上的「每年 1 月」 ===')
def year_avg(y):
    vs=[]
    for m in range(1,13):
        row=[S[n][(y,m)] for n in ALL if (y,m) in S[n]]
        if row: vs.append(sum(row)/len(row))
    return sum(vs)/len(vs) if vs else None
for y in (2022,2023,2024,2025):
    print('  %d：年平均 %.3f%%　每年1月 %.3f%%　CPI年增率 %.2f%%' % (y, year_avg(y), jan6[y], yoy[y]))
print('  書上「那幾年的一年期定存只有約 0.77%% 到 1.58%%」')
print('  → 2022–2024 逐月區間 %.3f%% ~ %.3f%%；年平均區間 %.2f%% ~ %.2f%%'
      % (min(min(sum([S[n][(y,m)] for n in ALL if (y,m) in S[n]])/len([1 for n in ALL if (y,m) in S[n]]) for m in range(1,13)) for y in (2022,2023,2024)),
         max(max(sum([S[n][(y,m)] for n in ALL if (y,m) in S[n]])/len([1 for n in ALL if (y,m) in S[n]]) for m in range(1,13)) for y in (2022,2023,2024)),
         min(year_avg(y) for y in (2022,2023,2024)), max(year_avg(y) for y in (2022,2023,2024))))
v=1.0
for y in range(2005,2025): v*= (1+year_avg(y)/100)
print('  20 年逐年續存改用「年平均」：%.4f 倍（100 元 → %.1f 元）' % (v, v*100))
print('  CPI 20 年（1月→1月）1.3230；（年平均）1.2932')
