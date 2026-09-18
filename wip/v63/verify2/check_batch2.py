# -*- coding: utf-8 -*-
"""v6.3 第二批裁判檢查（只讀）。exit 0 = 全過。
跑法：python3 wip/v63/verify2/check_batch2.py
"""
import json, re, os, sys
from decimal import Decimal, ROUND_HALF_UP
ROOT = '/Users/linyenchu/Cladue Code/family-finance'
PUB  = os.path.join(ROOT, 'output/full-v60-out.html')
LITE = os.path.join(ROOT, 'lite/index.html')
CALC = os.path.join(ROOT, 'lite/calc-results.json')
fails = []
def chk(name, cond, detail=''):
    print(('OK   ' if cond else 'FAIL ') + name + (('  ' + detail) if detail else ''))
    if not cond: fails.append(name)

S = open(PUB, encoding='utf-8').read()
T = re.sub('<[^>]+>', '', S)
L = re.sub('<[^>]+>', '', open(LITE, encoding='utf-8').read())
C = json.load(open(CALC, encoding='utf-8'))

# ---- 1. F 區口徑 ----
chk('F口徑 十分鐘版七件事', '股票那一塊從最近高點跌 10%、20%、30% 以上各做什麼先寫好' in T)
chk('F口徑 六個最貴的錯', T.count('股票那一塊從最近高點跌 10%、20%、30% 以上各做什麼') >= 1)
chk('F口徑 A–H 清單 F 規則', 'F 規則：股票那一塊從最近高點跌 10%、20%、30% 以上各做什麼' in T)
chk('F口徑 本指南的做法', '跌幅看股票那一塊，從最近的高點算。新存入、領出的錢不算' in T)
chk('F口徑 欄位表 F 跌幅跟什麼比', '例如股票那一塊從最近的高點算，新存入、領出的錢不算' in T)
chk('F口徑 欄位表第 19 格', '預設：股票那一塊，從最近的高點算；新存入、領出的錢不算' in T)
chk('F口徑 小安 F 規則', '跌幅怎麼算：股票那一塊，從最近的高點算；新存入、領出的錢不算。' in T)
chk('F口徑 第14節 市場下跌20%', '跌幅看股票那一塊，從最近的高點算。' in T)
chk('F口徑 演練卡（完整版）', 'F 區量的也是股票那一塊，不用換算：這一步的股票跌 50%，直接看 F 區「跌 30% 以上」那一格。' in T)
chk('F口徑 演練卡（工作表）', 'F 區量的也是股票那一塊，不用換算：這一步的股票跌 50%，直接看 F 區「跌 30% 以上」那一格。' in L)
chk('F口徑 無殘留「投資圈…跌 10%」',
    not re.search(r'投資圈[^。]{0,40}跌 10%', T), '殘留 0 處')
DEF3 = '□台幣定存　□短中期或整體投資等級債 ETF（跌 10%）　□長天期 20 年以上債 ETF（10% 不適用）'
chk('E區防守放三格 完整版空白版', DEF3 in T)
chk('E區防守放三格 工作表', DEF3 in L)

# ---- 2. 提領規則卡 / 勞保短卡 對 calc-results ----
fd = C['fee_demo_0_5pct']['chen']
chk('126 萬 = floor_5y_gap_wan', fd['floor_5y_gap_wan'] == 126.0 and '頭五年的缺口 126 萬放台幣定存' in T)
chk('25.2 萬 = first_year_withdrawal.amount_wan', fd['first_year_withdrawal']['amount_wan'] == 25.2)
chk('1,088 萬 = fv_2031_wan["46"].low', fd['fv_2031_wan']['46']['low'] == 1088)
chk('2.3% = pct_of_46_low', fd['first_year_withdrawal']['pct_of_46_low'] == 2.3)
chk('2.3% 可由 25.2/1088 重算', round(25.2 / 1088 * 100, 1) == 2.3, '%.4f%%' % (25.2/1088*100))
chk('33.6 萬 = stage2_amount_wan', fd['first_year_withdrawal']['stage2_amount_wan'] == 33.6)
chk('33.6 萬 = (21000+7000)*12', (21000 + 7000) * 12 / 10000 == 33.6)
chk('卡上五個數字逐字在文中',
    '第一年拿 25.2 萬，是 1,088 萬的 2.3%；勞退月退發完後改領一年 33.6 萬' in T)
chk('卡上數字＝第 12 節陳大哥', '提領率：第一年提領約 25.2 萬，是 1,088 萬的 2.3%' in T)
for w in ('應該', '最好', '推薦', '務必'):
    i = S.find('id="withdraw-rules"'); j = S.find('<div class="data-card"', i)
    chk('提領規則卡不含「%s」' % w, w not in re.sub('<[^>]+>', '', S[S.rfind('<div class="data-card"',0,i):j]))
chk('提領規則卡自陳不給比例', '下面只列常見做法和代價，不給建議比例。' in T)

# 勞保局逐字（2026-09-18 自行開頁核對）
chk('勞保 年金兩式', '平均月投保薪資×年資×0.775%＋3,000 元，或×1.55%' in T)
chk('勞保 45/50 個月', '超過 15 年的部分每滿 1 年給 2 個月，最多 45 個月' in T and '合併最多 50 個月' in T)
chk('勞保 60/36 個月平均', '年金取加保期間最高 60 個月的平均，一次請領取退保當月往前 36 個月的平均' in T)
chk('勞保 98 年一次請領資格', '98 年 1 月 1 日勞保年金上路以前就有勞保年資' in T)
chk('勞保 核付後不得變更', '老年給付一經勞保局核付就不得變更' in T)

