驗證完成。以下是判決書。

---

# 總判：**有條件可用**

兩個舊帳都查清了，而且都指向「書上現在的數字沒有錯，但都是舊版／舊口徑」。沒有任何一條是「書上寫錯數字」；但有兩條會讓結論改變（`實質`），兩條是交件說明本身不準（`阻斷級的事實描述錯誤`，因為它會誤導修法的人去改錯地方）。

---

## 發現清單（依嚴重度）

### 1. `阻斷`（針對交件說明，不是針對書）：交件說「第 1 節（`ten`）也有一句摘要」是錯的。那句在**第 3 節（`why`）**，而且交件漏掉了**第 16 節（`s12`）也帶著 0.4 與 1.1 這兩個數字**。

我沒有用交件給的清單，是對 HEAD 快照全檔掃「個百分點／Morningstar／落差」的全集。結果：

| 行號 | 節 | 是否在摺疊 | 逐字（節錄） |
|---|---|---|---|
| L229 | 第 3 節 `why` | 在 `<details class="more" data-print="open">` 內 | 「美國的基金投資人實際拿到的，比基金公布的成績**十年平均一年少約 1 個百分點**；其中多少是真的做錯時間，研究有爭議（有研究重算只有**約 0.1 個百分點**）」 |
| L2289 | 第 12 節 `s9` | **主線，不在摺疊** | 「Morningstar 2024 年估算：同一批基金，基金本身平均年化約 **7.3%**，投資人實際拿到約 **6.3%**，落差 **1.1 個百分點**。」 |
| L2290 | 第 12 節 `s9` | 在 `<details class="more">` 內（無 `data-print`，列印不展開） | 「…Fulkerson 等人 2026 年用 **Morningstar 2025 年版、2015–2024 的樣本重算，那一版的落差是 1.2 個百分點，擇時失誤只占每年約 0.1 個百分點**。」「只買單一產業的產業型基金，落差約 **2.6** 個百分點；股票債券已經混好的配置型，約 **0.4**。」「原報告註明：各數字四捨五入後相減未必等於落差。」 |
| L2337 | 第 12 節 `s9` 來源卡 | `<details class="source-card" data-print="open">` | 「Morningstar：Mind the Gap 2024（研究 PDF）／行為落差估算」＋「Fulkerson, Jordan, Riley & Yan (2026), Financial Analysts Journal **82(3): 34–42**／用 Morningstar 2025 版（2015–2024）的**同一樣本**重算，擇時失誤只占每年約 0.1 個百分點」 |
| **L2927** | **第 16 節 `s12`** | **主線，不在摺疊** | 「（第 12 節：股債已經混好的配置型基金，投資人的行為落差約 **0.4** 個百分點，比平均的 **1.1** 小）」 |
| L3069 | 第 18 節 `sidepaths` | **主線，不在摺疊** | 「第 12 節的美國研究裡，**產業型基金的行為落差（…）最大**。」 |

第 1 節 `ten`（L143–151）掃過，**零個** Morningstar／落差字樣。`grep -c` 回 0。
（另：L3294／L3298 的 Morningstar 是退休提領率 3.9%，不同主題，不在本次範圍。）

---

### 2. `實質`：最新版是 **Mind the Gap 2026**，官方數字全部查到，交件裡「未經查證」的那一組是**對的**。

**官方一手，逐字引：**
> "The average dollar invested in US mutual funds and exchange-traded funds earned **8.7%** annually over the trailing 10 years ended **Dec. 31, 2025**. That's about **1.2 percentage points** per year less than these funds' **9.9%** aggregate annual total return over that span, equivalent to about **12% of the funds' aggregate return**."
> — Jeffrey Ptak, CFA, *The Winning Formula for Fund Investors, and Why Others Left Money on the Table*, **Aug 6, 2026**
> https://www.morningstar.com/funds/winning-formula-fund-investors-why-others-left-money-table

> "On a positive note, the average dollar invested in US stock funds and ETFs gained **12.8%** per year, just shy of the funds' **13.3%** aggregate annual return…"

> "That's the bad news/good news story from **the 2026 edition of our long-running Mind the Gap study**."

