# 補充查證 A ——《隔離人性》行為金融原始來源

查證日期：2026-09-08
方法：WebSearch 定位 → 儘量開一手 PDF（直接讀取 PDF 全文，非僅摘要）或期刊/機構官方頁；.com 商業站對 WebFetch 常回 403（morningstar.com、advisorperspectives.com、dalbar.com 的部分頁面皆遇到），改用作者個人網站 PDF、SSRN／DOI 頁、或確實可開的二手引用媒體（並標明是二手）。
標記規則：**verified** = 我親自打開原文（PDF 全文或該站官方頁）並在其中看到數字／原句；**likely** = 只在搜尋摘要或需靠二手媒體轉引看到，未能打開一手頁面；**unverified** = 查無可靠來源。

---

## 1. Bar-Eli, Azar, Ritov, Keidar-Levin & Schein (2007)

**"Action bias among elite soccer goalkeepers: The case of penalty kicks"**, *Journal of Economic Psychology* 28(5), 606–621.

查證方式：直接打開共同作者 Ilana Ritov 個人網頁的全文 PDF（`https://pluto.huji.ac.il/~msiritov/BarEliAzarRitovKeidarSchein.pdf`），讀了摘要、方法、Table 1、Table 2、結論全文。**verified**

- 樣本：286 次十二碼罰球（原始收錄 311 次，扣除 18 次踢飛/踢中門柱門楣、7 次判讀不一致後剩 286 次）。
- 守門員選擇分佈（Table 1，扣除細節後的邊際百分比）：撲左 49.3%、**留在中間僅 6.3%**（18/286）、撲右 44.4%。原文結論句直接寫：「in 93.7% of the kicks the goalkeepers chose to jump to their right or left」——撲邊比例 93.7%。
- 撲救成功率（Table 2，Overall 列）：**留中央 33.3%**（6/18 撲成功）、撲左 14.2%、撲右 12.6%。
- 原文摘要句：「Goalkeepers, however, almost always jump right or left... given the probability distribution of kick direction, the optimal strategy for goalkeepers is to stay in the goal's center.」
- 結論句：「while the utility-maximizing behavior for goalkeepers is to stay in the goal's center during the kick, in 93.7% of the kicks the goalkeepers chose to jump to their right or left.」
- 解釋機制：作者提出「action bias」（動作偏誤，omission bias 的反轉）——因為「跳」才是常態（norm），根據 Kahneman & Miller (1986) 的 norm theory，守門員站在中間沒撲卻失球，感受上比跳錯邊沒撲到更難受，因此傾向多跳、少留中間。

來源：https://pluto.huji.ac.il/~msiritov/BarEliAzarRitovKeidarSchein.pdf （Ritov 個人頁全文 PDF，已讀取）；另可交叉核對 https://www.sciencedirect.com/science/article/abs/pii/S0167487006001048 （ScienceDirect 正式出版頁，未逐字開啟）。

---

## 2. Barber & Odean (2000)

**"Trading Is Hazardous to Your Wealth: The Common Stock Investment Performance of Individual Investors"**, *The Journal of Finance* 55(2), 773–806.

查證方式：直接打開 Terrance Odean 個人（UC Berkeley Haas）網站的全文 PDF（`https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/individual_investor_performance_final.pdf`），讀了摘要與前三頁正文。**verified**

- 摘要原句（英文原文）：「Of 66,465 households with accounts at a large discount broker during 1991 to 1996, those that trade most earn an annual return of 11.4 percent, while the market returns 17.9 percent. The average household earns an annual return of 16.4 percent, tilts its common stock investment toward high-beta, small, value stocks, and turns over 75 percent of its portfolio annually.」
- 樣本：66,465 個家庭帳戶，某大型折扣券商，1991–1996（正文另處寫為 1991 年 2 月至 1997 年 1 月，六年）。
- 交易最頻繁一組（依月周轉率分五分位，最高一組月周轉率 > 8.8%）年化淨報酬 **11.4%**；市場（NYSE/AMEX/Nasdaq 市值加權指數）年化報酬 **17.9%**；交易最少一組淨報酬 18.5%（正文 Figure 1 附近）。
- 平均家庭：淨報酬 16.4%、毛報酬 18.7%，年周轉率 75%。
- 核心結論句（摘要末句）：「Our central message is that trading is hazardous to your wealth.」
- 機制：文章將高周轉率與差報酬歸因於「過度自信」（overconfidence），而非流動性、稅務、風險再平衡等理性動機所能解釋。

