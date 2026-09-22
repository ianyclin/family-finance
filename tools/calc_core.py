# -*- coding: utf-8 -*-
"""新手實作版（v6.0 候選）案例重算。以 docs/core-edition/calc_core.py 為底，照 spec-v60-stage1 覆蓋：
- 報酬一律名目：股票 保守算 4%／普通算 6%／樂觀算 7%；防守 2%（定存 1.7% 只當事實，不進試算）
- 查表 11 列＝股票比例×4/6/7%＋防守比例×2%，四捨五入一位小數；案例一律用印出來的一位小數
- 物價倍數沿用完整版第 5 節表（中間年數取年數多的那格）
- 陳大哥：今天花費×物價倍數 → 退休那年價錢；勞保不乘倍數；勞退試算直接相減；缺口×12×25/33/40
- 倍數表：保守算報酬率、按月複利、月底投入
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
        'returns': '名目；股票 保守算 4%／普通算 6%／樂觀算 7%；防守 2%；定存 1.7% 不進試算',
        'lookup': '股票比例×4/6/7%＋防守比例×2%，四捨五入一位；案例用印出來的數字',
        'compounding': '年率/12 按月複利、每月月底投入',
        'month_1': '2026-10', 'amounts': '元；*_wan 為萬',
        'cpi': '完整版第 5 節物價倍數表，中間年數取年數多的那格',
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
ak['drill_2046_low']['story'] = '第一反應是「先賣一些」（2022 年真的賣過）；做完安排後：八成、七成他覺得還是會賣 → 六成他覺得能照計畫投入、不賣（虛構的回答，不是算出來的）'
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
ch['drill_2031_low']['story'] = '第一反應是賣掉（2008 年真的賣過）；做完安排後：七、六、五成他覺得還是會賣 → 四成他覺得能照計畫做、不賣，生活費從定存拿（虛構的回答，不是算出來的）'
ch['drill_2031_low']['q1_floor_covered'] = {'floor_wan': r1(gap_y * 5 / 10000), 'existing_deposit_wan': 240,
                                            'covered': 240 >= gap_y * 5 / 10000}
ch['stress_800wan']['_note'] = 'fix-r4：現在 800 萬是今天的錢、缺口是 2031 年的錢，時間點不同，指南不再印年數'
ch['switch_cost'] = {'stock_sale_200wan_tax_0.3pct': 2_000_000 * 0.003, 'etf_sale_280wan_tax_0.1pct': 2_800_000 * 0.001}
ch['allocation_46'] = {'stock_wan': 320, 'global_wan': 240, 'tw_etf_kept_wan': 80, 'defense_wan': 480, 'deposit_add_wan': 240,
                       'min_deposit_for_5y_gap_wan': r1(gap_y * 5 / 10000)}
ch['retire_ym'] = ym(60)
R['chen'] = ch

# ---------- v6.3 批 2 修正：退休那天早於勞保請領年齡的橋接缺口 ----------
# 退休 60 歲、勞保 2026 年起 65 歲才能請領：中間那幾年領不到勞保，
# 缺口要另外算（那幾年的「生活費 − 勞退」× 年數，直接加到目標上）。
# 這裡只算「比原本的算法多缺多少」＝勞保月給付 × 12 × 年數。
BRIDGE_RETIRE_AGE, BRIDGE_CLAIM_AGE = 60, 65
_bridge_years = BRIDGE_CLAIM_AGE - BRIDGE_RETIRE_AGE
_bridge_extra = round(labor) * 12 * _bridge_years
ch['retire_before_claim'] = {
    'retire_age': BRIDGE_RETIRE_AGE, 'claim_age': BRIDGE_CLAIM_AGE, 'years': _bridge_years,
    'labor_insurance_monthly': round(labor), 'extra_gap_total': _bridge_extra,
    'extra_gap_total_wan': r0(_bridge_extra / 10000),
    'printed': '21,297×12×5≈128 萬',
    'note': '這是「多缺」的部分：原本的算法已經扣掉勞保，橋接那幾年扣不到，要加回去；'
            '另一條路是選提前減額年金（每年減 4%、最多減 20%），用減額後的金額重算缺口'}

# ---------- N2（v6.3）：陳大哥的勞退月退分兩段 ----------
# 勞保局：勞退月退休金依年金生命表、平均餘命與利率計算，「按季發給至平均餘命止」，
# 平均餘命、利率及金額「至少每 3 年檢討調整一次」（開始領以後平均餘命不再變動，但會依調整後利率與專戶餘額重算）。
# 所以 7,000 元不能整段退休期都扣：這裡把退休期切成「領月退期間」與「之後」兩段。
PENSION_YEARS_ASSUMED = 20      # 假設領 20 年（65 → 85 歲）。這是本文的假設，不是勞保局公布的數字
RETIREMENT_YEARS_ASSUMED = 30   # 指南既有說法「退休後還要花三十年左右」
_stage2_years = RETIREMENT_YEARS_ASSUMED - PENSION_YEARS_ASSUMED
_extra_y = pension * 12                      # 第二段每年多缺的錢（月退停發）
_extra_total = _extra_y * _stage2_years
_two = lambda k: gap_y * k + _extra_total
ch['labor_pension_two_stage'] = {
    'source_url': 'https://www.bli.gov.tw/0104047.htm',
    'source_title': '勞保局：勞工退休金月退休金試算',
    'source_quote': '按季發給至平均餘命止。前述平均餘命、利率及金額至少每3年檢討調整一次',
    'assumption': {'pension_years': PENSION_YEARS_ASSUMED, 'retirement_years': RETIREMENT_YEARS_ASSUMED,
                   'note': '20 年與 30 年都是本文的假設，不是勞保局數字；實際年限要用勞保局試算'},
    'stage1': {'years': PENSION_YEARS_ASSUMED, 'gap_monthly': gap_m, 'gap_yearly': gap_y,
               'gap_yearly_wan': r1(gap_y / 10000)},
    'stage2': {'years': _stage2_years, 'extra_monthly': pension, 'extra_yearly': _extra_y,
               'extra_yearly_wan': r1(_extra_y / 10000), 'extra_total_wan': r1(_extra_total / 10000),
               'gap_yearly': gap_y + _extra_y, 'gap_yearly_wan': r1((gap_y + _extra_y) / 10000)},
    'targets_one_stage_wan': {str(k): r0(gap_y * k / 10000) for k in (25, 33, 40)},
    'targets_two_stage_wan': {str(k): r0(_two(k) / 10000) for k in (25, 33, 40)},
    'targets_two_stage_wan1': {str(k): r1(_two(k) / 10000) for k in (25, 33, 40)},
    # v6.3 批 1 修正（must-1）：小字用「未取整的每月缺口」算的第一段倍數，也要加上第二段的 84 萬才同基準
    'targets_two_stage_wan_if_exact_gap': {str(k): r0((gap_exact * 12 * k + _extra_total) / 10000) for k in (25, 33, 40)},
    'targets_two_stage_wan1_if_exact_gap': {str(k): r1((gap_exact * 12 * k + _extra_total) / 10000) for k in (25, 33, 40)},
}

# ---------- N1（v6.3）：0.5% 示範費率的扣費結果 ----------
# 書上規則（第 14 節查表頁表一上面那段小字）：整體報酬率＝表一查到的數字 －總費用率；
#   拿這個數字查表二，剛好沒有那一列就取「比它小的那一列」，再用表二印出來的數字相乘相加（by_book_table2）。
# 案例本文沿用原本的算法：用同一個扣完費的報酬率、按月複利、每月月底投入算精確值（exact）。
# 股票 0%、全放台幣定存的桶子沒有內扣費用，呼叫時傳 fee=0。
FEE_DEMO = 0.5
T2_ROWS = [r1(2.0 + 0.2 * i) for i in range(11)]     # 表二印出來的列：2.0%–4.0%，每 0.2 個百分點
def after_fee(rate, fee=FEE_DEMO): return r1(rate - fee)
def t2_row(rate):
    xs = [x for x in T2_ROWS if x <= rate + 1e-9]
    return max(xs) if xs else None
def t2_monthly_cell(rate, years): return wan1(fv(0, rate, years * 12, 1000))   # 表二「每月 1,000 元」那張
def t2_lump_cell(rate, years): return wan1(fv(100000, rate, years * 12, 0))    # 表二「現在有 10 萬」那張
def fee_case(rate, years, lump, monthly, target_wan=None, fee=FEE_DEMO):
    ra = after_fee(rate, fee); v = fv(lump, ra, years * 12, monthly)
    o = {'rate_table1': rate, 'fee_pct': fee, 'rate_after_fee': ra, 'years': years, 'lump': lump, 'monthly': monthly,
         'no_fee_wan': wan(fv(lump, rate, years * 12, monthly)),
         'exact': {'wan1': wan1(v), 'wan': wan(v), 'value': round(v)}}
    row = t2_row(ra)
    if row is not None and years in list(YEARS):
        b = t2_lump_cell(row, years) * (lump / 100000) + t2_monthly_cell(row, years) * (monthly / 1000)
        o['by_book_table2'] = {'row': row, 'lump_cell': t2_lump_cell(row, years),
                               'monthly_cell': t2_monthly_cell(row, years), 'wan1': r1(b), 'wan': r0(b)}
    else:
        o['by_book_table2'] = {'row': row, 'note': '表二沒有可取的列（或年數不在表上），書上要求改用複利計算機'}
    if target_wan is not None:
        o['target_wan'] = target_wan; o['enough_exact'] = v >= target_wan * 10000
        o['short_wan'] = 0 if v >= target_wan * 10000 else wan(target_wan * 10000 - v)
    return o

FD = {'fee_pct': FEE_DEMO,
      'method': '整體報酬率（表一查到的數字）直接減 0.5 個百分點（作者 2026-09-18 拍板 Q1-A）。'
                '＝把整個組合一起扣的簡化假設，不是按部位加權（v6.3.1：書上第 14 節第 12 格同步寫明）；'
                'exact＝用扣完費的報酬率按月複利算的精確值，案例本文用這個；'
                'by_book_table2＝讀者拿印好的表二會算出來的數字（沒有那一列就取比它小的那一列）。',
      'deposit_note': '股票 0%、全放台幣定存的桶子沒有內扣費用，不減示範費率'}

# 小安（第 14 節）：每月 2,000（前 10 個月）→5,000→6,500，八二
_c65f = lambda m: 2000 if m <= 10 else (5000 if m <= 26 else 6500)
_xaf = fv(0, after_fee(rt80['low']), 240, _c65f)
FD['xiaoan'] = {'rate_table1': rt80['low'], 'rate_after_fee': after_fee(rt80['low']), 'target_wan': 200,
                'no_fee_wan': wan(fv(0, rt80['low'], 240, _c65f)),
                'plan_6500_low_wan': wan(_xaf), 'plan_6500_low_wan1': wan1(_xaf),
                'enough_exact': _xaf >= 2_000_000,
                'base_plan_low_wan': wan(fv(0, after_fee(rt80['low']), 240, base)),
                'min_enough_step500': min(x for x in (5500, 6000, 6500, 7000, 7500, 8000)
                                          if fv(0, after_fee(rt80['low']), 240,
                                                (lambda m, x=x: 2000 if m <= 10 else (5000 if m <= 26 else x))) >= 2_000_000)}

# 主線 2026-09-18 拍板：第 14 節的小安也改成扣費後（0.5% 暫估）。以下鏡射上面 xa 的整套算法，只把報酬率換成扣完費的。
_rt80f = {k: after_fee(v) for k, v in rt80.items()}
_xf = FD['xiaoan']
_xf['rates_after_fee_all'] = _rt80f
_xf['base_plan'] = {k: {'fv_wan': wan(fv(0, v, 240, base)), 'fv_wan1': wan1(fv(0, v, 240, base)),
                        'vs_target_wan1': r1(wan1(fv(0, v, 240, base)) - 200)} for k, v in _rt80f.items()}
_xf['base_principal_wan'] = sum(base(m) for m in range(1, 241)) / 10000
_xf['options_step500'] = {}
for _x in (5500, 6000, 6500, 7000):
    _c = lambda m, x=_x: 2000 if m <= 10 else (5000 if m <= 26 else x)
    _xf['options_step500'][str(_x)] = {
        'low_fv_wan1': wan1(fv(0, _rt80f['low'], 240, _c)), 'low_fv_wan': wan(fv(0, _rt80f['low'], 240, _c)),
        'mid_fv_wan1': wan1(fv(0, _rt80f['mid'], 240, _c)), 'mid_fv_wan': wan(fv(0, _rt80f['mid'], 240, _c)),
        'high_fv_wan1': wan1(fv(0, _rt80f['high'], 240, _c)), 'high_fv_wan': wan(fv(0, _rt80f['high'], 240, _c)),
        'principal_wan': sum(_c(m) for m in range(1, 241)) / 10000,
        'enough_low': fv(0, _rt80f['low'], 240, _c) >= 2_000_000}
_v60f = fv(0, _rt80f['low'], 60, _c65f)
_m50f = months_to(0, _rt80f['low'], _c65f, 500000); _m100f = months_to(0, _rt80f['low'], _c65f, 1000000)
_xf['plan_6500'] = {'low_fv_wan1': wan1(_xaf), 'low_fv_wan': wan(_xaf),
                    'mid_fv_wan1': wan1(fv(0, _rt80f['mid'], 240, _c65f)), 'mid_fv_wan': wan(fv(0, _rt80f['mid'], 240, _c65f)),
                    'high_fv_wan1': wan1(fv(0, _rt80f['high'], 240, _c65f)), 'high_fv_wan': wan(fv(0, _rt80f['high'], 240, _c65f)),
                    'month60_wan1': wan1(_v60f), 'month60_wan': wan(_v60f),
                    'reach_50wan': {'month': _m50f, 'ym': ym(_m50f)}, 'reach_100wan': {'month': _m100f, 'ym': ym(_m100f)},
                    'month240': ym(240)}
# 壓力測試沿用 fix-r3／fix-r4：少的錢用表上印的整數萬算；換成幾個月薪水先除物價倍數再除月薪 3.8 萬
_xf['stress'] = {}
for _key, _v, _yrs in (('year5', _v60f, 5), ('y2046', _xaf, 20)):
    _l = {str(d): r0(wan(_v) * 0.8 * d / 100) for d in (40, 50, 60)}
    _m = cpi(_yrs)
    _xf['stress'][_key] = {'amount_wan': wan(_v), 'loss_wan': _l,
                           'loss50_today_money': {'cpi': _m, 'years': _yrs, 'today_wan': r0(_l['50'] / _m),
                                                  'months_salary_38k': r1(r0(_l['50'] / _m) * 10000 / 38000),
                                                  'months_salary_38k_unrounded': r1(_l['50'] / _m * 10000 / 38000)}}
# 延後（fix-r5 同一套）：不多存時，目標跟著年數重查物價倍數
_df = months_to_rescaled(0, _rt80f['low'], base, 134, 241)
_df.update({'ym': ym(_df['month']), 'extra_months': _df['month'] - 240, 'extra_years': round((_df['month'] - 240) / 12, 1),
            'max_delay_years': 5, 'within_max': _df['month'] - 240 <= 60})
_xf['delay_rescaled'] = _df
_xf['section5_2_example'] = {'now_3wan_80pct_loss50_wan': r1(3 * 0.8 * 0.5),
                             'y2046_loss50_wan': _xf['stress']['y2046']['loss_wan']['50']}

# 阿凱：六四（表一低 3.2%）→ 2.7%；已有 30 萬、20 年、目標 450 萬（2046-09）
_akf = {'note': '投入＝月收入的百分比，平均月收入 5 萬；未扣費時 24% 到得了 450 萬，扣 0.5% 以後不夠'}
_akf['pct20_10k'] = fee_case(low64, 20, 300000, 10000, 450)
_akf['options_step500'] = {str(x): fee_case(low64, 20, 300000, x, 450) for x in (12000, 12500, 13000, 13500)}
_akf['min_enough_step500'] = min(int(k) for k, v in _akf['options_step500'].items() if v['enough_exact'])
_akf['min_integer_pct'] = next(p for p in range(20, 41)
                               if fv(300000, after_fee(low64), 240, 50000 * p / 100) >= 4_500_000)
_akf['min_integer_pct_monthly'] = {'avg_50k': 50000 * _akf['min_integer_pct'] // 100,
                                   'low_month_30k': 30000 * _akf['min_integer_pct'] // 100,
                                   'high_month_80k': 80000 * _akf['min_integer_pct'] // 100,
                                   'prev_pct_24_monthly_low_month_30k': 30000 * 24 // 100}
_akm = _akf['min_enough_step500']
_akf['table_2046'] = {lab: {k: {'pct20_10k': wan(fv(300000, after_fee(lookup[s][k]), 240, 10000)),
                                'after_gap': wan(fv(300000, after_fee(lookup[s][k]), 240, _akm)),
                                'rate_after_fee': after_fee(lookup[s][k])} for k in ('low', 'mid', 'high')}
                      for lab, s in (('64', 60), ('82', 80))}
_akf['drill_2046_low'] = {}
for s in (80, 70, 60):
    _a = wan(fv(300000, after_fee(lookup[s]['low']), 240, _akm))
    _ls = {str(d): r0(_a * s / 100 * d / 100) for d in (40, 50, 60)}
    _t = r0(_ls['50'] / cpi(20))
    _akf['drill_2046_low'][str(s)] = {'rate_after_fee': after_fee(lookup[s]['low']), 'amount_wan': _a, 'loss_wan': _ls,
                                      'loss50_today_wan': _t, 'loss50_months_income_50k': r1(_t * 10000 / 50000)}
_d = months_to_rescaled(300000, after_fee(low64), 10000, 302, 241)
_d.update({'ym': ym(_d['month']), 'extra_months': _d['month'] - 240, 'extra_years': round((_d['month'] - 240) / 12, 1),
           'max_delay_years': 3, 'within_max': _d['month'] - 240 <= 36})
_akf['delay_pct20_rescaled'] = _d
_akf['lower_target_wan'] = int(fv(300000, after_fee(low64), 240, 10000) / 100000) * 10
FD['akai'] = _akf

# 小芸與阿哲：頭期款桶全放定存（沒有內扣費用）；長期桶八二（表一低 3.6%）→ 3.1%
_xyf = {'down_payment': {'rate': r0pct, 'fee_pct': 0,
                         'note': '股票 0%、全放台幣定存，沒有內扣費用，不減示範費率；金額和未扣費相同',
                         'fv_25k_wan1': wan1(fv(1_200_000, r0pct, 84, 25000)),
                         'fv_30k_wan1': wan1(fv(1_200_000, r0pct, 84, 30000)),
                         'if_fee_applied_wan1': wan1(fv(1_200_000, after_fee(r0pct), 84, 30000))}}
_ltr = lookup[80]['low']
_xyf['long_term'] = {'save10k': fee_case(_ltr, 30, 400000, 10000, 700),
                     'options_step500': {str(x): fee_case(_ltr, 30, 400000, x, 700) for x in (10000, 10500, 11000)}}
_xyf['long_term']['min_enough_step500'] = min(int(k) for k, v in _xyf['long_term']['options_step500'].items() if v['enough_exact'])
_xym = _xyf['long_term']['min_enough_step500']
_xyf['long_term']['extra_monthly'] = _xym - 10000
_xyf['long_term']['table_2056'] = {k: {'rate_after_fee': after_fee(lookup[80][k]),
                                       'save10k_wan': wan(fv(400000, after_fee(lookup[80][k]), 360, 10000)),
                                       'after_gap_wan': wan(fv(400000, after_fee(lookup[80][k]), 360, _xym))}
                                   for k in ('low', 'mid', 'high')}
_xylt = wan(fv(400000, after_fee(_ltr), 360, _xym))
_xyf['long_term']['stress_2056_low'] = {'amount_wan': _xylt,
                                        'loss_wan': {str(d): r0(_xylt * 0.8 * d / 100) for d in (40, 50, 60)}}
FD['xiaoyun_azhe'] = _xyf

# 陳大哥：防守放台幣定存，但照書上規則仍從整體報酬率直接減 0.5%（把錢算少一點）；股票 0% 那一列不減
_chr = lambda s, k: lookup[s][k] if s == 0 else after_fee(lookup[s][k])
_chf = {'note': '800 萬＋每月 3 萬、60 個月到 2031-09', 'deposit_row_note': FD['deposit_note'],
        'rates_after_fee': {lab: {k: _chr(s, k) for k in ('low', 'mid', 'high')}
                            for lab, s in (('73', 70), ('64', 60), ('55', 50), ('46', 40), ('28', 20), ('0', 0))},
        'fv_2031_wan': {lab: {k: wan(fv(8_000_000, _chr(s, k), 60, 30000)) for k in ('low', 'mid', 'high')}
                        for lab, s in (('73', 70), ('64', 60), ('55', 50), ('46', 40), ('28', 20), ('0', 0))}}
_chf['by_book_table2_46_low'] = fee_case(lookup[40]['low'], 5, 8_000_000, 30000)['by_book_table2']
_lo46f = fv(8_000_000, _chr(40, 'low'), 60, 30000); _lo73f = fv(8_000_000, _chr(70, 'low'), 60, 30000)
_chf['drill_2031_low'] = {}
for s in (70, 60, 50, 40):
    _a = wan(fv(8_000_000, _chr(s, 'low'), 60, 30000))
    _ls = {str(d): r0(_a * s / 100 * d / 100) for d in (40, 50, 60)}
    _chf['drill_2031_low'][str(s)] = {'rate_after_fee': _chr(s, 'low'), 'amount_wan': _a, 'loss_wan': _ls,
                                      'loss50_years_of_gap': r1(_ls['50'] * 10000 / gap_y)}
_chf['stress_800wan_today'] = ch['stress_800wan']  # 現在 800 萬那三列不受報酬率影響，沿用
_chf['first_year_withdrawal'] = {'amount_wan': r1(gap_y / 10000), 'pct_of_46_low': r1(gap_y / _lo46f * 100),
                                 'stage2_amount_wan': r1((gap_y + _extra_y) / 10000)}
_chf['vs_two_stage_targets'] = {
    'amount_46_low_wan': wan(_lo46f), 'amount_73_low_wan': wan(_lo73f),
    '46_low_reaches_33x_two_stage': _lo46f >= _two(33), '46_low_over_33x_two_stage_wan': wan(_lo46f - _two(33)),
    '46_low_reaches_40x_two_stage': _lo46f >= _two(40),
    '46_low_vs_40x_two_stage_wan': wan(abs(_lo46f - _two(40))),
    '73_low_reaches_40x_two_stage': _lo73f >= _two(40),
    '73_minus_46_low_wan': wan(_lo73f - _lo46f),
    'extra_loss50_73_vs_46_wan': _chf['drill_2031_low']['70']['loss_wan']['50'] - _chf['drill_2031_low']['40']['loss_wan']['50']}
_chf['floor_5y_gap_wan'] = r1(gap_y * 5 / 10000)
_chf['deposit_insurance_limit_wan'] = 300
FD['chen'] = _chf
R['fee_demo_0_5pct'] = FD

# ---------- v6.3 批 3（拍板 D02 選 C）：只有「全放定存的桶子」改用當下的一年期定存牌告利率 ----------
# 其他混合配置一律維持查表的防守 2%。1.7% 是 2026 年 9 月五大銀行一年期定存牌告利率
# （完整版第 5 節已經引用過同一個數字，不是新來源）。
# 範圍：小芸與阿哲的頭期款桶（股票 0%、全放台幣定存）、陳大哥「全放定存」那一列。
DEPOSIT_RATE_NOW = 1.7
_d02 = {'rate': DEPOSIT_RATE_NOW,
        'source': '2026 年 9 月五大銀行一年期定存牌告利率（完整版第 5 節已引用）',
        'scope': '只用在全放定存的桶子；股債混合的桶子仍用查表的防守 2%',
        'lookup_defense_rate_kept': DEFENSE}
# 小芸與阿哲 頭期款桶：現有 120 萬、每月存 X、84 個月（2033-09）要 400 萬
_dp17 = {'months': 84, 'target_ym': ym(84), 'target_wan': 400,
         'fv_25k_wan1': wan1(fv(1_200_000, DEPOSIT_RATE_NOW, 84, 25000)),
         'fv_25k_wan': wan(fv(1_200_000, DEPOSIT_RATE_NOW, 84, 25000))}
_dp17['gap_wan'] = r0(400 - _dp17['fv_25k_wan1'])
_dp17['save_more'] = {str(x): {'fv_wan1': wan1(fv(1_200_000, DEPOSIT_RATE_NOW, 84, x)),
                               'fv_wan': wan(fv(1_200_000, DEPOSIT_RATE_NOW, 84, x)),
                               'enough': fv(1_200_000, DEPOSIT_RATE_NOW, 84, x) >= 4_000_000}
                      for x in (25000, 28000, 28500, 29000, 29500, 30000, 30500)}
_dp17['save_more_min_step500'] = min(int(k) for k, v in _dp17['save_more'].items() if v['enough'])
_m17 = months_to(1_200_000, DEPOSIT_RATE_NOW, 25000, 4_000_000)
_dp17['delay_25k'] = {'month': _m17, 'ym': ym(_m17), 'extra_months': _m17 - 84}
_dp17['vs_2pct'] = {'fv_25k_wan1': wan1(fv(1_200_000, r0pct, 84, 25000)),
                    'fv_30k_wan': wan(fv(1_200_000, r0pct, 84, 30000)),
                    'note': '查表 2% 的舊數字，只留作對照'}
_d02['xiaoyun_azhe_down_payment'] = _dp17
# 陳大哥「全放定存」那一列：800 萬＋每月 3 萬、60 個月到 2031-09
_ch0now = fv(8_000_000, DEPOSIT_RATE_NOW, 60, 30000)
_ch0tbl = fv(8_000_000, lookup[0]['low'], 60, 30000)
_d02['chen_all_deposit'] = {
    'rate': DEPOSIT_RATE_NOW, 'amount_wan': wan(_ch0now), 'amount_wan1': wan1(_ch0now),
    'reaches_33x_two_stage': _ch0now >= _two(33), 'over_33x_two_stage_wan': wan(_ch0now - _two(33)),
    'reaches_40x_two_stage': _ch0now >= _two(40), 'vs_40x_two_stage_wan': wan(_two(40) - _ch0now),
    'lookup_2pct_amount_wan': wan(_ch0tbl),
    'stock20_after_fee_rate': after_fee(lookup[20]['low']),
    'stock20_after_fee_amount_wan': wan(fv(8_000_000, after_fee(lookup[20]['low']), 60, 30000)),
    'note': '書上小字的比較對象改成「查表 0% 那一列的 2%」：股票兩成扣完示範費率（1.9%）比查表 2% 那一列少一點，'
            '但比全放定存用 1.7% 算的多——這一句講的是扣費率的算法，不是定存利率'}
R['deposit_rate_d02'] = _d02

# ---------- 台灣家庭實際存多少（第 5 節「存多少算合理？兩個參考」） ----------
# 行政院主計總處「113 年家庭收支調查」統計表，2026-09-20 下載。
# 原始 ods 存在 wip/v63-review/sources/Year10.ods（第 10 表）、Year12.ods（第 12 表），
# 下面的數字是用 python 讀 content.xml 逐格核過的，不是抄新聞稿。
FIES_URL = 'https://www.stat.gov.tw/News_Content.aspx?n=3908&s=235198'
_fies_avg = {'disposable_income': 1165206, 'consumption': 888699, 'savings': 276507, 'savings_rate_pct': 23.73}
# 第 12 表：可支配所得按戶數五等分位組，113 年平均每戶儲蓄（元）與該年儲蓄率（%）。
# 最低所得組的儲蓄率官方印「--」（儲蓄為負，算不出比率）。
_fies_q = [
    {'group': '最低所得組（最低的 20%）', 'savings': -18214, 'savings_rate_pct': None, 'note': '儲蓄為負，官方表印「--」'},
    {'group': '第二組', 'savings': 55971, 'savings_rate_pct': 7.98},
    {'group': '第三組（中間）', 'savings': 152986, 'savings_rate_pct': 15.28},
    {'group': '第四組', 'savings': 306654, 'savings_rate_pct': 22.19},
    {'group': '最高所得組（最高的 20%）', 'savings': 885139, 'savings_rate_pct': 37.55},
]
R['tw_household_savings'] = {
    'basis': '行政院主計總處「113 年家庭收支調查」統計表第 10 表（可支配所得、消費支出及儲蓄）與第 12 表'
             '（戶數五等分位組之平均每戶儲蓄）；113 年＝西元 2024 年；2026-09-20 下載，'
             '原始 ods 存在 wip/v63-review/sources/Year10.ods、Year12.ods。',
    'source_url': FIES_URL, 'year_roc': 113, 'year_ad': 2024, 'downloaded': '2026-09-20',
    'unit': '元／每戶／年',
    'average_household': _fies_avg,
    'quintiles': _fies_q,
    # 書上用的四捨五入版本
    'guide_rounded': {'disposable_income_wan': r0(_fies_avg['disposable_income'] / 10000),
                      'savings_wan': r0(_fies_avg['savings'] / 10000),
                      'savings_rate_pct_1dp': r1(_fies_avg['savings_rate_pct']),
                      'lowest_group_shortfall_wan1': r1(abs(_fies_q[0]['savings']) / 10000),
                      'rates_1dp': [None] + [r1(q['savings_rate_pct']) for q in _fies_q[1:]]},
    'definitions': {
        '可支配所得': '所得收入總計 − 非消費支出（＝利息支出＋經常移轉支出，後者含綜合所得稅、社會保險保費等）；'
                 '報告名詞解釋第二十項「各種家庭所得結構關係」：可支配所得＝所得收入總計[400]−非消費支出[600]＝消費+儲蓄。',
        '儲蓄': '可支配所得 − 消費支出。',
        '利息支出': '報告名詞解釋第十八項：「消費性借款利息、典當利息、購置私有住宅貸款利息及死會利息支出等，'
                 '其中貸款利息是指扣除還本後的利息支出。」——房貸利息在算可支配所得以前就扣掉了。',
        '房貸本金': '報告沒有逐條定義償還本金怎麼歸類（書上因此不把這一點寫成官方定義）。',
    },
    'caveats': ['「平均每戶」是全體家庭的平均，不是中位數；五等分位各組的數字也是該組的平均',
                '家庭收支調查的口徑是「戶」，不是個人；戶內人口數各組不同',
                '儲蓄率是各該組的儲蓄 ÷ 該組可支配所得，最低所得組儲蓄為負，官方表印「--」'],
}
# 自己驗算一次：儲蓄＝可支配所得−消費支出；儲蓄率＝儲蓄÷可支配所得
assert _fies_avg['disposable_income'] - _fies_avg['consumption'] == _fies_avg['savings']
assert r1(100 * _fies_avg['savings'] / _fies_avg['disposable_income']) == 23.7
assert round(100 * _fies_avg['savings'] / _fies_avg['disposable_income'], 2) == _fies_avg['savings_rate_pct']
assert R['tw_household_savings']['guide_rounded']['disposable_income_wan'] == 117
assert R['tw_household_savings']['guide_rounded']['savings_wan'] == 28
assert R['tw_household_savings']['guide_rounded']['lowest_group_shortfall_wan1'] == 1.8
assert R['tw_household_savings']['guide_rounded']['rates_1dp'] == [None, 8.0, 15.3, 22.2, 37.6]
# 五組裡有三組平均存不到兩成（最低組為負、8.0%、15.3%）
assert sum(1 for q in _fies_q if q['savings_rate_pct'] is None or q['savings_rate_pct'] < 20) == 3


# ---------- 本金還小的時候：多拚 1 個百分點報酬 vs 多存 1,000 元（第 5 節） ----------
# 小安第一年：每月月底投 5,000 元，年率÷12 按月複利（和書上其他試算同一個口徑）。
_eff_6 = fv(0, 6, 12, 5000)
_eff_7 = fv(0, 7, 12, 5000)
R['small_base_effort'] = {
    'basis': '每月月底投 5,000 元、12 個月；年率 ÷ 12 按月複利，沒有扣費用與稅。'
             '6% 與 7% 是第 4 節的普通算、樂觀算，這裡只用來看「多 1 個百分點」值多少。',
    'monthly': 5000, 'months': 12, 'principal_year1': 60000,
    'fv_6pct': round(_eff_6, 2), 'fv_7pct': round(_eff_7, 2),
    'gap_1pp': round(_eff_7 - _eff_6, 2), 'gap_1pp_r0': r0(_eff_7 - _eff_6),
    'save_1000_more_per_month_year1': 12000,
    'times': r1(12000 / (_eff_7 - _eff_6)),
    'note': '書上主線寫「大約多 300 元」，實算 285 元；同一年多存 1,000 元／月是 12,000 元，差約 42 倍。',
}
assert R['small_base_effort']['gap_1pp_r0'] == 285
assert R['small_base_effort']['save_1000_more_per_month_year1'] == 12000

# ---------- v6.3 批 3（拍板 D04 選 B）：大跌那年，比例掉出門檻要不要動防守 ----------
# 純算術：股債比例 × 一次跌幅，不含報酬率、不含新錢的複利。
def _rebalance_after_crash(total, stock_pct, stock_drop_pct, band_lo=None, band_hi=None):
    st0 = total * stock_pct / 100; df0 = total - st0
    st1 = st0 * (1 - stock_drop_pct / 100); tot1 = st1 + df0
    share1 = st1 / tot1 * 100
    target_stock = tot1 * stock_pct / 100
    from_defense = target_stock - st1          # 從防守搬多少去買股票，比例才回到原設定
    # 只用新錢補、不動防守：新錢 x 全買股票，(st1+x)/(tot1+x)=stock_pct → x
    k = stock_pct / 100
    new_money = (k * tot1 - st1) / (1 - k)
    return {'total_wan': wan(total), 'stock_pct': stock_pct, 'stock_drop_pct': stock_drop_pct,
            'stock_before_wan': wan(st0), 'defense_wan': wan(df0),
            'stock_after_wan': wan(st1), 'total_after_wan': wan(tot1),
            'stock_share_after_pct': r1(share1),
            'band': [band_lo, band_hi], 'out_of_band': (band_lo is not None and share1 < band_lo),
            'move_from_defense_wan': wan(from_defense),
            'defense_left_wan': wan(df0 - from_defense),
            'new_money_only_wan': wan(new_money)}
R['rebalance_after_crash_d04'] = {
    '100wan_82_stock_half': _rebalance_after_crash(1_000_000, 80, 50, 75, 85),
    'note': '100 萬、股票八成防守兩成，股票跌一半：股票 80→40 萬、總資產剩 60 萬、股票占 66.7%，'
            '掉出 5/25 給八成的 75%–85%。要當天回到八成，從防守搬 8 萬去買股票（防守剩 12 萬）；'
            '只用新錢補、不動防守，要再投入 40 萬新錢才會回到八成'}

# v6.3 批 3（Q 組）的引用句：patch-Q.json 已整合進 guide/index.html，
# 下面在 quotes 定義完之後併進 quotes（見檔尾 quotes += QUOTES_V63_Q）。
QUOTES_V63_Q = [
    '每月存 2.5 萬，到 2033 年 9 月約 358 萬，差 42 萬',
    '每月 3 萬，約 403 萬，夠，選這個（2.95 萬只到約 398 萬，不夠）',
    '全放定存，試算改用當下的一年期定存 1.7%',
    '到 2031 年約 1,059 萬',
]

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
    'guide_basis': '第 5 節：每年年底投入 6 萬、一年 7%（第 4 節樂觀算，樂觀）',
    'years_first_60wan_7pct': round(yrs60, 2), 'return_share_7pct_pct': r0((1 - 60000 * yrs60 / 600000) * 100),
    'for_reference_low_4pct': {'years': round(yrs60_low, 2), 'return_share_pct': r0((1 - 60000 * yrs60_low / 600000) * 100),
                               'note': '完整版沒有這組數字；只供作者決定要不要改用保守算'}}
R['fee_gap'] = {'monthly': 5000, 'months': 360, 'fv_6pct_wan': wan(fv(0, 6, 360, 5000)), 'fv_5pct_wan': wan(fv(0, 5, 360, 5000)),
                'gap_wan': wan(fv(0, 6, 360, 5000) - fv(0, 5, 360, 5000)),
                'gap_share_pct': r1(100 * (1 - fv(0, 5, 360, 5000) / fv(0, 6, 360, 5000))),
                'gap_share_20y_pct': r1(100 * (1 - fv(0, 5, 240, 5000) / fv(0, 6, 240, 5000))),
                'note': '每年多付 1 個百分點：30 年少 gap_share_pct%、20 年少 gap_share_20y_pct%，兩個都超過一成'
                        '（完整版第 7 步「寫下目標」與第 6 節的 86 萬用的是同一組）'}
R['sweet_spot_guide'] = {'rule': '70÷整體報酬率', 'years': {str(k): r1(70 / k) for k in (7, 6, 4, 3.6, 2.8)}}

# ---------- 甜蜜點與滿足點（年複利、投入固定、不扣物價費用稅） ----------
# 每年年底投入 C、年報酬 r，n 年後資產＝C×((1+r)^n−1)/r，一年長出來的錢＝資產×r＝C×((1+r)^n−1)
# 甜蜜點：長出來的錢＝C            → (1+r)^n = 2       → n = ln 2 ÷ ln(1+r)
# 滿足點：長出來的錢＝一年生活費   → (1+r)^n = 1÷s     → n = ln(1÷s) ÷ ln(1+r)
#   （儲蓄率 s＝存下來÷收入；生活費＝收入−存下來＝C×(1÷s−1)）
# 所以 s＝50% 時滿足點＝甜蜜點；s＝1/3 是 ln3÷ln2≈1.585 倍，s＝1/4 是 ln4÷ln2＝2 倍（和報酬率無關）
SAVE_RATES = [('50%', 0.5), ('33%', 1 / 3), ('25%', 0.25)]
# v6.3 批 3 修正（讀者 should-a3）：表外那一句「存不到四分之一的人長很多」補一個數字，用同一條公式
BELOW_TABLE_RATE = 0.15
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
    'below_table_15pct': {'save_rate': BELOW_TABLE_RATE,
                          'years': {str(r): r1(years_to_point(r, BELOW_TABLE_RATE)) for r in (4, 6, 7)},
                          'extra_years_vs_25pct_at_4pct': r1(years_to_point(4, BELOW_TABLE_RATE) - years_to_point(4, 0.25)),
                          'note': '完整版第 5 節滿足點表下那一句：存 15%、保守算 4% 是 48.4 年，比存四分之一的 35.3 年多了十三年'},
    'guide_rounding': '完整版第 5 節寫的樂觀算 7% 約 10 年、普通算 6% 約 12 年、保守算 4% 約 18 年，就是這一組四捨五入',
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
    # 再減掉費用：物價 2 個百分點之外，再減暫估總費用率 0.5 個百分點（自己買指數 ETF 的暫估上限）
    'after_inflation_and_fee_0_5pct': {'method': '報酬率減 2 個百分點（物價）再減 0.5 個百分點（暫估總費用率）',
                                       'fee_pct': 0.5,
                                       'years_save_half': {str(r): r1(years_to_point(r - 2 - 0.5, 0.5)) for r in (4, 6, 7)},
                                       'note': '完整版第 5 節滿足點小字：保守算 4% 只減物價約 35 年；再減 0.5% 費用約 47 年'},
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

# ---------- 第 8 節：美股連續 20 年，扣掉物價最差的那一段（v7 第 20 版 B3） ----------
# 口徑：Shiller 公開月資料，S&P 500 含息（月報酬＝(P_t＋D_t/12)÷P_{t−1}，同 shiller_tr()）；
# 物價用同一份檔案的 Consumer Price Index 欄。視窗是 12 月到 12 月的整年視窗，第一個起點
# 1950 年 12 月（＝1951 到 1970 年），和 J.P. Morgan 那張「1950–2025、整年」的表對齊寫法。
# 視窗名稱寫成「起點年＋1 到終點年」：1961-12 → 1981-12 記成「1962–1981」。
# 股利欄只到 2023 年 6 月，最後一個算得出來的視窗是 2003–2022；所以最後三個視窗
# （2004–2023、2005–2024、2006–2025）算不到，那幾段不會是最差的。
def us_20y_windows(first_dec=1950, years=20):
    rows = list(_csv.DictReader(open(SHILLER_CSV, encoding='utf-8')))
    end = next(i for i, r in enumerate(rows) if float(r['Dividend'] or 0) == 0)
    rows = rows[:end]
    tr = [1.0]
    for k in range(1, len(rows)):
        p0 = float(rows[k - 1]['SP500']); p1 = float(rows[k]['SP500']); d = float(rows[k]['Dividend'])
        tr.append(tr[-1] * ((p1 + d / 12) / p0))
    idx = {r['Date'][:7]: i for i, r in enumerate(rows)}
    cpi = {r['Date'][:7]: float(r['Consumer Price Index']) for r in rows}
    out = []; y = first_dec
    while ('%d-12' % y) in idx and ('%d-12' % (y + years)) in idx:
        a = '%d-12' % y; b = '%d-12' % (y + years)
        g = tr[idx[b]] / tr[idx[a]]
        out.append({'window': '%d–%d' % (y + 1, y + years), 'from': a, 'to': b,
                    'nominal_pct': round((g ** (1.0 / years) - 1) * 100, 2),
                    'real_pct': round(((g * cpi[a] / cpi[b]) ** (1.0 / years) - 1) * 100, 2)})
        y += 1
    return out

def us_worst_20y_real():
    w = us_20y_windows()
    worst_real = min(w, key=lambda x: x['real_pct'])
    worst_nom = min(w, key=lambda x: x['nominal_pct'])
    return {'n_windows': len(w), 'first': w[0]['window'], 'last': w[-1]['window'],
            'worst_real': worst_real, 'worst_nominal': worst_nom,
            'note': ('書上第 8 節主線寫「放二十年，最差的那一段平均一年約 6%；但扣掉物價，'
                     '最差的二十年（1962 到 1981）一年只剩不到 1%」；6% 是 J.P. Morgan 那張表的數字，'
                     '「不到 1%」是這裡算出來的 ' + format(worst_real['real_pct'], '.2f') + '%。')}

R['us_worst_20y_real'] = us_worst_20y_real()
_w = R['us_worst_20y_real']
assert _w['worst_real']['window'] == '1962–1981', _w['worst_real']
assert 0.7 <= _w['worst_real']['real_pct'] <= 0.8, _w['worst_real']
assert abs(_w['worst_real']['nominal_pct'] - 6.68) <= 0.05, _w['worst_real']
assert _w['worst_nominal']['window'] == '1999–2018', _w['worst_nominal']
assert abs(_w['worst_nominal']['nominal_pct'] - 5.85) <= 0.05, _w['worst_nominal']
assert _w['worst_real']['real_pct'] < 1.0
# 第 20 版裁判後修正 S5：口徑小字要寫出四個數字（6.7／0.8／5.9／3.6）
assert abs(_w['worst_real']['nominal_pct'] - 6.7) <= 0.05, _w['worst_real']
assert abs(_w['worst_real']['real_pct'] - 0.8) <= 0.05, _w['worst_real']
assert abs(_w['worst_nominal']['real_pct'] - 3.6) <= 0.05, _w['worst_nominal']

# ---------- 第 8 節：兩張長線圖的關鍵點（v7 批 S2） ----------
# 兩條月序列的實作在 tools/v7_series.py（畫圖的 tools/v7_g08_long_run.py 匯入同一份，
# 所以圖上和這裡不會各算各的）。這裡只算關鍵點並 assert：起訖值、最大回撤發生在哪一年。
# 台股是價格指數（不含息，1990 起，證交所線上只有這一份追得到 1990 年）；
# 美股是含息、名目，1871-01～2023-06 用 Shiller，2023-07 起串接 S&P 500 總報酬指數。
sys.path.insert(0, HERE)
import v7_series as _vs


def shiller_tr_extended():
    """薄包裝：Shiller 含息月序列接上 ^SP500TR，延長到 2026-08。實作見 tools/v7_series.py。"""
    return _vs.shiller_tr_extended()


def long_run_key_points():
    tw_m, tw_v, _rows = _vs.taiex_price_monthly()
    us_m, us_tr = shiller_tr_extended()
    out = {'taiex': {'source': '證交所發行量加權股價指數（價格，不含股利），各月最後一個交易日收盤',
                     'file': 'research/data/taiex_price_monthend_1990_2025.csv',
                     'from': tw_m[0], 'to': tw_m[-1], 'n_months': len(tw_m),
                     'first': round(tw_v[0], 2), 'last': round(tw_v[-1], 2),
                     'max_drawdown_pct': round(_vs.max_drawdown(tw_m, tw_v)[0], 2),
                     'max_drawdown_peak': _vs.max_drawdown(tw_m, tw_v)[1],
                     'max_drawdown_trough': _vs.max_drawdown(tw_m, tw_v)[2]}}
    # v7 批 W：第 8 節台股長線圖改畫這一條——1990 價格指數接 2003 起的含息報酬指數，逐週收盤。
    sw_d, sw_v = _vs.taiex_spliced_weekly()
    _dd, _dv, factor = _vs.taiex_spliced_daily()
    hi_date, hi_close = max(((d, v) for d, v in zip(_dd, _dv) if d < '1991-01-01'), key=lambda r: r[1])
    lo_date, lo_close = min(((d, v) for d, v in zip(_dd, _dv) if '1991-01-01' > d >= hi_date),
                            key=lambda r: r[1])
    out['taiex_spliced'] = {
        'source': ('1990-01-04～2002-12-31 證交所發行量加權股價指數（價格），'
                   '2003-01-02 起發行量加權股價報酬指數（含股利），接在 2003-01-02'),
        'file': ('research/data/taiex_price_daily_1990_2002.csv＋'
                 'research/data/taiex_tr_monthly_raw.csv'),
        'splice_date': _vs.TAIEX_SPLICE_DATE, 'splice_factor': round(factor, 8),
        'from': sw_d[0], 'to': sw_d[-1], 'n_weeks': len(sw_d),
        'first': round(sw_v[0], 2), 'last': round(sw_v[-1], 2),
        'high_1990_date': hi_date, 'high_1990_close': round(hi_close, 2),
        'low_1990_date': lo_date, 'low_1990_close': round(lo_close, 2),
        # 只看價格（不含股利）什麼時候再收在 1990 年那個高點：用逐月檔的月內最高收盤查
        'back_to_high_month_price': next(
            (r['month'] for r in _rows
             if r['month'] > hi_date[:7] and float(r['month_high_close']) >= hi_close), None),
        # 算進 2003 年以後的股利以後，第一次收在那個高度的那一週
        'back_to_high_week_total': next(
            (d for d, v in zip(sw_d, sw_v) if d > hi_date and v >= hi_close), None),
    }
    for name, start in (('us_1950', '1950-01'), ('us_1929', '1929-01')):
        i = us_m.index(start)
        m2 = us_m[i:]
        v2 = [v / us_tr[i] for v in us_tr[i:]]
        dd = _vs.max_drawdown(m2, v2)
        out[name] = {'source': 'S&P 500 含息、名目（Shiller 1871-01～2023-06，之後串接 ^SP500TR）',
                     'from': m2[0], 'to': m2[-1], 'n_months': len(m2),
                     'first': 1.0, 'last_multiple': round(v2[-1], 1),
                     'annualised_pct': round((v2[-1] ** (12.0 / (len(v2) - 1)) - 1) * 100, 2),
                     'max_drawdown_pct': round(dd[0], 2),
                     'max_drawdown_peak': dd[1], 'max_drawdown_trough': dd[2]}
    return out


R['long_run'] = long_run_key_points()
_lr = R['long_run']
# 台股：1990-01 收 12,054.35 → 2025-12 收 28,963.60；月底收盤最深的一段是 1990-01 → 1990-09
assert _lr['taiex']['n_months'] == 432, _lr['taiex']
assert _lr['taiex']['first'] == 12054.35 and _lr['taiex']['last'] == 28963.60, _lr['taiex']
assert _lr['taiex']['max_drawdown_peak'][:4] == '1990' and _lr['taiex']['max_drawdown_trough'][:4] == '1990', _lr['taiex']
assert -78.0 <= _lr['taiex']['max_drawdown_pct'] <= -77.0, _lr['taiex']
# 台股串接序列（批 W）：1990-01-06～2025-12-31 共 1,859 週；1990 年最高的收盤是 1990-02-10 的
# 12,495.34，同年最低是 1990-10-01 的 2,560.47；只看價格要到 2020-07 才再收在那個高度，
# 算進 2003 年以後的股利則是 2013-12-27 那一週。圖說寫的就是這幾個數字。
_ts = _lr['taiex_spliced']
assert _ts['from'] == '1990-01-06' and _ts['to'] == '2025-12-31', _ts
assert _ts['n_weeks'] == 1859, _ts
assert _ts['splice_date'] == '2003-01-02' and abs(_ts['splice_factor'] - 1) < 1e-4, _ts
assert (_ts['high_1990_date'], _ts['high_1990_close']) == ('1990-02-10', 12495.34), _ts
assert (_ts['low_1990_date'], _ts['low_1990_close']) == ('1990-10-01', 2560.47), _ts
assert _ts['back_to_high_month_price'] == '2020-07', _ts
assert _ts['back_to_high_week_total'] == '2013-12-27', _ts
# 美股 1950 起（批 T 起指南不畫了，留著當對照）：起點 1 倍 → 2026-08 約 4,598 倍；
# 最深的一段是 2007-10 → 2009-03（約 −49%）
assert _lr['us_1950']['to'] == '2026-08' and _lr['us_1950']['n_months'] == 920, _lr['us_1950']
assert abs(_lr['us_1950']['last_multiple'] - 4598.2) <= 1.0, _lr['us_1950']
assert (_lr['us_1950']['max_drawdown_peak'], _lr['us_1950']['max_drawdown_trough']) == ('2007-10', '2009-03'), _lr['us_1950']
assert abs(_lr['us_1950']['max_drawdown_pct'] + 49.04) <= 0.1, _lr['us_1950']
# 美股 1929 起（批 T 起指南放這一版）：1929-01 到 2026-08 共 1,172 個月，起點 1 倍 → 約 9,899 倍
# （平均一年約 9.9%）；最深的一段是 1929-09 → 1932-06，帳面少掉約 82%。圖說寫的就是這兩個數字：
# 「1929 年初投進去的 1 元…變成大約 9,899 元；中間最深的一次，帳面少掉 82%。」
assert _lr['us_1929']['from'] == '1929-01' and _lr['us_1929']['to'] == '2026-08', _lr['us_1929']
assert _lr['us_1929']['n_months'] == 1172, _lr['us_1929']
assert abs(_lr['us_1929']['last_multiple'] - 9898.7) <= 2.0, _lr['us_1929']
assert '{:,}'.format(int(round(_lr['us_1929']['last_multiple']))) == '9,899', _lr['us_1929']
assert abs(_lr['us_1929']['annualised_pct'] - 9.89) <= 0.05, _lr['us_1929']
assert (_lr['us_1929']['max_drawdown_peak'], _lr['us_1929']['max_drawdown_trough']) == ('1929-09', '1932-06'), _lr['us_1929']
assert abs(_lr['us_1929']['max_drawdown_pct'] + 81.76) <= 0.1, _lr['us_1929']
assert round(-_lr['us_1929']['max_drawdown_pct']) == 82, _lr['us_1929']

# ---------- 第 8 節台股長線圖：1990–2002 那一段的股利補多少（v7 批 Z） ----------
# 官方含息指數只有 2003 年以後，1990–2002 沒有，只能回推：
#     當年含息報酬 ≈ 當年價格報酬 ×（1 ＋ 當年底全市場殖利率 × 0.74）
# 0.74 是折算係數。證交所公布的殖利率，分子含「盈餘轉增資股票股利」，而配股不改變市值、
# 加權指數本來就已經完整反映，不折算就是重複計算；係數取自 2003–2008 年官方含息指數隱含的
# 股利貢獻 ÷ 當年公布殖利率的中位數。1991–1993 證交所線上查不到殖利率，以 2.0% 代入
# （1994 年實際值 2.24%）。做法、對帳與敏感度見
# wip/v63-review/debate/verify-taiex-pre2003-dividends.md 第 1.4、1.5、4.5 節。
TAIEX_DIV_HAIRCUT = 0.74
TAIEX_ANNUAL_CSV = os.path.join(ROOT, 'research', 'data', 'taiex-price-vs-total-return-1990-2025.csv')


def _taiex_annual_rows(path=TAIEX_ANNUAL_CSV):
    """年底值的逐年表（欄位見 research/data/README.md），略過開頭的 # 註解行。"""
    import csv
    with open(path, encoding='utf-8') as f:
        lines = [l for l in f if not l.startswith('#')]
    return {int(r['year']): r for r in csv.DictReader(lines)}


