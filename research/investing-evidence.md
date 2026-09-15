# 查證筆記：投資的實證證據與台灣可用的工具

查證日：2026-09-07。凡逐年變動的數字皆標「以何時為準」。此檔為研究員查證清單，非教學文件；每條標「事實／數字／來源機構／網址／以…為準／信心等級／備註」。

---

## 一、長期報酬

### 1.1 台灣加權股價報酬指數（含息）自 2003 年以來年化報酬率
- **事實**：台灣證交所「發行量加權股價報酬指數」自 2003/1/1 起編製。實際查詢官方資料 API：2003/01/02 指數為 **4,524.92**；2026/09/04 指數為 **107,486.11**。
- **換算**：期間 = 2003-01-02 至 2026-09-04 ≈ 23.67 年。總報酬倍數 = 107,486.11 ÷ 4,524.92 ≈ 23.75 倍。年化報酬率 = 23.75^(1/23.67) − 1 ≈ **14.3%／年**（含息，名目，未扣通膨）。
- **來源機構**：台灣證券交易所（TWSE）
- **網址**：https://www.twse.com.tw/rwd/zh/TAIEX/MFI94U?date=20030102&response=json （官方資料 API，經 curl 實際查詢；對應公開查詢頁 https://www.twse.com.tw/zh/indices/taiex/mfi94u.html ，頁面註明「本資訊自民國92年1月1日起開始提供」）
- **以…為準**：2026-09-04（最新交易日）
- **信心等級**：verified（原始數字直接向 TWSE 官方 API 查得，年化率為自行換算）
- **備註**：這 14.3% 的高年化率明顯受近幾年台股（尤其 AI／半導體相關族群）大漲影響，屬於「事後高點」的區間，換一個結束日期會有顯著差異；寫作時務必註明計算區間與資料來源，不要暗示這是「保證」或「常態」報酬率。

### 1.2 S&P 500 長期年化報酬率（自 1926 起）
- **事實**：「S&P 500 has returned 10.47% per year from 1926 to 2026（含股息再投資，名目）；換算通膨後實質約 7.29%／年」。
- **來源機構**：officialdata.org（採用 Robert Shiller 資料集 + 美國勞工統計局 CPI 資料）
- **網址**：https://www.officialdata.org/us/stocks/s-p-500/1926
- **以…為準**：計算至 2026 年底（officialdata.org 頁面所載區間）
- **信心等級**：likely（已實際開啟該頁面讀取內容，但該站是民間資料聚合站，非 S&P Dow Jones Indices 官方發布；1926–1957 年的成分股是 S&P 90 而非現行 500 檔，方法論上有斷點）
- **備註**：原文：「S&P 500 has returned 10.47% per year from 1926 to 2026, or 7.29% per year after adjusting for inflation.」

### 1.3 MSCI ACWI（全球股票）長期年化報酬率
- **事實**：MSCI ACWI 指數（美元計價，淨報酬）自 2000/12/29 成立以來至 2026/8/31，年化報酬率為 **7.48%／年**。
- **來源機構**：MSCI（原始發行機構官方 Index Factsheet）
- **網址**：https://www.msci.com/documents/10199/255599/msci-acwi-net.pdf
- **以…為準**：2026-08-31
- **信心等級**：verified（直接讀取 MSCI 官方 PDF factsheet 原始表格）
- **備註**：原文表格欄位：「Since Dec 29, 2000 ... MSCI ACWI 7.48」。同文件亦載 MSCI ACWI 近 10 年年化 12.58%、近 5 年 10.88%、近 3 年 20.48%，供對照近年與長期的差距。

---

## 二、主動 vs 被動：SPIVA 數據

### 2.1 美國大型股主動基金 10 年、15 年期輸給 S&P 500 的比例（SPIVA Year-End 2024）
- **事實**：截至 2024/12/31，美國大型股（All Large-Cap）主動基金：10 年期間 **84.34%** 跑輸 S&P 500；15 年期間 **89.50%** 跑輸 S&P 500。
- **來源機構**：S&P Dow Jones Indices「SPIVA U.S. Scorecard Year-End 2024」（數字經由二手站 Ritholtz 轉載並附精確百分比）
- **網址**：https://ritholtz.com/2025/05/the-data-on-active-large-cap-underperformance/ （原始 SPIVA PDF：https://www.spglobal.com/spdji/en/documents/spiva/spiva-us-year-end-2024.pdf ，多次嘗試該官方 PDF 皆遭 403 阻擋，未能直接開啟）
- **以…為準**：SPIVA Year-End 2024（涵蓋至 2024/12/31 的 10 年、15 年期間）
- **信心等級**：likely（實際開啟 ritholtz.com 頁面讀取到具體百分比，但未能親自打開 S&P 官方 PDF 核對；20 年期數字在多個二手來源中出現 92% 的說法，但未能在已開啟的頁面中直接核對到，故 20 年數字標為 unverified）
- **備註**：ritholtz 原文：「Over 10 years, 84.34% underperformed... Over 15 years, 89.50% of large-cap funds underperformed the S&P 500」。20 年期「92%」數字僅見於搜尋摘要（多篇二手文章重複），未實際打開任何一篇逐字核對其出處是否為 SPIVA 官方原文，故不列為 likely，列為 **unverified**，且可能與「20 年期全體美股基金（非僅大型股）」的統計混淆。
- **20 年期（unverified）**：搜尋摘要顯示「Over the last 20 years, about 92% of domestic funds underperformed their benchmarks」，但未親自開啟原始 SPIVA PDF 或可信轉載頁核實此數字是否專指大型股類別。