# Vanguard（2026-09-18 自行下載原文核對）
chk('VG 2020 上下限 5%/1.5%', '每年最多比去年多拿 5%、最多少拿 1.5%（Vanguard 的例子）' in T)
chk('VG 2020 5% ceiling 註記在第 4 頁', '5% ceiling、−1.5% floor，第 4 頁' in T)
chk('VG 2020 deviate 第 18 頁', 'causes the allocation to deviate from the target by more than 5 percent' in T and '第 18 頁' in T)
chk('VG PRI 0.5pp 註記頁碼＝8（原文 printed page 8）',
    'Reducing your withdrawal rate by 0.5 percentage points can make your savings last another five years」，第 8 頁' in T,
    '目前書上寫第 7 頁 → 這條預期 FAIL')

# ---- 3. 五張圖 ----
def wan(v): return int(Decimal(str(v/10000)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
A = [-35,-25,-15,20,18,22,15,25,12,28]; B = [20,18,22,15,25,12,28,-35,-25,-15]
def run(rs):
    v = 100.0
    for r in rs: v = (v - 5) * (1 + r/100)
    return v
nw = 100.0
for r in A: nw *= 1 + r/100
sr = C['sequence_risk']
chk('G02 同一組報酬換順序', sorted(A) == sorted(B) and sr['people'][0]['returns_pct'] == A and sr['people'][1]['returns_pct'] == B)
chk('G02 A 末 36 萬', round(run(A)) == 36 == sr['people'][0]['end_wan_rounded'])
chk('G02 B 末 106 萬', round(run(B)) == 106 == sr['people'][1]['end_wan_rounded'])
chk('G02 不提領 148 萬', round(nw) == 148 == sr['no_withdrawal_end_wan_rounded'])
chk('G02 平均 6.5%', sum(A)/10 == 6.5 == sr['mean_return_pct'])
def fv(m, n, a):
    r = a/100/12; v = 0.0
    for _ in range(n): v = v*(1+r) + m
    return v
chk('G04 6% → 502 萬', wan(fv(5000,360,6)) == 502 == C['fee_gap']['fv_6pct_wan'])
chk('G04 5% → 416 萬', wan(fv(5000,360,5)) == 416 == C['fee_gap']['fv_5pct_wan'])
chk('G04 差 86 萬', 502-416 == 86 == C['fee_gap']['gap_wan'])
chk('G04 本金 180 萬', wan(5000*360) == 180)
db = C['drag_breakdown']
chk('G03 四項加總 100', sum(p['share_pct'] for p in db['parts']) == 100 == db['total_share_pct'])
chk('G03 稅＋費 66', 34+32 == 66 == db['trade_cost_share_pct'])
chk('G03 34/32 在第 9 節原文', '證交稅約 34%、手續費約 32%' in T)
chk('G03 27 在第 9 節原文', '買賣本身的價差損失約 27%' in T)
chk('G03 7 在第 9 節原文', '進出時機約 7%' in T)
for n in ('這筆錢','先顧好的','現在','試算','風險','規則','家人'):
    chk('G01 區名逐字：%s' % n, ('>%s：</strong>' % n) in S.replace('<strong>A ','<strong>').replace('<strong>B ','<strong>') or ('%s：' % n) in T)
chk('G01 H 區名逐字（圖上「紀錄」vs 原文「改計畫紀錄」）',
    'H 改計畫紀錄：' in T and '>紀錄<' not in re.sub(r'\s+','',S[S.find('data-chart="plan-flow"'):S.find('</figure>', S.find('data-chart="plan-flow"'))]),
    '目前 FAIL：圖上是「H 紀錄」')
for n in ('看懂每月現金流','先處理高利率債務','留緊急預備金','補上重大風險保障','把錢按使用日期分桶'):
    chk('G05 階名逐字：%s' % n, ('<strong>%s。</strong>' % n) in S)
for cid in ('plan-flow','sequence-risk','drag-breakdown','fee-gap','safety-steps'):
    m = re.search(r'data-chart="%s"' % cid, S); e = S.find('</figure>', m.start())
    t = re.sub('<[^>]+>', '', re.sub(r'<svg.*?</svg>', '', S[m.start():e], flags=re.S))
    chk('%s 圖說/note 無下結論用語、無舊口徑' % cid,
        not any(w in t for w in ('建議','應該','最好','推薦','投資圈')))

# ---- 4. 副標 ----
subs = re.findall(r'<p class="subtitle"[^>]*>(.*?)</p>', S, re.S)
eyebrow = re.search(r'<div class="eyebrow">(.*?)</div>', S).group(1)
chk('副標已落地', any('給台灣新手的長期投資與行為紀律指南' in x for x in subs))
chk('副標不與 eyebrow 打架（兩者都是一句話書籍描述）',
    not ('長期投資指南' in eyebrow and any('長期投資與行為紀律指南' in x for x in subs)),
    'eyebrow=%s' % re.sub('<[^>]+>','',eyebrow))

# ---- 5. 常設 ----
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import guidetools as G
def blocks(path, cls, tag):
    h = G.read(path)
    if tag == 'div': return [h[a:b] for a,b in G.div_blocks(h, cls)]
    return re.findall(r'<%s\b(?=[^>]*?(?<![\w-])class="%s")[^>]*>(.*?)</%s>' % (tag,cls,tag), h, re.S)
OLD = os.path.join(ROOT,'wip','v63','before-batch2.html'); NEW = os.path.join(ROOT,'guide','index.html')
for cls,tag,n in (('story','div',25), ('key','mark',14)):
    o = blocks(OLD,cls,tag); nn = blocks(NEW,cls,tag)
    chk('%s %d 條逐字不變' % (cls,n), o == nn and len(nn) == n, '%d→%d' % (len(o),len(nn)))

print()
print('FAILS: %d' % len(fails))
for f in fails: print('  -', f)
sys.exit(1 if fails else 0)
