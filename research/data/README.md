# research/data

| 檔案 | 進 repo？ | 來源 |
|---|---|---|
| `taiex_tr_monthly_raw.csv` | 是 | 證交所發行量加權股價報酬指數，逐日收盤（2003-01-02 起）。 |
| `shiller_sp_monthly.csv` | 是 | Robert Shiller 公開資料（耶魯）。 |
| `damodaran_histret.xls` | **否**（.gitignore 排除） | Damodaran（NYU Stern）Historical Returns on Stocks, Bonds and Bills。要重算 `asset_rotation` 的人，自己到 <https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html> 下載 histretSP.xls，改名成 `damodaran_histret.xls` 放在這裡。需要 `xlrd`（`pip install xlrd`）才讀得了 .xls。 |

第三方原始檔一律不進 repo（和 `research/pdf/`、`research/orig/` 同一個慣例）：本書只引用數字、自己重畫，不轉載檔案或圖。