### 2.2 台灣（SPIVA Asia Ex-Japan）主動基金輸給指數比例
- **事實**：依搜尋摘要轉述之 2024 年 SPIVA Asia Ex-Japan 報告，台灣大型股類別 5 年期約僅 16% 主動基金能贏過台灣大型股基準；2025 年報告則稱台灣大型股主動基金約 48% 跑輸指數（52% 跑贏），台灣中小型股類別 2025 年約 96% 主動基金跑贏指數。
- **來源機構**：S&P Dow Jones Indices SPIVA Asia Ex-Japan（僅見於中文二手轉述文章，未開啟官方原始報告）
- **網址**：（未開啟原始 SPIVA Asia 報告；此段資訊來自 WebSearch 摘要，未點開任何單一網頁核對出處）
- **以…為準**：不明確（摘要混雜引用 2024 與 2025 兩個年度報告）
- **信心等級**：unverified
- **備註**：此段數字彼此之間有明顯矛盾（16% vs 52%），且未查到單一可核實網址，建議在正文中避免引用具體百分比，或先取得 SPIVA Asia Ex-Japan 官方 PDF 後再用。

---

## 三、費用的影響

### 3.1 Morningstar：費用率是最可靠的報酬預測指標
- **事實**：Morningstar 研究員 Russel Kinnel 於 2016 年發表研究，發現在所有測試變數中，費用率（expense ratio）最能預測基金未來報酬；最低費用組基金的「成功機率」是最高費用組的 2 到 3 倍，此結論在幾乎所有資產類別與時間區間皆成立。
- **來源機構**：Morningstar（Russel Kinnel）
- **網址**：https://www.evidenceinvestor.com/post/fees-are-the-most-reliable-predictor-of-future-returns （二手轉述頁；嘗試直接開啟 Morningstar 原始文章 https://www.morningstar.com/funds/fund-fees-predict-future-success-or-failure 遭 403 阻擋，未能打開）
- **以…為準**：2016 年原始研究
- **信心等級**：likely（未親自打開 Morningstar 官方頁面，僅由 WebSearch 摘要與轉載頁得到一致敘述）
- **備註**：轉述原文：「The cheapest funds were at least two to three times more likely to succeed than the priciest funds... the lowest-cost U.S. equity funds succeeded three times as often as the highest-cost funds.」

### 3.2 1% 費用長期侵蝕範例（自行試算，非引用單一機構示例）
- **事實**：以每月投入 5,000 元、年化報酬 6%、投資 30 年為例：
  - 年化 6%（無 1% 額外費用）：終值 ≈ NT$5,022,600（公式與細節見第七節）
  - 若同一組合每年多負擔 1% 費用（即實得年化降為 5%），終值改為：月利率 r=0.05/12≈0.004167，n=360，(1+r)^360≈4.4677，FV=5000×(4.4677−1)/0.004167≈5000×832.3≈NT$4,161,500
  - 兩者差距 ≈ NT$861,100，即單純多 1% 年費，30 年下來終值少了約 17%。
- **來源機構**：本檔自行以複利公式計算（非直接引用 Vanguard 或 SEC 的既有示例圖表）
- **網址**：（自行計算，無外部網址；計算式見第七節）
- **以…為準**：不適用（純數學試算）
- **信心等級**：verified（公式本身可驗算），但**非**題目要求的「Vanguard 或 SEC 官方示例」——嘗試搜尋 SEC 官方 1% 費用示例未能在時間內找到並開啟其原始頁面，故此項以自算替代，請作者知悉此為替代方案而非直接引用官方示例。
- **備註**：SEC 投資人教育網站（investor.gov）過去有「費用計算器」與「費用如何侵蝕報酬」的說明頁，但本次查證未能實際開啟其網址核對現況，屬待補項目。

---

## 四、行為落差（Behavior Gap）