來源：https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/individual_investor_performance_final.pdf （Odean 個人頁全文 PDF，已讀取摘要與正文）

---

## 3. Odean (1998)

**"Are Investors Reluctant to Realize Their Losses?"**, *The Journal of Finance* 53(5), 1775–1798.

查證方式：直接打開 Odean 個人網站全文 PDF（`https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/areinvestorsreluctant.pdf`），讀了摘要、方法定義（PGR/PLR）與 Table I 結果。**verified**

- 摘要原句：「I test the disposition effect, the tendency of investors to hold losing investments too long and sell winning investments too soon, by analyzing trading records for 10,000 accounts at a large discount brokerage house. These investors demonstrate a strong preference for realizing winners rather than losers.」
- 樣本：10,000 個帳戶，1987–1993 年交易紀錄（其中 6,380 個帳戶有 CRSP 資料可用於本分析，97,483 筆交易）。
- 處分效應的操作型定義：
  - PGR（已實現獲利比例）= 已實現獲利 ÷（已實現獲利＋帳面未實現獲利）
  - PLR（已實現虧損比例）= 已實現虧損 ÷（已實現虧損＋帳面未實現虧損）
- **全年數字（Table I）：PGR = 0.148，PLR = 0.098**，差 0.050（t 值 −35，即拒絕虛無假設「PGR ≤ PLR」的統計極顯著）。也就是說，投資人賣掉獲利部位的比率（14.8%）比賣掉虧損部位的比率（9.8%）高出約 5 個百分點、相對高出約 51%。
- 12 月因避稅賣壓，PLR 明顯上升（12 月 PLR 0.128 vs 全年 0.098），PGR−PLR 差距在 12 月縮小（12月差 0.020 vs 1–11月差 0.058），顯示投資人年底確實有較多「賣輸家報稅損失」的行為，但全年整體仍是「賣贏家 > 賣輸家」。

來源：https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/areinvestorsreluctant.pdf （Odean 個人頁全文 PDF，已讀取摘要、方法、Table I）

---

## 4. Barber, Huang, Odean & Schwarz (2022)

**"Attention‐Induced Trading and Returns: Evidence from Robinhood Users"**, *The Journal of Finance* 77(6), 3141–3190.

查證方式：兩層。(a) 正式出版摘要：直接打開 Wiley 官方 DOI 頁（`https://onlinelibrary.wiley.com/doi/10.1111/jofi.13183`），讀到摘要原句。**verified**。(b) 對照 2020 年 11 月的工作論文草稿全文 PDF（第三方鏡像 `https://smallake.kr/wp-content/uploads/2020/12/SSRN-id3715077.pdf`），讀了完整摘要。**verified**（工作論文版本）。

- **正式發表版摘要原句（Wiley DOI 頁）**：「Average 20-day abnormal returns are −4.7% for the top stocks purchased each day.」——羊群式買進最集中的股票，之後 20 個交易日的平均異常報酬為 **−4.7%**。
- 對照：2020 年 11 月工作論文草稿摘要原句是：「Average five-day abnormal returns are -3% (-6%) for the top stocks purchased each day (more extreme herding) by Robinhood users.」——早期草稿用的是 5 日窗口、−3%（更極端羊群事件為 −6%）。**兩個版本的視窗長度與數字不同**，正式發表版（2022, JF）用的是 20 日 −4.7%，這是修訂後定稿的數字，寫文章請用 −4.7%／20 日這組。
- 機制：作者將 Robinhood 使用者的「注意力驅動交易」與其 App 簡化資訊呈現（如「熱門排行榜」）連結，發現這類集中買進事件之後股價傾向反轉下跌；Robinhood 當機期間，容易吸引散戶注意力的股票交易量會顯著下降，佐證是「注意力」而非單純基本面驅動了這些交易。