def taiex_pre2003_dividend_estimate(y0=1990, y1=2002, haircut=TAIEX_DIV_HAIRCUT):
    rows = _taiex_annual_rows()
    n = y1 - y0
    p0, p1 = float(rows[y0]['taiex_close']), float(rows[y1]['taiex_close'])
    idx_raw = idx_adj = 1.0
    for y in range(y0 + 1, y1 + 1):
        gr = float(rows[y]['taiex_close']) / float(rows[y - 1]['taiex_close'])
        dy = float(rows[y]['market_dy_pct']) / 100.0
        idx_raw *= gr * (1 + dy)
        idx_adj *= gr * (1 + dy * haircut)
    ann = lambda m: (m ** (1.0 / n) - 1) * 100
    price_ann, tr_adj, tr_raw = ann(p1 / p0), ann(idx_adj), ann(idx_raw)
    return {
        'source': ('證交所發行量加權股價指數（價格）年底收盤，加上證交所「市場交易月報」'
                   '第 1 表的全市場年底殖利率，殖利率乘 %.2f 折算後逐年連乘' % haircut),
        'file': 'research/data/taiex-price-vs-total-return-1990-2025.csv＋'
                'research/data/twse-market-dividend-yield-1994-2025.csv',
        'from': '%d-12' % y0, 'to': '%d-12' % y1, 'years': n,
        'haircut': haircut,
        'dy_assumed_years': [y for y in range(y0, y1 + 1) if rows[y]['dy_is_assumed'] == 'Y'],
        'price_close_first': p0, 'price_close_last': p1,
        'price_annualised_pct': round(price_ann, 2),
        'total_return_annualised_pct': round(tr_adj, 2),
        'dividend_contribution_pp': round(tr_adj - price_ann, 2),
        'total_return_annualised_pct_no_haircut': round(tr_raw, 2),
        'index_adj_last': round(p0 * idx_adj, 2),
    }


