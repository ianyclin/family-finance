# 補充查證：主動基金輸給指數的比例（SPIVA）

查證日期：2026-09-07
查證員角色：只核對數字與來源，不下結論、不做投資建議。

## 查證方法與過程紀錄

1. `spglobal.com` 的 SPIVA PDF 直接抓取一律回 403（已用 `curl -sIL` 與 WebFetch 各測一次，兩者皆 403，符合已知限制）。
2. 改用 `http://archive.org/wayback/available?url=...` 查詢，找到三份報告的存檔快照，用 `curl` 下載 PDF 到本機後用 Read 工具原文讀取（等同直接打開原始 PDF，非轉述）：
   - SPIVA U.S. Scorecard Year-End 2018（存檔時間戳 20250504135256）
   - SPIVA U.S. Scorecard Year-End 2024（存檔時間戳 20251205141232）
   - SPIVA Asia Ex-Japan Scorecard Year-End 2024（存檔時間戳 20250707210638）
3. 三份 PDF 都完整讀到全文（含 Report 表格與 Glossary／Appendix），數字直接抄自表格，非估算。
4. 本次共完成：2 次 WebSearch、2 次 spglobal.com 直接 WebFetch（皆 403）、3 次 wayback availability 查詢、3 次 PDF 下載、3 次 PDF 讀取。抓取總數遠低於 30 次上限。
5. 未查到 SPIVA 有獨立的「Taiwan-only」報告；台灣數字目前只出現在《SPIVA Asia Ex-Japan Scorecard Year-End 2024》這份區域報告裡（該報告本身第一頁就標注 "For use with institutions only, not for use with retail investors" — 機構專用，非給散戶的公開版本，見下方備註）。

---

## 一、核對作者提供的 IFA.com 轉繪圖（Year-End 2018，15 年期，2004–2018）

作者素材聲稱的八個數字 vs. 原始報告 **Report 1: Percentage of U.S. Equity Funds Outperformed by Benchmarks**（15-YEAR 欄，此欄位語意是「輸給指數的基金比例」——SPIVA 表格標題雖寫 outperformed by benchmarks，數字本身就是underperformance rate，即"outperformed BY the index"＝被指數打敗）：

| 主題 | 作者素材數字 | SPIVA 原文 15 年數字 | 差異 | 信心等級 |
|---|---|---|---|---|
| 大型成長股 | 95% | 94.59% (Large-Cap Growth Funds, vs S&P 500 Growth) | 四捨五入後相符 | verified |
| 大型核心 | 92% | 92.09% (Large-Cap Core Funds, vs S&P 500) | 相符 | verified |
| 大型價值 | 79% | 79.33% (Large-Cap Value Funds, vs S&P 500 Value) | 相符 | verified |
| 不動產 | 86% | 86.21% (Real Estate Funds, vs S&P United States REIT) | 相符 | verified |
| 小型成長 | 98% | 98.17% (Small-Cap Growth Funds, vs S&P SmallCap 600 Growth) | 相符 | verified |
| 小型核心 | 97% | 97.44% (Small-Cap Core Funds, vs S&P SmallCap 600) | 相符 | verified |
| 小型價值 | 94% | 93.51% (Small-Cap Value Funds, vs S&P SmallCap 600 Value) | 四捨五入後相符 | verified |
| 全體美國股票基金 | 89% | 88.97% (All Domestic Funds, vs S&P Composite 1500) | 相符 | verified |

- 來源機構：S&P Dow Jones Indices LLC
- 原始網址：https://www.spglobal.com/spdji/en/documents/spiva/spiva-us-year-end-2018.pdf（403，經由 wayback 存檔 http://web.archive.org/web/20250504135256/https://www.spglobal.com/spdji/en/documents/spiva/spiva-us-year-end-2018.pdf 讀取原文）
- 以此為準：SPIVA U.S. Scorecard Year-End 2018, Report 1, 15-YEAR 欄
- 信心等級：verified（已打開原始 PDF 核對表格）
- 原文引述：報告內文摘要句——
  > "Over the long-term investment horizon, such as 10 or 15 years, 80% or more of active managers across all categories underperformed their respective benchmarks."
- 備註：IFA.com 的圖是「轉繪」，作者拿到的八個數字本身與 SPIVA 原始表格高度吻合（誤差都在四捨五入範圍內，即 SPIVA 用兩位小數，IFA 圖表用整數）。可以放心引用 SPIVA 原始數字，不必再引 IFA 頁面本身當數字來源（IFA 只能算「存在性線索」，已依規則不採用它當出處）。

---

## 二、最新版 SPIVA U.S.（Year-End 2024）：大型股與全體美國股票基金的 10、15、20 年輸給指數比例

