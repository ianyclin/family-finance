# 補充查證：擇時、定期定額、錯過最好的日子

查證日期：2026-09-07
查證員角色聲明：以下只做查證與抄錄，不做論述取捨；數字後的「原文引述」逐字抄自原始文件，換算一律同時附原始數字與算式。媒體/部落格只當存在性線索的地方已在「備註」註明，不當數字來源使用。

---

## 1. Schwab Center for Financial Research「Does Market Timing Work?」（最新版）

**主題**：五種投資人 20 年期末金額比較（完美擇時 vs. 立即投入 vs. 定期定額 vs. 最差擇時 vs. 留在現金）

**事實**：目前 schwab.com 上的最新版一篇，發布/更新日期標示 **2025-07-18**，資料期間改為 **2005–2024（20 年）**，S&P 500 指數，五人每年年初各拿到 $2,000。

**數字（逐字抄錄自原文）**：
- Peter Perfect（完美擇時，每年都精準買在當年最低點）：**$186,077**
- Ashley Action（每年領到錢就在當年第一個交易日全部投入，不擇時）：**$170,555**（比 Peter 少 $15,522）
- Matthew Monthly（定期定額，每年分 12 等份、每月投入）：**$166,591**
- Rosie Rotten（每年都買在當年最高點，運氣/擇時能力最差）：article 原文只給出「比 Ashley 少 $19,212」→ 回推 = $170,555 − $19,212 = **$151,343**
- Larry Linger（完全不投入股市，只放美國 30 天期公債 T-bill）：**$47,357**

**結論句（原文逐字）**：
> "the cost of waiting for the perfect moment to invest—and essentially staying out of the stock market—typically exceeds the benefit of even perfect timing."

> "Ashley... came in second with $170,555—only $15,522 less than Peter Perfect."（也就是 20 年下來完美擇時只多賺 $15,522，文中換算「about $700 extra per year」）

**方法補充（原文）**：Schwab 一共檢驗了 80 個滾動 20 年期間（回溯到 1926 年），其中 70 個期間五人排名完全相同（Peter＞Ashley＞Matthew＞Rosie＞Larry）。

**來源機構**：Charles Schwab（Schwab Center for Financial Research）
**網址**：https://www.schwab.com/learn/story/does-market-timing-work
**以…為準**：頁面標示 2025-07-18；資料期間 2005-01-03 至 2024-12-31（20 年）
**信心等級**：verified（實際打開頁面全文讀取，未使用摘要）
**備註**：
1. 作者手上若引用的是舊版「20 年結束於 2020 年」（$186,077／$170,555／$166,591 這組數字剛好與新版一致——這組數字其實兩版相同，只是「20 年結束於哪一年」不同版本會變。目前 schwab.com 正文明確寫「the 20 years ending in 2024」，但列出的三個數字（$186,077 / $170,555 / $166,591）與坊間流傳「結束於 2020 年」版本的數字完全相同，代表這是 Schwab 官網文字更新時間軸但沒同步換算圖表數字的可能，或者 2020–2024 這五年剛好使排名前三的絕對金額變動極小。本查證只能照原文逐字抄錄，兩種可能都提請作者知悉，不代為判斷。
2. Rosie Rotten 與 Larry Linger 的金額是由「文字敘述的差額」回推得出（$170,555 − $19,212 = $151,343），並非直接看到數字本身，屬於算式推導，已註明算式。
3. 另有 nmpera.org、advisorservices.schwab.com、workplace.schwab.com 等鏡像/子網域，經 WebFetch 工具測試均回 403，改用直接下載頁面 HTML 的方式讀取 schwab.com 正文成功。

---

## 2. Vanguard 定期定額 vs. 單筆投入（2012 版 + 2023 版）

### 2-A：Vanguard 2012「Dollar-cost averaging just means taking risk later」

**事實**：2012 年 7 月發布，比較單筆投入（LSI）與定期定額（DCA，本文定義為「一筆錢分批在 6/12/18/24/30/36 個月內投入」），涵蓋美、英、澳三地。

