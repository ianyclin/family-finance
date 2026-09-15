# 補充查證：槓桿、生命週期、退休提領、台灣退休制度

查證日期 2026-09-11（研究代理 fable，逐字核對 PDF 全文）。用於指南 v3.2「槓桿、年齡與退休」一節。

I have everything I need. Here is the full report.

---

# 財務文獻查證報告：槓桿、年齡與退休

查證日期：2026-09-11。「verified」＝我親自在該網頁或 PDF 全文讀到；PDF 全文皆用 PyMuPDF 抽字後逐字核對。

## A. 生命週期投資與槓桿

### A1. Ayres & Nalebuff 原始論文

**A1-a｜NBER Working Paper 14094（2008 年 6 月）**
- 出處：Ayres, I. & Nalebuff, B., "Life-Cycle Investing and Leverage: Buying Stock on Margin Can Reduce Retirement Risk", NBER WP 14094, June 2008
- 網址：https://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/8/2019/06/LifecycleInvestingLeverage_v2008.pdf （NBER 頁：https://www.nber.org/papers/w14094）
- 信心：**verified**
- 逐字（摘要）："By employing leverage to gain more exposure to stocks when young, individuals can achieve better diversification across time. Using stock data going back to 1871, we show that buying stock on margin when young combined with more conservative investments when older stochastically dominates standard investment strategies—both traditional life-cycle investments and 100%-stock investments. The expected retirement wealth is 90% higher compared to life-cycle funds and 19% higher compared to 100% stock investments. The expected gain would allow workers to retire almost six years earlier or extend their standard of living during retirement by 27 years."
- 逐字（2:1 槓桿，p.2）："If a young investor with $10,000 in savings and a lifetime wealth of $100,000 were to buy stock on 2:1 margin, the resulting $20,000 investment would still leave her well short of the desired $60,000 in equities."
- 逐字（模型上限，p.13）："For most of the analysis, we assume that the maximum leverage on stocks is 2:1, pursuant to the Federal Reserve Regulation T."
- 逐字（他們自己的警告，p.3，股票溢酬）："As Barberis (2000) observes, this equity premium is based on relatively limited data and just one sample path; thus investors should not count on the equity premium persisting at historical levels."
- 逐字（借款成本，p.13）："in May 2006, low-cost brokers such as Vanguard and Fidelity charged margin rates of more than 9.5% on small-balance margin loans"
- 逐字（追繳／歸零，p.22-23，"Margin Calls and Wipeouts" 節）："The worst case arose in October 1929, where the leveraged single-target strategy would have produced negative returns of 53% for young investors who were fully leveraged (2:1). Leveraged strategies expose workers to a much larger probability of incurring a substantial negative monthly return sometime during their working life. Roughly one-quarter of the cohorts (22 out of 94) would have lost more than 40% in at least one month."
- 逐字（收入穩定前提，p.1 附註 & 內文）：策略建立在「discounted lifetime savings」上；"We assume that S is initially zero. The investor starts out with no savings."（p.11）

**A1-b｜"Diversification Across Time"（Yale 版，2010）**
- 網址：https://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/8/2020/12/Diversification-Across-Time.pdf （SSRN 1687272 標示 2010-10-04）
- 信心：**verified**（PDF 首頁無日期，內文提到 "in August 2010"）
- 逐字（摘要）："Buying stock on margin when young combined with reduced equity exposure when older can reduce lifetime portfolio risk. For example, an initially-leveraged portfolio can produce the same mean accumulation as a constant 75% stock allocation with a 21% smaller standard deviation. ... Based on historical returns, we find a 37% improvement in the certainty equivalent (for CRRA=4). Monte Carlo simulations show that these gains continue even with equity premia well below historical levels."
- 逐字（前提，p.2）："For this strategy to be effective, it requires the ability to borrow at low cost."
- 逐字（p.15）："The marginal cost of ... incremental borrowing required to move from 2:1 to 3:1 leverage is 8.01%. This is substantially higher than the 4.64% implied marginal interest rate for 2:1 leverage."

註：作者要的「63%」在兩篇原文都沒出現；出現的是 90%、19%、21%、37%、35-39%。

### A2. 主要批評