**分類別落差**——Morningstar 掛在該篇圖說下的官方 CSV（「Annual Investor Return Gaps by Category Group (10 Years Ended Dec. 31, 2025)」），我用 curl 讀到 stdout、未存檔：
https://cosmos-cdn.morningstar.com/playfair/01KWADCER3313KZ6691RX3SHDE/data.csv

```
US Category Group,Investor Return,Total Return,Gap
Allocation,7.77%,8.43%,-0.66%
Alternative,2.56%,4.11%,-1.55%      ← 最大
International Equity,7.78%,8.85%,-1.07%
Municipal Bond,1.09%,2.23%,-1.14%
Sector Equity,9.36%,10.58%,-1.22%
Taxable Bond,1.94%,2.97%,-1.03%
U.S. Equity,12.85%,13.29%,-0.44%    ← 最小
Overall,8.72%,9.89%,-1.17%
```

自算核對：8.72/9.89 = 88.2%，落差＝11.8%，對得上正文的 "about 12%"。

**所以「產業型落差最大」在最新版已經不成立。** 2026 版最大的是 alternative（另類）1.55，產業型 1.22 排第二；最小的是美國股票型 0.44，配置型 0.66 排第二。官方正文自己也只敢寫：
> "…investors in allocation funds… captured a larger share of those funds' total returns than they did in other types of funds, **the only exception being US equity**."

---

### 3. `實質`：2025 年版（Fulkerson 重算的那一版）官方數字查到，書上引的 1.2 是對的；而且 **2025 年版裡產業型仍是最大**。

live 頁被 AWS WAF 擋（403），改讀 Wayback 的 200 快照 `20250814033514`：
> "We estimate the average dollar invested in US mutual funds and exchange-traded funds earned **7.0%** per year over the decade ended **Dec. 31, 2024**. … about **1.2 percentage points** per year less than these funds' **8.2%** aggregate annual total return… equivalent to around **15%** of funds' aggregate total return"
> "In absolute terms, investors in **sector equity funds saw the largest shortfall**… the average dollar gained 7.0% per year compared with the funds' aggregate 8.5% annual total return."
> "Investors in **allocation funds captured the largest share**… 6.3% per year dollar-weighted return accounting for **nearly 97%** of the funds' 6.5% aggregate annual total return."
> — *The More Investors Traded, the Less Their Average Dollar Made*, Aug 13, 2025
> 原址 https://www.morningstar.com/financial-advisors/volatility-bedevils-fund-investors ／快照 https://web.archive.org/web/20250814033514/https://www.morningstar.com/financial-advisors/volatility-bedevils-fund-investors

官方圖 3 的 CSV（https://cosmos-cdn.morningstar.com/playfair/01K0A5QYRERXMSQ8Y8XJJS63CB/data.csv ）：
```
Allocation -0.14 / Alternative -0.10 / International Equity -1.11 / Municipal Bond -1.16
Sector Equity -1.50 / Taxable Bond -0.98 / U.S. Equity -0.57 / Overall -1.20
```

---

### 4. `次要`（好消息）：書上 2024 年版的五個數字，逐字對得上官方原文。

Wayback 200 快照 `20240815150442`：
> "Fund investors earned a **6.3%** per year dollar-weighted return ("investor return") over the **10 years ended Dec. 31, 2023**, while their fund holdings earned about **7.3%** per year ("total return")."
> "The **1.1-percentage-point** annual estimated return gap—which is equivalent to around 15% of funds' aggregate average total return…"
> "**Allocation funds had the narrowest gap (negative 0.4 percentage points** per year over the 10 years ended Dec. 31, 2023…)"
> "…**sector equity funds had the widest gap (lagging by negative 2.6 percentage points** annually)"
> 原址 https://www.morningstar.com/personal-finance/fund-investors-who-kept-it-simple-captured-more-return

書上 L2289／L2290／L2927 的 7.3、6.3、1.1、2.6、0.4 **全部正確**，L3069 的「產業型最大」對 2024 版也**正確**。書沒寫錯，只是停在兩版以前。
書上「原報告註明：各數字四捨五入後相減未必等於落差」也對得上官方圖說 "Gap numbers may not match differences in returns because of rounding."

---

### 5. `實質`：**台灣 1,094 對 971 的謎底 —— 971 是 2022 年底的數字**，不是口徑差。