**數字（逐字抄錄）**：
- 「on average, we find that an LSI approach has outperformed a DCA approach approximately two-thirds of the time」
- 12 個月期定期定額、60%股/40%債組合、滾動 10 年期間，LSI 勝出比例：
  - 美國（1926–2011）：**67%**（DCA 33%）
  - 英國（1976–2011）：**67%**（DCA 33%）
  - 澳洲（1984–2011）：**66%**（DCA 34%）
- 平均勝出幅度（60/40 組合，滾動 10 年期末平均值）：
  - 美國：DCA 平均終值 $2,395,824，LSI 平均終值 $2,450,264，**多 2.3%**
  - 英國：LSI 多 **2.2%**
  - 澳洲：LSI 多 **1.3%**
- 在美國，把 DCA 期間拉長到 36 個月時，LSI 在約 **90%** 的 10 年期間勝出

**來源機構**：The Vanguard Group（作者 Anatoly Shtekhman, CFA / Christos Tasopoulos / Brian Wimmer, CFA）
**網址**：https://militarymoneymanual.com/wp-content/uploads/2021/08/Dollar-Cost-Averaging-Just-Means-Taking-Risk-Later-Vanguard.pdf（Vanguard 官方 PDF 的第三方存檔鏡像，原始檔名 ICRDCA 072012）
**以…為準**：Vanguard research, July 2012
**信心等級**：verified（下載 PDF 全文逐頁讀取）
**備註**：Vanguard 官方網域 vanguard.com 對本文件的原始連結目前查無直接可下載頁面，改用 militarymoneymanual.com 與 passiveinvestingaustralia.com 兩個第三方存檔鏡像其中之一（內容含 Vanguard 版權頁與原始文件編號 ICRDCA 072012，可信為原文重製）。

### 2-B：Vanguard 2023「Cost averaging: Invest now or temporarily hold your cash?」

**事實**：2023 年 2 月發布，改用「CA（cost averaging，一次金額分 3 個月等額投入）」對比「LS（lump sum，單筆投入）」，資料為 MSCI World Index 1976–2022（另有各國指數見下）。

**數字（逐字抄錄）**：
- 「LS outperformed CA roughly two-thirds of the time」（全球市場、1976–2022）
- Figure 2：LS 勝 CA **68%** 的時間；CA 勝現金 69%；LS 勝現金 70%（3 個月分批、100% 股票、以一年後財富比較）
- Figure 3（60/40 組合，一年期，起始 $100,000，滾動期間中位數）：CA 平均終值 $107,453，LS 平均終值 $109,360，**多 1.8%**
- 100% 股票組合中位數：LS 比 CA 高 **2.2%**；40/60 組合：LS 比 CA 高 **1.2%**
- 加計現金利息（以 3 個月期美國公債利率為現金報酬）後：LS 仍勝 3 個月期 CA **65%** 的時間（100% 股票組合）
- 各國「LS 勝 CA」命中率（3 個月分批）：美國 66.4%（Russell 3000，1979–2022）、英國 68.1%（FTSE All-Share，1986–2022）、加拿大 67.2%（S&P/TSX，1985–2022）、歐洲 66.5%（MSCI Europe，1998–2022）、澳洲 67.5%（S&P/ASX 300，1992–2022）、新興市場 61.6%（MSCI EM，1988–2022）、全球（USD）67.7%（MSCI World，1976–2022）

**結論句（原文逐字）**：
> "Although the CA strategy won't, on average, produce higher returns, it is superior to remaining entirely in cash..."

**來源機構**：The Vanguard Group（作者 Megan Finlay / Josef Zorn, Ph.D., CFP®）
**網址**：https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf
**以…為準**：Vanguard research, February 2023
**信心等級**：verified（下載官方 PDF 全文逐頁讀取）
**備註**：2012 版與 2023 版方法不同（2012 版比的是「單筆 vs. 分批 6-36 個月」且用「10 年後終值」；2023 版比的是「單筆 vs. 分批 3-6 個月」且用「1 年後終值」），兩版「約 2/3」的結論數字巧合地接近（67% vs 68%），但不是同一份研究的兩個版本，是相隔 11 年的兩篇獨立報告，方法論不能互換引用。