R['taiex_pre2003_dividends'] = taiex_pre2003_dividend_estimate()
_pd = R['taiex_pre2003_dividends']
# 1990 年底 4,530.16 → 2002 年底 4,452.45：價格年化 −0.14%（十二年白做工）。
# 把股利折算後算進去，年化 +2.28%，股利貢獻 2.42 個百分點——圖說寫「−0.14%」與「大約 +2%」。
assert _pd['years'] == 12 and _pd['dy_assumed_years'] == [1991, 1992, 1993], _pd
assert abs(_pd['price_annualised_pct'] - (-0.14)) <= 0.05, _pd
assert 1.8 <= _pd['total_return_annualised_pct'] <= 2.3, _pd
assert round(_pd['total_return_annualised_pct']) == 2, _pd
assert abs(_pd['dividend_contribution_pp'] - 2.42) <= 0.05, _pd
# 和檔案裡預先算好的那一欄對帳（approx_tr_index_adj 的 2002 年那一格 ＝ 5,936.55）
assert abs(_pd['index_adj_last'] - 5936.55) <= 0.5, _pd
# 不折算會算成 +3.1%，那是把配股重複計算的結果，書上不用
assert abs(_pd['total_return_annualised_pct_no_haircut'] - 3.13) <= 0.05, _pd


