# 檢查：台幣一年期定存（五大銀行固定利率平均）逐年滾存，對上 CPI
import csv, collections
rows=list(csv.DictReader(open('A13Rate.csv',encoding='utf-8-sig')))
by=collections.defaultdict(list)
for r in rows:
    ym=r['年月']; v=r['定存利率-一年期-固定']
    if v: by[ym].append(float(v))
def rate(ym):
    return sum(by[ym])/len(by[ym])
# CPI annual averages & Jan values (DGBAS cpispl.xls)
import xlrd
sh=xlrd.open_workbook('cpispl.xls').sheet_by_name('CPI')
cpi={}
for i in range(3,sh.nrows):
    row=sh.row_values(i)
    if isinstance(row[0],float):
        cpi[int(row[0])+1911]=row
def roll(y0,y1):
    g=1.0
    for y in range(y0,y1):
        ym=f'{y-1911:03d}01'
        g*=1+rate(ym)/100
    return g
for y0,y1 in [(2005,2025),(2005,2026),(2016,2026),(2022,2025),(2023,2026)]:
    g=roll(y0,y1) if y1<=2025 or '11501' in by else None
    print(y0,y1,'deposit x', round(roll(y0,min(y1,2025)),4) if True else None)
print('Jan rates:',{y: round(rate(f'{y-1911:03d}01'),3) for y in range(2005,2026)})
print('CPI Jan 2005',cpi[2005][1],'Jan 2025',cpi[2025][1], 'ratio', round(cpi[2025][1]/cpi[2005][1],4))
print('CPI avg 2005',cpi[2005][13],'avg 2024',cpi[2024][13],'avg 2025',cpi[2025][13])
print('deposit roll Jan2005->Jan2025', round(roll(2005,2025),4), 'annualized', round(roll(2005,2025)**(1/20)-1,4))
print('CPI Jan2005->Jan2025 annualized', round((cpi[2025][1]/cpi[2005][1])**(1/20)-1,4))
print('CPI avg2005->avg2025 annualized', round((cpi[2025][13]/cpi[2005][13])**(1/20)-1,4))