---

## 3. Nick Maggiulli「Even God Couldn't Beat Dollar-Cost Averaging」（2019，ofdollarsanddata.com）

> **本條全部內容依作者指示，只能當「存在性線索＋方法描述」使用，不得當成可獨立佐證的數字來源**（部落格文章，非同行審查/機構研究）。

**事實**：2019-02-05 發表，作者 Nick Maggiulli。

**方法（原文逐字/釋義）**：
- 資料：美國股市（含股息、經通膨調整的實質報酬，S&P 500 為主）
- 情境設計：「Imagine you are dropped somewhere in history between 1920 and 1979 and you have to invest in the U.S. stock market for the next 40 years.」→ 也就是把起始年份從 1920 年到 1979 年逐一測試，每個起始年都投資 40 年（最晚可跑到 2018 年年底）
- 定期定額（DCA）定義：「You invest $100 every month for all 40 years.」
- 「Buy the Dip」定義：「You save $100 each month and only buy when the market is in a dip. A "dip" is defined as anytime when the market is not at an all-time high.」，且此策略被作者設定為「全知全能（God）」版本——永遠精準買在兩次歷史新高之間的最低點。

**主要結論數字（原文逐字，僅供參考、不當數字來源）**：
- 「Buy the Dip underperforms DCA over 70% of the time.」
- 「Missing the bottom by just 2 months lowers the chance of outperforming DCA from 30% to 3%.」（也就是只要抓錯底部 2 個月，跑贏 DCA 的機率從 30% 掉到 3%，等於 97% 的時間會輸給 DCA）
- 最佳情境（1928–1957，含 1932 年 6 月史上最大跌幅底部）：該區間 Buy the Dip 一度領先 DCA 最多達 **20%**；1932 年 6 月買在最低點的 $100，到期末實質成長為 **$4,000**
- 最差情境：1975 年起算的 40 年（因為錯過 1974 年的底部，且股市要到 1985 年才創新高，中間完全沒有「dip」可買），DCA 明顯勝出
- 額外提到的「時機運氣」對照組（非 DCA vs. Buy-the-Dip 的比較，是「哪個 40 年起始點運氣好」的比較）：1922–1961 這 40 年，總共投入 $48,000（40 年×12 月×$100）成長到超過 $500,000；最差的 1942–1981 這 40 年，同樣投入 $48,000 只成長到 $153,000，差距 226%，比 DCA 與 Buy-the-Dip 之間的差距還大

**來源機構**：Nick Maggiulli，Of Dollars And Data（個人部落格）
**網址**：https://ofdollarsanddata.com/even-god-couldnt-beat-dollar-cost-averaging/
**以…為準**：發表於 2019-02-05
**信心等級**：verified（實際打開文章全文讀取；但依規則，此類部落格內容本身只能當存在性線索+方法描述，不可當數字佐證）
**備註**：文中方法未使用嚴謹統計檢定，樣本為所有可能的 40 年滾動窗（1920–1979 起算，60 個窗口，重疊度高，不是獨立樣本）；「70% 的時間跑輸」是描述性統計，非顯著性檢定結果。

### Nick Maggiulli《Just Keep Buying》／中文版《持續買進》

**事實（存在性線索）**：
- 英文版：*Just Keep Buying: Proven Ways to Save Money and Build Your Wealth*，出版社 **Harriman House**，出版日期 **2022-04-12**（來源：搜尋摘要，Amazon／Harriman House／Pan Macmillan 條目）
- 繁體中文版：《持續買進：資料科學家的投資終極解答，存錢及致富的實證方法》，作者尼克．馬朱利（Nick Maggiulli），譯者李芳齡，出版社**商業周刊**，出版日期約 **2023-05-30**（來源：搜尋摘要，博客來／HyRead 電子書條目）