# ---------- 第 8 節：兩張滾動報酬圖的關鍵數字（v7 批 S6） ----------
# 圖 A「抱幾年，報酬落在哪個範圍」與圖 B「滾動 30 年的年化報酬」都用同一條序列
# （shiller_tr_extended）。每個月都當一次買進日，抱滿 N 年，換算成平均一年的報酬；
# 視窗彼此重疊，不是互相獨立的樣本。名目、沒扣物價費用稅。
def us_rolling_summaries(periods=(1, 3, 5, 10, 20, 30)):
    months, tr = shiller_tr_extended()
    return {'%d年' % y: _vs.rolling_summary(months, tr, y) for y in periods}


R['us_rolling'] = us_rolling_summaries()
_rr = R['us_rolling']
# 圖上寫的三個數字（最差／最好／中位）與視窗數，改資料時這裡會先斷
_ROLL_EXPECT = {'1年': (1856, -62.28, 139.81, 11.27),
                '3年': (1832, -40.20, 39.67, 9.92),
                '5年': (1808, -17.31, 33.66, 9.79),
                '10年': (1748, -4.02, 21.17, 8.75),
                '20年': (1628, 2.05, 17.95, 8.17),
                '30年': (1508, 3.64, 14.32, 9.93)}
for _k, (_n, _mn, _mx, _md) in _ROLL_EXPECT.items():
    _r = _rr[_k]
    assert _r['n'] == _n, (_k, _r['n'], _n)
    assert abs(_r['min'] - _mn) <= 0.02 and abs(_r['max'] - _mx) <= 0.02, (_k, _r)
    assert abs(_r['median'] - _md) <= 0.02, (_k, _r)
# 圖 B 的標註點（批 Y 改成三條線各自的最低，30 年最高只留在「想深入」那段）；
# 「30 年沒有一個起點是虧的」要站得住：30 年最差也還是正的
assert _rr['30年']['min_end'] == '1932-06' and _rr['30年']['max_end'] == '2000-07', _rr['30年']
assert _rr['30年']['min'] > 0, _rr['30年']
assert abs(_rr['30年']['p15'] - 6.71) <= 0.02 and abs(_rr['30年']['p85'] - 11.93) <= 0.02, _rr['30年']


# ---------- 第 8 節圖 B（v7 批 X：滾動報酬圖改成 10／20／30 年三條線） ----------
# 圖說寫的三句話各對一個數字：抱 10 年約 3% 的起點是虧的、最差 −4.0%；抱 20 年一個都沒有虧、
# 最差 +2.0%；抱 30 年最差 +3.6%。另外算「拿掉 1926 年以前那一段，30 年最差會變成多少」，
# 兩張圖的 p.note 都寫了這個數字（7.6%）。
def us_rolling_negative_share(periods=(10, 20, 30)):
    months, tr = shiller_tr_extended()
    out = {}
    for y in periods:
        pts = _vs.rolling_annualised(months, tr, y)
        neg = sum(1 for _m, v, _s in pts if v < 0)
        out['%d年' % y] = {'n': len(pts), 'negative': neg, 'negative_pct': round(neg * 100.0 / len(pts), 2),
                           'first_end': pts[0][0], 'last_end': pts[-1][0]}
    return out


def us_rolling_post1926(start='1926-01', years=30):
    """拿掉 Shiller 依 Cowles 回推的那一段（1926 年以前），30 年最差變成多少。"""
    months, tr = shiller_tr_extended()
    i = months.index(start)
    r = _vs.rolling_summary(months[i:], tr[i:], years)
    return {'start': start, 'years': years, 'n': r['n'], 'min': round(r['min'], 2),
            'min_start': r['min_start'], 'min_end': r['min_end']}


R['us_rolling_negative'] = us_rolling_negative_share()
R['us_rolling_post1926'] = us_rolling_post1926()
_rn = R['us_rolling_negative']
# 三條線的起點：最早的視窗從 1871-01 起算，所以 10 年線第一個點在 1881-01、20 年線 1891-01、30 年線 1901-01
assert (_rn['10年']['first_end'], _rn['20年']['first_end'], _rn['30年']['first_end']) == \
       ('1881-01', '1891-01', '1901-01'), _rn
assert _rn['10年']['last_end'] == _rn['30年']['last_end'] == '2026-08', _rn
assert _rn['10年']['negative'] == 51 and abs(_rn['10年']['negative_pct'] - 2.92) <= 0.02, _rn['10年']
assert _rn['20年']['negative'] == 0 and _rn['30年']['negative'] == 0, _rn
# 最差那一次是哪個起點開始的（圖說沒寫起點，但三個最差都落在 1929 年前後，這裡釘住免得換資料沒發現）
assert _rr['10年']['min_start'] == '1929-08' and _rr['10年']['min_end'] == '1939-08', _rr['10年']
assert _rr['20年']['min_start'] == '1929-09' and _rr['20年']['min_end'] == '1949-09', _rr['20年']
assert _rr['30年']['min_start'] == '1902-06', _rr['30年']
# 圖說四捨五入到一位小數之後要正好是這幾個數字
assert '%.1f' % _rr['10年']['min'] == '-4.0' and '%.1f' % _rr['20年']['min'] == '2.0', _rr
assert '%.1f' % _rr['30年']['min'] == '3.6', _rr['30年']
# 兩張圖 p.note 的 7.6%：1926-01 起算的 30 年最差（最差那一段結束在 1959-09，不再是 1932-06）
_rp = R['us_rolling_post1926']
assert abs(_rp['min'] - 7.63) <= 0.02 and '%.1f' % _rp['min'] == '7.6', _rp
assert _rp['min_end'] == '1959-09', _rp

