import sys, os, re, json
sys.path.insert(0, '/Users/linyenchu/Cladue Code/family-finance/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v63_g04_fee_gap as G
from _render import render, visible_numbers, flat_numbers, ROOT

res = G.compute()
json.dumps(res)
d = G.chart(res)
assert set(d) == {'title', 'sub', 'svgs', 'extras', 'caption'} and len(d['svgs']) == 2

# 1. 終值與差距要和 calc-results.json 完全一致
fg = json.load(open(os.path.join(ROOT, 'lite/calc-results.json'), encoding='utf-8'))['fee_gap']
assert (res['end']['6'], res['end']['5'], res['end']['gap_wan']) == (fg['fv_6pct_wan'], fg['fv_5pct_wan'], fg['gap_wan'])
assert res['principal_wan'] == 180

# 2. 指南第 3 節原文有同一組數字
g = open(os.path.join(ROOT, 'guide/index.html'), encoding='utf-8').read()
for s in ('每月投 5,000 元、投 30 年，自己放進去的本金共 180 萬',
          '如果一年長 6%，最後約 502 萬', '只剩 5%，約 416 萬', '三十年後差約 86 萬'):
    assert s in g, s

# 3. 圖上出現的數字都在 compute 結果裡
nums, alltext = visible_numbers(d)
flat = flat_numbers(res)
const = {'1', '2', '3', '4'} | {'0', '100', '200', '300', '400', '500'} | {'5', '15', '25'}
# 「1 個百分點」「第 1 節」「第 3 節」＋ y 軸刻度（萬）＋ x 軸年份刻度
missing = [n for n in nums if n not in flat and n not in const]
assert not missing, missing

# 4. 不下結論、不推薦商品
vis = re.sub(r'<[^>]+>', ' ', alltext)
for bad in ('一定', '保證', '建議買', '應該選'):
    assert bad not in vis, bad
assert '不是市場預測' in vis

shots = render('fee-gap', d, desktop_h=820, mobile_h=1000)
print('end:', res['end'], 'principal:', res['principal_wan'])
print('caption:', d['caption'])
print('note:', re.sub(r'<[^>]+>', ' ', d['extras']))
print('lead:', res['printed']['lead_sentence'])
print('numbers on chart:', nums)
print('shots:', *shots, sep='\n  ')
print('OK')
