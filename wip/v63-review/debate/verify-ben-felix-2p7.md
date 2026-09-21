# 查證：Ben Felix 的「2.7% 法則」與第 24 節的 2.31%

日期：2026-09-21　查證者：子代理（Opus 5）
任務來源：主線交辦，驗《隔離人性》第 24 節新寫進的 2.31% 那句，並釐清作者記憶中的「Ben Felix 影片 2.7%」。

## 0. 這次查證的環境限制（先講，影響把握程度）

這台機器對**所有** HTTPS 外部網域都有 TLS 攔截（self signed certificate in certificate chain）：
`WebFetch`、`curl`、瀏覽器面板（`navigate` / `preview_start`）全部失敗，不是只有部分網域。
因此：

- **能當一手依據的只有一項**：本機 `wip/v63-review/debate/jpef.html`（先前另一輪下載的 Cambridge 論文頁），裡面有已出版版本的摘要原文。
- 其餘結論都來自 **WebSearch 的搜尋摘要**（搜尋引擎回傳的整理文字），屬二手，且部分出自 Bogleheads 論壇貼文。把握程度已逐條標示。
- 建議：要把 2.7% 印進書裡之前，請人工打開影片說明欄／PWL 文章確認一次。

---

## 1. 影片：標題、日期、網址

| 項目 | 內容 |
|---|---|
| 標題 | **The 2.7% Rule for Retirement Spending** |
| 頻道 | Ben Felix（Common Sense Investing） |
| 網址 | https://www.youtube.com/watch?v=1FwgCRIS0Wg |
| 發布日期 | 2022-12-22 |

作者記憶正確：確實有這支影片，標題就是「2.7% 法則」。

相關的同一批內容（同一週推出，講同一份研究）：

- Rational Reminder Podcast **EP 229「The 2% (!?) Rule for Retirement Spending」**
  https://rationalreminder.ca/podcast/229
- PWL Capital 文章 **「The 2.7% Rule: Rethinking Safe Retirement Spending」**
  https://pwlcapital.com/the-2-7-rule-rethinking-safe-retirement-spending/

**把握程度**：標題與網址 **高**（多組搜尋結果一致指向同一個影片 ID）。
發布日期 **中高**（來自搜尋摘要，未能打開 YouTube 頁面核對）。
注意 podcast 那集標題寫的是「2%」不是「2.7%」，影片與 podcast 的招牌數字本來就不同步，這件事本身就暗示 2.7% 不是論文裡印出來的數字。

---

## 2. 2.7% 到底是什麼口徑

### 2.1 先確定：是同一組作者、同一份研究

**是。** 影片講的就是

> Anarkulova, Cederburg, O'Doherty & Sias, "The Safe Withdrawal Rate: Evidence from a Broad Sample of Developed Markets"

影片 2022-12 上線時，這份研究還只有 **SSRN 工作論文版**（SSRN abstract_id 4227132，版本日期 2022-09-22）：
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4227132

後來正式出版成書裡引的那篇：
Journal of Pension Economics & Finance **24(3), 464–500**，線上發表 **2025-02-17**，DOI **10.1017/S1474747225000010**
https://www.cambridge.org/core/journals/journal-of-pension-economics-and-finance/article/abs/safe-withdrawal-rate-evidence-from-a-broad-sample-of-developed-markets/5D6C1EBBAFE135FC27D236C9F46E677F

**把握程度：高。**（工作論文版與出版版是同一篇，標題、四位作者、資料集敘述完全一致。）

### 2.2 已出版版本的摘要（一手，逐字）

本機 `jpef.html` 抓到的摘要原文（Cambridge 頁面）：

> "A 65-year-old couple willing to bear a 5 percent chance of financial ruin can withdraw just 2.31 percent per year"

其餘摘要內容為：使用 38 個已開發國家的資產類別報酬新資料集，檢視「每年提領帳戶餘額固定百分比」這一類退休支出規則，並指出此提領率遠低於 4% 法則之類的傳統建議。