證期局〈上市、櫃各年度家數〉，更新日期 2026-03-26：
https://www.sfb.gov.tw/ch/home.jsp?id=1010&parentpath=0,4,109

逐字（表格內容）：
```
年度/家數 | 上市公司 | 上櫃公司
2020 948 782 / 2021 959 788 / 2022 971 808 / 2023 997 816 / 2024 1031 838 / 2025 1063 874
```

**971 ＝ 2022 年底。** 舊交班把 2026 年 9 月的自算拿去跟 2022 年底的官方數字比，所以「差 123 家」；更舊那句「差 11 家」則兩邊都算不起來，來源不明。**這不是口徑問題，是拿錯年份。**

---

### 6. `實質`：真正的口徑差只有一項 —— **書上的 1,094 含 10 檔 TDR**（官方家數不含）。

我直接打證交所同一支開放資料（出表日期 1150919＝2026-09-19，筆數仍是 1,094）：
https://openapi.twse.com.tw/v1/opendata/t187ap03_L

拆開來是：
- 1,094 筆 ＝ 本國 992 ＋ 第一上市外國 92（全是 KY 開曼）＋ **產業別 91 的存託憑證（TDR）10 筆**
  （外國企業註冊地國：KY 96、BM 3、TH 2、SG 1 ＝ 102，其中 10 筆是 -DR）
- 含 30 家創新板（簡稱以「-創」結尾）
- 上市日期 ≤2003-12-31：**549 筆**（其中 2 筆是 TDR：9103 美德醫療-DR、9105 泰金寶-DR）→ 只算公司是 **547**
- 上市日期 >2003：545 筆（含 8 筆 TDR）→ 只算公司是 **537**

**口徑對帳（不是猜，是對得起來的恆等式）：**
```
1,094（今天全部筆數）
 − 25（2026 年新上市，自 openapi 上市日期 ≥20260101 數）
 + 4 （2026 年終止上市：115/01/22 億而得-創、115/03/27 晶睿、115/06/23 森崴能源、115/09/01 三商壽，
       出自 https://openapi.twse.com.tw/v1/company/suspendListingCsvAndHtml）
 − 10（TDR）
 = 1,063  ＝ 證期局 2025 年底上市公司家數（完全吻合）
```
反證：若官方含 TDR，回推是 1,073（差 10）；若官方不含創新板，回推是 1,041（差 22）；若官方不含 KY，回推是 974（差 89）。三個都對不上。**所以官方口徑＝本國＋第一上市 KY＋創新板，不含 TDR**；今天對應官方口徑的家數是 **1,084**。

書上多的 10 家，就是 TDR。誤差 0.9%，「大約一半」「545 家是 2004 年以後才上市」這兩個結論不會翻轉（537/1,084 ＝ 49.5%）。

**注意：我沒有找到證期局逐字寫出這個口徑的註腳**——該頁沒有任何附註。上面是靠三方對帳推出來的，請在文字上照這樣標示。

---

### 7. `次要`：書上第 7 節小字把 549 說成「上市公司」，但那 549 含 2 檔 TDR。

逐字（L1462，主線，在 `<details class="more">`「想深入：一家對上整群的其餘數字…」摺疊內）：
> 「台灣沒有同一種研究，但『名單一直在換人』查得到：2003 年底台灣有 **669** 家上市公司，今天名單上還在的是 **549** 家；今天的 **1,094** 家裡，有 **545** 家是 2004 年以後才上市的。」

小字（L1463）：
> 「台灣那三個數字是本文自己數的：669 家出自證交所 60 週年專刊的歷年上市公司家數，**549 家與 1,094 家出自證交所開放資料〈上市公司基本資料〉（出表日 2026 年 9 月 17 日）裡的上市日期**。不在名單上不等於倒閉…所以 549 家是下限。」

來源卡（L1469）另寫：「出表日 2026 年 9 月 17 日，名單 1,094 家；其中上市日期在 2003-12-31 以前的 549 家、之後的 545 家是本文自算」。

問題：669（證交所〈歷年上市公司家數〉，應為公司家數）對上 549（含 2 檔 TDR），分母分子口徑不同一步。影響極小（549→547，82.1%→81.8%），但小字已經很誠實地列了三個但書，再加一句 TDR 成本很低。

---