來源：SPIVA U.S. Scorecard Year-End 2024，Report 1a: Percentage of U.S. Equity Funds Underperforming Their Benchmarks (Based on Absolute Return)

| 類別 | 比較指數 | 10 年 | 15 年 | 20 年 |
|---|---|---|---|---|
| All Domestic Funds（全體美國股票基金） | S&P Composite 1500 | 89.70% | 93.23% | 94.11% |
| All Large-Cap Funds（全體大型股基金） | S&P 500 | 84.34% | 89.50% | 91.99% |

- 來源機構：S&P Dow Jones Indices LLC
- 原始網址：https://www.spglobal.com/spdji/en/documents/spiva/spiva-us-year-end-2024.pdf（403，經由 wayback 存檔 http://web.archive.org/web/20251205141232/https://www.spglobal.com/spdji/en/documents/spiva/spiva-us-year-end-2024.pdf 讀取原文）
- 以此為準：SPIVA U.S. Scorecard Year-End 2024, Report 1a
- 信心等級：verified
- 原文引述：
  > "Over the 15-year period ending December 2024, there were no categories in which a majority of active managers outperformed."
  > "In our largest and most closely watched comparison, 65% of all active large-cap U.S. equity funds underperformed the S&P 500®, worse than the 60% rate observed in 2023 and slightly above the 64% average annual rate reported over the 24-year history of our SPIVA Scorecards."（此為 1 年期數字，附上供對照，不是 10/15/20 年）
- 備註：這是「絕對報酬」版（Report 1a）；2024 版新增了「風險調整後報酬」版（Report 1b），15 年期 All Domestic Funds 是 97.99%、All Large-Cap Funds 是 98.13%，比絕對報酬版更高，兩個版本口徑不同，若要引用建議註明是哪一種算法。

### 生存者偏差（survivorship bias）方法論原句

2024 版 Appendix B Glossary 的 "Survivorship Bias" 條目原文（與 2018 版幾乎逐字相同，只有極小用詞差異）：

> "Many funds might liquidate or merge during a period of study. This usually occurs due to continued poor performance by the fund. Therefore, if index returns were compared to fund returns using only surviving funds, the comparison would be biased in favor of the fund category. These reports remove this bias by (a) using the entire investment opportunity set, made up of all funds in that particular category at the outset of the period, as the denominator for outperformance calculations, (b) explicitly showing the survivorship rate in each category and (c) constructing peer average return series for each category based on all available funds at the outset of the period."

白話：已清算或合併消失的基金，**照樣算在一開始的母體（分母）裡**，且被視為"沒有打敗指數"（因為多半是績效差才被清算/合併）。只算還活著的基金會高估主動基金的表現，SPIVA 用這個辦法修正倖存者偏差。

- 來源機構：S&P Dow Jones Indices LLC
- 原始網址：同上（2024 版）
- 以此為準：SPIVA U.S. Scorecard Year-End 2024, Appendix B: Glossary, "Survivorship Bias" 段
- 信心等級：verified
- 補充數字（15 年期存活率，Report 2）：All Domestic Funds 期初 2,938 檔基金，15 年後只剩 49.49% 還存在（Survivorship）；All Large-Cap Funds 期初 1,067 檔，15 年存活率 48.17%。這代表超過一半的基金在 15 年內消失，而這些消失的基金全部被計入"輸家"。

---

## 三、SPIVA Asia Ex-Japan Year-End 2024：台灣主動基金數字

**重要備註（信心等級標註前必須先講）**：這份報告封面與每一頁頁尾都寫 **"For use with institutions only, not for use with retail investors"**（僅供機構使用，不得用於散戶／一般投資人）。也就是說 S&P DJI 官方目前沒有對外公開發布給一般讀者的「台灣版 SPIVA」，這份是 2024 年末才首次推出的區域報告（Asia Ex-Japan，涵蓋大中華、韓國、東南亞），台灣只是其中一個子類別，方法論上也用 Morningstar 資料而非美國版慣用的 CRSP 資料庫。若要在文件裡引用，建議加註「機構專用報告」這個限制。

### Report 1a: Percentage of Asia Ex-Japan Funds Underperforming Their Benchmarks（絕對報酬）

| 類別 | 基金註冊地 | 比較指數 | 1 年 | 3 年 | 5 年 |
|---|---|---|---|---|---|
| Taiwan Large-Cap（台灣大型股基金） | 台灣 | S&P Taiwan BMI | 100% | 80% | 84% |
| Taiwan Mid-/Small-Cap（台灣中小型股基金） | 台灣 | S&P Taiwan MidSmallCap | 10% | 53% | 44% |