**把握程度：高（一手原文在本機檔案裡）。**

**重要但容易被忽略的一點**：摘要**沒有指明這個 2.31% 對應哪一種股債配置**。它指明的只有三件事——65 歲夫妻、5% 破產機率、38 國資料。書裡那句話因為是照抄摘要的口徑，所以站得住。

### 2.3 三個數字的口徑差別

三個數字共用的框架（都一樣，不是差異點）：

- 對象：**一對 65 歲夫妻**
- 失敗定義：**5% 的機率在死亡前把錢用光**（financial ruin）
- 期間：**不是固定 30 年**。用死亡率表算實際餘命（夫妻至少一人存活），所以有機會拖到 35 年以上——這正是它比 Bengen 低這麼多的主因之一
- 資料：38 個已開發國家、回溯到 1890 年左右的 block bootstrap，修掉了美國獨強與國家存活者偏誤

差異點：

| 數字 | 出處 | 差在哪裡 | 把握 |
|---|---|---|---|
| **2.26%** | SSRN 工作論文版（2022-09）摘要 | 同一句話的舊版數字。公開草稿的模擬是**單一國家**：每個國家的退休者只投資自己國家的股債（本國偏誤到底） | 中高 |
| **2.31%** | JPEF 已出版版（2025）摘要 | **同一句話、同一情境**，只是論文改稿後數字微調。不是不同情境 | 高（一手） |
| **2.7%** | Ben Felix 影片標題與招牌數字 | **不是論文表格裡的數字**。據稱是作者群應 Felix 要求**另外跑的一次模擬**：把單一國家組合換成**全球分散**的組合（帶一點本國偏誤，被描述為約 6% 本國股／54% 國際股／40% 債），其餘設定不變 | **中**（來自 Bogleheads 論壇貼文轉述的私下通信，一手無法打開） |

補充（把握 **中低**）：PWL 那篇文章裡還出現 **2.85%**（股票部位 40% 換成國際股）與 **3.02%**（股票部位 90% 換成國際股）兩個數字。若屬實，則「國際分散把提領率拉高」這個方向是對的，但**具體拉到多少，不同來源給的數字並不一致**（2.7%／2.8%／2.85%／3.02% 都出現過）。這反過來更說明 2.7% 是個特定一次模擬的結果，而不是論文的公開結論。

### 2.4 一句話結論

> 2.31% 是論文印出來的數字（本國組合、已出版版）；2.7% 是同一份研究、同一套假設，但改用**全球分散組合**跑出來的版本，而那個版本**沒有印在論文裡**。
> 兩者不矛盾，差別就是「只投本國」和「投全世界」。

**把握程度：整體中高。**「同一份研究、差在本國 vs 全球分散」這個結構 **高**；「2.7% 具體對應 6/54/40 且來自私下通信」這個細節 **中**。

---

## 3. 可以直接寫進書的白話（建議）

### 建議版本 A（保守，推薦）

> Ben Felix 有一支影片叫〈The 2.7% 法則〉，講的就是這份研究的早期版本。2.7% 和 2.31% 不是兩份研究打架：論文算的是「只投自己國家」，2.7% 是同一批作者改用「投全世界」再跑一次的結果。方向一樣——都遠低於 4%。

（三句。不碰 6/54/40 這種查不實的細節，也不碰 2.85%／3.02%。）

### 建議版本 B（更保守，若主線不想承擔中等把握的風險）

> Ben Felix 有一支影片叫〈The 2.7% 法則〉，講的就是這份研究。影片用的 2.7% 和論文印出來的 2.31% 口徑不同，這裡只採論文的數字。

（兩句。提到影片以回應作者的記憶，但不替 2.7% 背書。）

### 不建議這樣寫

