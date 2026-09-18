"""G07 investor-cycle 自測：內容檢查（六種行為、節號、沒有數字、沒有抄流傳版本的用語）
＋版面檢查（桌面站名兩兩不重疊、不壓到曲線、不超出畫布；手機清單不重疊）＋截圖。

跑法：python3 wip/v63/stock-vs-index/charts/test_G07.py
"""
import sys, os, re, json

sys.path.insert(0, '/Users/linyenchu/Cladue Code/family-finance/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v63_g07_investor_cycle as G
from _render import render, visible_numbers, ROOT

res = G.compute()
json.dumps(res)                      # compute() 要能序列化（只用標準庫型別）
d = G.chart(res)
assert set(d) == {'title', 'sub', 'svgs', 'extras', 'caption'} and len(d['svgs']) == 2

# ---------- 1. 十一站、順序、六種行為都有人接 ----------
st = res['stations']
assert 10 <= len(st) <= 12, len(st)
assert [s['n'] for s in st] == list(range(1, len(st) + 1))
assert [s['t'] for s in st] == sorted(s['t'] for s in st)
for k in '123456':
    assert res['behaviors'][k], ('沒有站接住行為', k, res['behavior_names'][k])

# ---------- 2. 節號只用第 2、6、8、10、11 節，而且節名和書上逐字一致 ----------
g = open(os.path.join(ROOT, 'guide/index.html'), encoding='utf-8').read()
TITLE_IDS = {2: 's2', 6: 's6', 8: 's8', 10: 's10', 11: 's11'}
for sec, (title, _) in G.SECTIONS.items():
    assert '<span class="num">%d</span>%s' % (sec, title) in g, (sec, title)
    assert 'id="%s"' % TITLE_IDS[sec] in g
assert set(s['section'] for s in st) <= set(G.SECTIONS)

# 註解裡「擋它的是哪一句」要是書上的句子（第 2、6、8 節逐字；10、11 節是節錄改寫，單獨挑關鍵字檢查）
for quote in ('前幾年帳戶裡多半是自己存進去的錢，越往後，自己長出來的部分越多。',
              '猜低點要猜對兩次，等待也有代價',
              '賣掉以後，那筆錢就不再跟著漲跌；如果之後還想買回來，就要再猜一次什麼時候買',
              '捨不得認賠',
              '冷卻期',
              '什麼情況才賣',
              '大跌演練'):
    assert quote in g, quote

# ---------- 3. 圖面上不准有數字（節號與站號除外），也不准出現商品代號或結論句 ----------
nums, alltext = visible_numbers(d)
allowed = {'2', '6', '8', '10', '11', '1', '3', '4', '5', '7', '9', '1998'}
assert set(nums) <= allowed, sorted(set(nums) - allowed)
vis = re.sub(r'<[^>]+>', ' ', alltext)
for bad in ('0050', '006208', '台積電', '%', '元', '一定', '建議你', '資料來源'):
    assert bad not in vis, bad
assert '示意' in d['sub'] and '不是任何市場的資料' in d['sub']

# ---------- 4. 站名不是流傳版本的用語 ----------
for s in st:
    for b in G.BANNED:
        assert b not in s['name'] and b not in s['name_mobile'], (s['name'], b)
# 流傳最廣那一版獨有的英文標記，一個都不准出現
for b in ('Euphoria', 'Capitulation', 'Point of maximum', 'Westcore Funds /'):
    assert b not in alltext, b
assert 'Westcore Funds' in vis, 'note 要註明形狀借自哪裡'

# ---------- 5. 桌面版版面：方框兩兩不重疊、不壓曲線、不超出畫布 ----------
lay = G.layout_boxes()
W, H = lay['W'], lay['height']
PAD = 3.0


def overlap(a, b, pad=PAD):
    return (a['x0'] - pad < b['x1'] and b['x0'] - pad < a['x1']
            and a['y0'] - pad < b['y1'] and b['y0'] - pad < a['y1'])


bad = [(a['n'], b['n']) for i, a in enumerate(lay['boxes']) for b in lay['boxes'][i + 1:] if overlap(a, b)]
assert not bad, ('站名互相重疊', bad)
out = [(b['n'], b['x0'], b['x1'], b['y1']) for b in lay['boxes']
       if b['x0'] < 2 or b['x1'] > W - 2 or b['y0'] < 2 or b['y1'] > H - 2]
assert not out, ('站名超出畫布', out)
hit = [(b['n'], round(x), round(y)) for b in lay['boxes'] for x, y in lay['curve']
       if b['x0'] - 2 < x < b['x1'] + 2 and b['y0'] - 2 < y < b['y1'] + 2]
assert not hit, ('站名壓到曲線', hit[:6])
# 站點徽章（r=9）兩兩不重疊
dots = [b['dot'] for b in lay['boxes']]
close = [(i + 1, j + 1) for i in range(len(dots)) for j in range(i + 1, len(dots))
         if (dots[i][0] - dots[j][0]) ** 2 + (dots[i][1] - dots[j][1]) ** 2 < 19 ** 2]
assert not close, ('徽章疊在一起', close)

# ---------- 6. 手機版：清單每一行的站名不會撞到右邊的節號 ----------
m = d['svgs'][1]
mh = float(re.search(r'viewBox="0 0 360 ([\d.]+)"', m).group(1))
for s in st:
    name_w = G.tw(s['name_mobile'], 10.0)
    assert 12 + 19 + name_w < 348 - G.tw('第 %d 節' % s['section'], 10.0) - 6, s['name_mobile']
# 手機曲線上的徽章（r=7.5）不能疊在一起
mx = [12 + (348 - 12) * s['t'] for s in st]
my = [24 + (100 - s['v']) * 1.45 for s in st]
mclose = [(i + 1, j + 1) for i in range(len(st)) for j in range(i + 1, len(st))
          if (mx[i] - mx[j]) ** 2 + (my[i] - my[j]) ** 2 < 16 ** 2]
assert not mclose, ('手機徽章疊在一起', mclose)

shots = render('investor-cycle', d, desktop_h=760, mobile_h=900)

print('desktop viewBox height:', H, ' mobile viewBox height:', mh)
print('stations:')
for line in res['printed']['stations']:
    print('  ', line)
print('mobile:', ' ／ '.join(res['printed']['stations_mobile']))
print('behaviors:', json.dumps(res['behaviors'], ensure_ascii=False))
print('caption:', d['caption'])
print('note:', re.sub(r'<[^>]+>', ' ', d['extras']))
print('lead:', res['printed']['lead_sentence'])
print('numbers on chart:', sorted(set(nums)))
print('shots:', *shots, sep='\n  ')
print('OK')