### 4.1 Morningstar「Mind the Gap」2025 年版
- **事實**：Morningstar 2025 年版 Mind the Gap 研究指出，若基金投資人 2015–2024 年間完全不做任何交易（buy-and-hold），年化報酬可達 8.2%；但因投資人實際進出場時機不佳，實際年化報酬僅 7.0%，落差（Return Gap）約 **1.2 個百分點／年**，相當於同期基金報酬的約 15%。
- **來源機構**：Morningstar
- **網址**：https://www.cnbc.com/2025/10/27/morningstar-research-investors-lose-out-on-mutual-fund-etf-returns.html （轉述 Morningstar 原始研究；嘗試直接開啟 Morningstar 原頁 https://www.morningstar.com/business/insights/research/mind-the-gap 遭 403 / 空白內容，未能打開）
- **以…為準**：涵蓋期間 2015–2024
- **信心等級**：likely（CNBC 報導引用具體數字，但未能親自打開 Morningstar 官方報告核對；且已知有學術論文對此方法論提出質疑，見備註）
- **備註**：轉述原文：「if mutual fund investors had made no trades over the period 2015 to 2024, their return would have been 8.2%... investors' actual return was only 7.0%... equivalent to around 15% of those funds' gains over that span.」另有學術文章「Bad Timing Does Not Cost Investors 15% of Their Funds' Returns」對 Morningstar 方法論提出反駁，建議作者知悉此爭議存在，不要把 15% 寫成無爭議的定論。

---

## 五、定期定額 vs 單筆投入

### 5.1 Vanguard 2012 年研究：單筆投入約 2/3 時間勝出
- **事實**：Vanguard 2012 年 7 月研究比較美、英、澳三個市場的歷史數據（美 1926–2011、英 1976–2011、澳 1984–2011，滾動 10 年期），發現單筆投入（LSI）分別約 67%（美）、67%（英）、66%（澳）的期間勝過分 12 個月投入的定期定額（DCA）。「平均超額報酬約 1.5%～2.4%」與「DCA 拉長到 36 個月、LSI 勝率提高到近 90%」兩句在第 9 章來源條目（src-09-7）中查無依據，回推不到原始出處，不得引用；期間與勝率數字已依第 9 章來源訂正。（2026-09-07 依第 9 章來源同步）
- **來源機構**：Vanguard Research
- **網址**：https://sccaweb.org/resource/dollar-cost-averaging-vs-lump-sum-investing/ （轉述頁；嘗試直接開啟 Vanguard 原始 PDF https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf ，PDF 已下載但為 2023 年後續研究版本且內容為加密壓縮流無法直接讀取文字，未能核對逐字原文）
- **以…為準**：2012 年 7 月原始研究（後續 Vanguard 於 2023 年 2 月又發布过一篇同主題新研究，需注意版本）
- **信心等級**：likely（未能親自從 Vanguard 官方文件中逐字核對百分比，僅由二手轉述頁取得一致數字）
- **備註**：本次也嘗試打開 Vanguard 2023 年後續研究 PDF（「Cost averaging: invest now or temporarily hold your cash?」），已下載到本機但因 PDF 為圖片/加密流無法擷取文字內容，未能核對其是否更新了 2012 年的 2/3 這個數字。若要引用「2/3」這個具體數字，建議之後用可讀取的方式（例如另存 txt 或用 PDF 工具）重新核對 Vanguard 官方原文。

---

## 六、提領率（Safe Withdrawal Rate）

### 6.1 Bengen 1994 原始「4% 法則」
- **事實**：William Bengen 於 1994 年 10 月在《Journal of Financial Planning》發表〈Determining Withdrawal Rates Using Historical Data〉，以 1926–1963 年間各 30 年期、股債各半（美國大型股＋中期公債）組合回測，得出退休第一年提領約 **4%（精確計算原為 4.15%，後續文獻常引用為 4.2%）**、其後每年依通膨調整提領金額，在 30 年期間有很高機率（原始研究語境下）不會將本金提前用盡。Bengen 本人後續研究曾將建議上修至約 4.7%。
- **來源機構**：Journal of Financial Planning（原始論文），本次查證僅讀到二手轉述
- **網址**：https://finance.yahoo.com/news/4-rule-1994-original-author-120000250.html （轉述頁；未能開啟 1994 年原始期刊論文全文，該論文無公開免費全文連結）
- **以…為準**：1994 年原始研究；後續修正見備註
- **信心等級**：likely（多篇轉述互相印證細節一致，但未讀到原始期刊全文，「4.15%」「4.2%」「90% 機率」等具體數字存在轉述間的細微差異，需在正文中謹慎處理，避免給出過度精確的單一數字）
- **備註**：轉述原文：「Bengen found that if you withdrew no more than 4.2% of your portfolio in the first year of retirement, and adjusted the amount annually thereafter for inflation, there was a 90% chance your nest egg would last about 30 years.」另有轉述稱原始數學結果為 4.15%，出版時四捨五入才變成通稱的「4%法則」。