- ❌ 「研究說安全提領率是 2.7%」——論文沒有這個數字。
- ❌ 「2.7% 是 30 年退休期的版本」——錯。這份研究**整個都不用固定 30 年**，三個數字都是按死亡率表算餘命。
- ❌ 把 2.7% 和 2.31% 寫成「有人說 2.7 有人說 2.31」的爭議——它們是同一份研究的兩種組合，不是爭議。

---

## 4. 逐條結論、網址、把握程度

| # | 結論 | 網址 | 把握 |
|---|---|---|---|
| 1 | 影片是〈The 2.7% Rule for Retirement Spending〉，Ben Felix，2022-12-22 | https://www.youtube.com/watch?v=1FwgCRIS0Wg | 標題網址 高／日期 中高 |
| 2 | 同批內容另有 Rational Reminder EP 229 與 PWL 同名文章 | https://rationalreminder.ca/podcast/229 ／ https://pwlcapital.com/the-2-7-rule-rethinking-safe-retirement-spending/ | 高（連結存在）／內容 中 |
| 3 | 影片講的就是 Anarkulova/Cederburg/O'Doherty/Sias 那篇，當時是 SSRN 工作論文版 | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4227132 | 高 |
| 4 | 已出版版摘要：65 歲夫妻、5% 破產機率、**2.31%**；JPEF 24(3) 464–500，2025-02-17 線上，DOI 10.1017/S1474747225000010 | Cambridge 頁面（本機 `jpef.html` 一手原文） | **高** |
| 5 | 書裡第 24 節那句（38 國、65 歲夫妻、5%、2.31%）與摘要口徑一致，可以照登 | 同上 | **高** |
| 6 | SSRN 舊版同一句是 **2.26%**，改稿後變 2.31%，情境沒變 | SSRN 頁面 | 中高 |
| 7 | 三個數字都**不是**固定 30 年，而是按死亡率表算夫妻餘命 | 搜尋摘要多處一致 | 高 |
| 8 | **2.7% 不在論文裡**，是作者另外用全球分散組合跑的一次模擬（約 6/54/40），來源是與作者的私下通信 | Bogleheads 討論串 https://www.bogleheads.org/forum/viewtopic.php?t=393123 | **中** |
| 9 | PWL 文章另有 2.85%／3.02% 的國際分散版本；各來源數字不一致 | PWL 文章 | 中低 |
| 10 | 「2.26% 就是本國組合」這個對應 | Bogleheads 討論串 | 中 |

## 5. 待補（若主線要提高把握）

要把第 8 條從「中」升到「高」，需要人工（或在沒有 TLS 攔截的機器上）打開其中一項：

1. 影片 https://www.youtube.com/watch?v=1FwgCRIS0Wg 的**說明欄與逐字稿**（約 10:40 處據說就是講 2.7% 的出處）
2. PWL 文章全文
3. SSRN 工作論文 PDF 的表格，確認 2.26% 對應哪一個組合

在那之前，書上建議採**版本 A**（講關係、不講細節）或**版本 B**（只採 2.31%）。

---
---

# 2026-09-22 一手核對

查證者：子代理（Opus 5）　網路已恢復正常，本節全部改用一手來源重做。

> **一句話：上一輪第 2.3 節「2.7% ＝ 同一設定、只把組合換成全球分散」這個說法，被 Felix 自己的文章推翻了一半。**
> 2.7% 同時改了兩件事：組合換成全球分散**加上**壽命假設拉長。只換組合、不換壽命的數字是 2.85%／3.02%。

## A0. 這次實際取得了什麼

| 來源 | 結果 | 方法 |
|---|---|---|
| YouTube 影片頁 | **取得**（標題／日期／長度／說明欄全文） | curl ＋ 解析 `ytInitialPlayerResponse` |
| YouTube 逐字稿 | **未取得** | 見 A1 末 |
| Rational Reminder EP 229 | **取得全文逐字稿** | curl |
| SSRN 工作論文 PDF 全文（33 頁） | **取得** | 第三方鏡像，頁尾有 SSRN 浮水印 |
| PWL 同名文章 | **取得全文** | Wayback 快照（本站對 curl／WebFetch／瀏覽器一律 403） |
| JPEF 出版版正文 | **未取得**（付費牆，只有摘要） | 本機 `jpef.html` |