來源：https://onlinelibrary.wiley.com/doi/10.1111/jofi.13183 （Wiley 正式出版頁，已讀到摘要原句）；https://smallake.kr/wp-content/uploads/2020/12/SSRN-id3715077.pdf （2020 工作論文草稿全文 PDF，已讀取摘要，僅供對照早期版本數字，正式引用請用期刊版）

---

## 5. Vanguard (2020) "Cash panickers: Coronavirus market volatility"

Vanguard Research Note，2020 年 7 月，作者 Thomas J. De Luca、Jean A. Young。

查證方式：Vanguard 官方 corporate.vanguard.com 該 PDF 連結已回傳 404（原始網址可能已下架/搬遷），改用第三方機構鏡像的官方原檔全文 PDF（`https://mccareer.org/wp-content/uploads/2020/08/cash-panickers-coronavirus-market-volatility.pdf`，檔案內文件代碼為 Vanguard 官方文件編號 CVMV 072020，版權頁載明 © 2020 The Vanguard Group），讀了全文。**verified**（透過鏡像檔開到 Vanguard 原始全文，非僅摘要／二手轉述）

- 研究期間：**2020 年 2 月 19 日（S&P 500 高點）至 5 月 31 日**。這段期間 S&P 500 先跌 34%（3 月 23 日落底），再反彈 36%（至 5 月底）。
- 交易行為統計：這段期間僅 5% 的 DC 退休計畫自主投資參與者、17% 的自主零售帳戶投資人有進行任何交易；**不到 0.5% 的 Vanguard 投資人「恐慌」並將帳戶全數轉為現金**（"cash panickers"）。
- 這些「現金恐慌者」的中位數特徵：年齡中位數（DC 55 歲／零售 57 歲，文中概括說「mid-50s」）、平均已是 Vanguard 客戶 12 年以上（DC 12年／零售13年）、2019年12月時股票配置中位數約 DC 70%、零售 75%。
- 結果：原句「Through May 2020, more than 80% of these cash panickers would have been better off if they had simply "stayed the course."」——到 2020 年 5 月為止，**逾 80% 的現金恐慌者，若當初什麼都不做（continue holding 2/18 的原始持倉），結果會比實際轉現金更好**。
- 文中並引用另一篇 Vanguard 研究稱：「portfolio asset allocation accounts for about 90% of investment returns」（資產配置決定約九成報酬），用來說明「進出場擇時」的機會成本。

來源：https://mccareer.org/wp-content/uploads/2020/08/cash-panickers-coronavirus-market-volatility.pdf （Vanguard 原始研究筆記全文 PDF 鏡像，已讀取全文；官方原網址 institutional.vanguard.com/VGApp/iip/site/institutional/researchcommentary/article/InvComCashPanickersCoronavirus 目前對外部連結回應 404）

---

## 6. Morningstar "Mind the Gap" 2024 與 2025

### 2024 報告
標題：*Mind the Gap 2024*，Morningstar Portfolio and Planning Research，作者 Jeffrey Ptak, CFA，發布日 2024 年 8 月 15 日。

查證方式：直接打開 Morningstar 官方資產連結全文 PDF（`https://assets.contentstack.io/v3/assets/blt4eb669caa7dc65b2/blt0571178b63219c0b/66bdeb4a4f0e4749e15a5621/2024_Mind_the_Gap.pdf`），讀了 Executive Summary、Key Takeaways、Fund Fees and Volatility 三節全文。**verified**

- 研究涵蓋 10 年（截至 2023/12/31），逾 2 萬個基金股別、期初資產逾 12 兆美元、期末近 21 兆美元。
- 核心數字（原句）：「We estimate fund investors earned a 6.3% annual investor return over the 10 years ended Dec. 31, 2023, while their fund holdings earned about 7.3% per year ('total return'). The 1.1% annual estimated return gap stems from mistimed purchases and sales」——投資人實際年化報酬 6.3%，基金本身年化報酬 7.3%，落差 **1.1 個百分點**（約當基金報酬的 15%，封面副標即寫「Investors lost out on about 15% of the return their funds generated」）。
- 分類最窄／最寬缺口（原句）：「Allocation funds had the narrowest gap (a negative 0.4% gap per year...); sector equity funds had the widest (a negative 2.6% gap annually).」——**配置型基金缺口最小（−0.4%/年），產業型基金缺口最大（−2.6%/年）**。
- 「波動比費用更傷投資人」的原句（Fund Fees and Volatility 節）：「Though investor return gaps were narrower among cheaper funds in some category groups... this wasn't uniform; timing costs don't seem to be directly correlated with fees. The more volatile a fund's returns versus peers, the larger the gaps tended to be; the average dollar invested in the most volatile sector equity funds lagged the buy-and-hold return by over 7 percentage points per year.」——費用高低與缺口大小**沒有穩定的相關性**，但基金波動度越高，缺口越大；最波動的產業型基金投資人，缺口甚至超過 **7 個百分點/年**。這正是「波動比費用更影響投資人拿到的報酬」這句話的原始依據，但 2024 報告本身沒有用這麼簡潔的一句話下結論，是研究內容支持這個說法，逐字句是上面引的那幾句。

