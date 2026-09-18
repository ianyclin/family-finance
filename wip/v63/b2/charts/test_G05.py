import sys, os, re, json
sys.path.insert(0, '/Users/linyenchu/Cladue Code/family-finance/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v63_g05_safety_steps as G
from _render import render, visible_numbers, flat_numbers, ROOT

res = G.compute()
json.dumps(res)
d = G.chart(res)
assert set(d) == {'title', 'sub', 'svgs', 'extras', 'caption'} and len(d['svgs']) == 2

# 1. 五階的名稱要對得上指南「投資前的安全順序」那五點的標題
g = open(os.path.join(ROOT, 'guide/index.html'), encoding='utf-8').read()
sec = g[g.find('id="start"'):g.find('</section>', g.find('id="start"'))]
for s in ('<strong>看懂每月現金流。</strong>', '<strong>先處理高利率債務。</strong>',
          '<strong>留緊急預備金。</strong>', '<strong>補上重大風險保障。</strong>',
          '<strong>把錢按使用日期分桶。</strong>'):
    assert s in sec, s
assert [x['name'] for x in res['steps']] == ['看懂每月現金流', '先處理高利率債務', '留緊急預備金',
                                             '補上重大風險保障', '把錢按使用日期分桶']
assert res['source']['action_sentence'] in re.sub(r'<[^>]+>', '', sec)

# 2. 不重畫三個桶（那是第 11 節 buckets 的工作）
vis = re.sub(r'<[^>]+>', ' ', d['title'] + d['sub'] + ''.join(d['svgs']) + d['caption'])
assert '一年內' not in vis and '一到五年' not in vis
assert 'data-chart="buckets"' in g

# 3. 這張圖不產生新數字：圖面上只有第 11 節那個節號
nums, alltext = visible_numbers(d)
assert nums == ['11', '4'] or set(nums) <= {'11', '4', '5'}, nums

shots = render('safety-steps', d, desktop_h=760, mobile_h=900)
print('steps:', [x['name'] for x in res['steps']], '→', res['top'])
print('caption:', d['caption'])
print('note:', re.sub(r'<[^>]+>', ' ', d['extras']))
print('lead:', res['printed']['lead_sentence'])
print('numbers on chart:', nums)
print('shots:', *shots, sep='\n  ')
print('OK')
