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
const = {'80', '20', '5', '75', '85', '70', '90', '95', '100', '10', '500', '3', '25', '2002', '2000'}  # 3 個月、10 年期、5/25、note 裡的 2002 與 2000 起點年（2000 起點在 alt_starts 的 key）
missing = sorted(n for n in nums if n not in flat and n not in const)
# 驗收 must：防守是 3 個月國庫券，不再印公債版主線數字
from decimal import Decimal, ROUND_HALF_UP
m = res['main']
assert res['source']['columns'][1].startswith('3-month T.Bill')
assert (m['first_breach_year'], m['first_breach_years_after_start'], m['first_breach_stock_pct']) == (1995, 6, 86.1)
assert m['mark_year'] == {'year': 2008, 'stock_pct': 87.7, 'outside_band': True}
assert m['end_stock_pct'] == 98.3 and m['years_outside_band'] == 31 and m['years_back_inside_band_after_breach'] == []
assert (res['alt_starts']['2000']['first_breach_year'], res['alt_starts']['2000']['first_breach_stock_pct']) == (2001, 74.5)
sc = res['all_starts_scan']; assert sc['years_to_breach_min'] == 1 and sc['count'] == 94 and sc['robust_counts']['years_to_breach']['within_4'] == 60 and sc['robust_counts']['years_to_breach']['within_10'] == 90 and '最慢' not in d['extras'] and '規則卡' not in d['extras']
assert res['bond_sensitivity']['mark_year']['stock_pct'] == 78.3
assert '78.3%' not in ''.join(d['svgs']) and '96.6' not in alltext and '85.3' not in alltext
assert '防守用美國 3 個月國庫券代表定存（不跌價、利息低）' in d['extras']
assert '永遠' not in alltext
# half-up：Decimal(repr) 與精確十進位兩種取法一致（印出的值）
def both(x):
    return (Decimal(repr(x)).quantize(Decimal('0.1'), ROUND_HALF_UP), Decimal(x).quantize(Decimal('0.1'), ROUND_HALF_UP))
import v61_g10_rebalance_drift as GG
data = GG.load()[0]
raws = [r['stock_w_raw'] * 100 for r in m['series']]
raws += [r['stock_w'] * 100 for r in GG.drift_path(data, 2000, 2025)] + [r['stock_w'] * 100 for r in GG.drift_path(data, 1990, 2025, 'bond')]
bad = [x for x in raws if len(set(both(x))) > 1]
assert not bad, bad
print('lead:', res['printed']['lead_sentence'])
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
