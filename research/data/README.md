# research/data

| 檔案 | 進 repo？ | 來源 |
|---|---|---|
| `taiex_tr_monthly_raw.csv` | 是 | 證交所發行量加權股價報酬指數，逐日收盤（2003-01-02 起）。 |
| `shiller_sp_monthly.csv` | 是 | Robert Shiller 公開資料（耶魯）。 |
| `damodaran_histret.xls` | **否**（.gitignore 排除） | Damodaran（NYU Stern）Historical Returns on Stocks, Bonds and Bills。要重算 `asset_rotation` 的人，自己到 <https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html> 下載 histretSP.xls，改名成 `damodaran_histret.xls` 放在這裡。需要 `xlrd`（`pip install xlrd`）才讀得了 .xls。 |

第三方原始檔一律不進 repo（和 `research/pdf/`、`research/orig/` 同一個慣例）：本書只引用數字、自己重畫，不轉載檔案或圖。
| `sp500tr_monthend_2023_2026.csv` | 是 | S&P 500 Total Return Index（^SP500TR）各月最後一個交易日收盤，2023-01～2026-08，2026-09-22 由 Yahoo Finance 圖表 API 抓取。用途：把 Shiller 的含息月序列（股利資料止於 2023-06）用月報酬串接延長到 2026-08。口徑差異：Shiller 的價格是「當月每日收盤平均」、股利是年率÷12；SP500TR 是月底收盤、股利實際再投入。串接點（2023-06）兩邊各自的 1–6 月累積報酬相差約 0.5 個百分點（Shiller 約 10.5%、SP500TR 約 10.0%——差別主要來自平均價 vs 月底價的口徑），對 30 年年化的影響在 0.1 個百分點以內；圖說要寫明「2023 年 7 月以後用 S&P 500 總報酬指數串接」。 |
| `taiex_price_monthend_1990_2025.csv` | 是 | 臺灣證券交易所「每日市場成交資訊」（`https://www.twse.com.tw/rwd/zh/afterTrading/FMTQIK?date=YYYYMM01&response=json`）逐月抓下來，只留每月最後一個交易日的收盤，另存當月收盤最高／最低那一天，2026-09-22 抓取（共 432 個月，1990-01～2025-12）。**發行量加權股價指數，是價格指數、不含股利**（含息的報酬指數官方只從 2003 年起提供，見上面 `taiex_tr_monthly_raw.csv`）。用途：第 8 節台股長線圖要看到 1990 年那一段。注意：證交所線上的開高低收（`MI_5MINS_HIST`）只到 1999-01-05，所以 1990-02-12 盤中 12,682 點那個常被引用的數字查不到，本檔與圖一律用收盤價（1990 年最高的收盤是 1990-02-10 的 12,495.34）。 |
