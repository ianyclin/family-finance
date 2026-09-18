# -*- coding: utf-8 -*-
"""wip 用：只借 tools/calc_core.py 裡的 fv()，算「報酬率不等於報酬」的示意數字。
不 import calc_core（那個模組 import 時會跑全部計算並寫 lite/calc-results.json），
改成用 ast 把 fv 的原始碼抓出來 exec，確保跟正式腳本同一份實作、且沒有副作用。
用法：python3 wip/v63/stock-vs-index/calc_examples.py
"""
import ast, os, json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SRC = os.path.join(ROOT, 'tools', 'calc_core.py')
src = open(SRC, encoding='utf-8').read()
tree = ast.parse(src)
ns = {}
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name == 'fv':
        exec(compile(ast.Module(body=[node], type_ignores=[]), SRC, 'exec'), ns)
fv = ns['fv']
assert fv is not None, 'fv() 沒抓到'

def wan(x):  # 萬，一位小數
    return round(x / 10000, 1)

out = {'source': 'tools/calc_core.py 的 fv()（年率/12 按月複利、每月月底投入）', 'rows': []}

# A. 單一個股：買一張、漲一波
for cost, up in ((10000, 50), (10000, 100), (100000, 50), (300000, 50)):
    out['rows'].append({'kind': '個股一次', '成本元': cost, '漲幅%': up,
                        '賺到元': int(cost * up / 100), '結束後元': int(cost * (1 + up / 100))})

# B. 計畫：每月 5,000 元，4%（完整版第 1 節低情境：股票 100% → 4%）
for yrs in (3, 5, 10, 15, 20):
    v = fv(0, 4, yrs * 12, 5000)
    put = 5000 * yrs * 12
    out['rows'].append({'kind': '計畫定期定額', '每月元': 5000, '年數': yrs, '年報酬率%': 4,
                        '投入本金元': put, '到期元': int(round(v)), '到期萬': wan(v),
                        '其中報酬元': int(round(v - put)), '其中報酬萬': wan(v - put)})

# C. 每月 3,000 / 10,000 對照（同 4%、10 年）
for m in (3000, 10000):
    v = fv(0, 4, 120, m)
    out['rows'].append({'kind': '計畫定期定額', '每月元': m, '年數': 10, '年報酬率%': 4,
                        '投入本金元': m * 120, '到期元': int(round(v)), '到期萬': wan(v),
                        '其中報酬元': int(round(v - m * 120)), '其中報酬萬': wan(v - m * 120)})

# D. 換算：個股那一筆賺到的錢，等於計畫的幾個月投入／幾個月的「報酬」
v10 = fv(0, 4, 120, 5000)
gain10 = v10 - 5000 * 120
out['compare'] = {
    '個股 1 萬漲 50% 賺到元': 5000,
    '等於每月 5000 元計畫的幾個月投入': round(5000 / 5000, 2),
    '每月 5000 元 4% 10 年到期元': int(round(v10)),
    '每月 5000 元 4% 10 年投入本金元': 5000 * 120,
    '每月 5000 元 4% 10 年報酬元': int(round(gain10)),
    '計畫 10 年的報酬是那 5,000 元的幾倍': round(gain10 / 5000, 1),
    '要讓 1 萬元的個股賺到同樣多，需要漲幾 %': round(gain10 / 10000 * 100, 1),
}

# E. 同一筆 60 萬，一次全押個股 vs 分 120 個月投入（純示意，不是預測）
out['lump_vs_plan'] = {
    '一次投 60 萬、漲 50%：賺元': 300000,
    '每月 5,000 元投 10 年（本金同樣 60 萬）、4%：賺元': int(round(gain10)),
    '註': '兩邊口徑不同：一次投是一次漲幅，計畫是 10 年年化 4%；放在一起只為了看「報酬率 vs 報酬」的量級',
}

print(json.dumps(out, ensure_ascii=False, indent=1))