**來源機構**：Harriman House；商業周刊（Business Weekly, Taiwan）
**網址**：
- https://harriman-house.com/authors/nick-maggiulli/just-keep-buying/9780857199256
- https://www.books.com.tw/products/0011050392
**以…為準**：英文版 2022-04-12；中文版約 2023-05-30
**信心等級**：likely（僅在搜尋結果摘要中看到，未實際打開網頁逐字核對出版社/日期欄位）
**備註**：此條純屬存在性線索，未進一步查證版權頁或 ISBN 資料庫；若要寫入正式文件的版權資訊，建議另行打開博客來或國家圖書館 ISBN 查詢頁面核對一次。

---

## 4. J.P. Morgan「Impact of being out of the market」＋ 反方（錯過最差的日子）

### 4-A：J.P. Morgan Guide to Retirement — 最新版（2026 版，資料截至 2025-12-31）

**事實**：J.P. Morgan Asset Management《Guide to Retirement》2026 年版，第 41 頁「Impact of being out of the market」，S&P 500 Total Return Index，投資 $10,000，期間 **2006-01-02 至 2025-12-31（20 年）**。

**數字（逐字抄錄自圖表）**：
| 情境 | 年化報酬 | 期末金額 |
|---|---|---|
| 全程投入 | 11.0% | $80,619 |
| 錯過最好 10 天 | 6.6% | $35,866 |
| 錯過最好 20 天 | 3.8% | $21,177 |
| 錯過最好 30 天 | 1.6% | $13,826 |
| 錯過最好 40 天 | -0.3% | $9,462 |
| 錯過最好 50 天 | -1.9% | $6,763 |
| 錯過最好 60 天 | -3.4% | $4,966 |

**原文逐字（圖表旁註）**：
> "Six of the 10 best days occurred within two weeks of the 10 worst days"
> "Five of the six best days occurred after the worst days"
> "The second-worst day of 2020 — March 12 — was immediately followed by the second-best day of the year"

**來源機構**：J.P. Morgan Asset Management
**網址**：https://am.jpmorgan.com/content/dam/jpm-am-aem/global/en/insights/retirement-insights/guide-to-retirement-us.pdf
**以…為準**：Guide to Retirement 2026 版，圖表資料 "as of December 31, 2025"
**信心等級**：verified（下載官方 PDF 全文逐頁讀取，含圖表數字與旁註）
**備註（重要，請作者特別注意）**：
1. 作者原本引用的版本（2001-01-02 至 2020-12-31，全程投入 7.47%＝$42,231…最差 60 天 −6.81%＝$2,441，「最好 10 天有 7 天發生在最差 10 天兩週內」）是**更早一版**的同一張圖，本次查證**沒有找到**該確切版本的存檔可直接打開核對（JPM 官網只保留最新一版 PDF，未公開歷史版本的獨立連結；WebFetch 對 web.archive.org 存檔頁面此工具環境無法存取）。也就是說：作者原本的數字**本身沒有被本次查證推翻**，但也**沒有被本次查證重新驗證**——只能標示為 unverified（未查得原始檔案核對）。
2. 兩版比較：期間往後推移 5 年（2001-2020 → 2006-2025），年化報酬從 7.47%（舊版聲稱）變成 11.0%（新版，本次已驗證），「最好 10 天有 7 天在最差 10 天兩週內」這句話在新版改寫成「6 天中 5 天發生在最差日之後」，敘述方式與涵蓋天數都不同，兩者不是同一組數字，不可直接互相替換或平均。
3. 若要在文件中沿用作者原本那組 2001–2020 的數字，建議標註「來源：J.P. Morgan Guide to Retirement 舊版（約 2021 年版），本次查證未能重新調出該版 PDF 逐字核對，僅能存 unverified」。

### 4-B：反方——「錯過最差的日子」的效果（Javier Estrada, 2008）

