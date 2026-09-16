# -*- coding: utf-8 -*-
"""新手實作版（v6.0 候選）案例重算。以 docs/core-edition/calc_core.py 為底，照 spec-v60-stage1 覆蓋：
- 報酬一律名目：股票 低 4%／中 6%／高 7%；防守 2%（定存 1.7% 只當事實，不進試算）
- 查表 11 列＝股票比例×4/6/7%＋防守比例×2%，四捨五入一位小數；案例一律用印出來的一位小數
- 物價倍數沿用完整版第 2 節表（中間年數取年數多的那格）
- 陳大哥：今天花費×物價倍數 → 退休那年價錢；勞保不乘倍數；勞退試算直接相減；缺口×12×25/33/40
- 倍數表：低情境報酬率、按月複利、月底投入
用法：python3 tools/calc_core.py [--guide guide/index.html] [--out lite/calc-results.json]
"""
import sys, os, re, json, math
from decimal import Decimal, ROUND_HALF_UP
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
args = sys.argv[1:]
def opt(name, default):
    return args[args.index(name) + 1] if name in args else default
GUIDE = opt('--guide', os.path.join(ROOT, 'guide', 'index.html'))
OUT = opt('--out', os.path.join(ROOT, 'lite', 'calc-results.json'))

STOCK = {'low': 4, 'mid': 6, 'high': 7}
DEFENSE = 2
START = (2026, 10)          # 第 1 個月＝2026 年 10 月
CPI_TABLE = {5: 1.10, 10: 1.22, 15: 1.35, 20: 1.49, 25: 1.64, 30: 1.81, 35: 2.00, 40: 2.21}