### 8. `次要`：`tools/calc_core.py` 的數字與書一致，腳本沒有做 TDR 過濾。

`/Users/linyenchu/Cladue Code/family-finance/tools/calc_core.py:1015-1025`：
```python
'listed_end_2003': 669, 'today_total': 1094,
'today_listed_on_or_before_2003': 549, 'today_listed_after_2003': 545,
'still_listed_share_pct': r1(549 / 669 * 100),
'after_2003_share_pct': r1((1094 - 549) / 1094 * 100),
```
`basis` 只寫「資料筆數自算」——**「筆數」這個字其實是準的**，它數的就是筆數，不是家數。沒有任何地方按 `產業別 != '91'` 過濾。`assert` 只檢查 1094−549==545。

---

### 9. `次要`：兩張官方圖對「整體落差」給了兩個小數（−1.15 與 −1.17），都四捨五入到 1.2。

2026 版第一張圖的 CSV（https://cosmos-cdn.morningstar.com/playfair/01KWABTTR3NQYWD8RNMBKEYP5W/data.csv ）是 `Total Return 9.89% / Gap -1.15% / Investor Return 8.74%`（排除 funds of funds），類別表是 `Overall 8.72/9.89/-1.17`（只排除 commodities）。若要更新，**只引 1.2，不要引小數**。

---

### 10. `次要`：同專案的 `chapters/` 版本用的是另一版，兩個產品數字不一致；而且它的「轉引待核」現在可以升級。

`/Users/linyenchu/Cladue Code/family-finance/chapters/08-risk-diversification-cost.html:357`：
> 「Morningstar「Mind the Gap」2025 年版（經 CNBC 轉述）· 2015–2024 年基金投資人實際年化 7.0%，買進持有為 8.2%，落差約 1.2 個百分點 · 查證 2026-09-07（官方原文遭 403 阻擋；轉引，待官方原檔核對…）」

這組 7.0／8.2／1.2 我這輪已經對到 Morningstar 官方原文（見發現 3），可以把「轉引」改成「已核」。但 `guide` 用 2024 版、`chapters` 用 2025 版，同一個專案兩個數字，讀者交叉看會錯亂。

---

### 11. `疑問`（未查證）：Fulkerson 那篇的「0.10 個百分點」與「用 2025 年版的樣本」，我這輪無法從一手來源證實。

- Crossref 官方 metadata **證實**了書上來源卡的書目：
  `title: "Bad Timing Does Not Cost Investors 15% of Their Funds' Returns: An Examination of Morningstar's 'Mind the Gap' Study"`，`Financial Analysts Journal`，`volume 82, issue 3, page 34-42`，`published 2026-05-12`，作者 Fulkerson Jon／Jordan Bradford／Riley Timothy／Yan Qing。**書上寫的 82(3): 34–42、2026，完全正確。**
- 但 tandfonline（DOI 直連）、SSRN 4904652 都回 **403**，Crossref 沒有 abstract。**「擇時失誤只占每年約 0.1 個百分點」與「用的是 2025 年版樣本」這兩點，我沒讀到原文，未查證。**
- 旁證（不足以當證據）：SSRN 工作稿標題是 "…One Fifth of Their Funds' Returns…"，正式刊出版改成 "…15%…"；「15%」在 2024 版與 2025 版**都**出現過，所以標題無法用來判定它重算的是哪一版。論文 2026-05 刊出，介於 MTG 2025（2025-08）與 MTG 2026（2026-08）之間，時序上與「2025 年版」相容。
- 另註：來源卡 L2337 仍寫「用 Morningstar 2025 版（2015–2024）的**同一樣本**重算」。正文 L2290 已經照舊審改成「的樣本」，來源卡的「同一」沒跟著拿掉。在來源卡的語境下不算錯（同一＝那一版的），但用字不一致。

---

## 未能查證的範圍（以及要下載哪個檔）