**事實**：Javier Estrada（IESE Business School），"Black Swans and Market Timing: How Not to Generate Alpha"，*Journal of Investing*，Fall 2008，Vol. 17, pp. 20–34。

**方法**：道瓊工業指數（Dow Jones Industrial Average）1900-01-01 至 2006-12-31（29,190 個交易日，107 年），股價報酬（未含股息）。另外也分析 15 個國際股市（含以 S&P 500 代表的美股）1900s–2006 及 1990–2006 兩個窗口。

**數字（逐字抄錄，道瓊本體，Exhibit 1 Panel D）**：
- 全程持有：$100（1899-12-31 投入）→ **$25,746**（2006-12-31），年化複合報酬（MACR）**5.3%**
- 錯過最好 10 天：終值 **$9,008**（**−65.0%**），MACR **4.3%**
- 錯過最好 20 天：終值 **$4,313**（**−83.2%**），MACR **3.6%**
- 錯過最好 100 天：終值 **$83**（**−99.7%**），MACR **−0.2%**
- **避開最差 10 天**：終值 **$78,781**（**+206.0%**），MACR **6.4%**
- **避開最差 20 天**：終值 **$162,588**（**+531.5%**），MACR **7.2%**
- **避開最差 100 天**：終值 **$11,198,734**（**+43,396.8%**），MACR **11.5%**

**15 個國際市場平均（Exhibit 6，含美股 S&P 500）**：
- 錯過最好 10/20/100 天：終值分別減少 **50.8% / 70.7% / 97.7%**
- 避開最差 10/20/100 天：終值分別增加 **150.4% / 372.8% / 26,532.4%**

**原文逐字（摘要句）**：
> "On average across all 15 markets, missing the best 10 days resulted in portfolios 50.8% less valuable than a passive investment; and avoiding the worst 10 days resulted in portfolios 150.4% more valuable than a passive investment."

**來源機構**：Journal of Investing（IIJ）；作者任職 IESE Business School
**網址**：https://blog.iese.edu/jestrada/files/2012/06/BlackSwans.pdf（作者本人網站存檔的官方期刊 PDF 重製版，內含「IT IS ILLEGAL TO REPRODUCE THIS ARTICLE IN ANY FORMAT」版權警語）
**以…為準**：Journal of Investing, Fall 2008
**信心等級**：verified（下載全文 PDF 逐頁讀取，數字取自論文內 Exhibit 表格）
**備註**：這篇論文版權頁明白寫「禁止以任何形式重製本文」，本查證僅擷取其中的統計數字（表格數據）用於內部核對用途，不對外公開重製全文或大段文字；若文件要正式發表引用，建議之後改標準的期刊資料庫連結（如 JSTOR / IIJ 官網），不要直接連到這個作者自存的 PDF。另外，Meb Faber 也有類似「錯過最佳/最差日」的分析，但本次查證優先驗證了 Estrada 這篇（可直接打開全文核對表格數字），未再花額外次數查證 Meb Faber 版本；如需要 Meb Faber 版本作交叉比對，可另外排查證。

---

## 5. J.P. Morgan Guide to the Markets「S&P 500 intra-year declines vs. calendar year returns」（最新版）

**事實**：J.P. Morgan《Guide to the Markets – U.S.》第 17 頁「Annual returns and intra-year declines」，資料標示 **"Data are as of June 30, 2026"**（依 PDF metadata 建立時間 2026-07-02，屬於 2026 年第 3 季版）。

**數字（逐字抄錄，圖表標題）**：
> "Despite average intra-year drops of 14.2%, annual returns were positive in 35 of 46 years"

**原文逐字（頁尾來源與方法註）**：
> "Source: FactSet, Standard & Poor's, J.P. Morgan Asset Management. Returns are based on price index only and do not include dividends. Intra-year drops refers to the largest peak-to-trough decline during the year. Returns shown are calendar year returns from 1980 to 2025, over which the average annual return was 10.7%."

