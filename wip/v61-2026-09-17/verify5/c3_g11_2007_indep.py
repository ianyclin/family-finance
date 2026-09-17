# 獨立重算（不 import 專案模組）：台股含息指數 2007 高點前後非新高日，一年後報酬
# 口徑照模組文件：一年後＝滿 12 個月同一天，沒開盤取前一個交易日；新高＝≥到當天為止最高值（含平手），第一天不算
import csv, bisect
from datetime import date
ROOT = '/Users/linyenchu/Cladue Code/family-finance'
rows = list(csv.reader(open(ROOT + '/research/data/taiex_tr_monthly_raw.csv', encoding='utf-8')))[1:]
D = [date.fromisoformat(r[0]) for r in rows]; V = [float(r[1]) for r in rows]
at = [False]; m = V[0]
for v in V[1:]:
    m = max(m, v); at.append(v >= m)
def plus1y(d):
    try: return date(d.year + 1, d.month, d.day)
    except ValueError: return date(d.year + 1, d.month, 28)
def ret1y(i):
    t = plus1y(D[i])
    if t > D[-1]: return None
    j = bisect.bisect_right(D, t) - 1
    return (V[j] / V[i] - 1) * 100, D[j]
y07 = [i for i in range(len(D)) if D[i].year == 2007]
t = max(y07, key=lambda i: V[i])
print('2007 高點', D[t], V[t], 'at_high', at[t], '全資料到 2012 為止最高?', V[t] == max(V[:bisect.bisect_right(D, date(2012,12,31))]))
for w in (3, 5, 7, 10, 15):
    rs = [(D[i], round(ret1y(i)[0], 1)) for i in range(t - w, t + w + 1) if not at[i]]
    vals = [r for _, r in rs]
    print('±%d 交易日 非新高 n=%d  min=%.1f max=%.1f  全部落在 -55~-45: %s' % (w, len(rs), min(vals), max(vals), all(-55 < r < -45 for r in vals)))
    if w == 3: print('   ', rs)
# 日曆 ±7 天
rs = [(D[i], round(ret1y(i)[0], 1)) for i in range(len(D)) if abs((D[i] - D[t]).days) <= 7 and not at[i]]
print('日曆±7天', rs)
# 2007 全年非新高
allnh = [ret1y(i)[0] for i in y07 if not at[i]]
import statistics
print('2007 全年非新高 n=%d  跌>45%%: %d  賺: %d  中位 %.1f' % (len(allnh), sum(r <= -45 for r in allnh), sum(r > 0 for r in allnh), statistics.median(allnh)))
# 新高那幾天一年後
print('±3 內新高日', [(D[i], round(ret1y(i)[0], 1)) for i in range(t - 3, t + 4) if at[i]])
