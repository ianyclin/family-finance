# (a) 第 11 節示意算術：股八定存二，股票漲 70%／50% 後的股票占比；5/25 對股票 80% 的範圍
# (b) 第 14 節新句「賺錢的比例常常比較低，有時低很多；平均賺得多換年代會翻」逐格對第 6 節表與小字
import re
for g in (0.5, 0.7):
    s = 80 * (1 + g); print('漲 %d%%：股票占比 %.1f%%（定存不計息）；定存 1.7%% 計息 %.1f%%' % (g * 100, 100 * s / (s + 20), 100 * s / (s + 20 * 1.017)))
w = 80; band = min(5, w * 0.25); print('5/25 股票 80%%：±%.1f → %.0f%%–%.0f%%' % (band, w - band, w + band))
t = open('txt/after-s6.txt', encoding='utf-8').read()
rows = re.findall(r'\| (台股|美股) (\d+) 年 \| (\d+)% \| (\d+)%', t)
cmp_ = [(m + y, int(a), int(b)) for m, y, a, b in rows]
extra = [('美股1950前5年', 91, 75), ('美股1950後5年', 93, 91)]
cells = cmp_ + extra
lower = [c for c in cells if c[2] < c[1]]; same = [c for c in cells if c[2] == c[1]]; higher = [c for c in cells if c[2] > c[1]]
print('新高那組賺錢比例：較低 %d 格，一樣 %d 格，較高 %d 格；最大差 %d 個百分點' % (len(lower), len(same), len(higher), max(c[1] - c[2] for c in cells)))
print('  較高:', higher, ' 一樣:', same)
m = re.search(r'新高月份放五年平均一年 ([\d.]+)%、其他月份 ([\d.]+)%；1950 年以後變成 ([\d.]+)% 對 ([\d.]+)%', t)
a, b, c, d = map(float, m.groups()); print('平均：1950 前 新高 %.1f < 其他 %.1f；1950 後 新高 %.1f > 其他 %.1f → 翻過來 %s' % (a, b, c, d, a < b and c > d))
