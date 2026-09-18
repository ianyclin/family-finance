import sys, os, re, json
sys.path.insert(0, '/Users/linyenchu/Cladue Code/family-finance/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v63_g01_plan_flow as G
from _render import render, visible_numbers, flat_numbers, ROOT

res = G.compute()
json.dumps(res)
d = G.chart(res)
assert set(d) == {'title', 'sub', 'svgs', 'extras', 'caption'} and len(d['svgs']) == 2

# 1. 八個區名要和第 11 節那張卡逐字一致
g = open(os.path.join(ROOT, 'guide/index.html'), encoding='utf-8').read()
for key, name in zip('ABCDEFGH', ['這筆錢', '先顧好的', '現在', '試算', '風險', '規則', '家人', '改計畫紀錄']):
    assert '<strong>%s %s：</strong>' % (key, name) in g, (key, name)
assert [s['key'] for s in res['steps']] == list('ABCDEFGH')

# 2. 兩條回頭的出處在原文
for s in ('股票比例要等 E 區做完三問才定：先挑一個打算放的比例試算，寫「暫定」',
          '①多存：每月＿元', '③降低目標', '股票比例降一成（10 個百分點）再演練'):
    assert s in g, s
assert [(l['from'], l['to']) for l in res['loops']] == [('D', 'A'), ('E', 'step')]

# 3. 這張圖不引進新數字：圖面上只准出現原文本來就有的 4、10、20、30、11、12、14、2、3
nums, alltext = visible_numbers(d)
allowed = {'4', '10', '20', '30', '11', '12', '14', '2', '3', '24'}
assert set(nums) <= allowed, sorted(set(nums) - allowed)

# 4. 不推薦商品、不下結論
vis = re.sub(r'<[^>]+>', ' ', alltext)
for bad in ('0050', '006208', 'ETF ', '一定要', '建議你'):
    assert bad not in vis, bad

shots = render('plan-flow', d, desktop_h=1000, mobile_h=1100)
print('order:', res['printed']['order'], 'loops:', res['printed']['loops'])
print('caption:', d['caption'])
print('note:', re.sub(r'<[^>]+>', ' ', d['extras']))
print('lead:', res['printed']['lead_sentence'])
print('numbers on chart:', sorted(set(nums)))
print('shots:', *shots, sep='\n  ')
print('OK')