# ---------- 第 24 節第三題：2.31% 提領率換成幾倍（v7 第 20 版 B5） ----------
# Anarkulova, Cederburg, O'Doherty & Sias (2025), JPEF 24(3): 38 個已開發國家、
# 一對 65 歲夫妻、5% 破產容忍度 → 一年提 2.31%。倍數＝1 ÷ 提領率。
def swr_multiple(rate_pct):
    return round(100.0 / rate_pct, 2)

R['swr_multiples'] = {'2.31%（JPEF 2025，38 國、65 歲夫妻、5% 破產容忍度；基準組合 60% 本國股／40% 本國債）': swr_multiple(2.31),
                      '2.5%（書上 40 倍）': swr_multiple(2.5),
                      '2.7%（Ben Felix 影片自估：國際分散＋活得更久）': swr_multiple(2.7),
                      '2.85%（論文未列：股票部位 40% 換國際股）': swr_multiple(2.85),
                      '3%（書上 33 倍）': swr_multiple(3.0),
                      '3.02%（論文未列：股票部位 90% 換國際股）': swr_multiple(3.02),
                      '4%（書上 25 倍）': swr_multiple(4.0)}
assert abs(swr_multiple(2.31) - 43.3) <= 0.05, swr_multiple(2.31)
assert round(swr_multiple(2.31)) == 43
# 書上第 24 節摺疊那一句（批 R 起分開寫）：2.85% 寫「約 35 倍」、3.02% 寫「約 33 倍」；
# 2.7% 是 37 倍（只在 calc 留底，書上沒寫倍數）
assert round(swr_multiple(2.85)) == 35, swr_multiple(2.85)
assert round(swr_multiple(3.02)) == 33, swr_multiple(3.02)
assert round(swr_multiple(2.7)) == 37, swr_multiple(2.7)

# ---------- 第 16 節：台灣掛牌 vs 倫敦掛牌，每年差多少（v7 第 20 版 C2） ----------
# 兩項相加：
#   ① 內扣費用差。台灣掛牌的全球型＝經理費＋保管費，隨規模分級（貝萊德投信官方產品頁）：
#      小規模 0.45＋0.15＝0.60%／年，最大級距 0.40＋0.10＝0.50%／年。
#      倫敦掛牌（愛爾蘭註冊）的全球市值型 0.14%（Vanguard 官方頁）到 0.20%（iShares 官方頁）。
#   ② 基金層對美股股息的預扣差。台灣註冊與美國註冊一般 30%、愛爾蘭註冊 15%（書上第 16 節摺疊的
#      既有口徑「每 100 元美股股息，前兩者先少 30 元，愛爾蘭註冊的少 15 元」），差 15 個百分點，
#      只落在指數裡的美股那一塊。美股權重用書上來源卡那一筆（Vanguard FTSE All-World 官方揭露
#      61.68%）；美股股息率用書自己的 Shiller 月資料（年化股利 ÷ 指數，最後一個月與近十年平均）。
# 書上第 16 節的頭條數字改用下面 listing_annual_cost() 的基準 A（三腿同一天的發行商官方頁）；
# 這個函式的費用差與台灣／倫敦股息稅差留作穩健性對照（股息率用到 2023 年的長期資料，是上界）。
TW_FEE = (0.50, 0.60)      # 台灣掛牌全球型：經理費＋保管費（最大級距 → 最小級距）
LSE_FEE = (0.14, 0.20)     # 倫敦掛牌（愛爾蘭註冊）
US_FEE = (0.06, 0.32)      # 美國掛牌
US_WEIGHT = 0.6168         # 全球市值型指數裡美股的比重
WHT_GAP = 0.15             # 30% − 15%

def _shiller_us_div_yield():
    rows = list(_csv.DictReader(open(SHILLER_CSV, encoding='utf-8')))
    end = next(i for i, r in enumerate(rows) if float(r['Dividend'] or 0) == 0)
    rows = rows[:end]
    y = lambda r: float(r['Dividend']) / float(r['SP500']) * 100
    last = y(rows[-1]); avg10 = sum(y(r) for r in rows[-120:]) / 120.0
    return {'last_month': rows[-1]['Date'][:7], 'last_pct': round(last, 2), 'avg10y_pct': round(avg10, 2)}

def tw_vs_lse_annual_gap():
    dy = _shiller_us_div_yield()
    tax = (round(US_WEIGHT * dy['last_pct'] * WHT_GAP, 3),
           round(US_WEIGHT * dy['avg10y_pct'] * WHT_GAP, 3))
    fee = (round(TW_FEE[0] - LSE_FEE[1], 3), round(TW_FEE[1] - LSE_FEE[0], 3))
    tot = (round(fee[0] + tax[0], 3), round(fee[1] + tax[1], 3))
    return {'us_dividend_yield': dy,
            'fee_gap_pp_vs_lse': fee, 'fee_gap_pp_vs_lse_mid': round(sum(fee) / 2, 3),
            'tax_gap_pp_vs_lse': tax,
            'total_pp_vs_lse': tot, 'total_pp_vs_lse_mid': round(sum(tot) / 2, 3),
            'note': '書上第 16 節寫「差大約 0.4 個百分點」（費用；這裡算出來的中位 %s，兩端 %s 到 %s）。'
                    '台灣／倫敦的股息稅差與合計（中位 %s，兩端 %s 到 %s）在這裡只當穩健性上界，'
                    '書上的頭條數字以 listing_annual_cost() 的基準 A 為準。'
                    % (round(sum(fee) / 2, 2), fee[0], fee[1],
                       round(sum(tot) / 2, 2), tot[0], tot[1])}

R['tw_vs_lse_annual_gap'] = tw_vs_lse_annual_gap()
_g = R['tw_vs_lse_annual_gap']
# 書上寫「差大約 0.4 個百分點」：用中位數判，兩端（0.30–0.46）另外記在 json 裡
assert 0.35 <= _g['fee_gap_pp_vs_lse_mid'] <= 0.45, _g['fee_gap_pp_vs_lse']

# ---------- 第 16 節：三種註冊地／掛牌地的股息稅與每年總成本（第 20 版裁判後修正 M1） ----------
# 裁判查 IRS Publication 515 指出，上面 tw_vs_lse_annual_gap() 的口徑把美國註冊那一格放錯層：
#   台灣註冊、愛爾蘭註冊的基金，是「基金收到美股股息」那一關被扣（30%／15%），
#   只落在指數裡的美股那一塊（約六成）。
#   美國註冊的基金配息給非美國人時，是「整筆」普通配息先被扣 30%，連非美國公司那一塊也算：
#   美國公司與 RIC 發的股息屬美國來源所得（Pub 515「Source of Income」），
#   「Dividends paid by U.S. corporations—general (income code 6)」要求
#   "withhold on the entire amount of the distribution"；RIC 幾項免預扣的例外
#   （利息型、短期資本利得、資本利得分配等）都不含普通配息裡的外國成分。
# 所以美國註冊那一項的分母是「整筆配息」，要用全球型 ETF 的配息率，不是美股權重 × 美股股息率。
# 兩套基準：書上的頭條數字只用基準 A（三腿年份一致），基準 B 只當穩健性上界：
#   基準 A（發行商官方頁，同一天 2026-08-31）：
#     iShares MSCI ACWI ETF（美國註冊）12m Trailing Yield 1.40%；
#     Vanguard Total World Stock ETF 最近四次配息合計 2.4135 美元 ÷ 最後一次再投資價 158.55 ＝ 1.52%；
#     美股股息率用同一天同一家的 iShares Core S&P 500 ETF 12m Trailing Yield 1.06%。
#   基準 B（書上既有資料）：美股股息率用 Shiller 月資料（最後一個月 1.58%、近十年平均 1.85%），
#     全球配息率仍用基準 A 的官方頁數字（書裡沒有更早的全球配息率）。
# 配息率隨行情高低變動，這幾個數字是量級，不是精算。
GLOBAL_DIST_YIELD = (1.40, 1.52)   # 全球型 ETF 的 12 個月配息率（ACWI 官方頁／VT 官方頁自算）
US_EQ_YIELD_2026 = 1.06            # iShares Core S&P 500 ETF 官方頁 12m Trailing Yield，2026-08-31
WHT_US_REGISTERED = 0.30           # 美國註冊：配息給非美國人時整筆先扣
WHT_TW_REGISTERED = 0.30           # 台灣註冊：基金收到美股股息時扣
WHT_IE_REGISTERED = 0.15           # 愛爾蘭註冊：基金收到美股股息時扣

def listing_annual_cost(us_equity_yield_pct):
    """給定美股股息率，算三種掛牌地每年的『內扣費用＋股息稅』區間（百分點）。"""
    us_part = US_WEIGHT * us_equity_yield_pct          # 指數裡美股那一塊的股息，占整檔的百分之幾
    tax = {'tw': (round(us_part * WHT_TW_REGISTERED, 3),) * 2,
           'lse': (round(us_part * WHT_IE_REGISTERED, 3),) * 2,
           'us': tuple(round(y * WHT_US_REGISTERED, 3) for y in GLOBAL_DIST_YIELD)}
    fee = {'tw': TW_FEE, 'lse': LSE_FEE, 'us': US_FEE}
    # 費用低的那一檔配它自己的配息率（VT 0.06%／1.52%），費用高的配 ACWI（0.32%／1.40%）
    tot = {'tw': (fee['tw'][0] + tax['tw'][0], fee['tw'][1] + tax['tw'][1]),
           'lse': (fee['lse'][0] + tax['lse'][0], fee['lse'][1] + tax['lse'][1]),
           'us': (fee['us'][0] + tax['us'][1], fee['us'][1] + tax['us'][0])}
    mid = lambda p: round((p[0] + p[1]) / 2.0, 3)
    return {'us_equity_yield_pct': us_equity_yield_pct,
            'dividend_tax_pp': {k: tuple(round(x, 3) for x in v) for k, v in tax.items()},
            'dividend_tax_pp_mid': {k: mid(v) for k, v in tax.items()},
            'total_pp': {k: (round(v[0], 3), round(v[1], 3)) for k, v in tot.items()},
            'total_pp_mid': {k: mid(v) for k, v in tot.items()},
            'tw_minus_lse_mid': round(mid(tot['tw']) - mid(tot['lse']), 3),
            'tw_minus_us_mid': round(mid(tot['tw']) - mid(tot['us']), 3)}

R['listing_annual_cost'] = {
    'global_distribution_yield_pct': GLOBAL_DIST_YIELD,
    'basis_A_issuer_pages_2026': listing_annual_cost(US_EQ_YIELD_2026),
    'basis_B_shiller': listing_annual_cost(_shiller_us_div_yield()['avg10y_pct']),
    'basis_B_shiller_last_month': listing_annual_cost(_shiller_us_div_yield()['last_pct']),
    'note': ('書上第 16 節摺疊的頭條數字一律以基準 A 為準：三腿都用 2026-08-31 的發行商官方頁，年份一致。'
             '「台灣註冊的這一項一年約 0.2 個百分點，愛爾蘭註冊的約 0.1」＝基準 A 的 0.196／0.098；'
             '「多差約 0.1 個百分點」＝兩者相減 0.098；「一年大約 0.4 到 0.5 個百分點」＝美國註冊那一項的 '
             '0.42 到 0.456；「倫敦掛牌的每年比台灣掛牌少約半個百分點」＝0.478；「美國掛牌的只少 0.1 個百分點'
             '左右」＝0.118；主線 A 路「和直接買倫敦掛牌的相比，每年約多付半個百分點」也掛在這裡（0.478）。'
             '基準 B 兩腿年份不同（全球配息率仍是 2026 年官方頁，美股股息率是 Shiller 到 2023 年的長期資料，'
             '當年股息率較高），所以降為穩健性註腳、只當上界：台灣掛牌減美國掛牌 0.214（最後一個月）到 '
             '0.264（近十年平均），都比基準 A 大；書上不引基準 B 的數字，只用它確認方向沒有反過來。')}
_A = R['listing_annual_cost']['basis_A_issuer_pages_2026']
_L = [_A,
      R['listing_annual_cost']['basis_B_shiller'],
      R['listing_annual_cost']['basis_B_shiller_last_month']]
# 基準 A：書上每一個數字逐句對
# 「台灣註冊的這一項一年約 0.2 個百分點，愛爾蘭註冊的約 0.1」
assert round(_A['dividend_tax_pp_mid']['tw'], 1) == 0.2, _A['dividend_tax_pp_mid']
assert round(_A['dividend_tax_pp_mid']['lse'], 1) == 0.1, _A['dividend_tax_pp_mid']
# 「這一項台灣掛牌每年比倫敦掛牌多差約 0.1 個百分點」
_gap_A = round(_A['dividend_tax_pp_mid']['tw'] - _A['dividend_tax_pp_mid']['lse'], 3)
assert round(_gap_A, 1) == 0.1, _gap_A
# 「一年大約 0.4 到 0.5 個百分點」：美國註冊那一項的兩端
assert 0.4 <= _A['dividend_tax_pp']['us'][0] and _A['dividend_tax_pp']['us'][1] <= 0.5, _A
# 「倫敦掛牌的每年比台灣掛牌少約半個百分點」＝0.4 到 0.6
assert 0.4 <= _A['tw_minus_lse_mid'] <= 0.6, _A
# 「美國掛牌的只少 0.1 個百分點左右」：四捨五入到一位小數要是 0.1
assert round(_A['tw_minus_us_mid'], 1) == 0.1, _A['tw_minus_us_mid']
# 基準 B：只判方向與「三種裡最重」，並確認它確實是上界（比基準 A 大）
for _b in _L:
    # 「這一項是三種裡最重的」：美國註冊那一項在任何基準下都比另外兩種重
    assert _b['dividend_tax_pp']['us'][0] > _b['dividend_tax_pp']['tw'][0] > _b['dividend_tax_pp']['lse'][0], _b
    # 方向：倫敦掛牌、美國掛牌在任何基準下都比台灣掛牌便宜
    assert _b['tw_minus_lse_mid'] > 0 and _b['tw_minus_us_mid'] > 0, _b
for _b in _L[1:]:
    assert _b['tw_minus_lse_mid'] >= _A['tw_minus_lse_mid'], (_b['tw_minus_lse_mid'], _A['tw_minus_lse_mid'])
    assert _b['tw_minus_us_mid'] >= _A['tw_minus_us_mid'], (_b['tw_minus_us_mid'], _A['tw_minus_us_mid'])

# ---------- 台股跌 20% 以上的每一段，以及回到前高花多久（含息、逐日） ----------
# 走法：逐日更新「到今天為止的最高點」；從那個高點跌掉門檻以上就開一段，之後只要再創新高，
# 這一段就結束（那天就是回到前高的日子）。年數用 365.25 天一年。
def taiex_drawdowns(threshold=0.20):
    dates, vals = taiex_series()
    eps, peak, cur = [], 0, None
    for i in range(1, len(vals)):
        if vals[i] >= vals[peak]:
            if cur:
                cur['rec'] = i; eps.append(cur); cur = None
            peak = i
        elif cur is None:
            if vals[i] / vals[peak] - 1 <= -threshold:
                cur = {'peak': peak, 'trough': i}
        elif vals[i] < vals[cur['trough']]:
            cur['trough'] = i
    if cur:
        cur['rec'] = None; eps.append(cur)
    out = []
    for e in eps:
        p, t, rc = e['peak'], e['trough'], e['rec']
        row = {'peak_date': dates[p].isoformat(), 'peak_value': round(vals[p], 2),
               'trough_date': dates[t].isoformat(), 'trough_value': round(vals[t], 2),
               'drawdown_pct': r1((vals[t] / vals[p] - 1) * 100),
               'recovered': rc is not None,
               'recover_date': dates[rc].isoformat() if rc else None,
               'years_peak_to_recover': round((dates[rc] - dates[p]).days / 365.25, 2) if rc else None,
               'years_peak_to_trough': round((dates[t] - dates[p]).days / 365.25, 2),
               'years_trough_to_recover': round((dates[rc] - dates[t]).days / 365.25, 2) if rc else None}
        out.append(row)
    return out