**核心數字**：
- 平均年內最大跌幅（intra-year drop）：**14.2%**
- 資料期間：**1980–2025，共 46 年**
- 46 年中有 **35 年**全年為正（另有 2026 YTD 一根柱子單獨標示、不計入 46 年統計）
- 該 46 年期間的平均年報酬：**10.7%**

**來源機構**：J.P. Morgan Asset Management（資料來源 FactSet、Standard & Poor's）
**網址**：https://am.jpmorgan.com/content/dam/jpm-am-aem/global/en/insights/market-insights/guide-to-the-markets/mi-guide-to-the-markets-us.pdf
**以…為準**：Guide to the Markets – U.S.，Data are as of June 30, 2026
**信心等級**：verified（下載官方 PDF 全文，並將該頁另外轉成圖片逐字核對頁尾小字來源說明）
**備註**：
1. 作者原本引用的版本是「平均年內跌幅 14.3%，41 年中有 31 年全年為正（1980–2020）」——與本次查證的最新版本相比：
   - 期間從 41 年（1980–2020）延長為 46 年（1980–2025），多了 2021–2025 共 5 年
   - 平均年內跌幅從 14.3%（舊版）微降為 14.2%（新版），數字非常接近、屬於自然的滾動更新
   - 正報酬年數從 31 年增加為 35 年，即新增的 5 年中有 4 年（2021、2023、2024、2025，依圖表柱狀為正值）是正報酬、1 年（2022，圖表顯示約 −7% 左右負值柱）是負報酬，31+4=35 對得上
   這代表作者原本引用的舊版數字本身內部邏輯是合理的（只是版本較舊），本次查證確認的是「最新版」而非「重新調出作者原本那一版逐字核對」，兩者可視為同一張圖表的前後兩個更新版本。
2. 頁尾小字（來源與方法論）在用一般 PDF 文字擷取工具時會因為顏色設定的技術性錯誤而讀不出來，本查證改用把該頁面轉成圖片再讀取的方式，才拿到完整頁尾文字，過程已如實記錄。

---

## 查證過程總覽（給作者的交代）

- 總計實際打開/下載並讀取全文的來源：Schwab 官網文章（curl 直接讀取 HTML）、Vanguard 2012 PDF、Vanguard 2023 PDF、Nick Maggiulli 部落格文章（curl 直接讀取 HTML）、J.P. Morgan Guide to Retirement 2026 PDF、J.P. Morgan Guide to the Markets 2026Q3 PDF、Javier Estrada 2008 論文 PDF。以上七份全部標記 verified。
- 僅在搜尋摘要中看到、未實際打開核對的：《Just Keep Buying》英文版與《持續買進》中文版的出版社/年份資訊。標記 likely。
- 查不到／未能重新核對的：作者原本引用的 J.P. Morgan Guide to Retirement 舊版（2001–2020 那組數字）——JPM 官網只保留最新版 PDF，這次沒能找到該舊版本的可直接開啟連結，標記 unverified，已在第 4-A 條備註詳細說明。
- 曾嘗試但被擋下、後來改道成功的網域：schwab.com、schwabassetmanagement.com、advisorservices.schwab.com、workplace.schwab.com、international.schwab.com 用 WebFetch 工具全部回 403；改用終端機 curl 直接抓取 schwab.com 的 HTML 才成功讀到全文（international/advisorservices/workplace 三個子網域最終未取得內容，因為已經在 schwab.com 本站拿到完整文字，未再重複嘗試）。
- 未使用網頁存檔（web.archive.org）：此工具環境的 WebFetch 明確回報「無法存取 web.archive.org」，因此第 4-A 條的舊版 JPM 圖表沒有走存檔路線去核對，是本次查證最大的缺口，如實告知。
- 大約使用了 20 次左右的網路擷取（WebSearch + WebFetch + curl 下載），在授權的約 30 次額度內完成，沒有為了湊滿額度而做無意義的重複查詢。