### 6.2 Morningstar 近年下修至 3.7%～3.9%
- **事實**：Morningstar「State of Retirement Income」研究：2024 年報告建議 2025 年起始安全提領率為 **3.7%**；2025 年報告（對應 2026 年）將此上修為 **3.9%**（適用於股票配置 30%～50%、以 30 年期、90% 成功機率為前提的「基準情境」）。
- **來源機構**：Morningstar
- **網址**：https://static.twentyoverten.com/5b5730126af0247efe4f2066/zT8sbuFanVR/Morningstar-2025-State-of-Retirement-Income.pdf （於 WebSearch 摘要中列出的鏡像連結；本次未能實際開啟 Morningstar 官方頁 https://www.morningstar.com/retirement/whats-safe-retirement-withdrawal-rate-2026 ，該頁回傳 403，未能逐字核對）
- **以…為準**：3.7% 適用 2025 年報告；3.9% 適用 2026 年報告（即題目所稱「近年下修」之後，2026 年最新版數字其實已從 3.7% 小幅上修至 3.9%，並非持續下修，這點與題目假設的方向不同，需向作者說明）
- **信心等級**：likely（未能打開 Morningstar 官方原文核對，僅由 WebSearch 摘要與多篇轉述互相印證）
- **備註**：**重要提醒**：題目描述「近年下修（Morningstar 3.7%～4%）」，但查證顯示 Morningstar 最新（2026年）數字是 **3.9%**、比前一年的 3.7% 是「上修」而非「下修」，方向與原始題目假設相反，請作者確認是否要更新文件敘述邏輯。

---

## 七、複利計算示例

### 7.1 72 法則
- **公式**：doubling time（年）≈ 72 ÷ 年化報酬率（%）
- **示例**：年化 6% → 72 ÷ 6 = **12 年**翻倍（近似值）
- **精確值對照**：以複利公式 FV=PV×(1+r)^t 反推，doubling time = ln(2) / ln(1+r) = ln(2)/ln(1.06) ≈ 0.6931 / 0.05827 ≈ **11.9 年**（可見 72 法則在 6% 左右誤差很小，約 1 個月）
- **信心等級**：verified（純數學公式，自行驗算）

### 7.2 每月投入 5,000 元、年化 6%、30 年
- **公式**（月複利年金終值，假設每月月底投入）：
  FV = PMT × [ (1+r)^n − 1 ] / r
  其中 PMT = 5,000（每月）、r = 6%/12 = 0.005（月利率）、n = 30×12 = 360（期數）
- **代入計算**：(1.005)^360 ≈ 6.0226
  FV = 5,000 × (6.0226 − 1) / 0.005 = 5,000 × 1,004.52 ≈ **NT$5,022,600**
- **對照**：30 年總投入本金 = 5,000 × 360 = NT$1,800,000；複利產生的成長部分 ≈ NT$3,222,600（約為本金的 1.8 倍）
- **信心等級**：verified（標準年金終值公式，自行代入計算；可用任何複利計算機覆核）
- **備註**：此為稅前、未扣任何投資成本的理論值，實際結果會因市場波動、費用率、稅負而不同；6% 是示範用的假設年化報酬率，不代表對任何特定商品的報酬承諾。

---

## 八、風險：歷史最大回撤與復原時間

### 8.1 2008 金融海嘯 — S&P 500
- **事實**：S&P 500 從 2007/10/9 收盤高點 1,565.15 點，跌至 2009/3/9 收盤低點 676.53 點，**峰谷跌幅約 56.8%（約 57%）**。指數直到 2013/3/28 才收在超越 2007 年高點的新高，即從高點起算約 5 年 5 個月才「解套」。
- **來源機構**：資料聚合站轉述（未見官方 S&P Dow Jones Indices 原始逐日數據頁面）
- **網址**：（此段來自 WebSearch 摘要，多篇二手文章數字一致，但本次未實際開啟任一原始股價資料庫頁面逐日核對）
- **以…為準**：2007-10-09 高點至 2009-03-09 低點；解套日 2013-03-28
- **信心等級**：likely
- **備註**：57% 跌幅與 5 年多解套時間為市場上被廣泛引用的共識數字，多個獨立來源互相印證。

### 8.2 2008 金融海嘯 — 台灣加權指數
- **事實**：台灣加權指數（不含息）從 2007/10 最高點約 9,859 點，跌至 2008/11 最低點約 3,955 點，**峰谷跌幅約 60%**；若只看 2008 單一年度（年初到年底），跌幅約 44%～46%。
- **來源機構**：中文財經媒體／部落格轉述（未開啟 TWSE 官方逐日歷史數據核對峰值與谷值的精確日期與點位）
- **網址**：（來自 WebSearch 摘要，未實際開啟單一原始網頁核對；可用本檔第 1.1 節已驗證可用的 TWSE 官方 API 之後再查證精確峰谷值與日期）
- **以…為準**：峰值約 2007/10，谷值約 2008/11
- **信心等級**：unverified（峰谷點位數字在不同轉述間略有差異，且未親自向 TWSE 官方 API 查證精確點位與日期）