### 2025 報告
標題應為 *Mind the Gap US 2025*，Morningstar，發布約 2025 年 8 月，涵蓋十年至 2024/12/31。

查證方式：Morningstar 官方頁（morningstar.com/business/insights/research/mind-the-gap）多次對 WebFetch 回傳空白或 403，未能直接開到官方原文。改用兩個確實可開啟全文的第三方轉引媒體頁：`https://theideafarm.com/wealth-management/mind-the-gap-2025/`（已直接開啟讀取）、以及交叉搜尋摘要核對。**likely**（數字來自二手媒體逐字轉引 Morningstar 原句，非我親自打開 morningstar.com 原頁）

- 二手媒體轉引數字：「Investors lagged their funds by 1.2% annually over 10 years, losing ~15% of potential gains.」「Sector equity investors trailed by 1.5% annually」「allocation fund investors lost only 0.1%」「The most volatile cash flow funds saw 1.8% annual gaps vs. 0.8% for the most stable.」
- **注意**：查證過程中另外查到一篇 2026 年 8 月發布、討論「decade through Dec 2025」的更新版報告（暫稱 *Mind the Gap 2026*，institutionalinvestor.com 與 advisoranalyst.com 均有報導：整體缺口 1.2 個百分點、投資人年化 8.7% vs 基金 9.9%、最寬類別 alternative funds 1.6%、最窄 large-blend 0%整），這是**更新的一版、不是 2025 年那版**，數字不要混用。寫文章若只需要「2024／2025 兩年一致約 1.1–1.2 個百分點、產業型最寬、配置型最窄」這個穩定結論，2024（一手 PDF 驗證）＋2025（二手轉引）已經足夠支持；若要用到「8.7% vs 9.9%」這組數字，那其實是 2026 版，請按年份分開標注，不要說成 2025。

### 對 Mind the Gap 方法論的學術／專業批評
找到一篇同儕審查期刊文章直接針對 Mind the Gap 的方法論提出質疑：

Fulkerson, J. A., Jordan, B. D., Riley, T. B., & Yan, Q., **"Bad Timing Does Not Cost Investors 15% of Their Funds' Returns: An Examination of Morningstar's 'Mind the Gap' Study"**，*Financial Analysts Journal*（Taylor & Francis，DOI: 10.1080/0015198X.2026.2657253）。SSRN 版本 abstract_id=4904652。

查證方式：SSRN 摘要頁與期刊頁對 WebFetch 均回 403，未能親自讀到摘要全文，僅由 WebSearch 摘要看到其論點方向。**likely**——核心論點：Morningstar 把「資金加權報酬（dollar-weighted）低於時間加權報酬（time-weighted）」直接歸因於「投資人擇時能力差」，但這個缺口有一部分其實是統計建構上必然出現的效果（現金流進出時機造成的機械性落差），不必然代表投資人真的「追高殺低」；批評者稱此為對缺口的過度解讀。若要在文章中引用這篇批評，建議用「有同儕審查期刊論文質疑 Mind the Gap 把整個缺口都算成投資人擇時失誤，這個歸因過度簡化」這樣的概括寫法，避免逐字引用（因為我沒能親自讀到論文原句）。