| 我拿不到的東西 | 網址 | 大小 | 為什麼 |
|---|---|---|---|
| **Mind the Gap 2026 全文報告 PDF** | 入口頁 https://www.morningstar.com/business/insights/research/mind-the-gap | 取不到（入口頁被擋，PDF 直鏈未曝光） | AWS WAF JS 挑戰，curl 只拿到 HTTP 202 / 2,029 bytes 的挑戰頁。**文章正文＋官方圖表 CSV 已足以覆蓋書上要用的全部數字，不下載這份 PDF 也能改書。** |
| Fulkerson 等 (2026) FAJ 全文／摘要 | https://www.tandfonline.com/doi/full/10.1080/0015198X.2026.2657253 ／ https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4904652 | — | 兩邊都 403 |
| 證期局〈證券暨期貨市場 115 年 8 月份重要指標〉 | https://www.fsc.gov.tw/userfiles/file/20260915.zip | **2,289,539 bytes（2.18 MB）**，last-modified 2026-09-15 | 只以 zip 發佈，無 HTML 版。若要「2026 年 8 月底的官方上市家數」逐字引，需要這個檔 |
| 證交所《證交所 60 週年》專刊 P15（書上 669 的出處） | https://www.twse.com.tw/staticFiles/product/publication/twse60/P15.pdf | **2,108,424 bytes（2.01 MB）**，HTTP 200 可用 | 純 PDF。**669 這個數字本輪未核**；證期局的年度序列只到 2010（758），無法回推 2003 |
| 書上來源卡引的 2024 版 PDF | https://assets.contentstack.io/v3/assets/blt4eb669caa7dc65b2/blt0571178b63219c0b/66bdeb4a4f0e4749e15a5621/2024_Mind_the_Gap.pdf | 1,339,939 bytes，HTTP 200（連結仍有效） | 未下載；該版數字已由官方文章逐字核過 |
| 證期局年度家數的**口徑註腳** | https://www.sfb.gov.tw/ch/home.jsp?id=1010&parentpath=0,4,109 | — | 該頁沒有任何附註。TDR／KY／創新板的納入與否是我用對帳推出來的，不是官方逐字說明 |
| 2026 年 8–9 月「當月」官方家數 | — | — | 只查到年度序列（到 2025 年底 1,063）＋ 開放資料現況（1,084 家公司）。月頻官方數字在上面那個 zip 裡 |

另外：WebSearch／WebFetch 在本次 session 被停用，全部網路查證是用 `curl` 完成的；搜尋引擎（DuckDuckGo、Mojeek、Bing）全部回 captcha 或垃圾結果，文章網址是從 **Google News RSS ＋ Morningstar 自家 sitemap**（`media.morningstar.com/arc/outboundfeeds/sitemap3/2026-08-06/`）逐日比對找出來的。Morningstar 對 Chrome UA 會鎖 IP，換 Firefox UA 才通。所有網頁與 CSV 都是 pipe 到 stdout 讀的，**沒有任何檔案寫入磁碟，沒有動任何專案檔**。

---

## 總表

| 項目 | 書上現況（`guide/index.html` @HEAD） | 官方數字（已查證） | 建議 |
|---|---|---|---|
| MTG 版次 | 2024 版（10 年到 2023 年底） | **2026 版，2026-08-06 發表**，10 年到 2025-12-31 | 更新（見下方修法） |
| 整體：基金／投資人／落差 | 7.3% ／ 6.3% ／ 1.1（L2289） | **9.9% ／ 8.7% ／ 1.2**（原始 9.89/8.72/−1.17） | 三個數字一起換；只寫 1.2，不寫小數 |
| 產業型落差 | 2.6（L2290） | **1.22 → 1.2** | 換數字 |
| 配置型落差 | 0.4（L2290、L2927） | **0.66 → 0.7** | 兩處一起換 |
| 「產業型最大」 | 成立（L3069，主線） | **2026 版不成立**：最大是另類 1.55；產業型 1.22 第二 | 必須改（見下方 B 案） |
| 最小落差類別 | 書未明講 | **美國股票型 0.44**，配置型 0.66 第二 | 若補寫「最小」，不能寫配置型 |
| 2025 版落差（Fulkerson 用的那版） | 1.2（L2290、L2337） | **1.2（−1.20）確認正確**；該版產業型 1.50 最大 | 不用改 |
| 擇時失誤 0.1 個百分點 | L229、L2290、L2337 | **未查證**（tandfonline／SSRN 皆 403） | 維持現狀＋保留「有爭議」語氣；或在內部研究檔標 likely |
| Fulkerson 書目 82(3): 34–42, 2026 | L2337 | **Crossref 證實完全正確** | 不用改 |
| 第 3 節「一年少約 1 個百分點」 | L229 | 1.1／1.2／1.2 三版都成立 | **不用改**（這句是版次免疫的） |
| 台灣 1,094 | 主線與小字（L1462/L1463）、來源卡（L1469） | 對應官方口徑是 **1,084 家**；1,094 是「資料筆數」，含 **10 檔 TDR** | 最小修法：小字加一句口徑（見下方） |
| 549 家 | L1462 | 含 2 檔 TDR，純公司是 **547** | 同上，一句話涵蓋 |
| 545 家 | L1462／來源卡 | 含 8 檔 TDR，純公司是 **537**；「大約一半」仍成立 | 同上 |
| 「證期局 971」 | 交班文件 `docs/handoff-guide-2026-09-19.md:292` | **971 ＝ 2022 年底**；2025 年底是 **1,063** | 結案：拿錯年份，不是口徑差 |
| 669（2003 年底） | L1462／來源卡 | **本輪未核**（只在 2 MB 的 60 週年 PDF 裡） | 留待下一輪，或接受現有 PDF 出處 |

