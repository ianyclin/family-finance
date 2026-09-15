#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
twse_dca_freq.py  —— 算式 C：投入「頻率」對定期定額結果的影響（裁判輪自算，○ 本文推論）

延伸 twse_dca.py（同資料、同 IRR 函式），回答作者主張 C5：
「每月投入十天、每月三天、每月一天、每季、每年，對長期投資的結果幾乎沒有影響」。

資料：research/data/taiex_tr_monthly_raw.csv（證交所 MFI94U 含息報酬指數逐日收盤，
      2003-01-02 ~ 2025-12-31，由 twse_dca.py fetch 取得）。
規則：每個情境「總投入」都固定為 10,000 元 × 276 個月 = 2,760,000 元，只改變投入時點：
  every_day      每月 10,000 元平均分到該月每一個交易日買進（最貼近「指數本身」）
  first_10_days  每月 10,000 元平均分到該月前 10 個交易日
  first_3_days   每月 10,000 元平均分到該月前 3 個交易日
  first_day      每月第 1 個交易日一次買 10,000 元
  last_day       每月最後 1 個交易日一次買 10,000 元
  quarter_first  每季第 1 個交易日一次買 30,000 元
  year_first     每年第 1 個交易日一次買 120,000 元
期末：2025-12-31 收盤 65,905.98，全部贖回。
IRR：現金流按「月」歸戶（同一月內多筆買進合計），用 twse_dca.monthly_irr 二分法求月報酬率，
     年化 = (1+r)^12 − 1；因此 quarter/year 情境在沒買的月份現金流為 0。

用法：python3 tools/twse_dca_freq.py
輸出：research/data/algo_c_freq_results.csv 與 stdout。
限制：只用收盤值（無盤中價）；2003–2025 是事後看報酬偏高的區間；換一段期間數字會不同；
      這是算術不是預測。
"""

import csv
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twse_dca import load_raw, monthly_irr, DATA_DIR  # noqa: E402

OUT_CSV = os.path.join(DATA_DIR, "algo_c_freq_results.csv")
MONTHLY = 10000.0


def main():
    rows = load_raw()
    by_month = defaultdict(list)
    for d, v in rows:
        by_month[(int(d[0:4]), int(d[5:7]))].append((d, v))
    months = sorted(by_month)
    n_months = len(months)
    final_index = by_month[months[-1]][-1][1]
    total_invested = MONTHLY * n_months

    def run(buy_plan):
        """buy_plan: dict month_key -> list of (price, amount)。回傳 (期末資產, 年化IRR)。"""
        units = 0.0
        cash_by_month = []
        for mk in months:
            spent = 0.0
            for price, amt in buy_plan.get(mk, []):
                units += amt / price
                spent += amt
            cash_by_month.append(-spent)
        final_value = units * final_index
        cash_by_month[-1] += final_value
        m_irr = monthly_irr(cash_by_month)
        return final_value, (1.0 + m_irr) ** 12 - 1.0

    plans = {}

    def spread_first_n(n):
        plan = {}
        for mk in months:
            days = by_month[mk][:n] if n else by_month[mk]
            per = MONTHLY / len(days)
            plan[mk] = [(v, per) for _, v in days]
        return plan

    plans["every_day"] = spread_first_n(0)
    plans["first_10_days"] = spread_first_n(10)
    plans["first_3_days"] = spread_first_n(3)
    plans["first_day"] = {mk: [(by_month[mk][0][1], MONTHLY)] for mk in months}
    plans["last_day"] = {mk: [(by_month[mk][-1][1], MONTHLY)] for mk in months}

    q_plan = {}
    for mk in months:
        y, m = mk
        if m in (1, 4, 7, 10):
            q_plan[mk] = [(by_month[mk][0][1], MONTHLY * 3)]
    plans["quarter_first"] = q_plan

    y_plan = {}
    for mk in months:
        y, m = mk
        if m == 1:
            y_plan[mk] = [(by_month[mk][0][1], MONTHLY * 12)]
    plans["year_first"] = y_plan

    labels = [
        ("every_day", "每月分到每個交易日"),
        ("first_10_days", "每月前 10 個交易日"),
        ("first_3_days", "每月前 3 個交易日"),
        ("first_day", "每月第 1 個交易日"),
        ("last_day", "每月最後 1 個交易日"),
        ("quarter_first", "每季第 1 個交易日（30,000）"),
        ("year_first", "每年第 1 個交易日（120,000）"),
    ]

    print("=== 算式 C：投入頻率 vs 結果  樣本 %s ~ %s，%d 個月，總投入 %.0f 元，期末指數 %.2f ===" % (
        rows[0][0], rows[-1][0], n_months, total_invested, final_index))
    results = []
    for key, label in labels:
        fv, irr = run(plans[key])
        # 每筆投入金額檢查
        invested = sum(a for lst in plans[key].values() for _, a in lst)
        assert abs(invested - total_invested) < 1e-6, (key, invested)
        results.append((key, label, fv, fv / total_invested - 1.0, irr))
        print("[%s] 期末總資產: %.0f 元 | 總報酬率: %.2f%% | 年化 IRR: %.2f%%" % (
            label, fv, (fv / total_invested - 1.0) * 100, irr * 100))

    fvs = [r[2] for r in results]
    print("期末資產 最高/最低 = %.0f / %.0f，相差 %.2f%%" % (max(fvs), min(fvs), (max(fvs) / min(fvs) - 1) * 100))

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "label", "final_value", "total_return_pct", "annual_irr_pct"])
        for key, label, fv, tr, irr in results:
            w.writerow([key, label, round(fv, 2), round(tr * 100, 4), round(irr * 100, 4)])
    print("已寫入 %s" % OUT_CSV)


if __name__ == "__main__":
    main()