**A2-a｜Vars 書評（Vermont Law Review）**
- 出處：Fredrick E. Vars, "Book Review: Don't Try This at Home — Lifecycle Investing", 36 Vermont Law Review 373 (2011)
- 網址：https://lawreview.vermontlaw.edu/wp-content/uploads/2012/02/14-Vars-Book-2-Vol.-36.pdf
- 信心：**verified**
- 逐字："The danger is in moving from theory to practice. Here, the book falls short in important respects that need to be recognized before do-it-yourself investors go badly astray."（摘要）
- 逐字："The potential for a total wipeout in early years is not insubstantial and, without future income, potentially devastating. The lifecycle strategy treats future salary like a bond. Borrowing against that bond is risky when there is a substantial chance of default."（p.375）
- 逐字："Lifecycle investing is too complicated to be a viable option for the average investor."（p.380）
- 逐字（結論）："By far the most important assumption is that stock market returns will be greater than the cost of leverage. This appears to be a reasonable assumption at present, but if it fails, the Lifecycle Investing project fails with it."（p.384）
- 二手轉引書中原句（Vars 引 Ayres & Nalebuff 書 p.62）："It doesn't make any sense to pay a 10 percent margin rate to buy stock with an expected return of 8 percent."（信心：likely，我沒開書）
- 二手轉引 Bodie 2003（Vars 註 14）："If one's future labor income is relatively secure, it might be optimal to start out in the early years with a high proportion of one's investment portfolio in stocks"（Zvi Bodie, in *The Pension Challenge*, 2003, p.23；信心：likely）

**A2-b｜Samuelson 本人的反對（2008 年 10 月 BU 會議）**
- 出處：*The Future of Life-Cycle Saving and Investing: The Retirement Phase*, Research Foundation of CFA Institute, 2009（Bodie, Siegel, Sullivan 編），會議於 2008-10-22～24 Boston University；Samuelson 開場，書頁 p.2
- 網址：https://rpc.cfainstitute.org/sites/default/files/-/media/documents/book/rf-publication/2009/rfv2009n4.pdf
- 信心：**verified**
- 逐字："Many analysts argue that when you average over many investment periods, so favorable are the long-run returns of stocks that while you are still young, you should borrow substantially to hold large positions in stocks and you should do so because some kind of 'stochastic dominance' is supposed to justify it. Now, when I read such things, my eyebrows arch upwards. I think I have written 27 articles rebutting this idea"

**A2-c｜Bernstein《The Ages of the Investor》**：只有二手（Bogleheads 討論串、Amazon 簡介），信心 unverified，不列。

### A3. 台灣工具的代價

**A3-a｜槓桿型 ETF 官方警語**
- 證交所「槓桿型及反向型ETF」頁：https://www.twse.com.tw/zh/products/securities/etf/products/li.html ｜信心：**verified**
  - 逐字：「追求之正、反向倍數報酬率僅限於單日，每日複利計算下，長期報酬率會偏離原型指數之正、反向倍數表現，不宜長期持有。」
- 投信投顧公會「投資百寶箱」ETF 專區：https://www.sitca.org.tw/ROC/SITCA_ETF/etf-hub-product.html ｜信心：**verified**
  - 逐字：「基金連續兩日以上及長期之累積報酬率會受到計算累積報酬之複利效果影響，而偏離同期間標的指數正向2倍之累積報酬表現」
  - 逐字：「因此僅適合短期交易，不適合長期持有，若希望規畫中長期投資的投資人，建議以布局原型ETF為主」
  - 逐字：「基金經理人需依基金資產及市場現況，每日計算基金所需曝險額度及重新平衡投資組合」

**A3-b｜融資整戶擔保維持率 130%**
- 出處：《證券商辦理有價證券買賣融資融券業務操作辦法》（115.01.09 修正版）第 54、55 條
- 網址：https://twse-regulation.twse.com.tw/m/LawContent.aspx?FID=FL007121 ｜信心：**verified**
- 逐字第 54 條：「委託人信用帳戶之整戶擔保維持率低於百分之一百三十者，證券商應即通知委託人就各該筆不足擔保維持率之融資融券，於通知送達之日起二個營業日內補繳融資自備款或融券保證金差額。」
- 逐字第 55 條：「證券商依前條第一項規定通知補繳差額後，委託人未於通知送達之日起二個營業日內補繳或僅補繳其部分者，除雙方另有約定者外，證券商應依下列規定處理：一、當日委託人整戶擔保維持率仍不足者，自次一營業日起準用第八十一條第三項規定處分其擔保品。」