## A1. 影片（一手）

| 項目 | 內容 |
|---|---|
| 標題 | The 2.7% Rule for Retirement Spending |
| 頻道 | Ben Felix |
| 發布 | **2022-12-22**（08:45 PST） |
| 長度 | 792 秒＝13:12 |
| 觀看數 | 約 39.8 萬（抓取當下） |

說明欄全文已取得。內容只有一句提問 `Is the 4% rule really 2-3%?`、五個參考連結（含 SSRN 4227132、RR EP224）與例行的社群連結。

→ **說明欄沒有解釋 2.7% 怎麼來的，也沒有章節時間戳。** 上一輪「約 10:40 處講 2.7% 出處」的說法，在說明欄裡找不到依據。

**逐字稿未取得**（這次是認真找過的，不是沒試）。影片頁原始碼裡除了標題本身，沒有任何一處出現 `2.7`、`international`、`Cederburg`。試過而失敗的路徑：

- YouTube `timedtext` 端點：用當下新抓的、未過期的 `baseUrl`，再加 `fmt=json3／srv3／srv1／vtt` 各試一次，**一律 HTTP 200 但 body 為 0 bytes**。
- InnerTube `/player`：WEB／MWEB／ANDROID／IOS／TVHTML5 各用戶端 → `UNPLAYABLE` 或 400。
- InnerTube `/get_transcript`：用頁面裡真實的 `getTranscriptEndpoint.params` ＋ `INNERTUBE_API_KEY` ＋ `visitorData` → 400 `FAILED_PRECONDITION`。
- **真瀏覽器**（可執行 JS）：成功展開說明欄、找到並點到「顯示轉錄稿」按鈕，但 `ytd-transcript-renderer` 面板**始終沒有生成**——與上面 0 bytes 的現象一致，是 YouTube 端擋字幕，不是點不到按鈕。
- 第三方逐字稿站：youtubetotranscript（403）、tactiq（404）、notegpt（404）、summarize.tech（503）、kome.ai 與 downsub（純前端 JS，靜態 HTML 無內容）、youtubetranscript.com（明文回「YouTube 正在擋我們」）。
- Invidious 十個實例：bot 驗證、502、500 或連不上。
- Wayback：上述各站針對這支影片 ID **都沒有快照**。

→ 結論：**「2.7% 那段原話」這次拿不到。** 但 A4 的 PWL 文章是 Felix 自己署名的書面版本，已足以回答「2.7% 怎麼來的」，只是少了影片口述的交叉驗證。

## A2. Rational Reminder EP 229（一手，全文逐字稿）——這集是關鍵

日期 **2022-12-01**，比影片**早三週**。標題是「The 2% (!?) Rule」。

**`2.7` 在 EP229 的逐字稿正文裡一次都沒有出現。** 相關原話：

- 論文只看本國：`"they only looked at domestic investors."`
- 他還沒有這個數字：`"We would need Scott to run that analysis."`
- 他想要這個數字：`"I hope he does."`
- 他點名想看：`"love to see this data for an internationally diversified investor"`
- 壽命是另一個變數：`"These numbers are even worse if we're looking at Canadian mortality."`
- 目標日期基金不算數：`"the target date is really heavy on fixed income."`
- 60/40 最佳：`"the 60:40 portfolio gives the highest safe withdrawal rate."`

→ **這證實了兩件事**：(1) 2022-12-01 時 Felix 手上還沒有國際分散的數字，而且他公開說要等 Cederburg 跑；(2) 三週後影片就叫「2.7%」。時間軸強烈支持「2.7% 是為了這支影片另外跑的」這個說法。
→ **但 EP229 沒有講**誰跑的、用什麼組合、什麼壽命假設——那些只出現在 A3 的 PWL 文章裡。