### 8.3 2020 新冠疫情崩盤 — S&P 500
- **事實**：S&P 500 從 2020/2/19 收盤高點 3,386 點，5 週內跌至 2020/3/23 收盤低點 2,237 點，**跌幅約 34%**（另有來源稱約 33-34%），是史上最快的 30% 跌幅（約 22 個交易日）；其後**約 5 個月**即收復失土，是歷來重大股災中復原最快的一次。
- **來源機構**：資料聚合站與財經媒體轉述
- **網址**：（來自 WebSearch 摘要，未實際開啟單一原始頁面逐日核對）
- **以…為準**：2020-02-19 高點至 2020-03-23 低點
- **信心等級**：likely

### 8.4 2020 新冠疫情崩盤 — 台灣加權指數
- **事實**：台股從年初高點約 12,197 點（或轉述為 12,186 點），於 2020/3 跌至低點約 8,523 點，**波段跌幅約 30%**；約 8 週後觸底回升，是歷來復原最快的一次崩盤。
- **來源機構**：中文財經媒體轉述
- **網址**：（來自 WebSearch 摘要，未開啟單一原始頁面核對精確點位與日期；不同轉述文章的高點數字略有出入，12,197 vs 12,186）
- **以…為準**：2020 年初高點至 2020/3 低點
- **信心等級**：unverified（高點點位在轉述間不一致，需以 TWSE 官方歷史資料重新核對精確峰谷值）

---

## 九、台灣工具：ETF 費用率

### 9.1 元大台灣50（0050）
- **事實**：2025/1/23 金管會核准修正公開說明書後，經理費改為分級費率：規模 1,000 億以下收 0.15%、1,000～5,000 億收 0.10%、5,000 億～1 兆收 0.08%、超過 1 兆收 0.05%；保管費：1 兆以下收 0.03%、超過 1 兆收 0.025%。截至 2026/9/4 官網揭露之經理費約為 **0.0688%**（依當時規模加權計算後的實際費率）。
- **來源機構**：元大投信（YuantaETFs）官網
- **網址**：https://www.yuantaetfs.com/product/detail/0050/Basic_information
- **以…為準**：2026-09-04（官網查詢當下揭露之費率）
- **信心等級**：verified（直接開啟元大投信官方產品頁）
- **備註**：官網頁面未提供單一「總費用率」數字，總費用率需另外加計保管費、交易成本等，官網頁面本身未揭露此總和數字。

### 9.2 富邦台50（006208）
- **事實**：2025 年宣布調降並確立分級費率：經理費 0.05%～0.15%（依規模遞減）、保管費 0.025%～0.03%。依 2025/6/13 規模 2,329 億元估算，加權後經理費約 0.1215%。2024 全年整體費用率（含交易成本等）約占總規模 **0.23%**，歷史總費用率區間約在 0.23%～0.36% 之間。
- **來源機構**：財經媒體（經濟日報、商業周刊等）轉述富邦投信公告；未直接開啟富邦投信官網原始頁面
- **網址**：https://money.udn.com/money/story/5618/8828397 （轉述頁；未能直接開啟富邦投信官方產品頁核對）
- **以…為準**：2025/6/13 前後（調降公告時點）
- **信心等級**：likely
- **備註**：與 0050 相比，總費用率的 0.23%（006208, 2024全年）與 0050 官網揭露的經理費 0.0688%（僅經理費，不含保管費與交易成本）口徑不同，寫作時不可直接並列比較，需註明何者是「總費用率」、何者只是「經理費」。

### 9.3 元大台灣高股息（0056）
- **事實**：經理費採分級：規模 100 億以下收 0.40%、逾 100 億至 300 億收 0.34%、逾 300 億收 0.30%；保管費固定 **0.035%**。目前規模已逾 300 億，故經理費落在最低級距 0.30%，經理費加保管費合計約 0.335%。
- **來源機構**：元大投信（YuantaETFs）官網
- **網址**：https://www.yuantaetfs.com/product/detail/0056/Basic_information
- **以…為準**：查詢當下（2026-09-07 前後）
- **信心等級**：verified（直接開啟元大投信官方產品頁）
- **備註**：此為經理費＋保管費之和，非涵蓋交易成本的「總費用率」。

