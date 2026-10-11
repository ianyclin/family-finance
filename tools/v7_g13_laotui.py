#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G13（v7 批 DJ）：要不要自提的熱圖。只在指南（第 24 節新卡「要不要自提，先看你是哪種人」）。
規格：wip/v63-review/spec-v7-content-dj.md 的 B 段。

    laotui-heatmap  五個級距（5／12／20／30／40%）× 自提 5、10、…、35 年，每格是
                    「60 歲一次領、繳完稅剩的錢」自提比不自提（同一筆錢扣掉當年的稅、自己投台股 ETF）
                    多拿或少拿幾 %；最右一欄是翻盤年（從第幾年起自提開始少拿）。

計算（第四版模型，2026-10-11 主線改）
    假設 25 歲開始工作、60 歲一次領，年資 Y 固定 35 年；n＝自提年數＝現在離 60 歲還有幾年（橫軸 5–35）。
    第六版（和 tool6 同步）：退休那年的綜所稅，先從所得扣掉免稅額＋標準扣除額 237,000×g 再套級距
    （taxT 的輸入是 max(R − 237,000×g, 0)）；其餘同第五版。
    第五版起：每月提繳跟著級距走——月薪取該級距的代表值，雇主 6%、自提 6% 各一份
    （5% 級距月薪 45,000、各 2,700；12% 月薪 100,000、各 6,000；20／30／40% 月薪 150,000（提繳上限）、各 9,000）。
    雇主那份滾 35 年、自提那份滾 n 年、一次領的免稅額用 35 年資乘。
    其餘照第三版原型 calc3.py 的式子（逐行照抄，拿掉只給驗證用的 step 開關）：雇主同額、
    免稅額與級距每年隨物價 1.5%（從現在到 60 歲共 n 年，同乘 1.015^n）、退休那年沒有薪水、勞退 4.65%、
    自己投台股 ETF（配息課稅，5% 級距的配息稅率允許是負的）。線上工具的 JS 是同一套式子，可以切換假設；
    書上這張圖只畫預設那一組。

    compute() 斷言兩件事，對不上就 raise、不畫：
      1. 5×7 格的值（四捨五入到小數 6 位）逐格等於 EXPECT_GRID；
      2. 翻盤年（看 1–35 年每一年，不是只看 7 欄）等於 EXPECT_FLIP。
    兩個常數抄自第六版對照檔 tool6-data.json（由 tools/laotui/calc.py 產生，原在 scratchpad，已不依賴；
    抄之前 `--check-proto` 全 35 年逐格相等）。模型再改時兩個常數可以先設成 None：compute() 預設會擋（require_baseline=True），
    只有 main() 自測時放行並在 stderr 警告；新的對照檔出來，跑 `--check-proto` 過了再抄。

顏色（為什麼是五階離散，不是連續色階）
    指南裡六十張 SVG 全部只用 CSS 變數上色，深色模式靠 :root 換變數（@media prefers-color-scheme），
    沒有任何一張用 hex、也沒有「data-fill-dark 換色」那種機制；要做連續色階就得在指南加一段新 CSS，
    這一批不動指南。所以改成五階：琥珀深／琥珀淺／近白／綠淺／綠深，填色用 var(--amber)、var(--green)
    加 fill-opacity，近白用 var(--fill)。兩種模式都自動對應。
    opacity 取 0.20／0.45：格內墨色字的對比，淺色模式最低 7.98（綠 0.45），深色模式最低 5.07（綠 0.45），
    都過 4.5。0.50 在深色模式綠格會掉到 4.49，所以停在 0.45。
    分級：|值| < 5% 近白（差不到 5%，等於打平附近；剛好落在每一列的翻盤處）、5%–20% 淺、20% 以上深。

