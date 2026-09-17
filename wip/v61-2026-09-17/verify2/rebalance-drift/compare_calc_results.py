"""把 lite/calc-results.json 的 rebalance_drift 和 recompute_v2 的獨立結果逐項對照（不 import 模組）。"""
import json, subprocess, sys
from fractions import Fraction as F
import math
exec(open('recompute_v2.py').read().split("out = {}")[0])   # 只取讀檔與 path_A/hu1/summ 定義，不跑輸出
c = json.load(open('/Users/linyenchu/Cladue Code/family-finance/lite/calc-results.json'))['rebalance_drift']
bad = []
def chk(label, a, b):
    if a != b: bad.append((label, a, b))
for s in ('1990', '2000', '2009'):
    mine = [(y, hu1(w * 100)[0]) for y, w in path_A(int(s), 'bill')]
    theirs = [(r['year'], '%.1f' % r['stock_pct']) for r in c['alt_starts'][s]['series']]
    chk('series ' + s, mine, theirs)
    sm = summ(path_A(int(s), 'bill')); cs = c['alt_starts'][s]
    chk('first ' + s, (sm['first']['year'], sm['first']['n'], sm['first']['pct']), (cs['first_breach_year'], cs['first_breach_years_after_start'], '%.1f' % cs['first_breach_stock_pct']))
    chk('back ' + s, sm['back_inside'], cs['years_back_inside_after_breach'])
    chk('end ' + s, sm['end'], '%.1f' % cs['end_stock_pct'])
    chk('nout ' + s, sm['n_out'], cs['years_outside_band'])
rows = {r['start']: r for r in c['all_starts_scan']['rows']}
for s in range(1928, 2022):
    sm = summ(path_A(s, 'bill'))
    chk('scan %d' % s, (sm['first']['n'], {'up': 'above_85', 'down': 'below_75'}[sm['first']['dir']], sm['end']),
        (rows[s]['years_to_breach'], rows[s]['direction'], '%.1f' % rows[s]['end_stock_pct']))
bs = summ(path_A(1990, 'bond'))
chk('bond back', bs['back_inside'], c['bond_sensitivity']['summary']['years_back_inside_after_breach'])
chk('bond 2008', hu1(dict(path_A(1990, 'bond'))[2008] * 100)[0], '%.1f' % c['bond_sensitivity']['mark_year']['stock_pct'])
print('mismatches:', bad)