**A3-c｜銀行信貸利率**
- 臺灣銀行「消費者貸款適用利率一覽表(一)」，總費用年百分率計算基準日 115 年 8 月 21 日
  - 網址：https://www.bot.com.tw/Images/File/GetFileId/bc518e56-3341-4de4-ba88-65b0d74df77c ｜信心：**verified**
  - 逐字：「起適用利率指數1.751%」；「未提供擔保－個人（經本行信用評等達60分以上者）」最高額度 60 萬、最長 5 年、作業成本 4.156%、適用利率 5.907%、總費用年百分率 6.69%；「未提供擔保－公教機關或公營事業機構員工彙總」適用利率 4.617%、總費用年百分率 5.39%
- 中國信託分期型信用貸款：https://www.ctbcbank.com/content/dam/minisite/long/loan/leader/loan1.html ｜信心：**verified**
  - 逐字：總費用年百分率「4.13%~16.29%」；貸款年利率首期「0.01%(固定)」、第二期起「2.99%起(機動計息)」；開辦費「每案收取NT 9,000元」；「本貸款總費用年百分率之計算基準日為民國113年5月23日」
- 市場整體「約 2%～16%」只有比價網二手資料，unverified。

## B. 隨年齡調整的股債比例

### B4. Vanguard Target Retirement 滑翔軌道
- 出處 1：Vanguard, "Choice of equity landing points can benefit target-date investors", May 2025（Stockton & Chen）
  - 網址：https://workplace.vanguard.com/content/dam/inst/iig-transformation/insights/pdf/2025/231657-02_TDF_PTDF_OTH-TRIGT-Research.pdf ｜信心：**verified**
  - 逐字："Vanguard's Target Retirement glide path starts with a 90% equity allocation at age 25, gradually decreases to 50% equity at age 65, and ultimately lands at 30% equity around age 72, when the assets transition to Vanguard Target Retirement Income."
- 出處 2：Vanguard, "Vanguard's approach to target-date funds", March 2019（Donaldson 等）
  - 網址：https://workplace.vanguard.com/content/dam/inst/iig-transformation/insights/pdf/2022/Vanguards-approach-to-target-date-funds.pdf ｜信心：**verified**
  - 逐字："Vanguard's TDFs maintain a significant level of equity exposure (90%) to age 40 because during the early stages of wealth accumulation, a person's human capital remains so dominant over the small balances in financial capital. After age 40, the equity allocation continues to decline until age 72"
  - 逐字："Vanguard TDFs still offer 50% equity exposure at an investor's designated retirement year ... which is gradually reduced over the next seven years to 30%."
- 出處 3（頁面）：https://workplace.vanguard.com/investment/strategies/tdf-glide-path.html ｜verified：「90% stock allocation」(age 20)、「30% stocks and 70% bonds」(age 72)

### B5. 人力資本原始出處
- Bodie, Z., Merton, R.C., Samuelson, W.F. (1992), "Labor supply flexibility and portfolio choice in a life cycle model", *Journal of Economic Dynamics and Control*, 16(3-4), 427-449（NBER WP 3954，1992 年 1 月）
- 網址：https://www.nber.org/papers/w3954 ；https://ideas.repec.org/a/eee/dyncon/v16y1992i3-4p427-449.html ｜信心：**verified**（摘要在兩頁都讀到）
- 逐字摘要句："The ability to vary labor supply ex post induces the individual to assume greater risks in his investment portfolio ex ante. The model explains why the young (enjoying greater labor flexibility over their working lives) may take greater investment risks than the old."

### B6. 對「年齡公式」的說明／反方
- Vanguard 2019（同 B4 出處 2，p.4）｜信心：**verified**
  - 逐字："The human capital theory doesn't explicitly state how quickly or in what proportion equity exposure should diminish without the addition of a variety of assumptions and caveats. ... Widespread debate remains as to what level of equity exposure may be appropriate to diversify investors' human capital. There is no universally accepted optimal answer"
- Bernstein, "The One-Fund Holy Grail", *Efficient Frontier*, 2004：http://www.efficientfrontier.com/ef/404/grail.htm ｜信心：**verified**
  - 逐字："Mr. Bogle makes a good case for the bond allocation equal to your age; the 2045 and 2035 funds use age minus fifteen, and the 2025 and 2015 funds use age minus five."（注意：這是 Bernstein 說「年齡等於債券比」有道理，不是批評；Vanguard 自家基金比公式更積極）