def r1(x):  # 四捨五入一位（half-up）
    return float(Decimal(str(x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
def r0(x):
    return int(Decimal(str(x)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
def wan1(x): return r1(x / 10000)      # 萬，一位小數
def wan(x): return r0(x / 10000)       # 萬，整數

def fv(p0, rate, months, contrib):
    """每月月底投入、年率/12 按月複利。contrib: int 或 function(month 1-based)"""
    f = contrib if callable(contrib) else (lambda m: contrib)
    r = rate / 100 / 12; v = p0
    for m in range(1, months + 1):
        v = v * (1 + r) + f(m)
    return v

def months_to(p0, rate, contrib, target, cap=1200):
    f = contrib if callable(contrib) else (lambda m: contrib)
    r = rate / 100 / 12; v = p0
    for m in range(1, cap + 1):
        v = v * (1 + r) + f(m)
        if v >= target: return m
    return None

def months_to_rescaled(p0, rate, contrib, today_wan, start_month, cap=1200):
    """fix-r5：延後時目標跟著年數重查物價倍數表（今天的錢 × cpi(第 m 月的年數)），找第一個到得了的月份"""
    for m in range(start_month, cap + 1):
        t = today_wan * cpi(m / 12) * 10000
        if fv(p0, rate, m, contrib) >= t:
            return {'month': m, 'years': round(m / 12, 2), 'cpi': cpi(m / 12), 'target_wan': r0(t / 10000),
                    'target_wan1': r1(t / 10000)}
    return None

def ym(k):
    t = START[0] * 12 + (START[1] - 1) + (k - 1)
    return '%d-%02d' % (t // 12, t % 12 + 1)

def cpi(years):
    for y in sorted(CPI_TABLE):
        if years <= y: return CPI_TABLE[y]
    raise ValueError(years)

R = {'_meta': {
    'script': 'tools/calc_core.py', 'spec': 'spec-v60-stage1.md（覆蓋 proposal-core-edition.md）',
    'conventions': {
        'returns': '名目；股票 低4/中6/高7%；防守 2%；定存 1.7% 不進試算',
        'lookup': '股票比例×4/6/7%＋防守比例×2%，四捨五入一位；案例用印出來的數字',
        'compounding': '年率/12 按月複利、每月月底投入',
        'month_1': '2026-10', 'amounts': '元；*_wan 為萬',
        'cpi': '完整版第 2 節物價倍數表，中間年數取年數多的那格',
        'retirement': '今天花費×物價倍數；勞保不乘倍數；勞退試算為退休那年金額直接相減；缺口×12×25/33/40',
        'stress': '少的錢＝金額×股票比例×跌幅（防守放債券 ETF 時再加 金額×防守比例×10%）',
        'rounding_fix_r4': '到期金額印整數萬時，從原值直接四捨五入（wan），不用 wan1 再捨入',
        'months_fix_r4': '目標那年少的錢換成幾個月收入：先除以物價倍數換成今天的錢，再除以現在的月收入'}}}

# ---------- 查表 ----------
lookup = {}
for s in range(100, -1, -10):
    f = s / 100
    lookup[s] = {k: r1(f * v + (1 - f) * DEFENSE) for k, v in STOCK.items()}
R['lookup_table'] = [{'stock_pct': s, **lookup[s]} for s in lookup]
L = lambda s, k='low': lookup[s][k]

# ---------- 物價倍數 ----------
R['cpi_multiplier'] = {
    'table_guide_s2': {str(k): v for k, v in CPI_TABLE.items()},
    'exact_1.02^n': {str(n): round(1.02 ** n, 3) for n in (5, 7, 10, 15, 20, 25, 30, 35, 40)},
    'table_matches_round2': all(round(1.02 ** n, 2) == v for n, v in CPI_TABLE.items()),
    'note': '7 年照表規則取 10 年那格 1.22；精確 1.02^7＝1.149（提案的 ×1.15 不另外印）'}

# ---------- 倍數表 ----------
YEARS = (5, 7, 10, 15, 20, 25, 30)
low_rates = sorted({lookup[s]['low'] for s in lookup})
R['multiplier_tables'] = {
    'years': list(YEARS),
    'rates_all_low_column': low_rates,
    'rates_suggested_print': [2.0, 2.4, 2.8, 3.2, 3.6, 4.0],
    'monthly_1000_wan': {str(rt): [wan1(fv(0, rt, n * 12, 1000)) for n in YEARS] for rt in low_rates},
    'lump_100000_wan': {str(rt): [wan1(fv(100000, rt, n * 12, 0)) for n in YEARS] for rt in low_rates},
}
ex = fv(0, 3.6, 240, 1000) / 10000
R['multiplier_tables']['usage_example'] = {'text': '每月 5,000 元、20 年、3.6%', 'table_value': wan1(fv(0, 3.6, 240, 1000)),
                                            'times5_wan': r1(wan1(fv(0, 3.6, 240, 1000)) * 5), 'exact_wan': wan1(fv(0, 3.6, 240, 5000)),
                                            'times5_printed_int_step0': r0(r1(wan1(fv(0, 3.6, 240, 1000)) * 5))}
# r5：查表頁「扣費用」用法算例（整體報酬率＝表一的數字 − 總費用率，一步做完）：
# 每月 5,000 元、20 年、股票八成 → 表一 3.6%；總費用率 0.2% → 3.4%，表二 34.3 × 5
R['multiplier_tables']['usage_example_after_fee'] = {
    'text': '每月 5,000 元、20 年、股票八成（表一 3.6%）、總費用率 0.2%',
    'lookup_rate': 3.6, 'total_fee_pct': 0.2, 'rate_after_fee': r1(3.6 - 0.2),
    'rate_after_fee_in_table': r1(3.6 - 0.2) in low_rates,
    'table_value': wan1(fv(0, r1(3.6 - 0.2), 240, 1000)),
    'times5_wan': r1(wan1(fv(0, r1(3.6 - 0.2), 240, 1000)) * 5),
    'printed_int_wan': r0(r1(wan1(fv(0, r1(3.6 - 0.2), 240, 1000)) * 5)),
    'no_fee_printed_int_wan': r0(r1(wan1(fv(0, 3.6, 240, 1000)) * 5)),
    'exact_wan': wan1(fv(0, r1(3.6 - 0.2), 240, 5000))}
# fix-r2：查表頁「已經有一筆錢」用法算例：已有 30 萬＋每月 5,000 元、20 年、3.6% → 20.5 × 3 ＋ 35.1 × 5
R['multiplier_tables']['usage_example_lump'] = {
    'text': '已經有 30 萬、每月 5,000 元、20 年、3.6%',
    'table_sum_wan': r1(wan1(fv(100000, 3.6, 240, 0)) * 3 + wan1(fv(0, 3.6, 240, 1000)) * 5),
    'printed_int_wan': r0(r1(wan1(fv(100000, 3.6, 240, 0)) * 3 + wan1(fv(0, 3.6, 240, 1000)) * 5)),
    'exact_wan': wan1(fv(300000, 3.6, 240, 5000))}

# ---------- 100 萬壓力表 ----------
def loss(amount, stock_pct, drop, bond_drop=0):
    return amount * stock_pct / 100 * drop / 100 + amount * (100 - stock_pct) / 100 * bond_drop / 100
rows = []
for s in (100, 80, 60, 40, 20):
    for bd in ((0,) if s == 100 else (0, 10)):
        rows.append({'stock_pct': s, 'defense_drop_pct': bd,
                     'loss_wan': {str(d): r0(loss(100, s, d, bd)) for d in (40, 50, 60)}})
R['stress_100wan'] = rows

# ---------- 小安 ----------
xa = {}
base = lambda m: 2000 if m <= 10 else 5000
rt80 = lookup[80]
xa['rates'] = rt80
xa['target_wan'] = 200
xa['target_today_wan'] = {'cpi_20y': cpi(20), 'value': r0(200 / cpi(20)), 'exact': round(200 / cpi(20), 1), 'proposal': 135}
xa['base_plan'] = {k: {'fv_wan': wan(fv(0, v, 240, base)), 'fv_wan1': wan1(fv(0, v, 240, base)),
                       'vs_target_wan1': r1(wan1(fv(0, v, 240, base)) - 200)} for k, v in rt80.items()}
xa['base_principal_wan'] = sum(base(m) for m in range(1, 241)) / 10000
opts = {}
for x in (5500, 6000, 6500, 7000):
    c = lambda m, x=x: 2000 if m <= 10 else (5000 if m <= 26 else x)
    opts[str(x)] = {'low_fv_wan1': wan1(fv(0, rt80['low'], 240, c)), 'mid_fv_wan1': wan1(fv(0, rt80['mid'], 240, c)),
                    'high_fv_wan1': wan1(fv(0, rt80['high'], 240, c)),
                    'principal_wan': sum(c(m) for m in range(1, 241)) / 10000,
                    'enough_low': fv(0, rt80['low'], 240, c) >= 2_000_000}
xa['save_more_from_month27'] = {'month27': ym(27), 'options': opts,
                                'min_enough_step500': min(int(k) for k, v in opts.items() if v['enough_low'])}
c65 = lambda m: 2000 if m <= 10 else (5000 if m <= 26 else 6500)
v60 = fv(0, rt80['low'], 60, c65); v240 = fv(0, rt80['low'], 240, c65)
m50 = months_to(0, rt80['low'], c65, 500000); m100 = months_to(0, rt80['low'], c65, 1000000)
xa['plan_6500'] = {'low_fv_wan1': wan1(v240), 'low_fv_wan': wan(v240), 'month60_wan1': wan1(v60), 'month60_wan': wan(v60),
                   'reach_50wan': {'month': m50, 'ym': ym(m50)}, 'reach_100wan': {'month': m100, 'ym': ym(m100)},
                   'month240': ym(240)}
xa['delay_without_saving_more'] = (lambda m: {'month': m, 'ym': ym(m), 'extra_months': m - 240})(months_to(0, rt80['low'], base, 2_000_000))
xa['stress'] = {'year5': {'amount_wan': wan(v60), 'loss_wan': {str(d): r0(v60 * 0.8 * d / 100 / 10000) for d in (40, 50, 60)},
                          'loss50_months_salary_38k': r1(v60 * 0.8 * 0.5 / 38000)},
                'y2046': {'amount_wan': wan(v240), 'loss_wan': {str(d): r0(v240 * 0.8 * d / 100 / 10000) for d in (40, 50, 60)},
                          'loss50_months_salary_38k': r1(v240 * 0.8 * 0.5 / 38000)}}
# fix-r2：用表上印的整數萬除，讀者照表除得出來
xa['stress']['year5']['loss50_months_salary_38k_from_printed'] = r1(r0(v60 * 0.8 * 0.5 / 10000) * 10000 / 38000)
xa['stress']['y2046']['loss50_months_salary_38k_from_printed'] = r1(r0(v240 * 0.8 * 0.5 / 10000) * 10000 / 38000)
# fix-r3：壓力測試少的錢改用表上印的整數萬金額計算（讀者照表乘得出來）；未取整的留作對照
for key, v in (('year5', v60), ('y2046', v240)):
    xa['stress'][key]['loss_wan_unrounded_amount'] = xa['stress'][key]['loss_wan']
    xa['stress'][key]['loss_wan'] = {str(d): r0(wan(v) * 0.8 * d / 100) for d in (40, 50, 60)}
# fix-r4：換算幾個月薪水時，少的錢先除以物價倍數換成今天的錢，再除以現在的月薪（都用表上印的整數萬）
for key, yrs_ in (('year5', 5), ('y2046', 20)):
    l50 = xa['stress'][key]['loss_wan']['50']; m_ = cpi(yrs_)
    xa['stress'][key]['loss50_today_money'] = {'cpi': m_, 'years': yrs_, 'today_wan': r0(l50 / m_),
                                               'months_salary_38k': r1(r0(l50 / m_) * 10000 / 38000),
                                               'months_salary_38k_unrounded': r1(l50 / m_ * 10000 / 38000)}
# fix-r5：延後時目標要用新年數重查物價倍數（今天 134 萬；超過 20 年取 25 年那格 1.64）；delay_without_saving_more 作廢
_d = months_to_rescaled(0, rt80['low'], base, 134, 241)
_d.update({'ym': ym(_d['month']), 'extra_months': _d['month'] - 240, 'extra_years': round((_d['month'] - 240) / 12, 1),
           'max_delay_years': 5, 'within_max': _d['month'] - 240 <= 60,
           'superseded': 'delay_without_saving_more（目標沒重算，仍用 200 萬）'})
xa['delay_rescaled_fix_r5'] = _d
xa['section5_2_example'] = {'now_3wan_80pct_loss50_wan': r1(3 * 0.8 * 0.5), 'y2046_loss50_wan': r0(v240 * 0.8 * 0.5 / 10000)}
R['xiaoan'] = xa

# ---------- 阿凱 ----------
ak = {}
ak['rates'] = {'64': lookup[60], '82': lookup[80]}
ak['target_wan'] = 450
ak['target_today_wan'] = {'cpi_20y': cpi(20), 'value': r0(450 / cpi(20)), 'exact': round(450 / cpi(20), 1), 'proposal': 303}
ak['fv_10k'] = {lab: {k: {'fv_wan1': wan1(fv(300000, v, 240, 10000)), 'fv_wan': wan(fv(300000, v, 240, 10000)),
                          'vs_target_wan': wan(fv(300000, v, 240, 10000)) - 450} for k, v in lookup[s].items()}
                for lab, s in (('64', 60), ('82', 80))}
low64 = lookup[60]['low']
save = {}
for x in (11000, 11500, 12000, 12500):
    save[str(x)] = {'pct_of_50k': round(x / 50000 * 100, 1), 'low_fv_wan1': wan1(fv(300000, low64, 240, x)),
                    'enough': fv(300000, low64, 240, x) >= 4_500_000}
ak['save_more_64'] = {'options': save, 'min_enough_step500': min(int(k) for k, v in save.items() if v['enough'])}
pct_min = next(p for p in range(20, 41) if fv(300000, low64, 240, 50000 * p / 100) >= 4_500_000)
ak['save_more_64']['min_integer_pct'] = {'pct': pct_min, 'monthly': 50000 * pct_min / 100,
                                          'low_fv_wan1': wan1(fv(300000, low64, 240, 50000 * pct_min / 100))}
md = months_to(300000, low64, 10000, 4_500_000)
ak['delay_64_10k'] = {'month': md, 'ym': ym(md), 'extra_months': md - 240, 'extra_years': round((md - 240) / 12, 1)}
# fix-r5：延後時目標重查物價倍數（今天 302 萬；超過 20 年取 25 年那格 1.64 ≈ 495 萬）；delay_64_10k 作廢
_d = months_to_rescaled(300000, low64, 10000, 302, 241)
_d.update({'ym': ym(_d['month']), 'extra_months': _d['month'] - 240, 'extra_years': round((_d['month'] - 240) / 12, 1),
           'max_delay_years': 3, 'within_max': _d['month'] - 240 <= 36,
           'fv_at_max_delay_wan': wan(fv(300000, low64, 276, 10000)), 'target_at_max_delay_wan': r0(302 * cpi(276 / 12)),
           'exact_1.02^n_check': (lambda m: {'month': m, 'ym': ym(m)})(
               next(m for m in range(241, 1200) if fv(300000, low64, m, 10000) >= 302e4 * 1.02 ** (m / 12))),
           'superseded': 'delay_64_10k（目標沒重算，仍用 450 萬）'})
ak['delay_rescaled_fix_r5'] = _d
lv = fv(300000, low64, 240, 10000)
ak['lower_target_64'] = {'low_fv_wan1': wan1(lv), 'suggest_floor10_wan': int(lv / 100000) * 10}
ak['stress'] = {'now_30wan': {str(s): {str(d): r1(30 * s / 100 * d / 100) for d in (40, 50, 60)} for s in (80, 60)},
                'y2046_64_low': {'amount_wan': wan(lv), 'loss_wan': {str(d): r0(lv * 0.6 * d / 100 / 10000) for d in (40, 50, 60)},
                                 'loss50_months_income_50k': r1(lv * 0.6 * 0.5 / 50000)}}
lv82 = fv(300000, lookup[80]['low'], 240, 10000)
ak['check_82_low_reaches_target'] = lv82 >= 4_500_000
# fix-r4：換成今天的錢再換算月數（118 萬 ÷ 1.49 ≈ 79 萬 ÷ 5 萬）
_l50 = ak['stress']['y2046_64_low']['loss_wan']['50']
ak['stress']['y2046_64_low']['loss50_today_money'] = {'cpi': cpi(20), 'today_wan': r0(_l50 / cpi(20)),
                                                      'months_income_50k': r1(r0(_l50 / cpi(20)) * 10000 / 50000),
                                                      'months_income_50k_unrounded': r1(_l50 / cpi(20) * 10000 / 50000)}
# fix-r4：大跌演練一級一級降（2022 年賣時八成）：2046 年低情境、每月 1 萬、防守定存；少的錢用印出來的整數萬算
ak['drill_2046_low'] = {str(s): {'rate': lookup[s]['low'], 'amount_wan': wan(fv(300000, lookup[s]['low'], 240, 10000)),
                                 'loss_wan': {str(d): r0(wan(fv(300000, lookup[s]['low'], 240, 10000)) * s / 100 * d / 100) for d in (40, 50, 60)}}
                        for s in (80, 70, 60)}
ak['drill_2046_low']['story'] = '八成「先賣一些」沒通過 → 七成「想停扣」沒通過 → 六成「照常投入」通過（虛構的回答，不是算出來的）'
# step0-1（spec-v60-stage2 第 0 步）：C 區改投收入的 24%；壓力測試、大跌演練三列改用補完缺口後（每月平均 1.2 萬）的 2046 年低情境金額；
# 月數照第 16 格規則：少的錢（印出來的整數萬）÷ 物價倍數 → 今天的錢（整數萬）÷ 月收入 5 萬。drill_2046_low（每月 1 萬）作廢
_ag = {'pct': 24, 'monthly_avg': 50000 * 24 // 100, 'monthly_30k': 30000 * 24 // 100, 'monthly_80k': 80000 * 24 // 100,
       'first_version_pct': 20, 'drill_2046_low': {}}
for s in (80, 70, 60):
    a_ = wan(fv(300000, lookup[s]['low'], 240, _ag['monthly_avg']))
    ls_ = {str(d): r0(a_ * s / 100 * d / 100) for d in (40, 50, 60)}
    t_ = r0(ls_['50'] / cpi(20))
    _ag['drill_2046_low'][str(s)] = {'rate': lookup[s]['low'], 'amount_wan': a_, 'loss_wan': ls_,
                                     'loss50_today_wan': t_, 'loss50_months_income_50k': r1(t_ * 10000 / 50000),
                                     'loss50_months_income_50k_int': r0(t_ * 10000 / 50000)}
_ag['superseded'] = ['drill_2046_low', 'stress.y2046_64_low']
ak['after_gap_24pct'] = _ag
R['akai'] = ak

# ---------- 小芸與阿哲 ----------
xy = {}
r0pct = lookup[0]['low']
xy['down_payment'] = dp = {'rate': r0pct, 'target_wan': 400, 'months': 84, 'target_ym': ym(84)}
dp['fv_25k_wan1'] = wan1(fv(1_200_000, r0pct, 84, 25000)); dp['gap_wan'] = r0(400 - dp['fv_25k_wan1'])
opts = {}
for x in (27500, 28000, 28500, 29000, 30000):
    opts[str(x)] = {'fv_wan1': wan1(fv(1_200_000, r0pct, 84, x)), 'enough': fv(1_200_000, r0pct, 84, x) >= 4_000_000}
dp['save_more'] = opts
dp['save_more_min_step500'] = min(int(k) for k, v in opts.items() if v['enough'])
mdp = months_to(1_200_000, r0pct, 25000, 4_000_000)
dp['delay_25k'] = {'month': mdp, 'ym': ym(mdp), 'extra_months': mdp - 84}
v72 = fv(1_200_000, r0pct, 72, 30000)
dp['counter_example_month72_30k'] = {'ym': ym(72), 'amount_wan1': wan1(v72), 'amount_wan': wan(v72),
                                     'loss_60pct_stock_drop50_wan': r0(v72 * 0.6 * 0.5 / 10000),
                                     'note': '舊算法（fix-r2 起指南不用）：用 0% 股票（2%）滾出的金額，假設其中六成是股票'}
# fix-r2：反面例子改用正文條件——現有 120 萬、每月 2.5 萬、股票六成照查表低 3.2%，滾到第 72 個月（2032-09）
v72b = fv(1_200_000, lookup[60]['low'], 72, 25000)
dp['counter_example_month72_25k_60pct'] = {'ym': ym(72), 'rate': lookup[60]['low'], 'amount_wan1': wan1(v72b), 'amount_wan': wan(v72b),
                                           'loss_drop50_wan1': wan1(v72b * 0.6 * 0.5), 'loss_drop50_wan': wan(v72b * 0.6 * 0.5),
                                           'note': '照地板規則本來就不能這樣放，只示範會少多少'}
dp['floor_5y_from'] = ym(84 - 60)  # 2033-09 往前 5 年＝2028-09（提案寫法）
xy['long_term'] = lt = {'rates': lookup[80], 'target_wan': 700, 'target_ym': ym(360),
                        'target_today_wan': {'cpi_30y': cpi(30), 'value': r0(700 / cpi(30)), 'exact': round(700 / cpi(30), 1), 'proposal': 387}}
lt['fv_wan'] = {k: {'wan1': wan1(fv(400000, v, 360, 10000)), 'wan': wan(fv(400000, v, 360, 10000))} for k, v in lookup[80].items()}
lt['enough_low'] = fv(400000, lookup[80]['low'], 360, 10000) >= 7_000_000
# fix-r1：長期桶壓力測試兩列（現在 40 萬；2056 年低情境金額），股票八成、防守定存
lt_low = fv(400000, lookup[80]['low'], 360, 10000)
lt['stress'] = {'now_40wan': {str(d): r1(loss(40, 80, d)) for d in (40, 50, 60)},
                'y2056_low': {'amount_wan': wan(lt_low), 'loss_wan': {str(d): r0(loss(lt_low / 10000, 80, d)) for d in (40, 50, 60)}}}
# fix-r1 檢查（未寫進指南）：三問第 3 題「換較低比例還到得了嗎」
lt['q3_lower_ratio_check_low'] = {str(s): {'rate': lookup[s]['low'], 'fv_wan1': wan1(fv(400000, lookup[s]['low'], 360, 10000)),
                                           'reaches_700': fv(400000, lookup[s]['low'], 360, 10000) >= 7_000_000} for s in (70, 60, 50, 40)}
# fix-r2：頭期款 400 萬是到時候的錢；換回今天的錢用 1.02^7（約 1.15），不用表格取大格（取大格會把今天的價值估小）
dp['target_today_wan'] = {'years': 7, 'exact_1.02^7': round(1.02 ** 7, 3), 'value_1dp': round(400 / 1.02 ** 7, 1),
                          'print_wan': int(round(400 / 1.02 ** 7 / 10)) * 10,
                          'old_table_cell_1.22': {'value': r0(400 / cpi(7))}}
# fix-r3：示範順序改「今天 × 倍數 ＝ 到時候」：今天的錢取整到萬，乘印出來的 1.15 驗算
dp['target_today_wan'].update({'value_int': r0(400 / 1.02 ** 7), 'printed_mult': 1.15,
                               'forward_check_wan1': r1(r0(400 / 1.02 ** 7) * 1.15),
                               'forward_check_exact_wan1': r1(r0(400 / 1.02 ** 7) * 1.02 ** 7)})
# fix-r4：改照計畫表背面表三的規則（7 年在 5、10 年兩格中間，取 10 年那格 1.22）；fix-r2／r3 的 1.15、348、350 作廢，只留作紀錄
dp['target_today_wan']['fix_r4_table_rule'] = {'years': 7, 'table_mult': cpi(7), 'today_wan': r0(400 / cpi(7)),
                                               'forward_check_wan': r0(r0(400 / cpi(7)) * cpi(7)),
                                               'forward_check_exact': round(r0(400 / cpi(7)) * cpi(7), 2),
                                               'printed': '今天看的頭期款約 328 萬 × 1.22（7 年取 10 年那格）＝ 到時候約 400 萬'}
dp['target_today_wan']['superseded_by_fix_r4'] = ['exact_1.02^7', 'value_1dp', 'print_wan', 'value_int', 'printed_mult',
                                                  'forward_check_wan1', 'forward_check_exact_wan1']
xy['household_stock_share_pct'] = round(40 * 0.8 / 160 * 100, 1)
R['xiaoyun_azhe'] = xy

# ---------- 陳大哥 ----------
ch = {}
spend_today = 45000; yrs = 5; mult = cpi(yrs)   # fix-r2 作者拍板：退休後每月生活費 5 萬 → 4.5 萬（今天的錢）
spend_ret = spend_today * mult
labor = 45800 * 30 * 0.0155
pension = 7000
gap_exact = spend_ret - labor - pension
gap_m = round(gap_exact / 1000) * 1000         # 取到千元（提案慣例：21,703 → 2.2 萬）
gap_y = gap_m * 12
ch['retirement_need'] = {
    'spend_today': spend_today, 'cpi_5y': mult, 'spend_2031': round(spend_ret),
    'labor_insurance_monthly': round(labor), 'labor_insurance_note': '45,800×30×1.55%，不乘物價倍數',
    'labor_pension_monthly_illustrative': pension,
    'gap_monthly_exact': round(gap_exact), 'gap_monthly_rounded_1000': gap_m, 'gap_yearly': gap_y,
    'targets_wan_2031': {str(k): r1(gap_y * k / 10000) for k in (25, 33, 40)},
    'targets_wan_2031_if_exact_gap': {str(k): r1(gap_exact * 12 * k / 10000) for k in (25, 33, 40)},
    'targets_today_money_wan_for_reference': {str(k): r1(gap_y * k / mult / 10000) for k in (25, 33, 40)},
    'proposal': {'gap_monthly': 22000, 'gap_yearly': 264000, 'targets_today': {'25': 660, '33': 871, '40': 1056},
                 'target_2031_33x': 962, 'target_2031_40x': 1166}}
T33 = gap_y * 33
scen = {}
for lab, s in (('46', 40), ('73', 70), ('28', 20), ('0', 0)):
    scen[lab] = {k: wan1(fv(8_000_000, v, 60, 30000)) for k, v in lookup[s].items()}
    scen[lab]['rates'] = lookup[s]
ch['fv_2031_wan1'] = scen
lo46 = fv(8_000_000, lookup[40]['low'], 60, 30000); lo73 = fv(8_000_000, lookup[70]['low'], 60, 30000)
ch['comparison'] = {
    'target33_wan': r1(T33 / 10000),
    '46_low_over_target_wan': wan(lo46 - T33), '73_low_over_target_wan': wan(lo73 - T33),
    '73_minus_46_low_wan': wan(lo73 - lo46),
    'extra_loss_at_drop50_wan': r0(800 * 0.7 * 0.5 - 800 * 0.4 * 0.5),
    'all_deposit_2pct_enough_33x': fv(8_000_000, lookup[0]['low'], 60, 30000) >= T33,
    'all_deposit_over_target_wan': wan(fv(8_000_000, lookup[0]['low'], 60, 30000) - T33),
    '40x_target_wan': r1(gap_y * 40 / 10000), '46_low_reaches_40x': lo46 >= gap_y * 40, '73_low_reaches_40x': lo73 >= gap_y * 40,
    '73_high_reaches_40x': fv(8_000_000, lookup[70]['high'], 60, 30000) >= gap_y * 40}
# fix-r2：同一時間點（2031 年低情境）比較七三與四六；以及對 40 倍的餘裕
T40 = gap_y * 40
lo28 = fv(8_000_000, lookup[20]['low'], 60, 30000); lo0 = fv(8_000_000, lookup[0]['low'], 60, 30000)
ch['comparison'].update({
    '46_low_over_40x_wan': wan(lo46 - T40), '73_low_over_40x_wan': wan(lo73 - T40),
    '28_low_over_40x_wan': wan(lo28 - T40), 'all_deposit_over_40x_wan': wan(lo0 - T40),
    '28_low_reaches_40x': lo28 >= T40, 'all_deposit_reaches_40x': lo0 >= T40,
    'loss50_2031_low_wan': {'73': wan(lo73 * 0.7 * 0.5), '46': wan(lo46 * 0.4 * 0.5), '28': wan(lo28 * 0.2 * 0.5)},
    'extra_loss50_2031_low_73_vs_46_wan': wan(lo73 * 0.7 * 0.5 - lo46 * 0.4 * 0.5),
    'extra_loss50_2031_low_73_vs_46_wan_from_rounded': wan(1e4 * (wan(lo73) * 0.35 - wan(lo46) * 0.2)),
    'extra_loss50_2031_low_73_vs_46_wan_from_printed_losses': wan(lo73 * 0.7 * 0.5) - wan(lo46 * 0.4 * 0.5)})
ch['first_year_withdrawal'] = {'amount_wan': r1(gap_y / 10000), 'pct_of_46_low': round(gap_y / lo46 * 100, 2),
                               'pct_of_46_low_1dp': r1(gap_y / lo46 * 100), 'within_2.5_to_3pct': 2.5 <= gap_y / lo46 * 100 <= 3.0,
                               'proposal': {'amount_wan': 29.1, 'pct': 2.6}}
ch['five_year_gap_wan'] = {'value': r1(gap_y * 5 / 10000), 'proposal_today': 132, 'proposal_2031': 146,
                           'note': '缺口已是 2031 年的錢，不再乘倍數'}
st = {}
for lab, s, bd in (('73_deposit', 70, 0), ('46_deposit', 40, 0), ('46_bond10', 40, 10)):
    ls = {str(d): r0(loss(800, s, d, bd)) for d in (40, 50, 60)}
    st[lab] = {'loss_wan': ls, 'loss50_years_of_gap': r1(ls['50'] * 10000 / gap_y)}
ch['stress_800wan'] = st
# fix-r1：計畫表第 16 格要「目標那年」一列：2031 年 9 月、四六、低情境金額、防守定存
ls31 = {str(d): r0(loss(lo46 / 10000, 40, d)) for d in (40, 50, 60)}
ch['stress_2031_46_low'] = {'amount_wan': wan(lo46), 'loss_wan': ls31,
                            'loss50_years_of_gap': r1(ls31['50'] * 10000 / gap_y),
                            'loss50_years_of_gap_unrounded_loss': r1(lo46 * 0.4 * 0.5 / gap_y)}
# fix-r2：同一時間點（2031 年低情境）的七三壓力測試，和四六那一列並列
ls31_73 = {str(d): r0(loss(lo73 / 10000, 70, d)) for d in (40, 50, 60)}
ch['stress_2031_73_low'] = {'amount_wan': wan(lo73), 'loss_wan': ls31_73, 'loss50_years_of_gap': r1(ls31_73['50'] * 10000 / gap_y)}
# fix-r4（第 14 條）：到期金額直接從原值四捨五入到萬，不先捨入到一位小數（七三中情境 1,219.49 → 1,219）
ch['fv_2031_wan'] = {lab: {k: wan(fv(8_000_000, v, 60, 30000)) for k, v in lookup[s].items()}
                     for lab, s in (('46', 40), ('73', 70), ('28', 20), ('0', 0))}
# fix-r4：大跌演練從原本的七成一級一級降（2031 年低情境、防守定存）；年數＝跌 50% 少的錢 ÷ 2031 年的年缺口（同一時間點）
ch['drill_2031_low'] = {}
for s in (70, 60, 50, 40):
    a_ = wan(fv(8_000_000, lookup[s]['low'], 60, 30000))
    ls_ = {str(d): r0(a_ * s / 100 * d / 100) for d in (40, 50, 60)}
    ch['drill_2031_low'][str(s)] = {'rate': lookup[s]['low'], 'amount_wan': a_, 'loss_wan': ls_,
                                    'loss50_years_of_gap': r1(ls_['50'] * 10000 / gap_y)}
ch['drill_2031_low']['story'] = '七、六、五成「想賣」→ 四成「照常、不賣，生活費從定存拿」通過（虛構的回答，不是算出來的）'
ch['drill_2031_low']['q1_floor_covered'] = {'floor_wan': r1(gap_y * 5 / 10000), 'existing_deposit_wan': 240,
                                            'covered': 240 >= gap_y * 5 / 10000}
ch['stress_800wan']['_note'] = 'fix-r4：現在 800 萬是今天的錢、缺口是 2031 年的錢，時間點不同，指南不再印年數'
ch['switch_cost'] = {'stock_sale_200wan_tax_0.3pct': 2_000_000 * 0.003, 'etf_sale_280wan_tax_0.1pct': 2_800_000 * 0.001}
ch['allocation_46'] = {'stock_wan': 320, 'global_wan': 240, 'tw_etf_kept_wan': 80, 'defense_wan': 480, 'deposit_add_wan': 240,
                       'min_deposit_for_5y_gap_wan': r1(gap_y * 5 / 10000)}
ch['retire_ym'] = ym(60)
R['chen'] = ch

# ---------- XIRR ----------
def xirr(flows):
    d0 = flows[0][0]
    f = lambda r: sum(a / (1 + r) ** ((d - d0).days / 365) for d, a in flows)
    lo, hi = -0.9, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > 0: lo = mid
        else: hi = mid
    return mid
flows = [(date(2027, 1, 1), -100000), (date(2027, 7, 1), -20000), (date(2027, 12, 31), 128000)]
x = xirr(flows)
R['xirr_demo'] = {'flows': [[d.isoformat(), a] for d, a in flows], 'xirr': round(x, 6), 'xirr_pct_1dp': r1(x * 100),
                  'simple_pct': round(8000 / 120000 * 100, 2), 'simple_pct_1dp': r1(8000 / 120000 * 100),
                  'note': '與完整版報酬口徑無關，數字不變'}

# ---------- 無感期、甜蜜點、他幫我打工等引用完整版數字 ----------
yrs60 = math.log(1 + 600000 * 0.07 / 60000) / math.log(1.07)
yrs60_low = math.log(1 + 600000 * 0.04 / 60000) / math.log(1.04)
R['quiet_period'] = {
    'guide_basis': '第 2 節：每年年底投入 6 萬、一年 7%（第 1 節高情境，樂觀）',
    'years_first_60wan_7pct': round(yrs60, 2), 'return_share_7pct_pct': r0((1 - 60000 * yrs60 / 600000) * 100),
    'for_reference_low_4pct': {'years': round(yrs60_low, 2), 'return_share_pct': r0((1 - 60000 * yrs60_low / 600000) * 100),
                               'note': '完整版沒有這組數字；只供作者決定要不要改用低情境'}}
R['fee_gap'] = {'monthly': 5000, 'months': 360, 'fv_6pct_wan': wan(fv(0, 6, 360, 5000)), 'fv_5pct_wan': wan(fv(0, 5, 360, 5000)),
                'gap_wan': wan(fv(0, 6, 360, 5000) - fv(0, 5, 360, 5000)),
                'gap_share_pct': r1(100 * (1 - fv(0, 5, 360, 5000) / fv(0, 6, 360, 5000))),
                'gap_share_20y_pct': r1(100 * (1 - fv(0, 5, 240, 5000) / fv(0, 6, 240, 5000))),
                'note': '每年多付 1 個百分點：30 年少 gap_share_pct%、20 年少 gap_share_20y_pct%，兩個都超過一成'
                        '（完整版第 7 步「寫下目標」與第 3 節的 86 萬用的是同一組）'}
R['sweet_spot_guide'] = {'rule': '70÷整體報酬率', 'years': {str(k): r1(70 / k) for k in (7, 6, 4, 3.6, 2.8)}}

# ---------- 甜蜜點與滿足點（年複利、投入固定、不扣物價費用稅） ----------
# 每年年底投入 C、年報酬 r，n 年後資產＝C×((1+r)^n−1)/r，一年長出來的錢＝資產×r＝C×((1+r)^n−1)
# 甜蜜點：長出來的錢＝C            → (1+r)^n = 2       → n = ln 2 ÷ ln(1+r)
# 滿足點：長出來的錢＝一年生活費   → (1+r)^n = 1÷s     → n = ln(1÷s) ÷ ln(1+r)
#   （儲蓄率 s＝存下來÷收入；生活費＝收入−存下來＝C×(1÷s−1)）
# 所以 s＝50% 時滿足點＝甜蜜點；s＝1/3 是 ln3÷ln2≈1.585 倍，s＝1/4 是 ln4÷ln2＝2 倍（和報酬率無關）
SAVE_RATES = [('50%', 0.5), ('33%', 1 / 3), ('25%', 0.25)]
def years_to_point(rate_pct, s):
    return math.log(1 / s) / math.log(1 + rate_pct / 100)
R['sweet_satisfy'] = {
    'formula': 'n = ln(1÷儲蓄率) ÷ ln(1＋報酬率)；年複利、每年投入固定、不扣物價費用稅',
    'sweet_spot_note': '甜蜜點＝資產一年長出來的錢追上一年存進去的錢，等於儲蓄率 50% 那一欄（ln2÷ln(1+r)）',
    'save_rates': {k: round(v, 6) for k, v in SAVE_RATES},
    'note_33pct': '33% 以 1/3 計算（0.33 會得 28.3 年）',
    'years': {str(r): {k: r1(years_to_point(r, s)) for k, s in SAVE_RATES} for r in (4, 6, 7)},
    'sweet_spot_years': {str(r): r1(years_to_point(r, 0.5)) for r in (4, 6, 7)},
    'ratio_vs_sweet': {k: round(math.log(1 / s) / math.log(2), 3) for k, s in SAVE_RATES},
    'guide_rounding': '完整版第 2 節寫的高 7% 約 10 年、中 6% 約 12 年、低 4% 約 18 年，就是這一組四捨五入',
    # 滿足點那一年的資產÷年生活費：資產×r＝生活費 → 資產÷生活費＝1÷r，和儲蓄率無關。
    # 也就是這張表隱含「每年把資產的 r 拿出來花」；本書退休目標用的是 25 到 40 倍（一年拿 4% 到 2.5%）。
    'asset_over_living_multiple': {str(r): r1(100 / r) for r in (4, 6, 7)},
    'withdrawal_multiple_for_retirement': {'倍數': '25 到 40', '對應提領率': '4% 到 2.5%',
                                           'note': '完整版「年齡、槓桿與退休」第三題；25 倍對台灣讀者偏樂觀，只當最低參考'},
    # 生活費會跟著物價漲：把報酬率先減掉物價再算一次（減法，和書上「整體報酬率－總費用率」同一套寫法）
    'after_inflation_subtract_2pct': {'method': '報酬率直接減 2 個百分點（書上採用的寫法）',
                                      'years_save_half': {str(r): r1(years_to_point(r - 2, 0.5)) for r in (4, 6, 7)}},
    'after_inflation_exact_real': {'method': '精算實質報酬 (1+r)/(1+2%)−1（只供查證，書上不寫）',
                                   'years_save_half': {str(r): r1(math.log(2) / math.log((1 + r / 100) / 1.02)) for r in (4, 6, 7)}},
}

# ---------- 滾動視窗：抱多久、賺錢的機率（含息） ----------
import csv as _csv, bisect as _bisect
from datetime import date as _date
TAIEX_CSV = os.path.join(ROOT, 'research', 'data', 'taiex_tr_monthly_raw.csv')
SHILLER_CSV = os.path.join(ROOT, 'research', 'data', 'shiller_sp_monthly.csv')

def _add_months(d, months):
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    dd = d.day
    while True:
        try: return _date(y, m, dd)
        except ValueError: dd -= 1

def taiex_series():
    rows = list(_csv.reader(open(TAIEX_CSV, encoding='utf-8')))[1:]
    return [_date.fromisoformat(r[0]) for r in rows], [float(r[1]) for r in rows]

def taiex_windows(months):
    """日資料的日曆視窗：起點每一個交易日，終點取「滿 N 個月的同一天」當天或之前最後一個交易日。"""
    dates, vals = taiex_series(); out = []
    for i, d in enumerate(dates):
        tgt = _add_months(d, months)
        if tgt > dates[-1]: break
        j = _bisect.bisect_right(dates, tgt) - 1
        if j <= i: continue
        out.append((vals[i], vals[j]))
    return out

def _pos_share(pairs):
    c = sum(1 for a, b in pairs if b > a)
    return {'n': len(pairs), 'positive': c, 'pct': round(100 * c / len(pairs), 2), 'pct_int': r0(100 * c / len(pairs))}

def _ann_range(pairs, years):
    xs = sorted(((b / a) ** (1 / years) - 1) * 100 for a, b in pairs)
    return {'n': len(xs), 'min_pct': r1(xs[0]), 'max_pct': r1(xs[-1])}

_td, _tv = taiex_series()
_tw_pos = {'1天': _pos_share(list(zip(_tv, _tv[1:])))}
for _lbl, _m in [('1個月', 1), ('1年', 12), ('3年', 36), ('5年', 60), ('10年', 120)]:
    _tw_pos[_lbl] = _pos_share(taiex_windows(_m))
_tw_rng = {str(_y) + '年': _ann_range(taiex_windows(_y * 12), _y) for _y in (1, 5, 10, 20)}

# 交叉檢查：另一種常見寫法（把一年當 252 個交易日），只放進 json 備查，書上不用
def _fixed_step(k, years):
    pairs = [(_tv[i], _tv[i + k]) for i in range(len(_tv) - k)]
    return {'positive': _pos_share(pairs), 'range': _ann_range(pairs, years)}

def shiller_tr():
    """名目含息月指數：月報酬＝(P_t＋D_t/12)÷P_{t−1}。只取有股利資料的月份。"""
    rows = list(_csv.DictReader(open(SHILLER_CSV, encoding='utf-8')))
    end = next(i for i, r in enumerate(rows) if float(r['Dividend'] or 0) == 0)
    rows = rows[:end]
    tr = [1.0]
    for k in range(1, len(rows)):
        p0 = float(rows[k - 1]['SP500']); p1 = float(rows[k]['SP500']); d = float(rows[k]['Dividend'])
        tr.append(tr[-1] * ((p1 + d / 12) / p0))
    return rows[0]['Date'][:7], rows[-1]['Date'][:7], tr

_s_from, _s_to, _str = shiller_tr()
_us_pos = {}
for _y in (1, 5, 10, 20, 30):
    _k = _y * 12
    _us_pos[str(_y) + '年'] = _pos_share([(_str[i], _str[i + _k]) for i in range(len(_str) - _k)])

R['rolling'] = {
    'window_rule': '日曆視窗：從任一個交易日算到滿 N 年（月）的同一天；那天沒開盤就取前一個交易日。視窗每天重疊，不是互相獨立的樣本。',
    'caveats': ['視窗重疊，不是獨立樣本', '都沒扣物價、費用和稅', '台股只有 23 年，起點又在 2000–2002 大跌之後，10 年 100% 只代表這段期間',
                '美股是 S&P 500 含息、名目'],
    'taiex': {
        'source': '證交所發行量加權股價報酬指數（含息）', 'file': os.path.relpath(TAIEX_CSV, ROOT),
        'from': _td[0].isoformat(), 'to': _td[-1].isoformat(), 'trading_days': len(_td),
        'positive_share': _tw_pos,
        'annual_range': _tw_rng,
        'cross_check_252_trading_days': {str(_y) + '年': _fixed_step(252 * _y, _y) for _y in (1, 5, 10, 20)},
    },
    'us': {
        'source': 'Robert Shiller 公開月資料，S&P 500 含息、名目', 'file': os.path.relpath(SHILLER_CSV, ROOT),
        'from': _s_from, 'to': _s_to, 'months': len(_str),
        'end_note': '股利欄只到 %s，之後留白，所以序列在這裡截止' % _s_to,
        'positive_share': _us_pos,
    },
}

# grep 正式檔：引用數字所在行（guidetools text 行號）
quotes = ['第一格 7.84 年', '| 60 萬 | 7.84 年 | 22%', '一家是台積電（1.80%）', '2,458 家公司', '2026 年 8 月底的權重',
          '三十年後差約 86 萬', '2008 年跌了 53.59%', '1.7% 是 2026 年 9 月五大銀行一年期定存牌告利率',
          '用 3% 到 2.5%（33 到 40 倍）算會保守一些', '都落在股票三成到七成五之間', '2026 年最高一級 45,800 元',
          '平均月投保薪資 × 年資 × 1.55%', '2026 年起請領年齡 65 歲', '提前領每年減 4%、最多減 20%',
          '2022 年 2.95%、2023 年 2.49%、2024 年 2.18%', '〔投資等級〕債 −13.0%', '高 7% 約 10 年、中 6% 約 12 年、低 4% 約 18 年',
          '低情境下股票八成約 20 年、四成約 25 年', '低 4% 約 21 年', '| 80% | 3.6% | 5.2% | 6%', '| 40% | 2.8% | 3.6% | 4%',
          '| 物價倍數 | 1.10 | 1.22 | 1.35 | 1.49 | 1.64 | 1.81 | 2.00 | 2.21', '勞保那一層保守起見用今天的投保薪資試算、不乘物價倍數',
          '真實年成本 6.69%', '台灣 3.25%']
found = {}
try:
    sys.path.insert(0, HERE)
    import guidetools
    lines = guidetools.to_text(GUIDE).split('\n')
    for q in quotes:
        hit = [i + 1 for i, l in enumerate(lines) if q in l]
        found[q] = hit
except Exception as e:
    found['_error'] = repr(e)
R['guide_citations'] = {'guide': os.path.relpath(GUIDE, ROOT), 'line_numbers_in_guidetools_text': found,
                        'missing': [q for q, v in found.items() if v == []]}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- 摘要 ----------
p = print
p('查表:', ' / '.join('%d%%:%s-%s-%s' % (s, lookup[s]['low'], lookup[s]['mid'], lookup[s]['high']) for s in lookup))
p('倍數表 每月1000:', R['multiplier_tables']['monthly_1000_wan'])
p('倍數表 10萬:', R['multiplier_tables']['lump_100000_wan'])
p('小安 base:', xa['base_plan'], '6500:', xa['plan_6500'], '選項:', xa['save_more_from_month27']['options'], '不多存延後（fix-r5 重查倍數）:', xa['delay_rescaled_fix_r5'])
p('小安 stress:', xa['stress'])
p('阿凱 24% 後演練:', ak['after_gap_24pct'])
p('阿凱:', ak['fv_10k'], ak['save_more_64'], ak['delay_rescaled_fix_r5'],ak['lower_target_64'], ak['stress']['y2046_64_low'], '八二低到450?', ak['check_82_low_reaches_target'])
p('小芸阿哲:', xy)
p('陳大哥:', json.dumps(ch, ensure_ascii=False))
p('XIRR:', R['xirr_demo'])
p('無感期:', R['quiet_period'], '費用差:', R['fee_gap'])
p('甜蜜點/滿足點:', json.dumps(R['sweet_satisfy']['years'], ensure_ascii=False), '倍數:', R['sweet_satisfy']['ratio_vs_sweet'])
p('台股為正比例:', {k: v['pct'] for k, v in R['rolling']['taiex']['positive_share'].items()})
p('台股區間:', {k: (v['min_pct'], v['max_pct']) for k, v in R['rolling']['taiex']['annual_range'].items()})
p('台股 252 日交叉檢查:', {k: (v['positive']['pct'], v['range']['min_pct'], v['range']['max_pct'])
                          for k, v in R['rolling']['taiex']['cross_check_252_trading_days'].items()})
p('美股為正比例:', R['rolling']['us']['from'], '→', R['rolling']['us']['to'],
  {k: v['pct'] for k, v in R['rolling']['us']['positive_share'].items()})
p('引用缺漏:', R['guide_citations']['missing'])
p('wrote', OUT)
