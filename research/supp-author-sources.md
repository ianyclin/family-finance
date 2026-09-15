# 補充查證：作者自己的材料與兩個部落格

查證日期：2026-09-07
查證員角色：本文件只做查證，不做論述或改寫正文。鐵律：媒體／部落格／粉專只能當「存在性線索」，不能當數字來源；每個數字要能回推原文；不捏造網址。

---

## 1. Facebook 粉絲專頁「指數三寶飯」

- **主題**：作者提到的 FB 粉專「指數三寶飯」是否存在、簡介與近期貼文內容。
- **事實**：多輪搜尋（含 `site:facebook.com` 限定）皆找不到名為「指數三寶飯」的粉絲專頁。搜尋結果全部指向真實餐飲業的「三寶飯」（燒臘三寶飯，叉燒／油雞／燒鴨組合），與理財主題無關。也嘗試直接用 URL 猜測 `facebook.com/指數三寶飯`（URL-encode 後）以 WebFetch 開啟，回傳內容只有「Facebook」四字，判斷是登入牆／頁面不存在，抓不到任何簡介或貼文。
- **數字**：無。
- **來源機構**：無法確認機構／頁面存在。
- **網址**：
  - 嘗試 1：WebSearch「指數三寶飯 粉絲專頁 Facebook」→ 無關餐廳結果
  - 嘗試 2：WebSearch「"指數三寶飯" facebook.com」→ 無關餐廳結果
  - 嘗試 3：WebSearch「site:facebook.com 指數三寶飯」→ 全部是燒臘三寶飯貼文
  - 嘗試 4：WebFetch `https://www.facebook.com/%E6%8C%87%E6%95%B8%E4%B8%89%E5%AF%B6%E9%A3%AF`（即 facebook.com/指數三寶飯）→ 頁面內容僅「Facebook」，無法解析出粉專資訊
- **以…為準**：查無此頁，或該頁需要登入才能檢視，公開搜尋引擎未索引。
- **信心等級**：unverified
- **原文引述**：（無可引述內容）
- **備註**：這個粉專名稱很可能是作者記錯名稱、或是私人／小眾頁面沒有被公開索引，也可能已停用。建議請作者提供正確頁面網址或截圖，否則正文不應引用此來源的任何具體主張。

---

## 2. Podcast「人生不難 Life Lab」

- **主題**：podcast 節目簡介與各集標題／重點。
- **事實**：成功打開 Apple Podcasts 節目頁。節目由「老人」主持，屬自我成長類，2021 年更新、共 16 集，2021 年中結束連載。主持人自述是柏格頭（Boglehead）、指數化投資信徒。
- **數字**：共 16 集；Apple Podcasts 評分 5.0（315 則評論，數字為查證當下 Apple 頁面顯示值，會隨時間變動）。
- **來源機構**：Apple Podcasts（節目頁由節目方自行上傳簡介與集數資訊）。
- **網址**：https://podcasts.apple.com/tw/podcast/%E4%BA%BA%E7%94%9F%E4%B8%8D%E9%9B%A3-life-lab/id1554802167
- **以…為準**：Apple Podcasts 節目頁面文字（WebFetch 直接開啟並讀取，非僅搜尋摘要）。
- **信心等級**：verified
- **原文引述**：「大家好，歡迎來到人生不難、LifeLab。人生就是一場實驗，不管你喜不喜歡，面對它的各項挑戰是你終其一生的任務。」
- **備註**：實際抓到的部分集數標題與重點（依 Apple Podcasts 頁面，由新到舊列出前段）：
  - EP016（2021/05/28）〈十分之一的成功機率〉──收官集，用人生小故事說明節目宗旨
  - EP015（2021/05/21）〈投資的反智慧〉──用逆向思考談投資為何違反直覺
  - EP014（2021/05/13）〈金庸投資哲學之劍魔獨孤求敗（下）〉
  - EP013（2021/05/06）〈金庸投資哲學之劍魔獨孤求敗（上）〉
  - EP012（2021/04/30）〈給我一根槓桿，我將舉起地球〉──談資本主義本質與槓桿
  - EP011（2021/04/22）〈（老人的）指數化投資概論下〉──資產配置、再平衡、堅持
  - EP010（2021/04/15）〈（老人的）指數化投資概論上〉──費用控制、持續投入
  - EP009（2021/04/08）〈長期財務計畫〉──長期財務規劃與安全邊際
  （更早集數 EP001–EP008 頁面未完整讀出，若正文需要引用，建議另開頁面逐集核對。）
  這個節目與「指數化投資」「柏格頭」的主題高度吻合，作者若把它當存在性線索（證明「素人指數化投資者」確有其人在做內容）是合理的；但集數重點是查證員從節目頁摘要轉述，非逐字稿，不能當成投資報酬或具體數字的來源。