### 9.4 國泰永續高股息（00878）
- **事實**：經理費 0.25%，保管費已於 2024/7/10 調降至 0.03%（原 0.035%），兩者合計 0.28%。內扣總費用率呈階梯式逐年遞減：2021 年 0.57%、2022 年 0.50%、2023 年 0.46%、2024 年 0.42%。
- **來源機構**：財經媒體（經濟日報、Yahoo奇摩股市等）轉述國泰投信資料；嘗試直接開啟國泰投信官網 https://www.cathaysite.com.tw/ETF/detail/ECN?tab=basic_info 遭 403 阻擋，未能打開
- **網址**：https://money.udn.com/money/story/5618/8534022
- **以…為準**：2024 年度總費用率（最新可得的年度數字）
- **信心等級**：likely
- **備註**：00878 是查證清單中唯一有明確「逐年總費用率」歷史數字可引用的檔案，適合用來說明「內扣費用不只是官網寫的經理費+保管費」。

### 9.5 Vanguard VTI（全美股）
- **事實**：**費用率 0.03%**（As of June 30, 2026 官方 fact sheet 所載，as reported in the most recent prospectus）。
- **來源機構**：The Vanguard Group（官方 Fact Sheet PDF）
- **網址**：https://fund-docs.vanguard.com/F0970.pdf
- **以…為準**：2026-06-30
- **信心等級**：verified（直接讀取 Vanguard 官方 PDF 原始表格：「Expense ratio¹ 0.03%」）

### 9.6 Vanguard VOO（S&P 500）
- **事實**：費用率 **0.03%**（與 VTI 相同，Vanguard 官方多處公開資訊一致標示）。
- **來源機構**：Vanguard（本次僅由 WebSearch 摘要取得，未實際開啟 VOO 專屬官方 fact sheet PDF 核對）
- **網址**：（未開啟；建議之後直接查 https://investor.vanguard.com/investment-products/etfs/profile/voo 或其官方 fact sheet PDF 核對）
- **以…為準**：查詢當下
- **信心等級**：likely

### 9.7 Vanguard VT（全世界股票）
- **事實**：費用率 **0.06%**。
- **來源機構**：Vanguard（本次僅由 WebSearch 摘要及多個第三方站如 etf.com、Yahoo Finance 交叉印證，未實際開啟 Vanguard 官方 VT 頁面或 fact sheet 逐字核對）
- **網址**：（未開啟；建議查 https://investor.vanguard.com/investment-products/etfs/profile/vt ）
- **以…為準**：查詢當下
- **信心等級**：likely

### 9.8 Vanguard BND（美國整體債券市場）
- **事實**：費用率 **0.03%**。
- **來源機構**：Vanguard（嘗試開啟官方 fact sheet PDF https://workplace.vanguard.com/iippdf/pdfs/FS928R.pdf ，PDF 內容為加密圖層無法擷取文字，未能逐字核對；僅由 WebSearch 摘要與多個第三方站交叉印證）
- **網址**：（PDF 已下載但無法讀取內容；建議之後另外用可解析的方式重新核對）
- **以…為準**：查詢當下
- **信心等級**：likely

---

## 十、台灣券商複委託與海外券商稅務

### 10.1 複委託手續費一般行情
- **事實**：國內券商美股複委託手續費：電子下單約 0.1%～0.5%，人工下單約 0.5%～1%；多數券商設有最低手續費（約 US$20～35），但部分券商（群益、國泰、凱基等）已推出免低消或定期定額每筆僅 US$0.03 的優惠方案。
- **來源機構**：市場先生（rich01.com）等理財教學網站彙整（非官方數據，屬市場行情彙整）
- **網址**：https://rich01.com/what-sub-brokerage/
- **以…為準**：2026 年（文章自稱「2026年最新」）
- **信心等級**：likely（此為市場行情區間彙整，非單一官方公告數字，各券商實際費率請以其官網公告為準）

### 10.2 美國非居民股息預扣稅 30%
- **事實**：美國來源股利（dividends）支付給非居民外國人（NRA）須預扣 **30%**，除非有租稅協定降低稅率（台灣與美國無此類租稅協定，故台灣投資人一般適用 30% 全額）。
- **來源機構**：美國國稅局（IRS）
- **網址**：https://www.irs.gov/individuals/international-taxpayers/nra-withholding
- **以…為準**：現行規定（無到期日，屬長期穩定條文）
- **信心等級**：verified（直接開啟 IRS 官方頁面，原文：「Most types of U.S. source income received by a foreign person are subject to U.S. tax of 30%.」）

