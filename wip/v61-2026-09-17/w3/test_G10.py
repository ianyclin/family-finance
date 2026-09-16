import sys, os, re, json, subprocess
ROOT = '/Users/linyenchu/Cladue Code/family-finance'
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import v61_g10_rebalance_drift as G
import essay_charts as E
OUT = os.path.dirname(os.path.abspath(__file__))
res = G.compute()
json.dumps(res)   # 可 JSON 化
d = G.chart(res)
assert set(d) == {'title', 'sub', 'svgs', 'extras', 'caption'} and len(d['svgs']) == 2
# 圖上的每個數字都要在 compute 結果裡找得到
blob = json.dumps(res, ensure_ascii=False)
alltext = d['title'] + d['sub'] + ''.join(d['svgs']) + d['extras'] + d['caption']
vis = re.sub(r'<[^>]+>', ' ', alltext)
nums = set(re.findall(r'\d+(?:\.\d+)?', vis))
flat = set()
def walk(o):
    if isinstance(o, dict): [walk(v) for v in o.values()]
    elif isinstance(o, list): [walk(v) for v in o]
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        flat.add(str(o)); flat.add(str(int(o)) if float(o).is_integer() else str(o))
walk(res)
const = {'80', '20', '5', '75', '85', '70', '90', '95', '100', '10', '500'}
missing = sorted(n for n in nums if n not in flat and n not in const)
print('numbers on chart:', sorted(nums)); print('not directly in compute (check):', missing)
fig = E.figure('rebalance-drift', d['title'], d['sub'], d['svgs'], d['caption'], d['extras'])
g = open(os.path.join(ROOT, 'guide/index.html'), encoding='utf-8').read()
css = re.search(r'<style[^>]*>(.*?)</style>', g, re.S).group(1)
page = ('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<style>%s body{background:var(--paper);padding:8px 16px}</style><main style="max-width:760px;margin:auto">%s</main>' % (css, fig))
html = os.path.join(OUT, 'rebalance-drift.html')
open(html, 'w', encoding='utf-8').write(page)
chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
mhtml = os.path.join(OUT, 'rebalance-drift-mobile.html')
open(mhtml, 'w', encoding='utf-8').write(page.replace('max-width:760px', 'max-width:368px').replace('</style>', 'figure.chart svg.d{display:none!important}figure.chart svg.m{display:block!important}figure.chart{padding:14px 12px}</style>'))
for name, size, h in (('rebalance-drift-desktop.png', '900,1000', html), ('rebalance-drift-mobile.png', '500,1200', mhtml)):
    html_ = h
    subprocess.run([chrome, '--headless', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=2',
                    '--screenshot=' + os.path.join(OUT, name), '--window-size=' + size, 'file://' + html_],
                   check=True, capture_output=True)
print('caption:', d['caption']); print(re.sub(r'<[^>]+>', ' ', d['extras']))