## A3. 論文（一手，完整 PDF）

標題頁日期 **2022-09-22**，四位作者，每頁頁尾都有 `ssrn.com/abstract=4227132` 浮水印 → 就是 SSRN 工作論文版。

**基準組合（原文）**：

- `"portfolio weights of 60% domestic stocks and 40% bonds"`
- 為什麼選它：`"consistent with the well-known home bias in asset holdings"`
- 摘要：`"A 65-year-old couple ... can withdraw just 2.26% per year"`

**論文模擬了七組權重**：六組都是「**本國**股＋債」的固定比例（本國股 0／20／40／60／80／100%），第七組是目標日期基金的滑行路徑。

> **`international` 這個字，從來沒有出現在任何一組模擬的股債配置裡。**
> 唯一持有國際股的組合是目標日期基金，而它的結果**更差**：`"the target-date strategy supports just 2.14%"`。

**Table IV 完整數字**（5% 破產機率、developed sample、2022 年 65 歲夫妻）：

| 組合 | 5% 破產機率下的提領率 |
|---|---|
| 本國股 0／債 100 | 1.02% |
| 本國股 20／債 80 | 1.64% |
| 本國股 40／債 60 | 2.06% |
| **本國股 60／債 40（基準 †）** | **2.26%** |
| 本國股 80／債 20 | 2.21% |
| 本國股 100／債 0 | 1.85% |
| 目標日期基金（含國際股） | 2.14% |
| 2065 年退休（同 60/40 本國） | 2.02% |
| 2085 年退休（同 60/40 本國） | 1.95% |

→ **論文裡沒有任何國際分散的情境表。2.7%／2.85%／3.02% 一個都不在論文裡。**

**JPEF 出版版**：Cambridge 頁面只有摘要與參考文獻，正文在付費牆後，**無法一手確認出版版的基準組合**。不過摘要那句話的結構與工作論文版逐字相同（只有 `2.26` → `2.31`），參考文獻清單也一致，所以「出版版的基準組合仍是本國股 60／債 40」是**高度合理的推論，不是一手證實**。把握：中高。

## A4. PWL 文章（一手，經 Wayback 取得）——2.7% 的出處在這裡

署名 **Benjamin Felix**，頁面日期 `Jul 22, 2025`（看起來是改寫／重新標日期過的版本，但內文仍用 2.26%，即 SSRN 版口徑）。

原話依序：

1. `"For a retiree with a traditional 60% domestic stock / 40% bond portfolio:"`
2. `"...running out of money below 5% is about 2.26%."`
3. **`"Not reported in the paper, adding international diversification improves these numbers:"`**
4. `"Moving 40% of equity to international stocks raises ... to 2.85%."`
5. `"Increasing that to 90% of equities boosts it to 3.02%."`
6. **`"However, if you expect to live longer...the sustainable rate drops closer to 2.7%."`**（原句舉的例子是加拿大退休者與規劃活到 2085 的年輕世代）

**這段推翻了上一輪的結論。** 2.7% **不是**「同一設定、只換成全球分散」。依 Felix 自己的文章，2.7% 同時改了兩件事：

- (a) 股票部位換成全球分散，**而且**
- (b) 壽命假設拉長（加拿大人的死亡率，或 2085 世代）。

只改分散、不改壽命 → 2.85%／3.02%。只改壽命、不改分散 → 2.02%／1.95%（論文 Table IV）。兩個方向互相抵銷之後，落在 2.7%。這也解釋了為什麼影片（加拿大觀眾）用 2.7%，而不是 2.85%。

**順帶修正上一輪的第 8 條**：Bogleheads 上流傳的「2.7% 對應 6% 本國股／54% 國際股／40% 債」，對照 PWL 原文，6/54/40（＝股票部位的 90% 換成國際股）對應的是 **3.02%**，不是 2.7%。把 6/54/40 綁在 2.7% 上，是論壇轉述時的併接，不要採用。