_dd = taiex_drawdowns()
_dd_years = [e['years_peak_to_recover'] for e in _dd if e['recovered']]
R['taiex_drawdowns'] = {
    'source': '證交所發行量加權股價報酬指數（含息）', 'file': os.path.relpath(TAIEX_CSV, ROOT),
    'from': _td[0].isoformat(), 'to': _td[-1].isoformat(), 'threshold_pct': 20,
    'rule': '從「到當天為止的最高收盤」跌 20% 以上算一段；再創新高的那一天算回到前高。年數＝高點到回到前高，÷365.25。',
    'n': len(_dd), 'all_recovered': all(e['recovered'] for e in _dd),
    'years_min': min(_dd_years), 'years_max': max(_dd_years),
    'episodes': _dd,
    'caveats': ['只有 2003 年以後的含息資料，起點剛好在 2000–2002 年那波大跌之後',
                '七段全部回到前高，是這 23 年的結果，不是規律；第 7 節那張價格指數的表有 25 到 34 年才回本的例子',
                '含息、名目，沒有扣物價、費用和稅；只用收盤值'],
}


# ---------- 平常一天漲跌多大（第 8 節「錢變多以後：一天的漲跌，會開始超過月薪」） ----------
def taiex_daily_moves(threshold=0.01, down_levels=(0.01, 0.02, 0.04)):
    """台股含息逐日的單日報酬：當日收盤 ÷ 前一個交易日收盤 − 1。

    口徑：
    1. 資料是 2003-01-02 到 2025-12-31 的證交所發行量加權股價報酬指數（含息），共 5,665 個交易日。
       第一天沒有前一天，所以單日報酬有 5,664 個；**占比的分母是 5,664，不是 5,665**。
    2. 門檻用「大於或等於」（|r| ≥ N%、r ≤ −N%）。這份資料沒有剛好等於 ±1%、±2%、±4% 的日子，
       所以改成嚴格大於／小於，天數一樣。
    3. 「平均一年幾天」＝天數 ÷ 年數，年數用實際天數算：(2025-12-31 − 2003-01-02) ÷ 365.25 ＝ 22.995 年。
       和直接除以整數 23 年算出來的結果相同（69.9 與 31.9），所以口徑選哪一種都不影響書上的數字。
    4. 「大約每幾個交易日就有一天」＝ 5,664 ÷ 天數。
    5. `n_years` ＝這些日子分布在幾個不同的日曆年（23 個年度裡）；跌越深的門檻越集中在少數幾年。
    6. `worst_day`／`best_day` ＝這段期間單日跌最多／漲最多的那一天。
    含息、名目，沒有扣物價、費用和稅；只用收盤值。這是這 23 年的紀錄，不是未來的機率。
    """
    dates, vals = taiex_series()
    rets = [(dates[i], vals[i] / vals[i - 1] - 1) for i in range(1, len(vals))]
    years = (dates[-1] - dates[0]).days / 365.25

    def block(sel):
        hit = [(d, r) for d, r in rets if sel(r)]
        n = len(hit)
        ys = sorted({d.year for d, _ in hit})
        return {'days': n, 'share_pct': r1(100 * n / len(rets)), 'share_pct_int': r0(100 * n / len(rets)),
                'per_year': r1(n / years), 'per_year_int': r0(n / years),
                'per_year_div23': r1(n / 23), 'one_in_trading_days': r1(len(rets) / n),
                'n_years': len(ys), 'years_seen': ys}

    worst = min(rets, key=lambda x: x[1])
    best = max(rets, key=lambda x: x[1])
    return {'trading_days': len(dates), 'daily_returns': len(rets), 'years': round(years, 3),
            'threshold_pct': r1(threshold * 100),
            'abs_ge': block(lambda r: abs(r) >= threshold),
            'down_le': block(lambda r: r <= -threshold),
            'down_levels': {str(r1(lv * 100)): block(lambda r, lv=lv: r <= -lv) for lv in down_levels},
            'worst_day': {'date': worst[0].isoformat(), 'pct': r1(worst[1] * 100)},
            'best_day': {'date': best[0].isoformat(), 'pct': r1(best[1] * 100)}}


_dm = taiex_daily_moves()
R['taiex_daily_moves'] = dict(_dm, **{
    'source': '證交所發行量加權股價報酬指數（含息）', 'file': os.path.relpath(TAIEX_CSV, ROOT),
    'from': _td[0].isoformat(), 'to': _td[-1].isoformat(),
    'rule': taiex_daily_moves.__doc__,
    'caveats': ['一個市場、23 年的紀錄，不是規律，也不是未來的機率',
                '占比的分母是 5,664 個單日報酬（5,665 個交易日扣掉沒有前一天的第一天）',
                '跌 4% 以上的 40 天只出現在 15 個年份，不是每年都平均發生',
                '含息、名目，沒有扣物價、費用和稅；只用收盤值'],
})
_dl = R['taiex_daily_moves']['down_levels']
assert (R['taiex_daily_moves']['trading_days'], R['taiex_daily_moves']['daily_returns']) == (5665, 5664)
assert (R['taiex_daily_moves']['abs_ge']['days'], R['taiex_daily_moves']['abs_ge']['share_pct'],
        R['taiex_daily_moves']['abs_ge']['per_year_int'], R['taiex_daily_moves']['abs_ge']['one_in_trading_days']) == (1608, 28.4, 70, 3.5)
assert (R['taiex_daily_moves']['down_le']['days'], R['taiex_daily_moves']['down_le']['share_pct'],
        R['taiex_daily_moves']['down_le']['per_year_int']) == (733, 12.9, 32)
assert R['taiex_daily_moves']['abs_ge']['per_year_div23'] == R['taiex_daily_moves']['abs_ge']['per_year']
assert (_dl['1.0']['days'], _dl['1.0']['per_year'], _dl['1.0']['n_years']) == (733, 31.9, 23)
assert (_dl['2.0']['days'], _dl['2.0']['per_year'], _dl['2.0']['n_years']) == (238, 10.3, 20)
assert (_dl['4.0']['days'], _dl['4.0']['per_year'], _dl['4.0']['n_years']) == (40, 1.7, 15)
assert (R['taiex_daily_moves']['worst_day']['date'], R['taiex_daily_moves']['worst_day']['pct']) == ('2025-04-07', -9.7)


# ---------- 每月存月薪的一成兩成，股票那一塊要幾年才等於月薪的 N 倍（第 8 節那張表） ----------
def months_to_salary_multiple(multiple, annual_return=0.06, save_rate=0.2, cap=1200):
    """每月月底投入「月薪 × 儲蓄率」，問股票那一塊第一次 ≥ 月薪 × multiple 要幾個月。

    口徑（刻意寫得很陽春，因為它要回答的是「大概什麼時候會遇到」，不是「我會有多少錢」）：
    1. 月薪當成 1，所以結果和月薪多少無關；**假設月薪一路不變**（實際上薪水會漲：目標是月薪的倍數，分母跟著漲，會到得比較慢）。
    2. 月報酬＝(1+年化)^(1/12)−1，月底投入、當月不計息；錢全部在股票那一塊。
    3. 年化用書上第 4 節的三種算法：保守算 4%、普通算 6%、樂觀算 7%。**書上的表用普通算 6%。**
    4. 沒有扣物價、費用和稅；不是預測，是「照這個存法，大約走到第幾年」的量尺。
    回傳 months（第一次達標的月份數）與換算成年的整數與一位小數。
    """
    r = (1 + annual_return) ** (1 / 12) - 1
    bal = 0.0
    for m in range(1, cap + 1):
        bal = bal * (1 + r) + save_rate
        if bal >= multiple:
            return {'multiple': multiple, 'annual_return_pct': r1(annual_return * 100),
                    'save_rate_pct': r0(save_rate * 100), 'months': m,
                    'years_1dp': r1(m / 12), 'years_int': r0(m / 12)}
    return {'multiple': multiple, 'annual_return_pct': r1(annual_return * 100),
            'save_rate_pct': r0(save_rate * 100), 'months': None, 'years_1dp': None, 'years_int': None}


R['salary_multiple_years'] = {
    'rule': months_to_salary_multiple.__doc__,
    # 書上主線示範句用的那一組：每月投入月薪的兩成、一年 6%。
    'guide_line': {'save_rate_pct': 20, 'annual_return_pct': 6.0,
                   '25x_years_int': months_to_salary_multiple(25, 0.06, 0.2)['years_int'],
                   '100x_years_int': months_to_salary_multiple(100, 0.06, 0.2)['years_int']},
    'by_rate': {str(r1(a * 100)): {str(k): months_to_salary_multiple(k, a) for k in (10, 25, 50, 100)}
                for a in (0.04, 0.06, 0.07)},
    # 書上摺疊裡那兩張小表（列＝每月投入佔月薪，欄＝第 4 節的保守算／普通算／樂觀算）。
    'guide_grid': {str(k): {str(r0(s * 100)): {str(r1(a * 100)): months_to_salary_multiple(k, a, s)['years_int']
                                               for a in (0.04, 0.06, 0.07)}
                            for s in (0.1, 0.2, 0.3)}
                   for k in (25, 100)},
    'caveats': ['月薪假設一路不變；薪水會漲的人會到得比較慢（目標是月薪的倍數，分母跟著漲）',
                '沒有扣物價、費用和稅，也沒有算這筆錢中途被拿去用掉',
                '報酬率是第 4 節的保守算、普通算、樂觀算，不是預測；真實的路不會每年一樣'],
}
_sm = R['salary_multiple_years']['by_rate']
_sg = R['salary_multiple_years']['guide_grid']
assert [_sm['6.0'][k]['months'] for k in ('10', '25', '50', '100')] == [45, 98, 164, 255]
assert [_sm['6.0'][k]['years_int'] for k in ('10', '25', '50', '100')] == [4, 8, 14, 21]
assert _sm['4.0']['100']['months'] == 297 and _sm['4.0']['100']['years_int'] == 25
assert _sm['7.0']['100']['months'] == 239 and _sm['7.0']['100']['years_int'] == 20
# 主線示範句「大約第 8 年到 25 倍，第 21 年到 100 倍」
assert (R['salary_multiple_years']['guide_line']['25x_years_int'],
        R['salary_multiple_years']['guide_line']['100x_years_int']) == (8, 21)
# 摺疊那兩張小表的 18 格（列 10%／20%／30%，欄 4%／6%／7%）
assert [[_sg['25'][s][a] for a in ('4.0', '6.0', '7.0')] for s in ('10', '20', '30')] == \
       [[15, 14, 13], [9, 8, 8], [6, 6, 6]]
assert [[_sg['100'][s][a] for a in ('4.0', '6.0', '7.0')] for s in ('10', '20', '30')] == \
       [[37, 30, 28], [25, 21, 20], [19, 17, 16]]


# ---------- 「從高點跌 N% 就賣」這條規則，在台股這 23 年會發生什麼（第 11 節停損那一段） ----------
def taiex_stoploss(threshold=0.15, cash_rate=0.015):
    """回測「股票那一塊從最近高點跌 N% 就全部賣掉」。台股含息逐日，2003-01-02～2025-12-31。

    規則（本文自訂，寫出來是為了可以重算；不是任何人的建議做法）：
    1. 第一個交易日就持有。高點＝「持有期間到當天為止的最高收盤」，每創新高就更新。
    2. 當天收盤 ≤ 高點 ×(1−N) 就賣出，賣價＝當天收盤，記成一次觸發，之後空手。
    3. 空手時不重新起算高點：要等收盤「超過當初那個高點」才算創新高；創新高那天買回，
       並把那一天當成新的高點，回到第 1 步。（規格說的「賣出後以下一次創新高重新起算高點」）
    4. 「一年後高不高於賣價」＝賣出日起滿 12 個月的同一天、或之前最後一個交易日的收盤，
       和賣價比。資料不滿一年的觸發會標 short_window=True（這一份資料目前沒有這種）。
    5. 「兩年內最低」＝賣出當天到滿 24 個月之間（含賣出當天）的最低收盤，和賣價比。
    6. 空手期間的利息（`cash_rate`，預設年 1.5%，按 (1+r)^(天數/365.25) 複利）：賣價當成現金
       放到買回那天，得到 `cash_at_rebuy`。`rebuy_vs_cash_pct` ＝買回價比這筆現金高幾 %；
       `cash_vs_rebuy_pct` ＝這筆現金比買回價低幾 %（兩個看的是同一件事，分母不同）。
       算利息是為了回答「加了利息結論會不會翻」，不是說真的有人會去存定存。

    只用收盤值，含息、名目；沒有扣費用、稅與交易成本——扣了只會對這條規則更不利。
    書上正文的數字都是「沒有算空手期間利息」的版本；利息只用來做第 6 點那個驗算。
    """
    dates, vals = taiex_series()
    peak, holding, out = 0, True, []
    for i in range(1, len(vals)):
        if holding:
            if vals[i] >= vals[peak]:
                peak = i
            elif vals[i] <= vals[peak] * (1 - threshold):
                out.append({'peak': peak, 'sell': i}); holding = False
        elif vals[i] > vals[peak]:
            out[-1]['rebuy'] = i
            holding, peak = True, i
    eps = []
    for e in out:
        p, s = e['peak'], e['sell']
        sell_v = vals[s]
        tgt1 = _add_months(dates[s], 12); short = tgt1 > dates[-1]
        j = len(dates) - 1 if short else _bisect.bisect_right(dates, tgt1) - 1
        tgt2 = _add_months(dates[s], 24)
        k = min(_bisect.bisect_right(dates, tgt2) - 1, len(dates) - 1)
        lo = min(vals[s:k + 1]); lo_i = s + vals[s:k + 1].index(lo)
        cash = rb_cash = cash_vs = None
        if 'rebuy' in e:
            rb = e['rebuy']
            cash = sell_v * (1 + cash_rate) ** ((dates[rb] - dates[s]).days / 365.25)
            rb_cash = r1((vals[rb] / cash - 1) * 100)
            cash_vs = r1((cash / vals[rb] - 1) * 100)
        eps.append({'peak_date': dates[p].isoformat(), 'peak_value': round(vals[p], 2),
                    'sell_date': dates[s].isoformat(), 'sell_value': round(sell_v, 2),
                    'one_year_date': dates[j].isoformat(), 'one_year_value': round(vals[j], 2),
                    'one_year_higher': vals[j] > sell_v, 'short_window': short,
                    'low_within_2y_date': dates[lo_i].isoformat(), 'low_within_2y_value': round(lo, 2),
                    'low_within_2y_vs_sell_pct': r1((lo / sell_v - 1) * 100),
                    'rebuy_date': (dates[e['rebuy']].isoformat() if 'rebuy' in e else None),
                    'rebuy_value': (round(vals[e['rebuy']], 2) if 'rebuy' in e else None),
                    'rebuy_vs_sell_pct': (r1((vals[e['rebuy']] / sell_v - 1) * 100) if 'rebuy' in e else None),
                    'cash_rate_pct': r1(cash_rate * 100),
                    'cash_at_rebuy': (round(cash, 2) if cash is not None else None),
                    'rebuy_vs_cash_pct': rb_cash, 'cash_vs_rebuy_pct': cash_vs})
    return eps