---

## 修法建議（與上面的發現分開；我沒有改任何檔）

**A. Morningstar 更新，最小改動是五處（不是交件說的三處）：**
1. `guide/index.html` L2289 主線：`2024 年` → `2026 年`；`7.3%`→`9.9%`、`6.3%`→`8.7%`、`1.1`→`1.2`；建議補上期間「到 2025 年底的十年」（現在書上完全沒寫窗口，讀者無從判斷版次）。
2. L2290 摺疊：`1.1`→`1.2`；`2.6`→`1.2`（產業型）、`0.4`→`0.7`（配置型）。Fulkerson 那句**不動**（它講的是 2025 版，仍然正確）。
3. L2337 來源卡：MTG 2024 PDF 連結 → 2026 版入口 https://www.morningstar.com/business/insights/research/mind-the-gap ，或改掛可直接讀的官方文章 https://www.morningstar.com/funds/winning-formula-fund-investors-why-others-left-money-table 。順手拿掉 Fulkerson 註記裡多餘的「同一」二字。
4. **L2927（第 16 節，主線）**：`0.4`→`0.7`、`1.1`→`1.2`。交件沒提到這處，漏改會讓書內自相矛盾。
5. **L3069（第 18 節，主線）**：見下。

**B. L3069「產業型最大」二選一：**
- B1（保版次）：改成「第 12 節引的 Morningstar **2024 年版**裡，產業型基金的行為落差最大」——但這和主線改成 2026 版後會打架，不建議。
- B2（不排名，推薦）：改成不做排名的陳述，例如「主題越窄、越容易追著熱度買賣的基金，投資人實際拿到的和基金公布的差距通常越大（第 12 節）」。2024／2025／2026 三版都支持這句。
- B3（照 2026 版重寫）：「落差最大的是另類基金，產業型排第二」——但另類基金不在這本書的讀者範圍，講了反而分心。

**C. 第 3 節 L229 不用動。**「十年平均一年少約 1 個百分點」跨三版都成立，是全書最耐版次的一句。

**D. 台灣家數，最小修法是在 L1463 小字加一句，不動主線數字：**
> 「1,094 是這份開放資料的**筆數**，裡面含 10 檔台灣存託憑證（TDR）；扣掉後是 1,084 家上市公司（含第一上市 KY 與創新板），和主管機關公布的家數同一口徑（證期局：2025 年底 1,063 家）。」

這樣主線的 1,094／549／545 都不必動，「大約一半」的結論也保住（537/1,084 ＝ 49.5%）。
若要更乾淨：主線三個數字改成 1,084／547／537，同時把 `tools/calc_core.py:1015-1025` 加一個 `產業別 != '91'` 過濾並更新 assert——但那是改數字不是改口徑，成本高、結論不變，我建議走上面那句小字。

**E. 順手：** `docs/handoff-guide-2026-09-19.md:292` 那條「原因沒查完」可以結案，結論寫「971 是 2022 年底，比錯年份；真正差額是 10 檔 TDR」。`chapters/08-risk-diversification-cost.html:357` 的「轉引待核」可升級為已核（官方原文網址＋Wayback 快照 20250814033514）。