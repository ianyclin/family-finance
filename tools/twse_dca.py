#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
twse_dca.py

從證交所 (TWSE) 公開 API 抓取「發行量加權股價報酬指數」(含息報酬指數, TAIEX Total
Return Index) 的每日收盤值，2003-01 至指定年月，計算：

  算式 A：每月定期定額投入 10,000 元，分別用「當月最高收盤」「當月收盤均價」
          「當月最低收盤」買進，算期末總資產、總報酬率、年化報酬率 (IRR)。
  算式 B：每個日曆年的「年內最大跌幅」(自年內高點到其後低點的最大跌幅) 與
          「全年報酬率」，並統計平均年內最大跌幅、正報酬年數。

資料來源 API（唯一資料來源，不補其他來源）：
  端點：https://www.twse.com.tw/indicesReport/MFI94U?response=json&date=YYYYMM01
  說明：帶入該月任一日期（本腳本一律用當月 01 日）即回傳該月所有交易日資料。
  欄位：
    - 日　期：民國年/月/日（例如 "114/12/31" = 2025-12-31）
    - 發行量加權股價報酬指數：當日收盤指數值（僅收盤，無日內高低）

用法：
  python3 twse_dca.py fetch --start 2003-01 --end 2025-12
      依序抓取每月資料，每次請求間隔至少 3 秒，寫入
      research/data/taiex_tr_monthly_raw.csv（逐日收盤）。

  python3 twse_dca.py compute
      讀取上一步存的 CSV，輸出：
        research/data/algo_a_monthly_stats.csv   （逐月最高/均/最低/首日/末日）
        research/data/algo_a_results.csv         （三情境期末資產/報酬率/IRR）
        research/data/algo_b_yearly.csv          （逐年最大跌幅與全年報酬）
        research/data/algo_b_summary.csv         （平均最大跌幅、正報酬年數）
      並把結果印到 stdout，供撰寫報告時複製。

注意：本腳本只呼叫證交所官方端點，不使用任何非官方或第三方資料源；
若某月回傳非 OK 或缺資料，會照實記錄在 stderr / CSV 的 note 欄，不用其他來源填補。
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import date

BASE_URL = "https://www.twse.com.tw/indicesReport/MFI94U"
USER_AGENT = "Mozilla/5.0 (compatible; family-finance-research/1.0)"

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "research", "data")
RAW_CSV = os.path.join(DATA_DIR, "taiex_tr_monthly_raw.csv")
STATS_CSV = os.path.join(DATA_DIR, "algo_a_monthly_stats.csv")
RESULTS_CSV = os.path.join(DATA_DIR, "algo_a_results.csv")
YEARLY_CSV = os.path.join(DATA_DIR, "algo_b_yearly.csv")
SUMMARY_CSV = os.path.join(DATA_DIR, "algo_b_summary.csv")


def roc_to_iso(roc_date_str):
    """把 '114/12/31' 這種民國日期字串轉成 ISO 'YYYY-MM-DD'。"""
    roc_date_str = roc_date_str.strip()
    y, m, d = roc_date_str.split("/")
    return "%04d-%02d-%02d" % (int(y) + 1911, int(m), int(d))


def fetch_month(year, month, retries=3):
    """抓單一月份的 MFI94U 資料，回傳 list of (iso_date, value_float)。"""
    date_param = "%04d%02d01" % (year, month)
    url = "%s?response=json&date=%s" % (BASE_URL, date_param)
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
            obj = json.loads(raw)
            if obj.get("stat") != "OK":
                return [], obj.get("stat", "UNKNOWN_STAT")
            rows = []
            for rec in obj.get("data", []):
                d_str, v_str = rec[0], rec[1]
                iso = roc_to_iso(d_str)
                val = float(v_str.replace(",", ""))
                rows.append((iso, val))
            return rows, "OK"
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last_err = str(e)
            time.sleep(3)
    return [], "FETCH_ERROR: %s" % last_err


def cmd_fetch(args):
    start_y, start_m = [int(x) for x in args.start.split("-")]
    end_y, end_m = [int(x) for x in args.end.split("-")]

    os.makedirs(DATA_DIR, exist_ok=True)
    all_rows = []
    notes = []

    y, m = start_y, start_m
    n_requests = 0
    while (y, m) <= (end_y, end_m):
        rows, status = fetch_month(y, m)
        n_requests += 1
        print("%04d-%02d: status=%s, rows=%d" % (y, m, status, len(rows)), file=sys.stderr)
        if status != "OK":
            notes.append("%04d-%02d: %s" % (y, m, status))
        all_rows.extend(rows)

        m += 1
        if m > 12:
            m = 1
            y += 1

        if (y, m) <= (end_y, end_m):
            time.sleep(3)  # 每次請求間隔至少 3 秒

    with open(RAW_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "taiex_tr_index"])
        for iso, val in all_rows:
            w.writerow([iso, val])

    print("共 %d 個月份請求，取得 %d 筆逐日資料，寫入 %s" % (n_requests, len(all_rows), RAW_CSV))
    if notes:
        print("缺漏/失敗月份：")
        for n in notes:
            print("  - %s" % n)
    else:
        print("所有月份皆成功取得資料，無缺漏。")


