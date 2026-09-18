import sys, os, re, json
sys.path.insert(0, '/Users/linyenchu/Cladue Code/family-finance/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v63_g02_sequence_risk as G
from _render import render, visible_numbers, flat_numbers, ROOT

res = G.compute()
json.dumps(res)
d = G.chart(res)
assert set(d) == {'title', 'sub', 'svgs', 'extras', 'caption'} and len(d['svgs']) == 2

# 1. 兩條線：同一組報酬、同樣提領、平均一樣；不提領時終點相同
a, b = res['people']
assert sorted(a['returns_pct']) == sorted(b['returns_pct'])
assert a['returns_pct'] != b['returns_pct']
assert a['end_wan'] < b['end_wan']
assert res['mean_return_pct'] == 6.5
assert (a['end_wan_rounded'], b['end_wan_rounded']) == (36, 106)
assert res['no_withdrawal_end_wan_rounded'] == 148

# 2. 一定要標「示意」，而且不得出現 Vanguard 的逐年數字（原文沒有公布）
vis = re.sub(r'<[^>]+>', ' ', d['title'] + d['sub'] + ''.join(d['svgs']) + d['extras'] + d['caption'])
assert '示意' in d['sub'] and '示意圖，不是市場資料' in vis
# 圖上只准提到正文那個真實例子的存在，不准出現它的結果數字（原文沒公布逐年資料）
for bad in ('23 年', '30 萬', '50 萬', '2.5 萬'):
    assert bad not in vis, bad
assert '原文只公布結果、沒有公布逐年資產' in vis

# 3. 指南原文有 A、B 兩人各 100 萬、每年領一樣多的設定
g = open(os.path.join(ROOT, 'guide/index.html'), encoding='utf-8').read()
assert '兩個人退休時都有 100 萬，每年都拿一樣多的錢出來花，十年下來的平均報酬也一樣' in g
assert 'id="lifecycle-sequence"' in g

# 4. 圖上出現的數字都在 compute 結果裡
nums, alltext = visible_numbers(d)
flat = flat_numbers(res)
const = {'0', '100', '200', '300', '2', '4', '6', '8'}   # y 軸刻度（萬）與 x 軸年份刻度
missing = [n for n in nums if n not in flat and n not in const]
assert not missing, missing

# 5. 不替讀者下結論
for bad in ('所以要', '應該', '一定會', '不要投資'):
    assert bad not in vis, bad

shots = render('sequence-risk', d, desktop_h=820, mobile_h=1000)
print('A end %d 萬  B end %d 萬  平均 %s%%  不提領 %d 萬'
      % (a['end_wan_rounded'], b['end_wan_rounded'], res['mean_return_pct'], res['no_withdrawal_end_wan_rounded']))
print('A series:', [r['wan'] for r in a['series']])
print('B series:', [r['wan'] for r in b['series']])
print('caption:', d['caption'])
print('note:', re.sub(r'<[^>]+>', ' ', d['extras']))
print('lead:', res['printed']['lead_sentence'])
print('shots:', *shots, sep='\n  ')
print('OK')