---

## 3. fourpillarfreedom.com「Accumulating $1 Million」／$100k 里程碑文章

- **主題**：作者引用「每年投入 $10,000、年報酬率 7%，累積到每個 $100k 里程碑所需年數」與「儲蓄 vs 報酬占比」的文章與數字。
- **事實**：找到並開啟 Four Pillar Freedom 部落格文章〈Why Saving Your First $100k is a Big Deal〉，文章開頭明確假設「每年投入 $10,000、年報酬率 7%」，並在文中提供：第一個 $100k 需要 7.84 年、第二個 $100k（$100k→$200k）需要 5.1 年、累積到 $1,000,000 總共需要 30.73 年。文章的完整逐段 10 個 $100k 區間表格與儲蓄/報酬占比拆解，是以圖表（可能是圖片形式）呈現，WebFetch 的文字擷取沒有拿到圖表裡逐格的數字，只拿到文字段落提到的三個數字（7.84 / 5.1 / 30.73）。
- **數字（自行用 Python 重算，驗證假設一致性）**：
  用「每年底投入 $10,000、年報酬率 7%、連續複利近似」的年金公式 FV(t) = C×[(1+r)^t − 1]/r 反解 t，得到與作者提供的清單完全一致：
  - 累積年數（逐年）：7.84 / 5.10 / 3.78 / 3.01 / 2.50 / 2.14 / 1.87 / 1.66 / 1.49 / 1.35（年），總和 30.73 年 —— 與文章提供的「第一個 7.84 年、第二個 5.1 年、總計 30.73 年」三個錨點完全吻合。
  - 各區間儲蓄 vs 報酬占比（假設投入視為區間內連續發生的近似）：78/22、51/49、38/62、30/70、25/75、21/79、19/81、17/83、15/85、14/86 —— 與作者給出的清單完全一致。
- **來源機構**：Four Pillar Freedom（個人理財部落格，非機構研究）。
- **網址**：https://fourpillarfreedom.com/why-saving-your-first-100k-is-a-big-deal/
- **以…為準**：WebFetch 直接開啟該頁面文字內容（拿到 3 個錨點數字與假設），加上本地 Python 重算驗證其餘數字的內部一致性。
- **信心等級**：likely（頁面確實開啟且拿到假設與 3 個關鍵錨點數字，完全對得上；但完整 10 欄表格因原頁面以圖表呈現、文字擷取抓不到，未能逐格對照原文，故不列 verified）
- **原文引述**：（WebFetch 摘要轉述，非逐字擷取）「文章的核心論點是：存到第一個 $100k 要花很多年，但跨過這個門檻之後，複利會讓淨資產加速成長；儘管每年投入金額不變，投資報酬的貢獻會隨淨資產增加而愈來愈大。」
- **備註**：作者材料裡的完整清單（7.84/5.1/3.78/3.01/2.5/2.14/1.87/1.66/1.49/1.35 年；78/22 到 14/86 的占比）已用 Python 獨立重算確認，數學上完全站得住腳，且與 Four Pillar Freedom 文章的三個錨點數字一致。**正文應該用本文自算版**（重算腳本見下），只把這篇文章當「有人這樣畫過類似圖表」的存在性線索，不要直接引用該站的圖表數字當一手數據，因為：(a) 該站是個人部落格非機構研究、(b) 完整表格本身查證員未能逐格核對原圖。

  重算所用 Python 邏輯（可重現）：
  ```python
  import math
  C, r = 10000, 0.07
  def t_for_balance(FV):
      return math.log(FV*r/C + 1) / math.log(1+r)
  milestones = [100000*i for i in range(1,11)]
  cum_times = [t_for_balance(m) for m in milestones]
  # 逐年增量與占比另由 cum_times 差分計算
  ```

---

## 4. IFA.com「Style Drifters」與資產類別輪動圖

