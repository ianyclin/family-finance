import sys, os, re, json
sys.path.insert(0, '/Users/linyenchu/Cladue Code/family-finance/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v63_g03_drag_breakdown as G
from _render import render, visible_numbers, flat_numbers, ROOT

res = G.compute()
json.dumps(res)
d = G.chart(res)
assert set(d) == {'title', 'sub', 'svgs', 'extras', 'caption'} and len(d['svgs']) == 2

# 1. 四個比例與 3.8 都要在指南原文裡找得到（這張圖不產生新數字）
g = open(os.path.join(ROOT, 'guide/index.html'), encoding='utf-8').read()
for s in ('每年比「買了不動」少賺 3.8 個百分點',
          '證交稅約 34%、手續費約 32%',
          '買賣本身的價差損失約 27%',
          '進出時機約 7%',
          '1995 到 1999 年'):
    assert s in g, s
assert sum(p['share_pct'] for p in res['parts']) == 100

# 2. 圖上出現的數字都在 compute 結果裡
nums, alltext = visible_numbers(d)
flat = flat_numbers(res)
missing = [n for n in nums if n not in flat]
assert not missing, missing

# 3. 不替讀者下結論、不出現撤掉的 GDP 那句
for bad in ('GDP', '2.2', '所以不要', '應該', '一定'):
    assert bad not in re.sub(r'<[^>]+>', ' ', alltext), bad

shots = render('drag-breakdown', d, desktop_h=760, mobile_h=900)
print('numbers on chart:', nums)
print('caption:', d['caption'])
print('note:', re.sub(r'<[^>]+>', ' ', d['extras']))
print('lead:', res['printed']['lead_sentence'])
print('shots:', *shots, sep='\n  ')
print('OK')