def load_raw():
    rows = []
    with open(RAW_CSV, encoding="utf-8") as f:
        r = csv.DictReader(f)
        for rec in r:
            rows.append((rec["date"], float(rec["taiex_tr_index"])))
    rows.sort(key=lambda x: x[0])
    return rows


def monthly_irr(cashflows):
    """cashflows: list of monthly cash flows (negative=invest, positive=redeem)。
    以二分法求解月報酬率 r，使 NPV=0。回傳月報酬率 r（小數）。

    注意：NPV 以「多項式形式」sum(cf_i * (1+r)^(N-1-i)) 計算，而不是
    sum(cf_i / (1+r)^i)——後者在 N（月數）很大、r 趨近 -1 時，
    (1+r)^i 會下溢為浮點 0.0，導致除以零。兩種寫法在數學上等價
    （NPV_原始 = NPV_多項式 / (1+r)^(N-1)，(1+r)^(N-1) 在搜尋範圍內恆正），
    根的位置完全相同，多項式形式只是換一種算法避開下溢除以零。"""
    n = len(cashflows)

    def npv_poly(r):
        total = 0.0
        for i, cf in enumerate(cashflows):
            total += cf * ((1.0 + r) ** (n - 1 - i))
        return total

    lo, hi = -0.99, 1.0
    f_lo, f_hi = npv_poly(lo), npv_poly(hi)
    while f_lo * f_hi > 0 and hi < 50.0:
        # 找不到變號區間，逐步擴大上界嘗試（不擴大下界，避免逼近 -1 的下溢問題）
        hi *= 2
        f_hi = npv_poly(hi)
    if f_lo * f_hi > 0:
        raise ValueError("IRR 無法收斂：cashflow 兩端 NPV 同號")
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv_poly(mid)
        if abs(f_mid) < 1e-6:
            return mid
        if f_lo * f_mid < 0:
            hi = mid
            f_hi = f_mid
        else:
            lo = mid
            f_lo = f_mid
    return (lo + hi) / 2