**仍然沒有一手證據的**：誰跑的這次模擬。PWL 文章只說「論文沒報」，沒說是作者跑的；EP229 說的是「需要 Scott 去跑，希望他會跑」。所以「同一批作者另外跑的」這個說法**仍是二手**。

## A5. 小表：每個數字的口徑

所有數字共用：65 歲夫妻、5% 破產機率、38 國 1890–2019 資料、按 SSA 死亡率表算餘命（**不是固定 30 年**）。

| 數字 | 倍數 | 組合 | 壽命假設 | 在論文裡？ | 一手出處與原文短引 | 把握 |
|---|---|---|---|---|---|---|
| **2.26%** | 44 倍 | 本國股 60／債 40 | 2022 年退休 | **是**（基準） | 工作論文：`"can withdraw just 2.26% per year"` | **高** |
| **2.31%** | 43 倍 | 同上（推論） | 同上 | **是**（基準） | JPEF 摘要：`"can withdraw just 2.31 percent per year"` | 數字**高**／組合 中高 |
| 2.14% | 47 倍 | 目標日期基金（含國際股） | 2022 年退休 | **是** | 工作論文：`"the target-date strategy supports just 2.14%"` | **高** |
| 2.02% | 50 倍 | 本國股 60／債 40 | 2065 年退休 | **是** | 工作論文 Table IV | **高** |
| 1.95% | 51 倍 | 本國股 60／債 40 | 2085 年退休 | **是** | 工作論文 Table IV | **高** |
| **2.85%** | 35 倍 | 股票部位 40% 換國際股 | 2022 年退休 | **否** | PWL：`"Moving 40% of equity to international stocks raises"` | 中高 |
| **3.02%** | 33 倍 | 股票部位 90% 換國際股 | 2022 年退休 | **否** | PWL：`"Increasing that to 90% of equities boosts it"` | 中高 |
| **2.7%** | **37 倍** | 全球分散 | **拉長**（加拿大／2085） | **否** | PWL：`"if you expect to live longer...drops closer to 2.7%"` | 中高 |

（「中高」而非「高」的原因：PWL 那三個數字來自 Wayback 上一個 2025 年重新標日期的頁面，且論文本身無從對照；誰跑的仍不明。）

## A6. 對第 24 節的建議

### 前半段：**該補，而且重要**（把握 高）

「這是只投自己國家的算法」這半句**完全站得住，而且是一手逐字**——論文寫明基準組合是 `60% domestic stocks and 40% bonds`，還明說選它是因為 `home bias`。這對台灣讀者特別有意義：2.31% 是「一個只買本國股債的人」的數字。

### 後半段：**照草稿寫會過頭**（把握 中高，但方向錯）

草稿句「同一批作者改用全球分散的組合再算，大約是 2.7%」有兩個問題：

1. 「同一批作者…再算」——**沒有一手證據**。Felix 自己只說「論文沒報」。
2. 「改用全球分散…大約是 2.7%」——**不準**。只改分散是 2.85%／3.02%；2.7% 還多套了一個「活得更久」的假設。

### 可直接用的白話

**主線一句**（建議採用）：

> 要注意，這個 2.31% 算的是「只買自己國家的股票和債券」——論文的基準組合就是六成本國股、四成本國債。

**小字／摺疊**（二選一）：

（甲）完整版，把 2.7% 講清楚而不背書：

> Ben Felix 2022 年有一支影片叫〈2.7% 法則〉，講的就是這份研究。那個 2.7% 論文裡查不到：依他自己在 PWL 的文章，把股票換成全球分散會變成 2.85%～3.02%（約 33～35 倍），2.7% 則是再加上「活得更久」的假設之後的數字。

（乙）最短版，只保留對讀者有用的部分：

> 同一批資料，若把股票換成全球分散，提領率會高一些；但那些數字都不在論文裡。

### 不要這樣寫