_sl = taiex_stoploss()
_sl_2007 = [e for e in _sl if e['sell_date'].startswith('2007-11')]
R['taiex_stoploss'] = {
    'source': '證交所發行量加權股價報酬指數（含息）', 'file': os.path.relpath(TAIEX_CSV, ROOT),
    'from': _td[0].isoformat(), 'to': _td[-1].isoformat(), 'threshold_pct': 15,
    'rule': taiex_stoploss.__doc__,
    'n_triggers': len(_sl),
    'n_one_year_higher': sum(1 for e in _sl if e['one_year_higher']),
    'n_short_window': sum(1 for e in _sl if e['short_window']),
    'worst_2007': (_sl_2007[0] if _sl_2007 else None),
    'n_rebought': sum(1 for e in _sl if e['rebuy_date']),
    'rebuy_vs_sell_pct_min': min(e['rebuy_vs_sell_pct'] for e in _sl if e['rebuy_date']),
    'rebuy_vs_sell_pct_max': max(e['rebuy_vs_sell_pct'] for e in _sl if e['rebuy_date']),
    'episodes': _sl,
    # 「空手期間的利息也沒有算；算進去，結論不變」——這一條的驗算：
    # 把賣價當現金放到買回那天，11 次的買回價仍然全部高於這筆現金。年 1.5% 與書上用的
    # 一年期定存 1.7%（R['deposit_rate_d02']）兩種都試過，結論一樣。
    'cash_check': {
        'rates_pct': [1.5, 1.7],
        'by_rate': {str(r1(cr * 100)): {
            'n_rebuy_above_cash': sum(1 for e in taiex_stoploss(cash_rate=cr) if e['rebuy_vs_cash_pct'] > 0),
            'rebuy_vs_cash_pct_min': min(e['rebuy_vs_cash_pct'] for e in taiex_stoploss(cash_rate=cr)),
            'worst_2007_rebuy_vs_cash_pct': [e for e in taiex_stoploss(cash_rate=cr) if e['sell_date'].startswith('2007-11')][0]['rebuy_vs_cash_pct'],
            'worst_2007_cash_vs_rebuy_pct': [e for e in taiex_stoploss(cash_rate=cr) if e['sell_date'].startswith('2007-11')][0]['cash_vs_rebuy_pct'],
        } for cr in (0.015, 0.017)},
        'note': '書上不印這些數字，只寫「空手期間的利息也沒有算；算進去，結論不變」。'
                '2007-11-28 賣、2010-12-09 買回那一次空手 1,107 天：年 1.5% 複利下，買回價仍比這筆現金高 13.6%'
                '（換個分母說＝這筆現金比買回價低 12.0%）。',
    },
    'caveats': ['一個市場、23 年、一條門檻的紀錄，不是規律；換門檻、換市場、換期間，數字就會變',
                '沒有扣交易成本與稅（扣了對這條規則更不利）；正文的數字也沒有算空手期間的現金報酬，'
                '算進去 11 次的買回價仍然都高於現金（見 cash_check）',
                '「一年後高於賣價」只是說那一天的指數比賣價高，不等於賣出的人實際虧多少'],
}
assert (R['taiex_stoploss']['n_triggers'], R['taiex_stoploss']['n_one_year_higher']) == (11, 9)
assert R['taiex_stoploss']['worst_2007']['low_within_2y_vs_sell_pct'] == -47.9
assert (R['taiex_stoploss']['n_rebought'], R['taiex_stoploss']['rebuy_vs_sell_pct_min'], R['taiex_stoploss']['rebuy_vs_sell_pct_max']) == (11, 18.2, 22.8)
# v7 審核團批 A4：買回價／賣價的下限是規則本身的算術（1 ÷ 0.85），和資料無關；書上印 17.6%
R['taiex_stoploss']['rebuy_vs_sell_pct_floor_from_rule'] = r1((1 / 0.85 - 1) * 100)
assert R['taiex_stoploss']['rebuy_vs_sell_pct_floor_from_rule'] == 17.6
assert R['taiex_stoploss']['rebuy_vs_sell_pct_min'] >= R['taiex_stoploss']['rebuy_vs_sell_pct_floor_from_rule']
assert R['taiex_stoploss']['worst_2007']['rebuy_date'] == '2010-12-09' and R['taiex_stoploss']['worst_2007']['rebuy_vs_sell_pct'] == 18.9
# 加了空手期間的利息，11 次的買回價仍然全部高於現金（兩種利率都是）——所以「結論不變」站得住
assert all(v['n_rebuy_above_cash'] == 11 and v['rebuy_vs_cash_pct_min'] > 0
           for v in R['taiex_stoploss']['cash_check']['by_rate'].values())
assert (R['taiex_stoploss']['cash_check']['by_rate']['1.5']['worst_2007_rebuy_vs_cash_pct'],
        R['taiex_stoploss']['cash_check']['by_rate']['1.5']['worst_2007_cash_vs_rebuy_pct']) == (13.6, -12.0)

# ---------- 四類資產逐年輪換（美股、10 年期公債、3 個月國庫券、台股） ----------
# 美國三類取 Damodaran（紐約大學）公開資料集；台股用本文自己的含息報酬指數。
# 台股是台幣、美國三類是美元，沒有換成同一種貨幣，所以名次只比「各自市場那一年漲跌多少」。
DAMODARAN_XLS = os.path.join(ROOT, 'research', 'data', 'damodaran_histret.xls')
ROT_FROM, ROT_TO = 2004, 2025          # 兩邊都有完整年度資料的每一年（台股含息 2003-01-02 起，2004 才是第一個完整年度）
ROT_LABEL = {'us_stock': '美股', 'us_bond10': '公債', 'us_bill3m': '現金', 'tw_stock': '台股'}

def damodaran_annual():
    import xlrd
    sh = xlrd.open_workbook(DAMODARAN_XLS).sheet_by_name('Returns by year')
    hdr = next(r for r in range(sh.nrows) if str(sh.cell_value(r, 0)).strip() == 'Year')
    names = [str(sh.cell_value(hdr, c)).strip() for c in range(sh.ncols)]
    col = lambda key: next(c for c, n in enumerate(names) if n.startswith(key))
    c_st, c_bd, c_bl = col('S&P 500 (includes dividends)'), col('US T. Bond'), col('3-month T.Bill')
    out = {}
    for r in range(hdr + 1, sh.nrows):
        y = sh.cell_value(r, 0)
        if isinstance(y, float) and 1900 < y < 2100:
            out[int(y)] = {'us_stock': sh.cell_value(r, c_st), 'us_bond10': sh.cell_value(r, c_bd),
                           'us_bill3m': sh.cell_value(r, c_bl)}
    return out

def taiex_calendar_returns():
    dates, vals = taiex_series()
    last = {}
    for d_, v_ in zip(dates, vals):
        last[d_.year] = v_
    return {y: last[y] / last[y - 1] - 1 for y in sorted(last) if y - 1 in last}

_us_yr, _tw_yr = damodaran_annual(), taiex_calendar_returns()
_rot, _wins = [], {}
for _y in range(ROT_FROM, ROT_TO + 1):
    _items = sorted(list(_us_yr[_y].items()) + [('tw_stock', _tw_yr[_y])], key=lambda t: -t[1])
    _wins[ROT_LABEL[_items[0][0]]] = _wins.get(ROT_LABEL[_items[0][0]], 0) + 1
    _rot.append({'year': _y, 'ranking': [{'key': k, 'label': ROT_LABEL[k], 'return_pct': r1(v * 100)} for k, v in _items]})
R['asset_rotation'] = {
    'from': ROT_FROM, 'to': ROT_TO, 'years': ROT_TO - ROT_FROM + 1,
    'assets': {'us_stock': 'S&P 500 含息（美元）', 'us_bond10': '美國 10 年期公債（美元）',
               'us_bill3m': '美國 3 個月國庫券（美元，本文當「現金」）', 'tw_stock': '證交所發行量加權股價報酬指數（含息，台幣）'},
    'sources': {'us': 'Damodaran（紐約大學 Stern）Historical Returns on Stocks, Bonds and Bills，檔案 %s'
                      % os.path.relpath(DAMODARAN_XLS, ROOT),
                'us_url': 'https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html',
                'tw': os.path.relpath(TAIEX_CSV, ROOT)},
    'note': '名目、含息、不扣物價費用稅；台股以台幣計、美國三類以美元計，沒有換成同一種貨幣，'
            '所以這張表只比「各自市場那一年漲多少」，不是台灣人換回台幣實際拿到的報酬。',
    'winner_counts': _wins,
    'rows': _rot,
}

# G9/G10：兩張只在指南的新圖，各自的 compute()
sys.path.insert(0, HERE)
import v61_g9_country_recovery as _g9
import v61_g10_rebalance_drift as _g10
R['country_recovery'] = _g9.compute()
R['rebalance_drift'] = _g10.compute()

# G11：在歷史新高買進（第 9 節「現在是歷史新高，會不會太高了？」）
import v61_g11_ath_returns as _g11
_ath = _g11.compute()
# 「任選一天」一律用上面 rolling 的數字；模組的 all 組起點已對齊，這裡確認 n 與整數比例和 rolling 完全一樣，不准出現兩個 n
for _mk, _rk, _hs in (('taiex_daily', 'taiex', (('1y', '1年'), ('3y', '3年'), ('5y', '5年'), ('10y', '10年'))),
                      ('us_monthly_shiller', 'us', (('1y', '1年'), ('5y', '5年'), ('10y', '10年'), ('20y', '20年')))):
    for _hk, _rl in _hs:
        _a, _r = _ath[_mk]['horizons'][_hk]['all'], R['rolling'][_rk]['positive_share'][_rl]
        assert (_a['n'], _a['positive_share_int']) == (_r['n'], _r['pct_int']), ('ath_returns 與 rolling 不一致', _mk, _hk, _a, _r)
_ath['book_table'] = {
    'note': '第 9 節那張小表：「任選一天」取 rolling.*.positive_share.pct_int（第 8 節同一個數），「只挑創新高那天」取本 key 的 at_high.positive_share_int',
    'taiex': [{'years': _y, 'any_day': R['rolling']['taiex']['positive_share']['%d年' % _y]['pct_int'],
               'at_high': _ath['taiex_daily']['horizons']['%dy' % _y]['at_high']['positive_share_int']} for _y in (1, 3, 5, 10)],
    'us': [{'years': _y, 'any_month': R['rolling']['us']['positive_share']['%d年' % _y]['pct_int'],
            'at_high': _ath['us_monthly_shiller']['horizons']['%dy' % _y]['at_high']['positive_share_int']} for _y in (1, 5, 10)],
}
_nb3 = sorted(_ath['taiex_daily']['sensitivity']['at_high_nonpositive_by_start_year']['3y'])
_ath['book_facts'] = {
    'taiex_3y_losing_at_high_start_years': [int(_nb3[0]), int(_nb3[-1])] if _nb3 else None,
    'us_1929_record_10y_ann_pct': next(c['10y_ann_pct'] for c in _ath['us_monthly_shiller']['cases'] if c['label'] == '1929'),
    'us_1929_record_5y_ann_pct': next(c['5y_ann_pct'] for c in _ath['us_monthly_shiller']['cases'] if c['label'] == '1929'),
    # 2026-09-17 fix2：第 9 節改稿後新增的句子
    'taiex_5y_losing_at_high_start_years': sorted(int(_k) for _k in _ath['taiex_daily']['sensitivity']['at_high_nonpositive_by_start_year']['5y']),
    'taiex_gap_pp_excluding_windows_spanning_2008_low': {_y: [_ath['taiex_daily']['sensitivity']['excluding_windows_spanning_2008_low'][_y]['gap_pp_full'],
                                                              _ath['taiex_daily']['sensitivity']['excluding_windows_spanning_2008_low'][_y]['gap_pp_excluding']] for _y in ('3y', '5y')},
    'taiex_1y_worst_not_at_high_pct': _ath['taiex_daily']['sensitivity']['worst5_starts_1y_not_at_high_range_pct'],
    'us_record_months_10y_ann_pct_range_by_year': {_yr: [min(_r['10y_ann_pct'] for _r in _rows), max(_r['10y_ann_pct'] for _r in _rows), len(_rows)]
                                                   for _yr, _rows in _ath['us_monthly_shiller']['record_months_10y_ann_pct_by_year'].items()},
    'us_split_1950_5y_positive_share_int': {_k: [_v['at_high']['positive_share_int'], _v['not_at_high']['positive_share_int']]
                                             for _k, _v in _ath['us_monthly_shiller']['split_1950']['5y'].items()},
}
assert _ath['book_facts']['us_split_1950_5y_positive_share_int'] == {'starts_before_1950': [75, 91], 'starts_1950_on': [91, 93]}, _ath['book_facts']['us_split_1950_5y_positive_share_int']
R['ath_returns'] = _ath

# v6.3 第二批：五張只在指南的新圖，各自的 compute()（模組在 tools/v63_g0*.py）
import v63_g01_plan_flow as _g01
import v63_g02_sequence_risk as _g02
import v63_g03_drag_breakdown as _g03
import v63_g04_fee_gap as _g04
import v63_g05_safety_steps as _g05
R['plan_flow'] = _g01.compute()
R['sequence_risk'] = _g02.compute()
R['drag_breakdown'] = _g03.compute()
R['fee_gap_chart'] = _g04.compute()
R['safety_steps'] = _g05.compute()

# v6.3 批 3（P2）：個股 vs 市值型指數（第 7 節新卡）、報酬率不等於報酬（第 5 節新卡）
# 學術與官方數字是查證過的定值，逐條出處與但書在 wip/v63/stock-vs-index/evidence.md；
# 這裡只集中存放（書上引用它），並用本檔的 fv() 現算「報酬率不等於報酬」那幾個數字。
import v63_g07_investor_cycle as _g07
R['investor_cycle'] = _g07.compute()