def cmd_compute(args):
    rows = load_raw()
    if not rows:
        print("沒有資料，請先執行 fetch。", file=sys.stderr)
        sys.exit(1)

    # 依月分組
    from collections import defaultdict
    by_month = defaultdict(list)  # (year, month) -> list of (date, value)
    for d, v in rows:
        y, m = int(d[0:4]), int(d[5:7])
        by_month[(y, m)].append((d, v))

    months_sorted = sorted(by_month.keys())

    # ---- 算式 A：逐月統計 ----
    monthly_stats = []
    for (y, m) in months_sorted:
        vals = [v for _, v in by_month[(y, m)]]
        dates = [d for d, _ in by_month[(y, m)]]
        monthly_stats.append({
            "year": y, "month": m,
            "first_date": dates[0], "last_date": dates[-1],
            "n_days": len(vals),
            "max": max(vals), "min": min(vals),
            "avg": sum(vals) / len(vals),
            "first_close": vals[0], "last_close": vals[-1],
        })

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(STATS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["year", "month", "first_date", "last_date", "n_days",
                    "max", "min", "avg", "first_close", "last_close"])
        for s in monthly_stats:
            w.writerow([s["year"], s["month"], s["first_date"], s["last_date"],
                        s["n_days"], round(s["max"], 2), round(s["min"], 2),
                        round(s["avg"], 2), round(s["first_close"], 2), round(s["last_close"], 2)])

    monthly_invest = 10000.0
    n_months = len(monthly_stats)
    final_index_value = monthly_stats[-1]["last_close"]
    total_invested = monthly_invest * n_months

    scenarios = {}
    for key in ("max", "avg", "min"):
        total_units = 0.0
        for s in monthly_stats:
            price = s[key]
            total_units += monthly_invest / price
        final_value = total_units * final_index_value
        total_return = final_value / total_invested - 1.0

        cashflows = [-monthly_invest] * n_months
        cashflows[-1] += final_value  # 最後一個月同時投入並贖回全部
        m_irr = monthly_irr(cashflows)
        annual_irr = (1.0 + m_irr) ** 12 - 1.0

        scenarios[key] = {
            "total_units": total_units,
            "final_value": final_value,
            "total_return": total_return,
            "annual_irr": annual_irr,
        }

    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "n_months", "monthly_invest", "total_invested",
                    "final_index_value", "final_value", "total_return_pct", "annual_irr_pct"])
        for key, label in (("max", "buy_at_monthly_high"), ("avg", "buy_at_monthly_avg_close"), ("min", "buy_at_monthly_low")):
            r = scenarios[key]
            w.writerow([label, n_months, monthly_invest, total_invested,
                        round(final_index_value, 2), round(r["final_value"], 2),
                        round(r["total_return"] * 100, 4), round(r["annual_irr"] * 100, 4)])

    print("=== 算式 A：定期定額 %d 個月, 每月 %.0f 元, 樣本 %s ~ %s ===" % (
        n_months, monthly_invest, monthly_stats[0]["first_date"], monthly_stats[-1]["last_date"]))
    print("期末指數值 (最後交易日收盤): %.2f  |  總投入: %.0f 元" % (final_index_value, total_invested))
    for key, label in (("max", "買在當月最高"), ("avg", "買在當月均價"), ("min", "買在當月最低")):
        r = scenarios[key]
        print("[%s] 期末總資產: %.0f 元 | 總報酬率: %.2f%% | 年化報酬率(IRR): %.2f%%" % (
            label, r["final_value"], r["total_return"] * 100, r["annual_irr"] * 100))

    # ---- 算式 B：逐年最大跌幅 vs 全年報酬 ----
    by_year = defaultdict(list)
    for d, v in rows:
        y = int(d[0:4])
        by_year[y].append((d, v))

    years_sorted = sorted(by_year.keys())
    yearly_records = []
    prev_end = None   # 前一年最後一個收盤：曆年報酬的標準起點（2003 年沒有，退回當年第一個收盤）
    for y in years_sorted:
        series = by_year[y]  # already date-sorted overall, but re-sort just in case
        series.sort(key=lambda x: x[0])
        vals = [v for _, v in series]

        # 年內最大跌幅：peak 在 trough 之前，跌幅 = (peak-trough)/peak，取最大值
        max_drawdown = 0.0
        peak = vals[0]
        for v in vals:
            if v > peak:
                peak = v
            dd = (peak - v) / peak
            if dd > max_drawdown:
                max_drawdown = dd

        base = prev_end if prev_end is not None else vals[0]
        year_return = vals[-1] / base - 1.0          # 2026-09-11 起改用前一年底收盤為基準（曆年報酬）
        yearly_records.append({
            "year": y, "n_days": len(vals),
            "first_close": vals[0], "last_close": vals[-1],
            "prev_end_close": prev_end,
            "max_drawdown_pct": max_drawdown * 100,
            "year_return_pct": year_return * 100,
        })
        prev_end = vals[-1]

    with open(YEARLY_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["year", "n_days", "first_close", "last_close", "prev_end_close", "max_drawdown_pct", "year_return_pct"])
        for r in yearly_records:
            w.writerow([r["year"], r["n_days"], round(r["first_close"], 2), round(r["last_close"], 2),
                        "" if r["prev_end_close"] is None else round(r["prev_end_close"], 2),
                        round(r["max_drawdown_pct"], 2), round(r["year_return_pct"], 2)])

    avg_dd = sum(r["max_drawdown_pct"] for r in yearly_records) / len(yearly_records)
    n_positive = sum(1 for r in yearly_records if r["year_return_pct"] > 0)
    n_total = len(yearly_records)

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n_years", "n_positive_years", "avg_max_drawdown_pct"])
        w.writerow([n_total, n_positive, round(avg_dd, 2)])

    print("\n=== 算式 B：逐年最大跌幅 vs 全年報酬 (%d ~ %d 年, 共 %d 個日曆年) ===" % (
        years_sorted[0], years_sorted[-1], n_total))
    print("平均年內最大跌幅: %.2f%%" % avg_dd)
    print("全年報酬為正的年數: %d / %d" % (n_positive, n_total))
    print("\n逐年明細已寫入 %s" % YEARLY_CSV)
    print("逐月統計已寫入 %s" % STATS_CSV)
    print("算式 A 結果已寫入 %s" % RESULTS_CSV)
    print("算式 B 摘要已寫入 %s" % SUMMARY_CSV)


def main():
    parser = argparse.ArgumentParser(description="TWSE 發行量加權股價報酬指數 DCA 自算工具")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_fetch = sub.add_parser("fetch", help="逐月抓取 MFI94U 資料")
    p_fetch.add_argument("--start", required=True, help="起始年月 YYYY-MM，例如 2003-01")
    p_fetch.add_argument("--end", required=True, help="結束年月 YYYY-MM，例如 2025-12")
    p_fetch.set_defaults(func=cmd_fetch)

    p_compute = sub.add_parser("compute", help="讀取已抓的 CSV，計算算式 A / B")
    p_compute.set_defaults(func=cmd_compute)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