來源：
- 2024 報告 PDF（已讀全文）：https://assets.contentstack.io/v3/assets/blt4eb669caa7dc65b2/blt0571178b63219c0b/66bdeb4a4f0e4749e15a5621/2024_Mind_the_Gap.pdf
- 2025 報告（二手轉引，已開啟該頁全文）：https://theideafarm.com/wealth-management/mind-the-gap-2025/
- 2026 更新版（不要與 2025 混用，二手轉引）：https://www.institutionalinvestor.com/article/returns-gap-shows-investors-cant-stop-chasing-performance ；https://advisoranalyst.com/2026/08/10/the-gap-that-keeps-growing-what-morningstars-2026-investor-return-study-tells-advisors.html/
- 方法論批評（未能開到原文，僅搜尋摘要）：https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4904652 ；https://www.tandfonline.com/doi/full/10.1080/0015198X.2026.2657253

---

## 7. DALBAR QAIB 2024，848 個基點

查證方式：DALBAR 官方新聞稿頁面直接打開讀取。**verified**

- 來源：DALBAR 官方新聞稿〈Investors Missed the Best of 2024's Market Gains, Latest DALBAR Investor Behavior Report Finds〉，網址 `https://www.dalbar.com/press-release/investors-missed-the-best-of-2024s-market-gains-latest-dalbar-investor-behavior-report-finds/`。
- 原句：「The Average Equity Investor earned just 16.54% in 2024, compared to the S&P 500's 25.02% return.」
- **25.02% − 16.54% = 8.48 個百分點 = 848 個基點**，這就是常被引用的「848 bps」落差的算術由來（新聞稿本身用百分比表述，848bps 是換算後常見的引用方式，但兩個原始百分比數字 16.54% 與 25.02% 是我直接從 DALBAR 官方新聞稿讀到的）。
- 另外新聞稿也提到固定收益端：「The Average Fixed Income Investor lost 1.07%, underperforming the Bloomberg U.S. Aggregate Bond Index's 1.25% gain.」

### 對 DALBAR 方法論的批評（Wade Pfau, 2017）

Wade Pfau，**"A Warning to the Advisory Profession: DALBAR's Math Is Wrong"**，Advisor Perspectives，2017 年 3 月 6 日。

查證方式：Advisor Perspectives 原文頁對 WebFetch 回 403，無法直接打開；改用 Kitces.com 同期〈Weekend Reading for Financial Planners〉一文（該頁本身可直接打開讀取，其中逐字引用並解讀了 Pfau 的論點）。**likely**（透過可信的二手轉引頁確認論點方向與部分逐字句，未能親自讀到 Advisor Perspectives 原文）

- Kitces.com 轉引 Pfau 的核心論點：DALBAR 把投資人報酬拿去跟「假設一次性全部投入」的市場報酬相比，但多數投資人根本不是一次性拿出全部本金投資，而是逐年逐月慢慢加碼（accumulation）。Kitces 轉引句：「much of what DALBAR attributes to the investor behavior gap is actually just the effect of accumulators who make ongoing savings over time, 'lagging' the returns available with lump-sum investing because they simply didn't have the money to initially invest.」
- Pfau 建議應該拿投資人報酬去跟「定期定額（dollar-cost averaging）基準」比較，而不是跟「一次性投入」基準比較；若改用這個更公平的基準，Pfau 認為過去 20 年滾動期間投資人其實**沒有跑輸**、甚至略微跑贏。
- 這篇批評鎖定的是「計算基準本身有沒有系統性偏誤」，跟 Fulkerson et al. 對 Morningstar Mind the Gap 的批評邏輯類似（都是質疑「用一次性投入當基準,再把落差全部歸咎於投資人心理」這個推論方式）。

來源：
- 848bps 原始出處（已直接開啟讀取）：https://www.dalbar.com/press-release/investors-missed-the-best-of-2024s-market-gains-latest-dalbar-investor-behavior-report-finds/
- Pfau 批評（透過可開啟的二手轉引頁確認，原文頁 403 未能親自打開）：https://www.kitces.com/blog/weekend-reading-for-financial-planners-mar-11-12/ ；原文出處（僅知網址，未能打開）：https://www.advisorperspectives.com/articles/2017/03/06/a-warning-to-the-advisory-profession-dalbar-s-math-is-wrong

---

## 8. 「彼得‧林區麥哲倫基金平均投資人虧損」