- Samuelson 1969 理論（CFA 2008 版 Bodie 序，p.xviii）｜verified："he proved that the rational welfare-maximizing individual would invest exactly the same fraction of his or her total wealth—human capital plus financial wealth—in the risky asset at every age."（https://rpc.cfainstitute.org/sites/default/files/-/media/documents/book/rf-publication/2008/rfv2008n1.pdf）

## C. 退休提領

### C7. Bengen 1994
- 出處：William P. Bengen, "Determining Withdrawal Rates Using Historical Data", *Journal of Financial Planning*, October 1994
- 網址：https://robberger.com/wp-content/uploads/2024/01/retailinvestor.org_pdf_Bengen1.pdf（FPA 官方 PDF 回 403）｜信心：**verified**
- 逐字："Assuming a minimum requirement of 30 years of portfolio longevity, a first-year withdrawal of 4 percent, followed by inflation-adjusted withdrawals in subsequent years, should be safe. In no past case has it caused a portfolio to be exhausted before 33 years"
- 逐字："an 'absolutely safe' (to the extent history is a guide) initial withdrawal level is 3 percent, in that it ensures that portfolio longevity is never less than 50 years."
- 逐字（配置）："It is appropriate to advise the client to accept a stock allocation as close to 75 percent as possible, and in no cases less than 50 percent."；"the historical record supports an allocation of between 50-percent and 75-percent stocks as the best starting allocation"
- 逐字（資料）："I will rely on actual historical performance of investments and inflation, as presented in Ibbotson Associates' Stocks, Bonds, Bills and Inflation: 1992 Yearbook."（美國資料，自 1926 年起）
- 註：Bengen 用的是「股票＋中期公債」，不是作者猜的 60/40；50/50 與 75/25 皆在文中。

### C8. Trinity Study
- 出處：Cooley, Hubbard & Walz, "Retirement Savings: Choosing a Withdrawal Rate That Is Sustainable", *AAII Journal*, February 1998
- 網址：https://www.aaii.com/journal/199802/feature.pdf ｜信心：**verified**
- 逐字資料設定："The Standard & Poor's 500 index was used to represent stocks, and long-term, high-grade corporate bonds were used to represent bonds."（1926-1995）
- Table 1（未調通膨，30 年）：4% 提領：100% 股 98、75/25 **100**、50/50 100、25/75 100、100% 債 100；5%：95／98／100／100／51
- Table 3（通膨調整，30 年）：4% 提領：100% 股 95、75/25 **98**、50/50 95、25/75 71、100% 債 20；5%：85／83／76／27／17；6%：68／68／51／20／12
- 逐字結論："Most retirees would likely benefit from allocating at least 50% to common stocks."；"For stock-dominated portfolios, withdrawal rates of 3% and 4% represent exceedingly conservative behavior."

### C9. Morningstar State of Retirement Income 2025
- 出處：Morningstar, *The State of Retirement Income: 2025*, Dec. 3, 2025（Arnott, Benz, Kephart, Guo 等）
- 網址：https://static.twentyoverten.com/5b5730126af0247efe4f2066/zT8sbuFanVR/Morningstar-2025-State-of-Retirement-Income.pdf（morningstar.com 本站回 403）｜信心：**verified**
- 逐字："Morningstar's 2025 research suggests that 3.9% is the highest starting safe withdrawal rate for retirees seeking a consistent level of inflation-adjusted spending from year to year (assuming a 90% probability of having funds remaining at the end of an assumed 30-year retirement period)."
- 逐字："Our 'base-case' safe withdrawal rate is up slightly from the starting safe withdrawal percentage of 3.7% we estimated in last year's report. (The base-case estimates ... were 3.3% in 2021, 3.8% in 2022, and 4.0% in 2023.)"
- 逐字："The highest starting safe withdrawal percentage for a 30-year time horizon comes from portfolios that hold between 30% and 50% in equities and the remainder in bonds and cash."
- 逐字：「two of which lifted the starting safe withdrawal rate to 5.7%」（彈性提領法）

### C10. 報酬順序風險
- 出處 1：Vanguard, *Vanguard's Principles for Retirement Income*, 2026（p.10）
  - 網址：https://corporate.vanguard.com/content/dam/corp/research/pdf/vanguard_principles_retirement_income.pdf ｜信心：**verified**
  - 逐字："This is especially impactful if a significant downturn happens early in retirement—commonly referred to as sequence-of-returns risk. Poor returns early on can permanently impair a retiree's portfolio since necessary withdrawals reduce the assets available to participate in a subsequent market recovery."