### 10.3 美國遺產稅：非居民外國人 6 萬美元免稅門檻
- **事實**：非居民外國人（NRNC）持有美國境內資產（含美股、美股 ETF），身故時若美國境內資產（加計特定生前贈與調整項目）超過 **US$60,000**，超過部分即需申報並可能課徵聯邦遺產稅（稅率最高**40%**——此稅率回推不到 IRS Form 706-NA 指示頁原文，標記為 unverified；第 9 章正文已刪除稅率，只寫 6 萬美元門檻），此 6 萬美元門檻**不隨通膨調整**。相較之下，美國公民/居民 2026 年的免稅額高達約 US$15,000,000。
- **來源機構**：美國國稅局（IRS），Form 706-NA 指示
- **網址**：https://www.irs.gov/instructions/i706na
- **以…為準**：現行規定（$60,000 門檻長期未變，非年度調整項目）
- **信心等級**：$60,000 門檻 verified（直接開啟 IRS 官方 Form 706-NA 指示頁面，原文：「The executor must file Form 706-NA if the date of death value of the decedent's U.S.-situated assets... exceeds the filing threshold of $60,000.」）；**40% 稅率 unverified**（未見於同一頁原文）（2026-09-07 依第 9 章來源同步）

---

## 待補／需要作者知悉的查證缺口

1. **SPIVA 20 年期大型股數字（92%）**：未能打開官方 PDF 或任何單篇逐字核對，暫列 unverified，正文若要引用建議先補查。
2. **SPIVA 官方 PDF 全面受阻**：本次多次嘗試直接開啟 spglobal.com 的 SPIVA 官方 PDF（year-end 2024、2025）皆遭 403 或重新導向到錯誤頁，只能透過二手轉述頁交叉核對，信心等級因此普遍降為 likely。
3. **Morningstar 官方頁面全面受阻**：Fund fees 研究原文、Mind the Gap 2025 原文、2026 年安全提領率頁面皆遭 403，只能靠二手轉述，且「Mind the Gap」的 15% 說法有學術論文提出方法論質疑（見 4.1 備註），建議正文附帶「有爭議」的但書。
4. **Morningstar 提領率方向與題目假設不符**：題目假設「近年下修」，但查證結果是 2026 年（3.9%）比 2025 年（3.7%）**上修**，需要作者確認要如何調整文件敘述邏輯（見 6.2 備註，此為最重要的一條待拍板項目）。
5. **Vanguard DCA vs LSI「2/3」數字**：官方 PDF 下載後因加密圖層無法讀取文字，僅能靠二手轉述頁核對，且不確定是否為 2012 年原版或 2023 年後續版本的數字。
6. **台股 2008／2020 崩盤精確峰谷點位與日期**：僅由中文財經媒體轉述取得，不同文章對高點點位（如 2020 年初 12,197 vs 12,186）有出入，尚未用本檔已驗證可用的 TWSE 官方 API（見 1.1 節方法）重新逐日核對，建議之後補查。
7. **SPIVA 台灣／亞洲數據自相矛盾**：搜尋摘要中 16% 與 52%／48% 的說法互相矛盾且分屬不同年度報告，未查到可核實的單一官方原始頁面，正文應避免引用具體百分比。
8. **SEC／Vanguard「1% 費用侵蝕」官方示例**：未能在時間內找到並開啟官方原始示例頁面，本檔以自行計算的替代示例代替（見 3.2），如需忠實呈現官方示例需再補查。
9. **VOO、VT、BND 費用率**：VTI 已用官方 PDF 逐字核對（verified），但 VOO／VT／BND 三檔僅由 WebSearch 摘要取得，未逐一開啟官方 fact sheet 核對文字內容，列為 likely。

---

## 補查 2026-09-07

> 對應總編輯點名的原大綱編號 24（SPIVA 美國大型股10/15年）、39／88（Bengen 1994原文）、80（Morningstar提領率方向）；其餘 25、26、27、29、30、31、81、82、85、86 因 spglobal.com／morningstar.com／financialplanningassociation.org 對WebFetch持續回傳403、或TWSE API本輪未及呼叫，未能完成，列於文末。

### 補24．SPIVA美國大型股基金10年、15年跑輸比例（截至2024年底）

- **事實／數字**：截至2024年12月31日止，**10年期**：84.34%的美國大型股主動基金跑輸S&P 500指數（僅15.66%跑贏）；**15年期**：89.50%跑輸（僅10.50%跑贏）；文中並指出「15年期沒有任何一個基金類別由多數主動經理人跑贏」。
- **來源機構**：轉引S&P Dow Jones Indices「SPIVA U.S. Scorecard Year-End 2024」報告數字之財經部落格
- **網址**：https://ritholtz.com/2025/05/the-data-on-active-large-cap-underperformance/ （The Big Picture／Barry Ritholtz，2025年5月29日發表，逐字引用SPIVA報告數字）
- **以…為準**：SPIVA U.S. Scorecard Year-End 2024（資料截至2024-12-31）
- **信心等級**：likely（本輪多次嘗試直接開啟 spglobal.com 官方SPIVA PDF與網頁，包括用curl偽裝瀏覽器UA下載，皆遭403 Forbidden封鎖，故改以已實際開啟、且逐字列出官方報告數字的財經評論網站作為信心等級likely的替代來源；此網站作者為知名指數投資評論者，逐字轉引SPIVA報告數字之可信度高，但**非**本報告直接開啟S&P官方原始PDF）
- **備註**：呼應原題目第24條「解決16% vs 52%矛盾」的指示——第8章應**只引用美國數字**（10年84.34%跑輸／15年89.50%跑輸），不使用任何台灣或亞洲類別的百分比（16%、48%、52%皆不用，理由見原研究檔已有的第2.2條備註）。第81條（16% vs 52%矛盾）與第82條（20年92%）維持原研究檔的「不使用」結論，本輪未找到可推翻此結論的新官方來源。

