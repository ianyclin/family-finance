# 隔離人性 v6.3.1 連結檢查報告
測試日期：2026-09-25
HTML 檔：guide/index.html

## 總體統計
- **總網址數**：218
- **2xx 成功（200、202 等）**：203
- **3xx 轉址**：0
- **4xx 客戶端錯誤**：13
- **5xx 伺服器錯誤**：0
- **逾時（TIMEOUT）**：1
- **TLS 攔截**：0
- **其他錯誤**：1
- **非 2xx 總數**：15

## 非 2xx 狀態網址

- **403** | https://claude.ai/artifact/492iv4AuQeSHVPRN2XEC1E | 行 168 | 未找到節號
- **403** | https://www.ubs.com/content/dam/assets/wm/static/cio/documents/giry2026-summary-public.pdf | 行 554 | 第 4 節
- **406** | https://time.com/6916834/how-to-budget-60-30-10/ | 行 792 | 第 5 節
- **403** | https://www.simonandschuster.com/books/Unconventional-Success/David-F-Swensen/9780743228381 | 行 939 | 第 6 節
- **403** | https://www.spglobal.com/spdji/en/documents/spiva/spiva-us-year-end-2025.pdf | 行 939 | 第 6 節
- **403 (→ https://www.tandfonline.com/doi/full/10.1080/0015198X.2023.2188870)** | https://doi.org/10.1080/0015198X.2023.2188870 | 行 1631 | 第 7 節
- **curl: (92) HTTP/2 stream 1 was not closed cleanly: INTERNAL_…** | https://fred.stlouisfed.org/series/NASDAQCOM | 行 2895 | 第 8 節
- **403** | https://www.tandfonline.com/doi/full/10.1080/0015198X.2026.2657253 | 行 3186 | 第 12 節
- **403** | https://onlinelibrary.wiley.com/doi/10.1111/jofi.13183 | 行 3335 | 第 13 節
- **429 (→ https://www.pm-research.com/content/iijpormgmt/24/4/52?implicit-login=true)** | https://www.pm-research.com/content/iijpormgmt/24/4/52 | 行 3335 | 第 13 節
- **curl: (28) Operation timed out after 20009 milliseconds with…** | https://cemi.ehess.fr/docannexe/file/2780/tversjy_kahneman_advances.pdf | 行 3335 | 第 13 節
- **403** | https://www.nhi.gov.tw/ch/cp-4516-74b0f-2613-1.html | 行 4018 | 第 22 節
- **403** | https://www.journals.uchicago.edu/doi/abs/10.1086/380085 | 行 4045 | 第 23 節
- **403** | https://www.aaii.com/journal/199802/feature.pdf | 行 4275 | 第 24 節
- **403** | https://www.books.com.tw/products/0010800817 | 行 4275 | 第 24 節

## 總計
- 非 2xx 網址：15

## 補測（批 BZ 新增兩筆，主線 curl 2026-09-25）
- **200** | https://fcstock.fbs.com.tw/RegularWeb/Home/Index | 第 20 節（富邦證券：台股定期定額）
- **200** | https://rich01.com/dollar-cost-averaging-fee/ | 第 20 節（Mr.Market 市場先生：全台券商定期定額總整理）

這兩筆不在上面那次程式全掃的 218 個網址裡（當時還沒加進來源卡），是批 BZ 之後單獨 curl 的。加上這兩筆，來源卡裡的唯一網址是 209 個。