- 來源機構：S&P Dow Jones Indices LLC（資料源自 Morningstar）
- 原始網址：https://www.spglobal.com/spdji/en/documents/spiva/spiva-asia-ex%20japan-year-end-2024.pdf（403，經由 wayback 存檔 http://web.archive.org/web/20250707210638/https://www.spglobal.com/spdji/en/documents/spiva/spiva-asia-ex%20japan-year-end-2024.pdf 讀取原文）
- 以此為準：SPIVA Asia Ex-Japan Scorecard Year-End 2024, Report 1a
- 信心等級：verified
- 原文引述：
  > "Conversely, all Taiwan Large-Cap funds fell short of the S&P Taiwan BMI's impressive 35.3% return."（2024 單年：台灣大型股基金 100% 輸給指數，因為指數當年漲 35.3% 太猛）
  > "Taiwan Mid-/Small-Cap funds excelled, with 90% of funds outperforming the S&P Taiwan MidSmallCap"（即 1 年期只有 10% 輸，90% 贏，這是報告特別點名的例外亮點）
- 備註（重要，避免誤讀）：
  1. 台灣大型股基金 1 年期 100% 輸給指數，是 **2024 這單一年**的極端結果（該年 S&P Taiwan BMI 大漲 35.34%，主動基金平均只有 19.81%~18.92%，落後幅度很大），**不是長期常態**；3 年期已回落到 80%，5 年期 84%。不要把「100%」誤植為長期或穩定數字。
  2. 台灣中小型股基金是這份報告裡少數「主動打敗指數」的例外類別（1 年期只 10% 輸、5 年期 44% 輸，代表 5 年期有 56% 的台灣中小型主動基金贏過指數）——這點與美國版「幾乎全部類別長期都輸」的結論明顯不同，值得在文件裡特別註明是例外，不要套用美股的結論到台股。
  3. 該報告目前只到 5 年期，沒有 10/15/20 年期的台灣數字（因為是 2024 年才首次發布，且台灣大型股基金期初只有 19–29 檔基金，樣本數遠小於美國）。
  4. 台灣基金存活率極高：1 年期 100%、3 年期 100%（Taiwan Large-Cap）／97.6%（Taiwan Mid-/Small-Cap）、5 年期 94.7%／97.6%，遠高於美國同期存活率（美國 15 年期存活率常在 40–50%），代表台灣主動基金業還沒經歷過大規模的長期倖存者偏差修正考驗，這份數字的「長期」意義有限。
  5. 找不到 SPIVA 有單獨的「Taiwan-only」正式報告；本節數字全部來自這份區域合併報告，且該報告明示是機構專用、不對散戶公開，這點請在文件中一併說明來源限制。

---

## 查證總結（給作者拍板用）

| 待確認事項 | 結論 |
|---|------|
| IFA.com 圖表八個數字是否忠實反映 SPIVA 2018 原始報告？ | 是，八個數字全部核對通過（verified），誤差僅四捨五入 |
| 最新（2024）美國大型股/全體股票基金 10/15/20年輸給指數比例？ | 10年 84.34%/89.70%；15年 89.50%/93.23%；20年 91.99%/94.11%（大型股/全體，verified） |
| SPIVA 生存者偏差原句？ | 已逐字抄錄 2024 版 Appendix B（與 2018 版幾乎相同），verified |
| 台灣主動基金數字？ | 有，但只到 SPIVA Asia Ex-Japan 2024（首次發布、機構專用、僅到 5 年期）；台灣大型股長期落後但中小型股是例外，verified |


## 2026-09-11 更新：Year-End 2025 報告

- 來源：https://web.archive.org/web/20260909171903/https://www.spglobal.com/spdji/en/documents/spiva/spiva-us-year-end-2025.pdf（網路檔案館 2026-09-09 存檔之官方 PDF，46 頁，「Data as of Dec. 31, 2025」；spglobal 直連仍回 Error）。verified。
- Report 1a（絕對報酬版）All Large-Cap Funds vs S&P 500：1 年 78.78、3 年 66.84、5 年 88.96、10 年 85.59、15 年 89.93、20 年 92.89。
- Report 2 15-Year All Large-Cap Funds：期初 1,082 檔、Survivorship 50.55、Style Consistency 54.53。
- 摘要句逐字：「79% of all active large-cap U.S. equity funds underperformed the S&P 500, worse than the 65% rate observed in 2024 and the fourth-worst year for active large-cap managers over the 25-year history of our SPIVA Scorecards.」
- 手冊第 8 章、第 17 章與專篇第 3 節已換成這組數字；舊值 84.34／89.50／91.99／48.17 留在本檔前段作對照。