### 4a. IFA.com Style Drifters: Countries

- **主題**：作者提到 IFA.com「Style Drifters: Can You Pick the Next Country Winner?」頁面的資料來源說明。
- **事實**：查無獨立網頁完全符合「Can You Pick the Next Country Winner?」這個標題字串（WebSearch 多次查詢皆未命中）。但找到 IFA.com 投資組合頁面 `ifa.com/portfolios/50/`（IFA Index Portfolio 50 S2B2），該頁列出 15 張分析圖表，其中第 13 張是「Style Drifters: Asset Classes」、第 15 張是「Style Drifters: Countries」，主題與作者描述相符（用圖表說明「各國股市輪流領先，難以預測下一個贏家」）。頁面另有兩支相關短片：「Step 6: Style Drifters in Under a Minute」與「Step 6: Style Drifters - Know What You're Buying」，內容用穀片比喻說明「style drift」（基金風格漂移）概念，但影片頁面文字說明本身沒有寫出用了哪些指數、哪個期間（該資訊可能只出現在嵌入的影片語音或圖表本身，文字爬取抓不到）。
- **數字**：無（頁面未在文字部分列出具體指數清單或年份區間）。
- **來源機構**：Index Fund Advisors, Inc.（IFA.com）
- **網址**：
  - https://www.ifa.com/portfolios/50/（找到「Style Drifters: Countries」圖表所在頁）
  - https://www.ifa.com/videos/step-6-style-drifters-know-what-youre-buying
  - https://www.ifa.com/videos/step-6-style-drifters-under-a-minute
- **以…為準**：WebFetch 直接開啟 `ifa.com/portfolios/50/` 頁面文字。
- **信心等級**：likely（確認 IFA.com 上確實有「Style Drifters: Countries」這類圖表存在，主題吻合；但「Can You Pick the Next Country Winner?」這個確切標題、以及圖表所用指數與期間，未能在文字內容中直接核對到，故不到 verified）
- **原文引述**：頁面免責聲明原文：「The data provided in charts referring to IFA Index Portfolios is hypothetical back-tested performance and is not actual client performance. Performance data for the IFA Index Portfolios is shown net of IFA's highest advisory fee and the underlying mutual fund expenses.」以及「None of the data reflects trading costs or taxes, which would have lowered performance.」
- **備註**：這頁的效能數字明確標示是「假設性回測（hypothetical back-tested）」，不是真實客戶績效 —— 這點如果正文要引用 IFA.com 的任何報酬數字，必須把這句警語一併帶到，不能只取圖表結論。建議請作者提供他實際看到「Can You Pick the Next Country Winner?」字樣的網址或截圖，因為公開搜尋與這次能開啟的頁面都對不上這個確切標題。

### 4b. 資產類別輪動圖（Novel Investor「Asset Class Returns」）

- **主題**：資產類別輪動圖（quilt chart）的資料來源說明——用哪些指數、涵蓋哪個期間。
- **事實**：成功開啟 Novel Investor 的「Asset Class Returns」頁面。頁面列出 8 個資產類別各自對應的指數，並涵蓋近 15 年資料（查證當下頁面顯示至 2026 年 6 月 30 日）。
- **數字**：涵蓋期間為近 15 年（頁面當前版本顯示 2011–2025，資料截至 2026/6/30；此頁會隨時間持續更新滾動，之後查證需重新確認年份區間）。
- **來源機構**：Novel Investor（個人理財部落格，非官方指數機構——但它是直接引用官方指數名稱）
- **網址**：https://novelinvestor.com/asset-class-returns/
- **以…為準**：WebFetch 直接開啟頁面文字內容。
- **信心等級**：verified（頁面直接開啟，指數清單與期間文字明確列出）
- **原文引述**：（轉述整理，非逐字擷取全文，指數對照如下，逐一列出於備註）
- **備註**：頁面列出的資產類別與對應指數：
  | 資產類別 | 指數 |
  |---|---|
  | 大型股 | S&P 500 Index |
  | 小型股 | Russell 2000 Index |
  | 國際已開發市場股票 | MSCI EAFE Index |
  | 新興市場股票 | MSCI Emerging Markets Index |
  | 不動產投資信託（REITs） | FTSE NAREIT All Equity Index |
  | 投資等級債券 | Bloomberg U.S. Aggregate Bond Index |
  | 高收益債券 | ICE BofA US High Yield Index |
  | 現金 | S&P U.S. Treasury Bill 0-3 Mth Index |

  頁面聲明報酬為「年度總報酬（含配息再投資），不含費用」，並附「過去績效不代表未來表現」的一般警語。若正文要用這張圖當存在性線索沒問題，但具體逐年報酬數字要用官方指數資料（如 S&P Global、MSCI 官網）或 JPM Guide to the Markets 這類機構原始資料，不要直接搬 Novel Investor 網站上的逐年數字。