compute() 只用標準庫；chart(res) 才 lazy import essay_charts。
"""
import json
import os
import sys

# ---------------------------------------------------------------------------
# 模型（calc3.py 的式子，年資改成固定 35；參數寫死為 DEF）
KS = [5, 12, 20, 30, 40]                       # 綜所稅級距（%）
COLS = [5, 10, 15, 20, 25, 30, 35]             # 圖上的七欄：自提了幾年
NMAX = 35                                      # 翻盤年看 1–35 年
# 115 年度綜所稅：(級距上限, 稅率, 累進差額)
BR = [(610000, 0.05, 0), (1380000, 0.12, 42700), (2770000, 0.20, 153100),
      (5190000, 0.30, 430100), (float('inf'), 0.40, 949100)]
# 「退休那年薪水和現在一樣」時的其他所得代表值（級距區間中點）；預設 sal=0 用不到，留著是為了和工具同一套式子。
MID = {5: 305000, 12: 995000, 20: 2075000, 30: 3980000, 40: 6400000}
START_AGE, PAYOUT_AGE = 25, 60
YTOT = PAYOUT_AGE - START_AGE                  # 年資固定 35
DEF = dict(emp=1, idx=1, sal=0, rl=0.0465, path='tw', Ytot=YTOT)
# 每個級距的代表月薪與每月提繳（雇主、自提各一份＝月薪 6%；月提繳工資上限 15 萬）
SALARY = {5: 45000, 12: 100000, 20: 150000, 30: 150000, 40: 150000}
RATE = 0.06
PMONTH = {k: round(SALARY[k] * RATE) for k in KS}
assert PMONTH == {5: 2700, 12: 6000, 20: 9000, 30: 9000, 40: 9000}


def vdef(k, n):
    """預設假設下的值：每月提繳照級距（PMONTH）。"""
    return val(k, n, P=PMONTH[k], **DEF)


def fv(p, r, n):
    """每月 p、年報酬 r（換成月複利）、n 年的期末值。"""
    if n <= 0:
        return 0.0
    m = (1 + r) ** (1 / 12) - 1
    return p * ((1 + m) ** (12 * n) - 1) / m


def tau(t):
    """配息的稅率：級距 − 8.5%（股利可抵減，允許負值＝抵減超過退稅）；40% 級距用 28% 分開計稅。"""
    return 0.28 if t >= 0.40 else t - 0.085


GROSS = 0.075                                  # 自己投台股 ETF 的毛報酬（tool5／tool6 的 gi）


def ri(t, path):
    """自己投的年報酬。tw：總報酬 7.5%、配息 3% 要繳 tau(t)＋二代健保 2.11%；acc：不配息；none：不課稅。"""
    if path == 'tw':
        return GROSS - 0.03 * (tau(t) + 0.0211)
    if path == 'acc':
        return GROSS - 0.02 * 0.15
    return GROSS


def taxT(x, g=1.0):
    """115 年度級距算的綜所稅；級距上下限與累進差額同乘 g（隨物價）。"""
    y = x / g
    for hi, r, d in BR:
        if y <= hi:
            return g * max(y * r - d, 0)


# 第六版：退休那年先扣免稅額＋標準扣除額（單身一人 237,000，同乘 g）再套級距。
DEDUCT = 237000


def taxable(L, Y, g):
    """一次領退職所得的應稅部分：每年資 20.6 萬內全免、20.6–41.4 萬課一半、超過全課（同乘 g）。"""
    lo, hi = 206000 * Y * g, 414000 * Y * g
    return 0.5 * max(min(L, hi) - lo, 0) + max(L - hi, 0)


def gfac(n, idx):
    return 1.015 ** n if idx else 1.0


def cell(k, n, P, emp=1, idx=1, sal=0, rl=0.0465, path='tw', Ytot=YTOT):
    """級距 k%、自提 n 年（＝離 60 歲 n 年）。A＝自提那份滾 n 年；E＝雇主那份滾 Y＝Ytot 年（固定 35）；
    B＝不自提、同一筆錢扣掉當年級距的稅、自己投 n 年。免稅額用 Y 乘、隨物價 n 年。
    自提多繳的稅＝（A＋E）的退職所得稅 −（只有 E）的退職所得稅。值＝(A − 多繳的稅)/B − 1。"""
    assert 1 <= n <= Ytot
    t = k / 100
    Y = Ytot
    g = gfac(n, idx)
    A = fv(P, rl, n)
    E = fv(P, rl, Y) if emp else 0.0
    B = fv(P * (1 - t), ri(t, path), n)
    O = MID[k] * g if sal else 0.0
    ded = DEDUCT * g
    tx = (taxT(max(O + taxable(A + E, Y, g) - ded, 0), g)
          - taxT(max(O + taxable(E, Y, g) - ded, 0), g))
    return dict(v=(A - tx) / B - 1, A=A, E=E, B=B, tax_self=tx, Y=Y)


def val(k, n, **s):
    return cell(k, n, **s)['v']


def flip(vs):
    """第一個轉負的年（1 起算）；35 年內都沒轉負回 None。"""
    for i, v in enumerate(vs):
        if v < 0:
            return i + 1
    return None


# 基準：第六版對照檔 tool6-data.json 的 default 在 5、10、…、35 年那幾格（round 到小數 6 位）與 flip_default。
# 2026-10-11 從 tool6-data.json（values_default、flip_default；由 tools/laotui/calc.py 產生）抄進來；抄之前 --check-proto 全 35 年逐格相等。
# 期望值就寫死在這裡，執行時不讀任何外部檔；--check-proto 只是選用的對照（要先在別處跑 calc.py 產生 json）。
# 模型再改時：先設回 None，跑 --check-proto 新的對照檔，過了再從那個檔抄（不要從本檔自己的輸出抄）。
EXPECT_GRID = {
    5:  [-0.018882, -0.09262, -0.16622, -0.238566, -0.308659, -0.375657, -0.43891],
    12: [0.064573, -0.009756, -0.08432, -0.158043, -0.229944, -0.299173, -0.365048],
    20: [0.129307, 0.066821, -0.001806, -0.072148, -0.144291, -0.215428, -0.287085],
    30: [0.300076, 0.238228, 0.168964, 0.097109, 0.022274, -0.052449, -0.129103],
    40: [0.523961, 0.459179, 0.385535, 0.308486, 0.227358, 0.145663, 0.060767],
}
EXPECT_FLIP = [4, 10, 15, 27, None]

MODEL_NOTE = ('第六版。退休那年先扣免稅額＋標準扣除額 237,000×g 再套級距。每月提繳跟著級距走（月薪 4.5／10／15／15／15 萬的 6%，雇主、自提各一份）；25 歲開始工作、60 歲一次領，年資固定 35；n＝自提年數＝離 60 歲年數。值＝(A−因自提多繳的稅)/B−1。'
              'A＝自提 n 年滾 r_l；雇主那份滾 35 年；免稅額按 35 年資；隨物價時免稅額、級距同乘 1.015^n（連續）。'
              '配息稅 τ＝t−8.5% 允許負值，40% 用 28%。')


def compute(require_baseline=True):
    """require_baseline=False 只給 main() 自測用：基準還沒抄進來時照算、標 verified=False。"""
    full = {k: [vdef(k, n) for n in range(1, NMAX + 1)] for k in KS}
    grid = {k: [round(full[k][n - 1], 6) for n in COLS] for k in KS}
    flips = [flip(full[k]) for k in KS]
    verified = EXPECT_GRID is not None and EXPECT_FLIP is not None
    if verified:
        bad = ['級距 %d%% 第 %d 年：算出 %r，基準 %r' % (k, n, grid[k][j], EXPECT_GRID[k][j])
               for k in KS for j, n in enumerate(COLS) if grid[k][j] != EXPECT_GRID[k][j]]
        assert not bad, '自提熱圖的值和 tool6-data.json 基準對不上：\n  ' + '\n  '.join(bad)
        assert flips == EXPECT_FLIP, '翻盤年 %r，基準 %r' % (flips, EXPECT_FLIP)
    else:
        assert not require_baseline, ('自提熱圖的基準（EXPECT_GRID／EXPECT_FLIP）還沒抄進來：'
                                      '先跑 --check-proto tool6-data.json，過了再抄')
    return {
        'id': 'laotui-heatmap',
        'illustrative': False,      # 模型試算，不是市場資料；假設全寫在圖說與 basis
        'basis': {
            'what': '60 歲一次領、繳完稅剩的錢：自提那份（扣掉因為自提多繳的退職所得稅）對上不自提、'
                    '同一筆錢扣掉當年級距的稅後自己投台股 ETF；值＝(A−多繳的稅)/B−1，正＝自提多拿',
            'monthly_each': {str(k): PMONTH[k] for k in KS},
            'salary_by_bracket': {str(k): SALARY[k] for k in KS},
            'contribution_rate_each': RATE,
            'employer_match': bool(DEF['emp']),
            'start_age': START_AGE,
            'payout_age': PAYOUT_AGE,
            'service_years': DEF['Ytot'],
            'n_means': '自提年數＝離 60 歲年數',
            'exemption_indexed_cpi': 0.015 if DEF['idx'] else 0.0,
            'salary_in_retirement_year': bool(DEF['sal']),
            'pension_return': DEF['rl'],
            'pension_return_note': '勞退新制 2006–2025 年化（圖說的口徑）',
            'self_invest': '台股 ETF：總報酬 7.5%、配息 3%，配息繳（級距−8.5%，40% 級距用 28%）＋二代健保 2.11%',
            'tax_table': '115 年度綜所稅級距；一次領退職所得每年資 20.6 萬內免稅、20.6–41.4 萬課一半（年資 35）；'
                         '免稅額與級距隨物價同乘 1.015^n',
            'payout': '60 歲一次領',
            'model_note': MODEL_NOTE,
            'source_prototype': 'tools/laotui/calc.py 產生的 tool6-data.json 的 values_default（和 tools/laotui/laotui-tool.html 同步）',
        },
        'brackets': list(KS),
        'years': list(COLS),
        'grid': {str(k): grid[k] for k in KS},
        'flip': {str(k): f for k, f in zip(KS, flips)},
        'verified': verified,
    }


def check_proto(path):
    """對 tool6-data.json 逐格比（全部 5 級距 × 35 年）與翻盤年。回不一致清單。
    值在 values_default（tool5／tool6 的形狀）；舊的 proto3 形狀放在 default，兩種都認。
    另外比 fixed 裡的每月提繳、月薪與 default 裡的兩個報酬，假設不同就算不一致。"""
    d = json.load(open(path, encoding='utf-8'))
    vals = d.get('values_default')
    if vals is None:
        vals = d['default']
    bad = []
    for k in KS:
        exp = vals[str(k)]
        got = [round(vdef(k, n), 6) for n in range(1, NMAX + 1)]
        bad += ['級距 %d%% 第 %d 年：%r ≠ %r' % (k, n + 1, got[n], exp[n])
                for n in range(NMAX) if got[n] != exp[n]]
        f = flip([vdef(k, n) for n in range(1, NMAX + 1)])
        if f != d['flip_default'][str(k)]:
            bad.append('flip_default 級距 %d%%：%r ≠ %r' % (k, f, d['flip_default'][str(k)]))
    fx = d.get('fixed') or {}
    if 'monthly_by_bracket' in fx and {int(k): v for k, v in fx['monthly_by_bracket'].items()} != PMONTH:
        bad.append('每月提繳不同：%r ≠ %r' % (fx['monthly_by_bracket'], PMONTH))
    if 'salary_by_bracket' in fx and {int(k): v for k, v in fx['salary_by_bracket'].items()} != SALARY:
        bad.append('月薪不同：%r ≠ %r' % (fx['salary_by_bracket'], SALARY))
    dd = d.get('default') if isinstance(d.get('default'), dict) and 'rl' in d.get('default', {}) else None
    if dd is not None and (dd.get('rl') != DEF['rl'] or dd.get('gi', GROSS) != GROSS):
        bad.append('報酬假設不同：%r ≠ rl=%r gi=%r' % (dd, DEF['rl'], GROSS))
    return bad


# ---------------------------------------------------------------------------
# 畫圖
TITLE = '要不要自提：自提比自己投指數多拿或少拿幾成'
SUB = '60 歲一次領，繳完稅剩的錢；正＝自提多拿'
# 注意：essay_charts --guide 會保留指南裡已有的 figcaption，改這裡要同步改 guide/index.html 那一句。
CAPTION = ('每月提薪水的 6%（雇主、自提各一份）、25 歲開始工作、60 歲一次領、退休那年沒有薪水、免稅額隨物價調；'
           '勞退 4.65%（2006–2025 年化），自己投台股 ETF（配息課稅）。換假設整張圖會變，線上工具可以自己切。')
# 翻盤年那一欄的說明（規格沒寫；主線不要就設成空字串，extras 就只剩色帶）。
FLIP_NOTE = '翻盤年：從第幾年起，自提開始少拿；「—」是 35 年內都多拿。'
LEG_LOSE, LEG_WIN = '自提輸', '自提贏'

# 五階：(下界含, 上界不含, 顏色變數, 透明度)；近白那一階用 var(--fill)、不帶透明度。
BIN_NEAR, BIN_FAR = 0.05, 0.20
OP_WEAK, OP_STRONG = 0.20, 0.45


def shade(v):
    """回 (fill, fill-opacity 或 None, 階 −2..2)。"""
    a = abs(v)
    if a < BIN_NEAR:
        return 'var(--fill)', None, 0
    col = 'var(--green)' if v > 0 else 'var(--amber)'
    if a < BIN_FAR:
        return col, OP_WEAK, (1 if v > 0 else -1)
    return col, OP_STRONG, (2 if v > 0 else -2)


def pct(v):
    """整數百分比，帶正負號，負號用 −（U+2212）。"""
    s = '%d' % round(abs(v) * 100)
    if s == '0':
        return '0%'
    return ('+' if v > 0 else '−') + s + '%'


def flip_label(f, mobile):
    if f is None:
        return '—'
    return ('%d 年' if mobile else '第 %d 年') % f


def _aria(res):
    parts = ['熱圖：五個綜所稅級距乘自提 5 到 35 年，每格是 60 歲一次領、繳完稅剩的錢，'
             '自提比不自提、自己投指數多拿（正）或少拿（負）的百分比；最右一欄是翻盤年']
    for k in KS:
        cells = '、'.join('%d 年 %s' % (n, pct(v)) for n, v in zip(COLS, res['grid'][str(k)]))
        f = res['flip'][str(k)]
        tail = '從第 %d 年起自提少拿' % f if f else '35 年內都是自提多拿'
        parts.append('級距 %d%%：%s；%s' % (k, cells, tail))
    return '。'.join(parts) + '。'


def _geom(mobile):
    # 手機：級距欄 26（「40%」粗體 11px 約 23）、翻盤年欄 34（「翻盤年」三個字 33），省下來的寬給七格，
    # 每格 41.7，「−48%」左右各留約 4px（375 寬實量）。格寬夠，所以手機也留百分號。
    if mobile:
        return dict(W=360, pad=2.0, labW=26.0, gapF=4.0, flipW=34.0, ch=30.0, fz=11, fh=11, fr=11,
                    yAxis=13.0, yHead=31.0, top=40.0)
    return dict(W=640, pad=4.0, labW=52.0, gapF=10.0, flipW=70.0, ch=32.0, fz=12, fh=12, fr=12.5,
                yAxis=14.0, yHead=34.0, top=44.0)


def layout(mobile):
    """回每個格子與字的座標（畫圖與自測共用）。"""
    g = _geom(mobile)
    x0 = g['pad'] + g['labW']
    cw = (g['W'] - 2 * g['pad'] - g['labW'] - g['gapF'] - g['flipW']) / len(COLS)
    g['x0'], g['cw'] = x0, cw
    g['fx'] = x0 + cw * len(COLS) + g['gapF']
    g['H'] = g['top'] + g['ch'] * len(KS) + 6
    return g


def chart(res):
    import essay_charts as E

    def draw(kind):
        mob = kind == 'm'
        g = layout(mob)
        lay = E.L(kind)
        out = [E.svg_open(lay, g['H'], _aria(res))]
        x0, cw, ch, top = g['x0'], g['cw'], g['ch'], g['top']
        # 欄首：上面一行「自提了幾年」，下面一行各欄年數；左上「級距」、右上「翻盤年」
        out.append(E.text(x0 + cw * len(COLS) / 2, g['yAxis'], '離 60 歲幾年（＝自提幾年）', g['fh'], 'middle', E.MUTED))
        out.append(E.text(g['pad'], g['yHead'], '級距', g['fh'], 'start', E.MUTED))
        for j, n in enumerate(COLS):
            out.append(E.text(x0 + j * cw + cw / 2, g['yHead'], '%d 年' % n, g['fh'], 'middle', E.MUTED))
        out.append(E.text(g['fx'] + g['flipW'] / 2, g['yHead'], '翻盤年', g['fh'], 'middle', E.MUTED))
        for i, k in enumerate(KS):
            y = top + i * ch
            base = y + ch / 2 + g['fz'] * 0.36
            out.append(E.text(g['pad'], y + ch / 2 + g['fr'] * 0.36, '%d%%' % k, g['fr'], 'start', E.INK, '700'))
            for j, v in enumerate(res['grid'][str(k)]):
                fill, op, _lv = shade(v)
                o = ' fill-opacity="%s"' % op if op is not None else ''
                out.append('<rect class="hm" data-v="%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s"%s/>'
                           % (v, x0 + j * cw + 1, y + 1, cw - 2, ch - 2, fill, o))
                out.append(E.text(x0 + j * cw + cw / 2, base, pct(v), g['fz'], 'middle', E.INK))
            out.append(E.text(g['fx'] + g['flipW'] / 2, base, flip_label(res['flip'][str(k)], mob),
                              g['fz'], 'middle', E.INK, '700'))
        out.append('</svg>')
        return '\n'.join(out)

    # 色帶圖例（HTML）：兩端「自提輸」「自提贏」，中間五格照圖上的五階
    sw = []
    for v in (-1.0, -0.1, 0.0, 0.1, 1.0):
        fill, op, _lv = shade(v)
        style = 'background:%s;width:1.6em;height:.7em;margin:0;border-radius:0' % fill
        if op is not None:
            style += ';opacity:%s' % op
        else:
            style += ';box-shadow:inset 0 0 0 1px var(--line)'
        sw.append('<span class="swatch" style="%s"></span>' % style)
    band = ('<ul class="legend"><li>%s<span style="display:inline-flex;margin:0 .5em;vertical-align:baseline" aria-hidden="true">%s</span>%s</li></ul>'
            % (E.esc(LEG_LOSE), ''.join(sw), E.esc(LEG_WIN)))
    extras = band + ('\n' + E.note(FLIP_NOTE) if FLIP_NOTE else '') + '\n'
    return dict(title=TITLE, sub=SUB, svgs=[draw('d'), draw('m')], extras=extras, caption=CAPTION)


def main(argv):
    if '--check-proto' in argv:
        path = argv[argv.index('--check-proto') + 1]
        bad = check_proto(path)
        print('PROTO OK（5 級距 × 35 年逐格相等，翻盤年相等）' if not bad else '\n'.join(bad))
        return 1 if bad else 0
    res = compute(require_baseline=False)
    if not res['verified']:
        print('⚠ 基準還沒抄進來（EXPECT_GRID／EXPECT_FLIP 是 None），這份輸出沒有對照過。', file=sys.stderr)
    if '--table' in argv:
        print('      ' + ' '.join('%6d' % n for n in COLS) + '  翻盤年')
        for k in KS:
            f = res['flip'][str(k)]
            print('%3d%%  ' % k + ' '.join('%+6.1f' % (v * 100) for v in res['grid'][str(k)]) + '  %s' % (f if f else '—'))
        return 0
    if '--json' in argv:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    d = chart(res)
    if '--figure' in argv:
        import essay_charts as E
        print(E.figure(res['id'], d['title'], d['sub'], d['svgs'], d['caption'], d['extras']))
    else:
        print('\n'.join(d['svgs']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