- 出處 2（有數字例子）：Vanguard Research, *Safeguarding retirement in a bear market*, June 2020（Khang & Clarke）
  - 網址：https://www.vanguard.co.uk/content/dam/intl/europe/documents/en/whitepapers/safeguarding-retirement-bear-market.pdf ｜信心：**verified**
  - 逐字："consider two hypothetical investors, one retiring in 1973 and one in 1974, with a 35-year retirement horizon. Assume that both entered retirement with $500,000 invested in a portfolio of 50% US equities and 50% US bonds ... Both planned to withdraw $25,000 per year, adjusted for inflation. ... 5.23% real return per year for the 1973 investor, and 5.1% for the 1974 investor. ... The 1973 retiree would have run out of money 23 years into retirement. The 1974 retiree's portfolio, by contrast, would have maintained a balance of $300,000 for most of the 35 years of retirement"
  - 逐字："the unlucky ones with a poor sequence of returns were 31% more likely to outlive their wealth, had 11% lower retirement income streams, and left 37% smaller bequests."

## D. 台灣的退休制度

### D11. 勞退新制
- 出處 1：《勞工退休金條例》（最新修正 108.05.15）第 14、23 條
  - 網址：https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=N0030020 ｜信心：**verified**
  - 逐字第 14 條：「不得低於勞工每月工資百分之六」；「每月工資百分之六範圍內，自願提繳退休金；其自願提繳之退休金，不計入提繳年度薪資所得課稅」
  - 逐字第 23 條：「不得低於以當地銀行二年定期存款利率計算之收益；有不足者，由國庫補足之」
- 出處 2：勞動部「勞退新制」頁（更新 2024/02/16）：https://www.mol.gov.tw/1607/28162/28540/28560/ ｜verified
  - 逐字：「雇主負擔提繳之退休金，不得低於勞工每月工資6%」；「另勞工得在其每月工資6%範圍內，自願提繳退休金，並自當年度個人綜合所得總額中全數扣除」；「此專戶所有權屬於勞工。」

### D12. 勞保老年年金
- 出處：勞保局「勞保年金－給付標準－老年年金給付」（更新 2024-09-26）：https://www.bli.gov.tw/0019825.html ｜verified
  - 逐字：「平均月投保薪資×年資× 0.775% + 3,000 元」／「平均月投保薪資×年資× 1.55%」擇優；「每延後 1 年請領，依原計算金額增給 4％，最多增給 20％」；「每提前 1 年，依原計算金額減給4%，最多減給20%」
- 出處：勞保局 FAQ（更新 2022-10-25）：https://www.bli.gov.tw/0017461.html ｜verified
  - 逐字：「『平均月投保薪資』按加保期間最高60個月之月投保薪資平均計算。」
- 出處：勞保局「請領資格」（更新 2024-12-24）：https://www.bli.gov.tw/0004856.html ｜verified
  - 逐字：「年滿60歲，保險年資合計滿15年，並辦理離職退保者」；年齡時程 98-106 年 60 歲、107 年 61、109 年 62、111 年 63、113 年 64、「115年以後為65歲」

### D13. 試算工具
- 勞保局「勞保老年給付及勞退試算整合」（一頁同時算勞保一次金、勞保年金、勞退月退）：https://www.bli.gov.tw/0109187.html ｜verified；頁面註「試算結果僅供參考，實際領取金額仍以本局核定為主」
- 勞保局「老年年金給付」單項試算：https://www.bli.gov.tw/0100398.html ｜likely（搜尋結果，未開）
- 勞退個人專戶查詢及試算（需憑證登入 e 化服務系統 https://edesk.bli.gov.tw/me/ ）：https://www.bli.gov.tw/0012942.html ｜verified
- 勞動部「勞工個人退休金試算表（勞退新制）」：https://calcr2.mol.gov.tw/trial ｜verified（自 0012942 頁連結讀到）

---

## 可以放進指南的句子清單（只列 verified）