_one_cost, _one_up_pct = 10000, 50
_one_gain = _one_cost * _one_up_pct / 100
_plan_m, _plan_rate, _plan_years = 5000, 4, 10
_plan_fv = fv(0, _plan_rate, _plan_years * 12, _plan_m)
_plan_put = _plan_m * _plan_years * 12
_plan_gain = _plan_fv - _plan_put
R['stock_vs_index'] = {
    'us_bessembinder_2018': {
        'cite': 'Bessembinder (2018), Do stocks outperform Treasury bills?, JFE 129(3): 440–457',
        'doi': '10.1016/j.jfineco.2018.06.004',
        'basis': 'CRSP 月報酬、NYSE／Amex／Nasdaq 普通股，1926 年 7 月–2016 年 12 月，含股利再投資；'
                 '「終身」＝從第一次出現在 CRSP 到下市或 2016 年 12 月；基準是一個月期國庫券',
        'n_stocks': 25967, 'n_firms': 25332,
        'beat_tbill_pct': 42.6, 'below_tbill_pct': r1(100 - 42.6),
        'positive_lifetime_pct': 49.5, 'median_lifetime_return_pct': -2.29,
        'most_common_outcome': '報酬四捨五入到最近的 5% 時，出現最多次的是虧損 100%',
        'wealth_creator_firms': 1092, 'wealth_creator_share_pct': 4.31,
        'wealth_creator_share_check': r1(1092 / 25332 * 100),
        'caveat': '4.31% 說的是「淨財富創造」集中在這些公司，不是「只有 4% 的股票有賺錢」',
    },
    'global_bessembinder_2023': {
        'cite': 'Bessembinder, Chen, Choi & Wei (2023), Long-Term Shareholder Returns: '
                'Evidence from 64,000 Global Stocks, FAJ 79(3): 33–63',
        'doi': '10.1080/0015198X.2023.2188870',
        'basis': '1990 年 1 月–2020 年 12 月、逾 64,000 檔全球普通股；基準同為一個月期美國國庫券',
        'n_stocks_text': '逾 64,000 檔',
        'us_below_tbill_pct': 55.2, 'nonus_below_tbill_pct': 57.4,
        'top_wealth_creator_share_pct': 2.4, 'net_wealth_creation_usd_trillion': 75.7,
        'caveat': '和 2019 年工作論文版（1990–2018、1.3%／44.7 兆）期間不同，不能混用',
    },
    'taiwan_listed_counts': {
        'basis': '2003 年底家數出自臺灣證券交易所《證交所 60 週年》專刊 P15〈歷年上市公司家數統計〉；'
                 '今天的家數與上市日期出自證交所開放資料〈上市公司基本資料〉，出表日 2026-09-19，'
                 '不含產業別 91 的存託憑證（TDR）：資料筆數 1,094 扣掉 10 檔 TDR ＝ 1,084 家上市公司（家數自算）',
        'listed_end_2003': 669, 'today_total': 1084,
        'today_listed_on_or_before_2003': 547, 'today_listed_after_2003': 537,
        'today_listed_after_2003_check': 1084 - 547,
        'still_listed_share_pct': r1(547 / 669 * 100),
        'after_2003_share_pct': r1((1084 - 547) / 1084 * 100),
        'caveat': '「不在名單上」不等於倒閉（含合併、轉上櫃、收購後下市）；曾下市又重新上市或由上櫃轉上市的，'
                  '上市日期算後來那一次，所以 547 是下限。不要寫「倒了幾家」',
    },
    'one_share_vs_plan': {
        'basis': '個股那一邊是一次漲幅；計畫那一邊用本檔 fv()：年率÷12 按月複利、每月月底投入，未扣費用與稅。'
                 '4% 是第 4 節保守算（股票 100%）',
        'stock_cost': _one_cost, 'stock_up_pct': _one_up_pct, 'stock_gain': r0(_one_gain),
        'plan_monthly': _plan_m, 'plan_rate_pct': _plan_rate, 'plan_years': _plan_years,
        'plan_fv': r0(_plan_fv), 'plan_fv_wan1': wan1(_plan_fv),
        'plan_put': _plan_put, 'plan_put_wan': wan(_plan_put),
        'plan_gain': r0(_plan_gain), 'plan_gain_wan1': wan1(_plan_gain),
        'gain_over_stock_gain_times': r1(_plan_gain / _one_gain),
        'gain_over_stock_gain_times_int': r0(_plan_gain / _one_gain),
        'stock_up_needed_pct': r1(_plan_gain / _one_cost * 100),
        'stock_up_needed_pct_int': r0(_plan_gain / _one_cost * 100),
    },
}
assert R['stock_vs_index']['us_bessembinder_2018']['below_tbill_pct'] == 57.4
assert R['stock_vs_index']['taiwan_listed_counts']['today_listed_after_2003_check'] == 537
assert (R['stock_vs_index']['one_share_vs_plan']['plan_fv_wan1'],
        R['stock_vs_index']['one_share_vs_plan']['plan_gain_wan1']) == (73.6, 13.6)
assert (R['stock_vs_index']['one_share_vs_plan']['gain_over_stock_gain_times_int'],
        R['stock_vs_index']['one_share_vs_plan']['stock_up_needed_pct_int']) == (27, 1362)

# grep 正式檔：引用數字所在行（guidetools text 行號）
quotes = ['第一格 7.84 年', '| 60 萬 | 7.84 年 | 22%',
          '三十年後差約 86 萬', '2008 年跌了 53.59%', '1.7% 是 2026 年 9 月五大銀行一年期定存牌告利率',
          '用 3% 到 2.5%（33 到 40 倍）算，會保守一些', '都落在股票三成到七成五之間', '2026 年最高一級 45,800 元',
          '平均月投保薪資 × 年資 × 1.55%', '2026 年起請領年齡 65 歲', '提前領每年減 4%、最多減 20%',
          '2022 年 2.95%、2023 年 2.49%、2024 年 2.18%', '〔投資等級〕債 −13.0%', '樂觀算 7% 約 10 年、普通算 6% 約 12 年、保守算 4% 約 18 年',
          '用保守算，股票八成約 20 年、四成約 25 年', '保守算 4% 約 21 年', '| 80% | 3.6% | 5.2% | 6%', '| 40% | 2.8% | 3.6% | 4%',
          # v7 手機表格批：第 5 節物價倍數表由橫排 9 欄改成直排兩欄，原本一行八格的引用改成逐列八條（數字與配對都沒變）
          '| 5 | 1.10', '| 10 | 1.22', '| 15 | 1.35', '| 20 | 1.49',
          '| 25 | 1.64', '| 30 | 1.81', '| 35 | 2.00', '| 40 | 2.21',
          '勞保那一層保守起見用今天的投保薪資試算、不乘物價倍數',
          '真實年成本 6.69%',
          # G11（第 9 節「現在是歷史新高」）：數字來自 ath_returns
          '大約每十個月就有三個月是新高', '| 台股 3 年 | 95% | 87%', '| 美股 5 年 | 90% | 85%',
          '全部落在 2005 到 2007 年', '新高月份放五年平均一年 4.5%、其他月份 9.0%；1950 年以後變成 12.0% 對 10.6%',
          '1950 年以前低很多（75% 對 91%），1950 年以後只低一點（91% 對 93%）',
          '1929 年、2000 年新高時買進美股的人，放十年都還是虧的', '就算挑不是新高的日子買，一年後一樣跌掉約一半',
          '三年、五年的差距，主要就是這一次大跌',
          # v6.3 第一批（C 組 #cases、D 補丁小安扣費後）落地後的句子
          '四個人的試算都已經扣掉 0.5% 的示範費率',
          '保守算約 369 萬，差 81 萬',
          '投入從收入的 20% 調到 26%（25% 只到約 449 萬，不夠），保守算約 465 萬',
          '3 萬的月份投 7,800 元',
          '每月 1 萬改成 1.05 萬，保守算約 724 萬',
          '按季發給，領到平均餘命為止',
          '33 倍 832＋84＝約 916 萬',
          '保守算約 1,088 萬，916 萬的目標夠',
          '本息合計最高保 300 萬（中央存保）',
          # 小安改成扣費後（主線 2026-09-18 拍板）
          '每月改投 6,500 元 → 保守算約 203 萬',
          '2046 年約 203 萬、跌 50% 少 81 萬',
          # v6.3 批 1 修正
          '第一段 40 倍約 1,018 萬，加上第二段的 84 萬約 1,102 萬',
          '同一段時間的一年期定存年平均是 2022 年約 1.14%、2023 年約 1.55%、2024 年約 1.68%',
          '要到 2054 年 1 月左右（多約 7.3 年）',
          # v6.3 批 2：G02 sequence-risk、G04 fee-gap 的圖說與圖下說明（數字由 tools/v63_g02、g04 算）
          '先跌的那一個第 10 年剩約 36 萬，後跌的那一個剩約 106 萬',
          '所以兩個人的平均報酬一樣（一年 6.5%）',
          '同一組報酬不管什麼順序，十年後都是 148 萬',
          '一年 6% 到約 502 萬，一年 5% 到約 416 萬，第 30 年差 86 萬',
          # v6.3 批 2 修正：退休早於請領年齡的橋接缺口（#lifecycle 第三題）
          '五年多缺 21,297×12×5≈128 萬']
quotes += QUOTES_V63_Q
# v6.3 批 3（拍板 D04 選 B）：欄位表第 20 格的八二腰斬例子
quotes += ['股票跌一半以後股票剩 40 萬、總共剩 60 萬，股票占 66.7%',
           '從防守搬 8 萬去買股票（防守從 20 萬剩 12 萬）',
           '要再投入 40 萬新錢才回得到八成']
# v6.3 批 3（P2）：第 7 節「一家對上整群」、第 5 節「報酬率不等於報酬」
quotes += ['只有 42.6% 的終身報酬贏過同一段時間的一個月期國庫券',
           '中間那一檔的終身報酬是 −2.29%',
           '排在最前面的 1,092 家（4.31%）',
           '美國股票有 55.2%、非美國股票有 57.4%',
           '表現最好的 2.4% 公司，解釋了全部 75.7 兆美元',
           '2003 年底台灣有 669 家上市公司，今天名單上還在的是 547 家',
           '今天的 1,084 家上市公司裡，有 537 家是 2004 年以後才上市的',
           '漲 50%，賺到 5,000 元',
           '到期約 73.6 萬：其中 60 萬是自己存的，13.6 萬是報酬',
           '是前面那 5,000 元的 27 倍',
           '它得漲 1,362%']
# v6.3 批 3 修正：第 5 節滿足點表外那一句補數字；第 7 節兩個分母與名單口徑
# v7 六位模擬讀者批第二輪（裁判⑥ M2/M3）：第 11 節停損那一段的口徑小字，數字來自 taiex_stoploss
quotes += ['「從高點跌 15% 就賣、等指數回到原來的高點才買回」會觸發 11 次。這條規則的結果是算術，不是運氣：'
           '賣在高點下面 15%、等回到高點才買，買回價一定比賣價高至少 17.6%（1 ÷ 0.85）；台股這 11 次實際高 18% 到 23%',
           '賣出後兩年內指數最低比賣價再低近五成；但照這條規則要到 2010 年 12 月才買回，買回價比賣價高約一成九']
# v7 預覽「錢變多以後：一天的漲跌，會開始超過月薪」批：第 8 節 #s5-daily 那一段。
# 主線那張表的第三欄來自 taiex_daily_moves；示範句與摺疊裡兩張小表來自 months_to_salary_multiple。
quotes += ['沒有發生過：台股有單日漲跌幅限制，這份資料最大的一天約 −9.7%',
           '平均一年約 10 天',
           '平均一年約 32 天',
           '大約第 8 年到 25 倍，第 21 年到 100 倍',
           '| 月薪的一成 | 15 | 14 | 13',
           '| 月薪的兩成 | 9 | 8 | 8',
           '| 月薪的三成 | 6 | 6 | 6',
           '| 月薪的一成 | 37 | 30 | 28',
           '| 月薪的兩成 | 25 | 21 | 20',
           '| 月薪的三成 | 19 | 17 | 16']
# v7 第 20 版（辯證批）：兩句新的主線數字
quotes += ['最差的二十年（1962 到 1981）一年不到 1%',
           '一年只能拿 2.31%，大約是 43 倍']
# 第 20 版裁判後修正 M1／S5：第 16 節三方比較與第 8 節口徑小字
quotes += ['這一項是三種裡最重的，一年大約 0.4 到 0.5 個百分點',
           '美國掛牌的只少 0.1 個百分點左右',
           '名目一年約 6.7%，扣掉物價約 0.8%',
           '名目最差的是 1999 到 2018（約 5.9%，扣掉物價約 3.6%）']
# 批 P／批 R：第 24 節 2.31% 的口徑（主線那一句）與摺疊裡的國際分散版本
quotes += ['這個 2.31% 算的是「只買自己國家的股票和債券」：這份研究的基準組合是六成本國股、四成本國債',
           '把股票的四成換成國際股，可以拿 2.85%（約 35 倍）；換九成，可以拿 3.02%（約 33 倍）']
# 批 T：美股長線圖改成 1929 年起，圖說的兩個數字釘在這裡
quotes += ['1929 年初投進去的 1 元，含息到 2026 年變成大約 9,899 元；中間最深的一次，帳面少掉 82%']
# v7 批 W：第 8 節台股長線圖的圖說（串接後回到 1990 年高點的那一週）
quotes += ['算進 2003 年以後的股利，這條線在 2013 年 12 月就回到那個高度']
# v7 批 Z：同一張圖的圖說，1990–2002 那一段股利的估算（數字來自 taiex_pre2003_dividend_estimate）
quotes += ['一年大約多 2.4 個百分點：那十二年從價格指數的 −0.14% 變成大約 +2%，還是接近打平']
# v7 批 X：第 8 節滾動報酬圖的圖說三句，與兩張圖 p.note 的 Cowles 揭露
quotes += ['抱 10 年，歷史上有大約 3% 的起點是虧的，最差一年 −4.0%；抱 20 年，沒有一個起點是虧的，'
           '最差一年 2.0%；抱 30 年，最差也有 3.6%',
           '拿掉它 30 年最差會變成 7.6%']
quotes += ['存 15%、保守算 4% 是 48.4 年，比存四分之一的 35.3 年多了十三年',
           '買一整群，名單上就有那 1,092 家',
           '前兩項的分母 25,967 是資料庫裡的股票檔數，財富創造那一項的分母 25,332 是公司數']

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
p('陳大哥 勞退兩段（N2）:', json.dumps(ch['labor_pension_two_stage'], ensure_ascii=False))
p('扣 0.5% 示範費率（N1）:', json.dumps(R['fee_demo_0_5pct'], ensure_ascii=False))
p('XIRR:', R['xirr_demo'])
p('無感期:', R['quiet_period'], '費用差:', R['fee_gap'])
p('甜蜜點/滿足點:', json.dumps(R['sweet_satisfy']['years'], ensure_ascii=False), '倍數:', R['sweet_satisfy']['ratio_vs_sweet'])
p('台股為正比例:', {k: v['pct'] for k, v in R['rolling']['taiex']['positive_share'].items()})
p('台股區間:', {k: (v['min_pct'], v['max_pct']) for k, v in R['rolling']['taiex']['annual_range'].items()})
p('台股 252 日交叉檢查:', {k: (v['positive']['pct'], v['range']['min_pct'], v['range']['max_pct'])
                          for k, v in R['rolling']['taiex']['cross_check_252_trading_days'].items()})
p('美股為正比例:', R['rolling']['us']['from'], '→', R['rolling']['us']['to'],
  {k: v['pct'] for k, v in R['rolling']['us']['positive_share'].items()})
p('台股 1990–2002 股利估算:', json.dumps(_pd, ensure_ascii=False))
p('台股 ≥20% 回檔:', R['taiex_drawdowns']['n'], '段；回本年數', R['taiex_drawdowns']['years_min'], '到', R['taiex_drawdowns']['years_max'])
for _e in R['taiex_drawdowns']['episodes']:
    p('   %s %.2f → %s %.2f（%s%%）→ %s，%s 年' % (_e['peak_date'], _e['peak_value'], _e['trough_date'],
                                                  _e['trough_value'], _e['drawdown_pct'], _e['recover_date'],
                                                  _e['years_peak_to_recover']))
p('四類資產輪換 %d–%d 第一名次數:' % (ROT_FROM, ROT_TO), R['asset_rotation']['winner_counts'])
p('美股 20 年最差（第 20 版 B3）:', R['us_worst_20y_real']['worst_real'], '／名目最差:', R['us_worst_20y_real']['worst_nominal'])
p('提領率換倍數（第 20 版 B5）:', R['swr_multiples'])
p('台灣掛牌 vs 倫敦掛牌 每年差（第 20 版 C2）:', R['tw_vs_lse_annual_gap'])
p('三種掛牌地每年成本（第 20 版裁判後 M1）:',
  {k: {'股息稅': v['dividend_tax_pp_mid'], '合計': v['total_pp_mid'],
       '台減倫敦': v['tw_minus_lse_mid'], '台減美國': v['tw_minus_us_mid']}
   for k, v in R['listing_annual_cost'].items() if isinstance(v, dict) and 'total_pp_mid' in v})
p('引用缺漏:', R['guide_citations']['missing'])
p('wrote', OUT)