### 補39／88．Bengen（1994）原始論文的精確表述

- **事實／數字**：William Bengen於1994年10月在《Journal of Financial Planning》發表〈Determining Withdrawal Rates Using Historical Data〉，以1926年起、50%股票／50%債券配置，回測每一個可能起始年份的30年期間，得出的最壞情況（worst historical starting year，起始於1966年）可支撐的「最高安全提領率」（後人稱SAFEMAX）為**4.15%**；作者本人後續將其四捨五入通稱為「4%法則」。原始論文的核心陳述是「在最壞情況下仍可撐滿30年」的**保證性結論**，而非以蒙地卡羅模拟得出的「成功機率」百分比（如「90%成功率」這類表述**不是**1994年原始論文的用語，而是後續其他研究者用歷史回測資料重新包裝出的機率化說法）。
- **來源機構**：二手學術轉述文章（原始1994年FPA期刊PDF本輪嘗試開啟遭403 Forbidden，故以下列已實際開啟的轉述文章替代）
- **網址**：https://www.mcleanam.com/william-bengens-safemax/ （McLean Asset Management，逐字引用「With a 50/50 allocation for stocks and bonds, the SAFEMAX was 4.15%, and it occurred in 1966.」）
- **以…為準**：原始論文結論（1994年發表，數字本身不隨時間變動；後續1997年作者本人修正為4.3%、2006年修正為4.5%、2024年新書修正為4.7%，均為作者後續更新版本，非1994年原文）
- **信心等級**：likely（未能開啟FPA或Journal of Financial Planning官方原始PDF，僅以逐字引用「4.15%」「1966年」等具體細節的二手學術轉述頁作為來源；多篇獨立轉述互相一致，交叉驗證度高）
- **備註**：**呼應原題目第88條指示**——第10章應只寫「約4%，原始計算約4.15%」，**不寫成功率百分比**（例如不寫「90%機率」），因為本輪查證未在1994年原始論文的任何轉述中找到作者本人使用機率式表述；「90%成功率」的說法更接近後續學界（如Trinity Study或Morningstar）以蒙地卡羅法重新詮釋的產物，與Bengen原始「最壞情況仍可行」的邏輯不同，兩者不應混為一談。

### 補80（補充確認）．Morningstar安全提領率方向確係上修

- **事實／數字**：Morningstar「State of Retirement Income」研究：2025年報告建議的起始安全提領率為**3.9%**，高於「去年」（即2024年報告）的**3.7%**（原文摘要：「a starting safe withdrawal rate of 3.9% ... up from 3.7% last year」）。
- **來源機構**：WebSearch摘要轉引Morningstar官方研究內容（Morningstar官方頁面 https://www.morningstar.com/retirement/whats-safe-retirement-withdrawal-rate-2026 及 .../how-retirees-can-determine-safe-withdrawal-rate-2025 本輪嘗試開啟皆遭403 Forbidden）
- **網址**：無法提供本人實際開啟過的Morningstar原始網址（403封鎖），此條信心等級因此標記為**likely**而非verified，僅供交叉核對原研究檔既有結論方向是否一致
- **以…為準**：2025年報告（相對2024年報告而言為上修）
- **信心等級**：likely
- **備註**：與原研究檔第6.2條、原題目第80條的結論**方向一致**——查證再次確認是「上修」（3.7%→3.9%），不是原題目最初假設的「下修」，第10章行文請維持原研究檔已經採用的「近年在3.7%–4%之間浮動、每年依市場估值重估」寫法，不要改回「下修」的敘述。

---

## 本輪（2026-09-07補查）未完成清單

以下編號本輪未能逐條開啟官方原文查證，供下一輪查證員參照，勿在正文中當作已核實引用：
25（Morningstar三篇原文與質疑Mind the Gap方法論之學術文章出處）, 26（Vanguard DCA vs LSI原文版本）, 27（TWSE官方API逐日峰谷點位，含S&P 500對應日期）, 29（Sharpe 1991原文DOI）, 30（不同投信ETF費用揭露口徑逐一核對）, 31（Vanguard VOO/VT/BND官方fact sheet）, 85（台股歷史峰谷點位重算）, 86（ETF費用口徑逐一核對，本檔第9節既有內容應視為likely而非最終定論）。