1. 年輕時 2:1 融資買股、老了減碼，模擬退休財富比目標日期基金高 90%。［A1-a］
2. 同一群作者也承認：股票溢酬只是一條歷史路徑，不該指望它持續。［A1-a］
3. 1929 年 10 月，2:1 全槓桿的年輕人單月虧 53%。［A1-a］
4. 這套策略要能成立，前提是借得到便宜的錢。［A1-b］
5. 法學書評的結論：對一般投資人來說，這套做法太複雜。［A2-a］
6. 只要股票報酬低於借款成本，整個計畫就跟著失敗。［A2-a］
7. Samuelson 本人：讀到「年輕時大舉借錢買股」，我的眉毛就往上挑。［A2-b］
8. 證交所：槓桿 ETF 倍數報酬僅限單日，長期會偏離，不宜長期持有。［A3-a］
9. 投信投顧公會：槓反 ETF 僅適合短期交易，中長期請用原型 ETF。［A3-a］
10. 整戶擔保維持率低於 130%，兩個營業日內補繳，否則次日起處分擔保品。［A3-b］
11. 臺銀無擔保個人信貸總費用年百分率 6.69%（基準日 115.8.21）。［A3-c］
12. 中信信貸第二期起年利率 2.99% 起，總費用年百分率 4.13%～16.29%。［A3-c］
13. Vanguard 目標日期基金：25 歲股票 90%、65 歲 50%、72 歲 30%。［B4］
14. Vanguard 40 歲前維持 90% 股票，因為此時人力資本遠大於金融資本。［B4］
15. 人力資本觀念出自 Bodie、Merton、Samuelson 1992：能調整工作量的人，能承擔更多投資風險。［B5］
16. Vanguard 承認：人力資本理論並沒說股票該多快、多少地減碼，沒有公認答案。［B6］
17. Bengen 1994：30 年退休，第一年提 4% 再逐年隨通膨調整，歷史上都安全。［C7］
18. Bengen：股票配置盡量接近 75%，任何情況不低於 50%。［C7］
19. Trinity：75/25、4% 提領、30 年、通膨調整，成功率 98%。［C8］
20. Trinity：多數退休者至少配 50% 股票會比較好。［C8］
21. Morningstar 2025：安全起始提領率 3.9%，前提 30 年、90% 成功率、股票 30-50%。［C9］
22. Morningstar：彈性提領可把起始提領率拉到 5.7%。［C9］
23. Vanguard：退休初期跌一段，提領會把暫時虧損變成永久損失。［C10］
24. 1973 與 1974 年退休、同樣 50/50、同樣年提 2.5 萬，前者 23 年就花光。［C10］
25. 雇主提撥不得低於工資 6%；勞工自提上限 6%，不計入當年度薪資所得課稅。［D11］
26. 勞退基金保證收益不低於當地銀行二年定存利率，不足由國庫補足。［D11］
27. 勞保老年年金＝平均月投保薪資 × 年資 × 1.55%，與另一式擇優。［D12］
28. 平均月投保薪資＝加保期間最高 60 個月的平均。［D12］
29. 民國 115 年起勞保年金請領年齡 65 歲，年資須滿 15 年。［D12］
30. 提前領每年減 4% 最多 20%；延後領每年加 4% 最多 20%。［D12］
31. 勞保局整合試算頁可一次算勞保一次金、年金與勞退月退。［D13］

## 找不到或沒核到的

- Ayres & Nalebuff 論文中沒有「63%」這個數字；作者若記得該數字，需另指來源。
- Journal of Financial Planning 上針對 Lifecycle Investing 的正式回應：搜不到；Vars 書評（Vermont Law Review）與 Samuelson 2008 開場是替代。
- Bernstein 對「100 減年齡」的批評：他 2004 年的原句反而是「Bogle 的年齡＝債券比有道理」；《The Ages of the Investor》只有二手摘要，未列。
- 台灣「主要銀行信貸利率區間」整體數字只有比價網（2%～16%），未列入 verified。
- morningstar.com、schwab.com、bogleheads wiki、FPA 官方 Bengen PDF 全部回 403，改用其他可開連結。

抽字暫存檔在 `/private/tmp/claude-501/-Users-linyenchu-Cladue-Code/74b71b1c-f70a-4f20-89ce-2952d977c51c/scratchpad/`（ayres2008.txt、divtime.txt、vars.txt、trinity.txt、bengen.txt、mstar2025.txt、vgprinc.txt、vguk.txt、vg2019.txt、vgtdf.txt、cfa2008.txt、cfa2009.txt、botrate.txt），需要更多逐字段落可直接 grep。未動任何專案檔案。