- ❌ 「同一批作者改用全球分散的組合再算，大約是 2.7%」——誰跑的無一手證據，且 2.7% 不只換了組合。
- ❌ 「研究說安全提領率是 2.7%」——論文沒有這個數字，Felix 自己寫 `Not reported in the paper`。
- ❌ 引用「6% 本國股／54% 國際股／40% 債 ＝ 2.7%」——那個組合對應的是 3.02%。
- ❌ 把 2.7% 和 2.31% 寫成兩派爭議——不是爭議，是三個變數（組合、壽命、論文版本）不同。

## A7. 我實際打開／取得的頁面

1. `https://www.youtube.com/watch?v=1FwgCRIS0Wg`（curl，取得標題／日期／長度／說明欄全文）
2. `https://rationalreminder.ca/podcast/229`（curl，**全文逐字稿**約 12.8 萬字元）
3. `https://www.emiratescapitalassetmanagement.com/uploads/2/5/5/4/25541321/updated_safe_withdrawal_rates.pdf`（SSRN 工作論文全文 33 頁）
4. `https://web.archive.org/web/20260131001110/https://pwlcapital.com/the-2-7-rule-rethinking-safe-retirement-spending/`（PWL 文章全文）
5. 本機 `jpef.html`（Cambridge 出版版摘要）
6. `https://sites.google.com/site/cederburg/research`、`https://www.anarkulova.com/research`（作者頁，均只指回 SSRN，無新版 PDF）

**打不開的**：`pwlcapital.com` 直連（403，curl／WebFetch／瀏覽器皆同）、`papers.ssrn.com`（403）、YouTube 逐字稿端點（0 bytes／UNPLAYABLE）、JPEF 正文（付費牆）、archive.org 的 CDX 端點（該站暫時離線，但 availability API 與快照本身可用）。

## 2026-09-22 補：主線用內建瀏覽器拿到影片的自動字幕（一手）

做法：開 https://www.youtube.com/watch?v=1FwgCRIS0Wg ，播放器自己發出的 `timedtext`（帶 pot token、`kind=asr&lang=en&fmt=json3`）在頁面內重新 fetch，拿到 705 段、約 12,900 字元的英文自動字幕（ASR，會有聽寫錯字；數字與關鍵詞前後文一致）。以下是摘要，不是逐字稿：

- 開場：近期研究修正資料偏誤後，安全提領率大約在 2% 到 3% 之間，視組合與預期壽命而定；他要講為什麼 2.7% 是新的 4%。
- 論文（他稱 2022 paper）：38 個已開發國家、1890–2019；基準組合 **60% 本國股票／40% 本國債券**，另測 0–100% 本國股票與目標日期基金；**「in unreported analysis one of the co-authors also tests」各種國際股票分散程度的 60/40 組合**（＝未列入論文的分析，由共同作者之一做的——這一點現在有一手出處）。用美國社安局死亡率表納入長壽風險，不用固定 30 年。
- 結果：65 歲夫妻（2022 年）、本國股債、5% 破產機率 → **2.26%**（for a domestic investor）；60/40 是各配置裡最高的，目標日期基金更差。
- 加國際分散：把股票部位的 40% 換成國際股 → **2.85%**；換 90% → **3.02%**；這兩個數字已多扣每年 0.5% 的國際持有成本。
- **2.7% 的來歷**：再加長壽調整——預期壽命像今天 65 歲加拿大人那樣長的「2085 世代」美國退休者，用國際分散的 60/40 組合，可持續的支出率「closer to 2.7 percent」；片尾他說這是他自己估的（"which I estimate at 2.7 percent"）。
- 他另外強調：這些數字用的是市值加權的本國＋國際股票與政府公債；固定提領率本來就不是實際做財務規劃的方式。

對書的含意：2.31%（出版版）＝只買本國的 60/40；全球分散 → 2.85%～3.02%（論文未列、共同作者另跑、Felix 在影片與 PWL 文章轉述）；2.7% ＝ 全球分散再加「活得更久」的假設，是 Felix 的估計。三個數字都遠低於 4%。