---

## 5. 「短期／中期／長期」目標分桶（bucket）概念的一手出處

- **主題**：財務目標依時間長短分桶（bucket strategy）概念最早出自何處。
- **事實**：多個獨立來源（Moneycrashers、Capital Group、Morningstar 等機構文章）一致指出：bucket 策略最早由財務規劃師 Harold Evensky 於 1985 年提出，原本是「現金桶＋投資桶」兩桶制（不預留超過 5 年生活費在投資桶以外），後續才演變成三桶制（現金／中期／長期成長）。這是查證員能找到、多來源互相印證的說法，但沒有直接打開 Evensky 本人 1985 年原始文章或期刊（搜尋沒有找到可公開存取的原始 1985 年文獻連結）。
- **數字**：起始年份 1985 年；原始設計為「至少 5 年生活費現金儲備」。
- **來源機構**：多為財務規劃業界二手轉述（Moneycrashers、Capital Group、Morningstar、Financial Planning Association 等），非 Evensky 本人網站或期刊一手來源。
- **網址**：
  - https://www.moneycrashers.com/three-bucket-strategy-retirement/
  - https://www.capitalgroup.com/advisor/practicelab/articles/bucket-strategy-retirement-income.html
  - https://www.morningstar.com/retirement/how-retire-consider-retirement-bucket-portfolio-strategy （morningstar.com 已知對 WebFetch 回 403，只能引用搜尋摘要）
  - https://www.financialplanningassociation.org/article/journal/SEP13-benefits-cash-reserve-strategy-retirement-distribution-planning
- **以…為準**：以上均為 WebSearch 搜尋摘要，查證員未能直接 WebFetch 開啟逐一核對全文（時間所限，且部分站點對自動化抓取有限制）。
- **信心等級**：likely（多個獨立二手來源說法一致，指向同一個人、同一年份、同一機制，可信度高，但未觸及一手原始文獻，不能標 verified）
- **原文引述**：（轉述）「Evensky 描述他原始的做法為『五年箴言』（five-year mantra）──永遠不要投資五年內會用到的錢。」
- **備註**：另外嘗試尋找 J.P. Morgan《Guide to Retirement》裡對應的「目標分層／time segmentation」頁面作為機構版一手來源，搜尋只找到第三方轉述與相關同主題文章（Hunt Country Wealth Management、Seeking Alpha 等），沒有找到可直接開啟的 JPM 官方 PDF 特定頁碼，故此節暫缺機構版一手來源，標記為 unverified 待補：若要在正文引用「JPM 也用類似分桶邏輯」，建議直接向 J.P. Morgan Asset Management 官網下載當期《Guide to Retirement》PDF 核對頁碼，而不要引用本次搜尋到的三方轉述。

---

## 查證方法總覽（供覆核）

本次共執行約 20 次 WebSearch／WebFetch（在授權的約 30 次額度內）。已知對 WebFetch 回 403 的網域（spglobal.com、morningstar.com、nhi.gov.tw）本次未直接測試，但 morningstar.com 的一則搜尋結果因此只能標記為搜尋摘要層級，未強行抓取。web.archive.org 曾嘗試一次（查 fourpillarfreedom 舊版頁面），但此環境的 WebFetch 工具回報「無法抓取 web.archive.org」，故放棄存檔路線，改以直接開啟現存頁面＋自行用 Python 重算驗證內部一致性的方式補強信心等級。

尚待作者確認或補件的項目：
1. FB 粉專「指數三寶飯」的正確網址（目前查無此頁）。
2. IFA.com「Can You Pick the Next Country Winner?」的確切頁面網址（目前只找到主題相符但標題不同的 `ifa.com/portfolios/50/`）。
3. JPM《Guide to Retirement》分桶頁面的官方 PDF 與頁碼一手核對。