**查證結論：unverified —— 這是廣泛流傳的二手轉述，查不到可具名、可核對方法論的原始出處。**

搜尋過程：
1. 先以「Peter Lynch Magellan average investor lost money study original source Fidelity」搜尋，找到的都是財經部落格、Medium、Forbes 專欄等二手轉述，眾口一致說「根據 Fidelity 內部研究」或「Lynch 自己在訪談中提過」，但沒有任何一篇附上可查證的原始報告名稱、發布年份、或方法論說明。常見的版本是：林區 1977–1990 管理麥哲倫基金年化 29%，但「平均投資人」同期反而是虧損（或另一版本說平均投資人年化僅約 7%）。
2. 進一步以「Magellan average investor lost money Zweig behavior gap primary source citation」搜尋，試圖追到 Jason Zweig《Your Money and Your Brain》或「behavior gap」一詞的出處，結果顯示「behavior gap」一詞其實是理財顧問 Carl Richards 提出、後來被廣泛使用的概念，跟麥哲倫這個具體故事並非同一條考證線；沒有找到任何學術論文、Fidelity 官方文件、或 SEC 申報文件把這個說法的具體樣本數、計算方法、資料期間講清楚。
3. 這個故事最常見的量化版本（「29% vs 7%」或「平均投資人虧損」）在各家轉述之間彼此不一致，且都沒有腳註可回溯，符合典型的「金融圈口耳相傳但源頭已佚失」案例。

建議寫法：文章中若要用這個故事，務必明講「這是財經圈廣泛流傳的說法，常被歸為『Fidelity 內部研究』或林區本人受訪時的說法，但我查不到可公開核對的原始報告」，不要當作有出處的硬數字引用；如果需要一個「同樣道理、但有紮實原始論文撐腰」的替代例證，可以用本文查證清單裡第 2 條 Barber & Odean (2000) 或第 6 條 Morningstar Mind the Gap（都已驗證到一手數字），或第 5 條 Vanguard cash panickers（同樣是「基金報酬 vs 投資人實際拿到的報酬」落差的真實案例）。

來源（皆為二手轉述，未列入引用清單）：
- https://x.com/SteadyCompound/status/1761553485391417532
- https://www.theglobeandmail.com/investing/article-how-some-investors-lost-money-on-a-fund-that-averaged-30-per-cent/
- https://www.gulaq.com/blog/basics-of-investing/the-paradox-of-success-how-investors-lost-money-in-peter-lynchs-magellan-fund/
- https://www.alphawealthfunds.com/2022/11/most-of-the-magellan-funds-investors-lost-money/

---

## 給寫作的速查表

| # | 主張 | 關鍵數字 | 信心 |
|---|---|---|---|
| 1 | 守門員動作偏誤 | 留中央 6.3%、撲邊 93.7%；留中央撲救率 33.3% vs 撲邊 12.6–14.2% | verified |
| 2 | 交易越頻繁報酬越差 | 交易最多組 11.4% vs 市場 17.9%（1991–1996，66,465 戶） | verified |
| 3 | 處分效應 | PGR 0.148 vs PLR 0.098（1987–1993，10,000 戶） | verified |
| 4 | Robinhood 羊群交易後續報酬 | 20 日異常報酬 −4.7%（正式發表版） | verified |
| 5 | Vanguard 現金恐慌者 | <0.5% 轉全現金；>80% 事後更差；期間 2020/2/19–5/31 | verified |
| 6a | Mind the Gap 2024 | 缺口 1.1pp（6.3% vs 7.3%）；配置型 −0.4% 最小、產業型 −2.6% 最大 | verified |
| 6b | Mind the Gap 2025 | 缺口約 1.2pp；產業型 1.5%、配置型 0.1% | likely（二手轉引） |
| 6c | Mind the Gap 方法論批評 | Fulkerson et al. 質疑把整個缺口都算成擇時失誤 | likely（未讀原文） |
| 7a | DALBAR 2024 | 16.54% vs 25.02%（差 848bps） | verified |
| 7b | Pfau 對 DALBAR 的批評 | 一次性投入基準對定期定額投資人不公平 | likely（經 Kitces 轉引） |
| 8 | 林區麥哲倫故事 | 查無可查證原始出處 | unverified，需明講是二手傳說 |
