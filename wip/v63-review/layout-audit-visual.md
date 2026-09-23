# 出版社視角：版式與視覺一致性（judge／opus xhigh，2026-09-23）

驗證完成。以下是判決書。所有數字都來自對 `guide/index.html` 的實際解析與 headless Chrome 在 **375px iframe** 裡的 computed style 量測（不是讀 CSS 推論）。

---

# 總判：**有條件可用**

版面沒有壞掉（375px 下 50 張表只有 1 張需要橫捲、圖沒有出界），但「略顯雜亂」是成立的，而且可以量化到三個數字：

1. **同一階層的正文，左緣有 18 個不同的 x 值**（375px 實測）。
2. **15 種盒子樣式、8 種底色、9 種框線做法、13 種字級、7 種行高、9 種區塊間距**，用在 383 個框上。
3. **94 個「想深入」摺疊標題有 78 個換行，而且 78 個的續行都比首行往左突出 16px**（首行 x=63、續行 x=47）。

雜亂的成因不是「顏色太多」，是**沒有間距尺規、沒有字級梯度、每個框各自決定自己的內距與框線**。這三件事修掉，視覺會立刻收斂，而且大部分只動 CSS。

**檔案狀態警告（先讀）**：我量測期間 `guide/index.html` 被別人改過（10:52 的 1,587,499 B → 11:14 的 1,587,257 B，`#ten` 節的紅框與摺疊被換成 `h3.stage-label`＋`ol.checklist`）。**本報告的全部數字已用最終快照 md5 `ca65805f2ae7ed9528b9fd5fa13f8102`（1,587,257 B）複驗過一次**，只有 `.warning` 從 9 降為 8。另外 `wip/v63-review/layout-audit-structure.md`（11:14 產生）是另一份針對「結構與區塊順序」的稽核，與本報告互補、不衝突；請確認沒有第三個代理同時在動這支檔。

---

# 一、容器樣式盤點（手機 375px 實測值）

CSS 全部在 `guide/index.html` 第 8–105 行的單一 `<style>` 裡。**第 10 行是整張基礎樣式表（一行 22,000 字元）**，第 11 行以後是逐批疊上去的補丁層，所以下表的「CSS 位置」凡是寫 L10 的，都要用選擇器去找。

| # | 容器 | 次數 | 底色 | 框線 | 圓角 | 內距(手機) | 內文左緣 | CSS |
|---|---|---|---|---|---|---|---|---|
| 1 | `section.part` | 34 | `#fffdf8` | 1px `#d8d4ca`＋陰影 | 18px | 22/18 | 35 | L10 |
| 2 | `p.explain`（白話版） | 28 | `#dceee7` | **無** | 16px | 14/16 | 51 | L10 |
| 3 | `div.data-card` | 84 | `#f3f6f4` | 1px `#cfdad5` | 16px | 18/**14** | 50 | L10, L95 |
| 4 | `details.source-card` | 27 | `#f8f3e9` | 1px `#e4d6ba` | 16px | 18/20 | 56 | L10 |
| 5 | `div.story`（黃框） | 26 | `#f6e7cf` | **左 5px** `#b66d18` | 16px | 18/20 | 60 | L10 |
| 6 | `div.warning` | 8 | `#faece9` | **左 5px** `#a4483f` | 16px | 18/20 | 60 | L10 |
| 7 | `p.decision` | 27 | **透明** | 2px **實線**綠 | 16px | 18/20 | 57 | L10 |
| 8 | `div.planstep` | 10 | `#fffdf8` | 2px **虛線**綠 | 16px | 16/18 | 55 | L38–40 |
| 9 | `figure.chart` | 28+1 | `#fffdf8` | **上 3px 綠**，左右 0 | **0** | 18/0/14 | 17（出血） | L58, L105 |
| 10 | `div.table-wrap` | 50 | `#fffdf8` | 1px `#d8d4ca` | 16px | 0 | 51 | L10 |
| 11 | `details.more` | 94 | 無 | **左 2px** `#d8d4ca` | 0 | 0/0/10 | 47 | L41–43, L95 |
| 12 | `.col-card`（JS 產生，5 組 14 張） | 14 | `#fffdf8` | 1px `#d8d4ca` | **12px** | 0 | 30 | L92 |
| 13 | `table.stack-mobile tr`（18 張表） | — | `#fffdf8` | 1px `#d8d4ca` | **12px** | 2/12/8 | 63 | L90 |
| 14 | `.promise`（封面） | 1 | `#fffdf8` | 1px＋**左 6px** 綠＋陰影 | 16px | 18/20 | — | L10 |
| 15 | `nav.toc` | 1 | `#fffdf8` | 1px | **18px** | 22/28 | — | L10 |

**行內元素**：`mark.key` 97（黃底線 `#f7e4ab`）／`mark.key.top` 14（淡紅底線 `#f7d8d2`＋900 字重）／`a.xref` 715（綠點線底）／`a.term` 129（藍點線底）／`span.pn` 100（實底線）／`span.tag` 29（綠膠囊 999px）／`span.later` 13（黃膠囊 999px）／`span.plain-title` 28／`span.credit` 1。
**小字**：`p.small` 151＋`span.small` 87（都是 13.44px muted）／`p.note` 28（**兩種外觀，見 F3**）／`span.chart-sub` 29（13.44px）／`figcaption` 28（14.4px）。
**表格**：51 張、**21 種 class 組合**，由 9 個修飾類疊出來（`compact/wide/tight/text/prose/tight-mobile/stack-mobile/stack-inline/stack-mobile-cols/sticky-first/situations/dca`）。
**摺疊**：136 個 `<details>`／`<summary>`，**5 種外觀**（見 F4）。
`blockquote`：**0 個**（交件單列了，全書沒用）。

---

# 二、亂的來源（依嚴重度，每條附證據）

## 【實質】F1 — 同一階層的正文有 18 個左緣，因為每個框自己決定內距

375px 實測，`section.part` 底下所有 `<p>` 的 `rect.left` 直方圖：

```
17(16) 18(3) 29(6) 35(236) 47(114) 50(139) 51(6) 55(40) 56(4)
60(31) 62(103) 63(5) 65(1) 74(3) 77(4) 79(27) 91(10) 106(3)
```

「往內縮一層」這件事，因為框線寬度（0/1/2/5px）＋內距（10/14/16/18/20px）各不相同，產生 6 個不同結果：`details.more` 47、`data-card` 50、`explain` 51、`planstep` 55、`source-card` 56、`story/warning` 60。讀者在手機上垂直滑，每換一種框，文字左牆就位移 3–13px —— **這是「雜亂」最主要的生理來源，比顏色多更嚴重**。再往下巢狀（`data-card > details.more` = 62、再一層 = 79、再一層 = 91/106）。

證據：全部可從 CSS 反推（`.part` 16+1+18=35；`.data-card` 35+1+14=50；`.story` 35+5+20=60…），實測值與反推完全吻合。

## 【實質】F2 — 標題階層是壞的：h3 有 5 種字級，而且卡內標題比正文還小

| 標籤 | 字級（375px） | 個數 | 來源 |
|---|---|---|---|
| h2 | 24.8px | 34 | `.part h2` clamp |
| h2 | **25.5px** | 1 | `.toc h2` **沒有宣告，吃瀏覽器預設** |
| h3 | **19.89px** | 23 | **沒有宣告，吃瀏覽器預設 1.17em** |
| h3 | 16px | **84** | `.data-card h3{font-size:1rem}` |
| h3 | 14.4px | 5 | `h3.stage-label` |
| h3 | 12.48px | 2 | `.toc h3` |
| h4 | **17px** | 21 | **沒有宣告＝與正文同級**，只有粗體 |
| h4 | 14.4px | 14 | `.data-card h4{font-size:.9rem}` |

三個致命點：
- **全書沒有任何一條 `h3{}` 或 `h4{}` 通則**（我用選擇器全掃過 L9–L105，只有 `.toc h3`、`.data-card h3`、`.source-card h3`、`h3.stage-label`、`.afterword h3`）。23 個節內小標的大小是 Chrome 給的，不是設計決定的。
- **84 個卡名（16px）比正文（17px）還小**。一張卡的標題比卡裡的句子小 1px，只靠粗體撐 —— 視覺上卡名「沉下去」，讀者要找地標時找不到。
- **21 個 h4 = 17px 粗體 = 和內文 `<strong>` 完全一樣**，等於沒有第四層。

實例對照：`#lifecycle` 的節內小標「一、年齡真的該影響比例嗎？」是 19.89px；`#costs` 的卡名「常見成本」是 16px。兩個都是 `h3`，差 4px，而且大的那個沒人宣告過。

## 【實質】F3 — 同一個 class，兩種外觀

- **`p.note`（28 個）**：22 個在 `figure.chart` 裡 → 13.44px muted（`figure.chart .note`，L68）；**6 個在圖外 → 17px 墨色，跟正文一模一樣**。實測首例：「官方原圖（英文）：J.P. Morgan Asset Management…」fs=17px color=rgb(23,33,29)。作者以為在寫小字註，讀者看到的是正文。
- **`p.small` 151 個 vs `span.small` 87 個**：同為 13.44px muted，但 `p.small` 帶 13.44px 上下外距、`span.small` 沒有 → 同一種「小字」有兩種留白。而且 **80 個 `p.small` 在框外、72 個在框內**，在框外時它是全幅 343px 寬的灰字塊，看起來像被降級的正文。
- **`.credit` 1 個（`guide/index.html:3989`）**：`figure.photo .credit{color:var(--line)}`（L78）→ `#d8d4ca` 在 `#fffdf8` 上，**對比 1.46:1**，實質看不見。內容是「指數三寶飯」—— 這是對**外部圖片作者的出處標示**。深色模式一樣壞（`var(--line)` = `#35423b` 在深底上）。

## 【實質】F4 — 摺疊有 5 種外觀、標題 6–76 字，78 個換行且續行往左突出

| 容器 | 個數 | 字級/字重/顏色 | 字數 | 平均行數 | ≥2 行 |
|---|---|---|---|---|---|
| `details.more` | 94 | 14.72 / 700 / muted | 10–62 | 1.9 | **78** |
| `details.source-card` | 27 | 16 / 800 / green | 9–23 | 1.0 | 1 |
| `details`（無 class） | 7 | **17 / 800 / green** | 9–76 | 2.1 | 5 |
| `details.toc-part` | 7 | 17 / 800 / green＋自繪 ▸▾ | 39–67 | 2.4 | 7 |
| `details.promise` | 1 | 17 / 800 / green | 6 | 1.0 | 0 |

- **續行往左突出**：用 `Range.getClientRects()` 量，78 個換行的 `details.more>summary` **全部**是首行 x=63、續行 x=47（或 78/62）。`summary` 是 `display:list-item`＋外置 marker，marker 只佔第一行，第二行往左跑 16px。畫面證據見 `#costs` 那張截圖：「▶ 如果你走複委託：手續費怎麼看，最低收／費會吃掉多少」。**這一條在全書出現 78 次，是版面最顯眼的鋸齒**。
- **最長 76 字**（`guide/index.html:3989`）：「年底算報酬的步驟：只記跨過投資圈的錢（一張圖）、圈裡圈外有什麼、三行例子、1 月 1 日怎麼寫、用 XIRR 算年化、指數那一邊怎麼算（網頁版可以展開）」—— 而且它是無 class 的 `<details>`，所以用 17px 綠色大粗體顯示，**比正文還搶眼，語意上卻是選讀**。
- 94 個「想深入」**預設全收合**（open=0），27 個來源卡也全收合 → 手機上滑過去，看到的是連續的灰色兩行小標，密度極高。

## 【實質】F5 — 圖在卡內時，把卡切斷

L105 讓 `figure.chart` 在 ≤660px 左右出血（作者在 L104 的註解說明了理由：手機 SVG 被內距壓到 247–275px）。理由成立，但副作用沒處理：

- 實測 29 張圖，**28 張的左右緣固定在 x=17 / x=358**，等於 `.part` 的 padding box。
- 其中 **14 張在 `data-card` 內**：卡的 border-box 是 35–340，圖是 17–358 → **圖用不透明底色（`#fffdf8`）蓋掉卡的左右框線**，卡的輪廓在圖的高度內整段消失，卡的 `#f3f6f4` 底色被白色橫帶切斷（見 `#s2` 截圖）。加上 `data-card` 與 `part` 的底色差只有 **ΔE=3.6 / L\*差 2.7**（幾乎看不出來），卡本來就只靠那一條 1px 框線存在 —— 框線一斷，卡就散了。
- **3 張在 `details.more` 內**：圖從 x=17 起，直接蓋掉 `details.more` 在 x=35–37 的 2px 灰色左直線，直線斷一截再接回來。
- 負邊距是 **4 條硬寫的組合**（L105：`-18/-18`、`.data-card>` `-33/-33`、`details.more>` `-30/-18`、兩條 `-45/-33`）。我逐條驗算過，四條的算術都對；但它是白名單，**漏了一條路**：`guide/index.html:3989` 的 `details.more > details > figure.chart.photo` 沒有對應規則，實測 **左緣 61、右緣 358，左右差 44px**，是全書唯一一張歪的圖。

## 【實質】F6 — 段末四種框連放，四種視覺語言

`guide/index.html:3024–3027` 連續四行：`details.source-card`（米底＋1px 棕框）→ `div.story`（黃底＋左 5px 棕棒）→ `div.planstep`（白底＋2px 綠**虛**框）→ `p.decision`（透明＋2px 綠**實**框）。加上節首的 `p.explain`（薄荷底、無框），一節之內出現 5 種淺色框。

全書**相鄰但不同型的框轉換 154 次**，最高頻：`explain→data-card` 17、`source-card→story` 16、`data-card→details.more` 12、`story→decision` 9、`story→planstep` 8、`planstep→decision` 8。

**這些框的寬度、圓角（都是 16px）、外距（都是 22px）完全相同，只有底色與框線不同** —— 所以它們讀起來不是「四種不同的東西」，是「同一種東西換了四次皮」。這正是作者說的「雜亂」。

## 【次要】F7 — 膠囊在 375px 會換行

`span.later`（13 個）與 `span.tag`（29 個）用 `border-radius:999px`＋`padding:2px 9px`。375px 實測 **各有 3 個換成兩行**（`.later` 最寬 287px、`.tag` 最寬 275px），上下內距只有 2px，兩行擠在一個圓角膠囊裡。320px 時 `.later` 換行的變成 7 個。
最糟的內容：`.tag`「第 9 節「手上已經有一筆錢：一次投入，還是分批？」」—— 一整句話包在膠囊裡。

## 【次要】F8 — 沒有間距尺規

`section.part` 直接子元素的上下外距實測有 **9 種**：10.2（`ol.part-map`）／13.44（`p.small`）／14（`details.more`）／16（`a.back`）／17（`p`、`p.explain`）／19.89（`h3`，**來自瀏覽器預設**）／22（五種卡）／24（`figure`）／26.88（`p.lede` 下）。
行高 **7 種**：1.28 / 1.35 / 1.40 / 1.50 / 1.60 / 1.70 / 1.78。
字級 **13 種**：24.8 / 19.89 / 19.2 / 17 / 16.37 / 16 / 14.96 / 14.72 / 14.4 / 13.44 / 12.8 / 12.6 / 11.84。

## 【次要】F9 — 表格 21 種 class 組合、6 種手機策略

51 張表，21 種組合。手機上同時存在 **6 套不同的變形機制**：
1. `stack-mobile`＋JS 加 `is-stacked`（CSS 把 tr 變成 12px 圓角卡，L90）—— 18 張
2. `stack-mobile-cols`＋JS 把表藏起來另建 `.col-cards`（L92）—— 5 張
3. `tight-mobile` 壓縮欄距到 6px/3px、字級 12.6px（L93）—— 19 張
4. `sticky-first` 固定首欄＋橫捲（L94）—— 3 張
5. `#s11 details[data-print="open"]:not([data-lite-alt])` 專用堆疊（L50，**11 個超長選擇器**，用 `::before` 寫死「區／格／怎麼填／擋住哪個錯」四個標籤）
6. `#plan-starter+.table-wrap` 專用堆疊（L52，**12 條規則**，`::before` 寫死「小安寫的（虛構示範，不要抄）」「你寫」）

第 5、6 條是為兩張特定表格寫的一次性 CSS，佔 ≤660px 規則總量的三分之一。
表格字級 **3 種**：14.4px（747 格）／12.6px（565 格）／13.44px（26 格）。正文 17px vs 表格 12.6px 的落差是 4.4px。

## 【次要】F10 — 黃線與淡紅線：亮度幾乎一樣，靠色相和字重分辨

`mark.key` `#f7e4ab` vs `mark.key.top` `#f7d8d2`：**ΔE76 = 26.1，但 L\* 只差 2.2**。色相差夠（黃 vs 粉），所以彩色螢幕分得出來；但**灰階列印或色弱讀者幾乎分不出來**。目前 `.top` 另外加了 `font-weight:800`，是唯一的非顏色線索 —— 這一條要保留。
兩者上的文字對比都足夠（13.08:1、12.35:1）。

## 【次要】F11 — 死樣式與共用樣式表的陷阱

在 guide 裡完全沒有對應 DOM 的 class：`.audit-stamp`、`.audit-table`、`.bars/.bar-row/.bar-track/.bar-value/.bar-note/.bar-label`（14 條規則）、`.chip`、`.tasks`（3 條）、`.toc-tag`、`.caveat`、`.ok`、`.fix`、`.rules`、`figure.chart details.orig`（**7 條規則，含自繪 ▸▾ 箭頭，全書 0 個 `details.orig`**）、`.label-principle/.label-practice`（4 條，含深色模式覆寫）。約 **40 條規則是死的**。

**但不要直接刪**：`tools/build_lite.py:791-792` 會抓 guide 的 `<style>` 內容當 Lite 版的基礎樣式再接上 `LITE_CSS`。`.lite-plan`（L49 那整塊）在 guide 裡是死的，**在 `lite/index.html` 用了 12 次**。任何 CSS 改動都必須跟著重跑 `build_lite.py` 並驗 lite 哨兵。另外 build_lite 的正規表示式寫死 `<style>`（不吃屬性、只抓第一塊），所以重構時**不能把樣式拆成兩個 `<style>`、也不能加屬性**，否則 Lite 版會靜默變成無樣式。

## 【疑問】Q1

- `.credit` 那張圖（`guide/index.html:3989`，出處「指數三寶飯」）的授權條款我沒查 —— 如果是要求標示出處的授權，1.46:1 的隱形標示可能不只是設計問題。**未查證**。
- 深色模式我只核對了 token 覆蓋（L56 的 10 條、L78 的 2 條、L87 的 1 條），**沒有實際在深色模式下算過每個框的對比**。`.explain/.story/.planstep/.decision/.table-wrap/figure.chart` 都靠 token 換色，理論上安全，但 `.data-card` 的 `#f3f6f4`、`.warning` 的 `#faece9`、`thead` 的 `#eef2ef` 是硬寫色、各自有覆寫，`.source-card` 也是 —— **我沒逐一驗**。
- 列印樣式共 **8 個 `@media print` 區塊、約 50 條規則**，散在 L29/37/57/77/78/88/89/103。**完全未查證**（交件單沒要求）。任何容器收斂都會動到列印，要另外驗一次。

---

# 三、收斂方案

## 3-A 容器收成 4 種（這是主結論）

| 新類別 | 收進來的舊容器 | 外觀 | 用途 |
|---|---|---|---|
| **① 主線卡** `.card` | `data-card`(84)、`table-wrap`(50)、`figure.chart`(29)、`col-card`(14)、`stack-mobile tr` | 白底 `--surface`＋1px `--line`＋**圓角 12px**＋內距 16/14＋外距 20px。**卡內不再有卡**：表與圖直接用卡的內距，不自帶框 | 放數字、表、圖 |
| **② 提示框** `.note-box` | `explain`(28)、`warning`(8)、`decision`(27)、`planstep`(10) | **無底色**、**左 4px 色棒**（綠／紅／綠／綠虛線）＋內距 14/16＋外距 20px，語意靠既有的標籤字（白話版／注意／本節行動／你的計畫）區分，不靠底色 | 提示、警告、行動 |
| **③ 作者聲音** `.story` | `story`(26) | **全書唯一保留底色的框**：`--amber2` 底＋左 4px amber，`::before` 標籤不變 | 只有作者的第一人稱 |
| **④ 摺疊** `details` | `more`(94)、`source-card`(27)、無 class(7) | 無框無底、左 2px `--line`、summary 一律 15px/700/muted＋**自繪 ▸▾**、`list-style:none` | 選讀 |

**效果**：淺色底從 7 種降到 2 種（卡的白、黃框的黃）；框線做法從 9 種降到 4 種；`data-card` 與 `part` 那個看不見的 ΔE=3.6 色差問題自動消失（卡改用白底、靠框線與間距存在）。

⚠️ **這一條要作者拍板**：`.warning`（紅底）與 `.explain`（薄荷底）拿掉底色會改變全書的「彩度」。另一份結構稽核（E11）指出紅框是**唯一沒有標籤字**的框 —— 若照本方案拿掉紅底，**必須先補上「注意」這類標籤字**，否則紅框會弱到不存在。**這兩件事要一起做，不能只做 CSS。**

## 3-B 字級梯度收成 4 級（＋1 個表格例外）

| 級 | 值 | 用在 |
|---|---|---|
| 大標 | 1.55rem（24.8px） | `h2`（含 `.toc h2`，補宣告） |
| 小標 | 1.2rem（19.2px） | **`h3` 通則**（含卡名）、`p.lede` |
| 正文 | 1rem（17px） | `p`、`li`、`td`、`summary` 用 0.94rem |
| 小字 | 0.85rem（14.4px） | `figcaption`、`.small`、`.note`、`.chart-sub`、`.source-link`、表格 |
| （例外） | 0.78rem（13.3px） | 只給 `.tight-mobile` 的密集數字表 |

**要刪掉的中間級**：16px（84 個卡名 → 升到 19.2）、16.37、14.96、14.72、13.44（992 個元素 → 升到 14.4）、12.8、12.6、11.84。
**副作用**：13.44 → 14.4 會讓全書小字區塊變高約 7%，`figcaption`（中位數 67 字、最長 187 字）與 `.source-link`（246 條）都會變長。**這是版面高度的取捨題，要作者拍板。** 若不想變長，替代方案是把小字定在 13.6px（0.8rem）一級，但那樣 `figcaption` 14.4 要跟著降。
**`h4` 的處置**：21 個節層 h4 和內文 `<strong>` 已經無法分辨 —— 要嘛給 `h4` 一個真的級（例如 1.05rem＋字距），要嘛承認書裡只有三層標題、把它們改成 `h3`（DOM 改動）。

## 3-C 間距尺規

只留 4 個值：`--gap-s:8px`（標題與其後第一塊）／`--gap-m:16px`（段落之間）／`--gap-l:24px`（框之間、框與正文之間）／`--gap-xl:32px`（節內分段）。
現在的 9 種外距全部映射到這四個；`h3` 的 19.89px 外距由瀏覽器預設改成明寫 `margin:24px 0 8px`。

## 3-D 圖的統一做法

**建議 A（我推薦）**：**圖一律是節的直接子元素**，不再放進卡或摺疊。這樣 L105 的 4 條硬寫負邊距壓縮成 1 條（`margin-inline:-18px`），`details.more>details>figure` 那條漏網路徑（歪 44px 的那張）自動修好，卡被切斷的問題（14 張）消失。
　→ **需改 DOM**：把 14 張圖搬出 `data-card`、3 張搬出 `details.more`，卡的 `h3` 與圖的 `chart-title` 會撞名（另一份結構稽核 E3 已列出 14 組重複），要順手合併。

**建議 B（CSS-only 的退路）**：把 `details.more` 的 `padding-left:10px` 改成 `padding-inline:10px`（左右對稱），然後全部負邊距換成一條
`figure.chart{width:auto;margin-inline:calc(50% - 50vw + 17px)}`。
所有容器對 `.part` 置中後，這一條對任意巢狀深度都成立。
　⚠️ **風險（我沒測）**：`100vw` 在桌機視窗縮到 640px 以下且有實體捲軸時會多出捲軸寬度，可能製造橫向捲動。手機瀏覽器是覆蓋式捲軸，理論上安全。**採用前必須在桌機縮窗與 iOS Safari 各測一次。**

不論 A 或 B，都要加一條：**圖在卡內時不得使用不透明底色蓋住卡框**（等同於「圖不進卡」）。

## 3-E 表格統一成一種

目標：**一套 `stack-mobile`＋`data-label`**，把 21 種組合降到「預設」＋「密集（tight）」兩種。
- 刪掉 L50（`#s11` 專用，11 條）與 L52（`#plan-starter` 專用，12 條），改成在 DOM 給那兩張表加 `class="stack-mobile"` 與每格 `data-label="區"`⋯ → **需改 DOM，但只有 2 張表、約 30 個 `<td>`**。
- `stack-mobile-cols`（JS 建 col-cards，5 張）與 `stack-mobile`（純 CSS，18 張）功能重疊，**留 CSS 那套、退掉 JS 那套**，可同時刪掉 L92 的 9 條規則與對應 JS。
- 保留 `sticky-first`（3 張，真的需要橫捲）。

## 3-F 摺疊統一

- `summary{list-style:none}`＋`::before{content:"▸"}`／`[open]::before{content:"▾"}`＋`display:block;position:relative;padding-left:1.4em`（照 L13–16 `toc-part` 現成的寫法）→ **一條 CSS 修掉 78 個鋸齒**，而且三種摺疊外觀統一。
- summary 長度上限訂 **20 字**（現在中位數 26、最長 76）→ **需改文字**，78 條。
- 7 個無 class 的 `<details>` 補上 `class="more"` → **需改 DOM，7 處**。

## 3-G 小字統一

`.small`、`.note`、`.chart-sub`、`.source-note`、`figcaption` 全部定在同一級（3-B 的小字級）＋同一個 muted 色＋同一個行高 1.6。
`p.note` 的雙面人格：把 `figure.chart .note` 改成全域 `.note{}`（**一條 CSS，修好 6 個誤植成正文的註**）。
`.credit` 的 `color:var(--line)` 改成 `var(--muted)` —— **一個 token，1.46:1 → 5.57:1**。

## 3-H 工作量分級

| 批 | 內容 | 只動 CSS？ | 量 | 風險 |
|---|---|---|---|---|
| **P0** | `.credit` 對比、`p.note` 全域化、summary 自繪箭頭（修 78 鋸齒）、`h3/h4/h2` 補通則、間距尺規 | **是** | 約 25 條宣告 | 低。但 `h3` 通則會一次改 114 個標題的大小，**要作者看過一版截圖** |
| **P1** | 容器收成 4 種、小字統一、膠囊改成非膠囊（`border-radius:8px`，修 F7） | **是**（但配色語意要作者拍板） | 約 40 條宣告 | 中。`.warning` 要同時補標籤字（DOM） |
| **P2** | 圖搬出卡（17 處）、兩張表改 `data-label`（2 張）、7 個 `<details>` 補 class、78 條 summary 縮短 | **否** | DOM 約 105 處＋78 條文案 | 高。文案要過裁判 |
| **P3** | 刪 40 條死規則 | 是 | — | **必須先確認 lite 沒用到**（`.lite-plan` 就是反例） |

**每一批做完都要**：重跑 `tools/build_lite.py`（guide 的 `<style>` 是 lite 的來源）＋ lite 哨兵，並在 **375 / 660 / 661 / 1024 四個寬度＋列印預覽**各量一次。`tools/v7_check.py` 只檢查內容（主線字數、數字保全、planstep 結構、錨點），**沒有任何版面哨兵** —— CSS 重構目前是裸奔的，建議順便補一支「量 29 張圖與 51 張表在 375px 的左右緣」的哨兵。

---

# 四、660px 以下的規則：現況與簡化

**現況**：全檔 29 個 `@media`。扣掉 8 個 `print`、3 個 `dark`，螢幕用的有 **18 個**，其中 **16 個是同一個斷點 660px**，但寫成兩種語法：`@media screen and (max-width:660px)` ×12、`@media(max-width:660px)` ×4。位置：L45, 46, 48, 49, 50, 52, 53, 55, 90, 92, 93, 94, 95, 96, 97, 105。

**打架與例外**：

1. **640 vs 660 的斷點錯位**（L65 是唯一的 640px）。實測 650px 寬：`figure.chart` 已經進入手機模式（`margin:-18px`、`radius:0`、`border-left:0`、實寬 618px 全出血），**但顯示的還是桌機版 SVG**（`svg.d display=block`）。641–660px 這 20px 區間是無人管的中間態。**建議：640 改成 660，一行修掉。**
2. **`.data-card` 的內距在別的區塊被改**（L95 把 18/20 改成 18/14），而依賴這個數字的負邊距寫在 L105（`-33`）。兩個相隔 10 行、互相耦合、沒有註解關聯。**建議：內距改用 `--pad-card` 變數，負邊距用 `calc()` 引用。**
3. **兩張表的一次性 CSS 佔掉三分之一**（L50 的 11 條＋L52 的 12 條，選擇器長到 `#s11 details[data-print="open"]:not([data-lite-alt])>.table-wrap>table:not(.is-stacked)>tbody>tr>td:nth-child(3)::before`）。**建議：改用通用 `stack-mobile`＋`data-label`（3-E），這兩塊整塊刪。**
4. **`::before` 提示字互相關掉**：L46 加「← 表格可左右滑動 →」，L49 對三種表把它 `content:none`，L50 對 `#s11` 再關一次，L52 對 `#plan-starter` 再關一次，L90 對 stacked 表再關一次。**五處關同一個東西。** 實測 50 個 `.table-wrap` 裡 **49 個是 `no-scroll`、只有 1 個真的需要捲**（375px）。**建議：提示字改成純 JS 條件加上（JS 本來就在算 `is-scrollable`），CSS 端只留一條。**
5. **`pointer:coarse`（L54）夾帶了兩件不相干的事**：一張表的 overflow 設定＋`a.xref` 的觸控熱區。後者是無障礙設定，不該綁在 coarse 上（桌機鍵盤使用者也需要）。
6. **`.wide{min-width:520px}` 在手機被保留**（L55），是 51 張表裡唯一還會橫向溢出的來源之一。
7. **320px 的邊界**：375px 只有 1 張表需橫捲，**320px 變成 12 張**。目前的 `tight-mobile` 是照 375 校準的，沒有餘裕。若要涵蓋 iPhone SE，需再壓一級或接受橫捲。

**簡化後的目標**：`@media (max-width:660px)` **一個區塊**（約 25 條規則）＋`@media (pointer:coarse)` 一個（只放觸控熱區）。刪掉 L50、L52、L92 共 32 條一次性規則，L45/46/49/90 的五處 `content:none` 互消收成一條。

---

# 五、我實際做了什麼查證

- 用 Python 解析 `<style>`（L8–105），拆出 **198 條頂層規則**，統計每個屬性的值域（background 28 種、border-radius 12 種、font-size 27 種、padding 39 種、margin 37 種…）。
- 用 `html.parser` 建 DOM 樹，窮舉每個容器的**祖先鏈**（不是手寫清單）：`figure.chart` 的 5 種落點、`table` 的 21 種 class 組合、`details.more` 的 6 種位置。
- **在 headless Chrome 裡用 375px 的 iframe 實際跑版**（Chrome 在 macOS 最小視窗寬 500px，直接 `--window-size=375` 量到的是 500px；我用 iframe 繞過，已驗證 `innerWidth=375`），取 computed style 與 `getBoundingClientRect`，量到：18 種正文左緣、13 種字級、7 種行高、9 種區塊外距、78/94 摺疊換行（另用 `Range.getClientRects()` 確認續行左突 16px）、6 個膠囊換行、1/50 表格橫捲。
- 在 **650 / 661 / 375 / 320** 四個寬度各跑一次，驗出 640/660 錯位與 320px 的 12 張橫捲表。
- 截了 8 張 375px 截圖（`#s5`、`#s11`、`#costs`、`#lifecycle`、`#s7` 段末四框連放、`#s2` 圖切斷卡）做視覺對照。
- 算了 12 組對比度與 6 組 CIE Lab ΔE（`.credit` 1.46:1、兩種螢光筆 ΔE 26.1/L\*差 2.2、`data-card` vs `part` ΔE 3.6）。
- 用「CSS 有的 class ∩ DOM 沒有的 class」反掃死樣式，再逐個回頭查 `<script>` 與 `lite/index.html`，**修正了 6 個誤判**（`col-card*`、`is-stacked`、`no-scroll`、`is-scrollable`、`stacked-away`、`backbar` 是 JS 產生的；`.lite-plan` 是 Lite 版在用）。
- 追了建置鏈：`tools/build_lite.py:791-792` 用 guide 的 `<style>` 當 Lite 的基礎樣式；`tools/v7_check.py` 沒有版面檢查項。
- **沒有修改任何檔案**。所有暫存（探針副本、截圖）都寫在 session scratchpad，倉庫工作區在我進場前就已經是髒的（11 個檔被別人改著），我沒有動過其中任何一個。

# 六、沒能查證的範圍

1. **列印樣式**（8 個 `@media print`、約 50 條規則）完全沒看。容器收斂一定會動到它。
2. **深色模式**只核對 token 覆蓋，沒有逐框算對比。`.data-card`/`.warning`/`.source-card`/`thead` 是硬寫色＋各自覆寫，要另外驗。
3. **真機**：全部量測都在 Chrome headless。iOS Safari 的 `summary` marker 行為、`::before` 內容、`100vw` 捲軸、`env(safe-area-inset)` 我沒有驗。
4. **`.credit` 那張圖的授權條款**未查 —— 隱形出處標示是否構成授權問題，未知。
5. **1024px 桌機版**只在 661px 抽查一次（確認 padding 33px、radius 24px、圖不出血），沒有整頁看過。
6. **檔案在我量測期間被改動**：`.warning` 9→8。我已用最終快照（md5 `ca65805f2ae7ed9528b9fd5fa13f8102`）複驗過所有頭條數字，但截圖是改動前拍的 —— `#ten` 節的截圖我沒有（也沒拍到），那一節的新版式我**沒看過**。

**相關檔案**：`/Users/linyenchu/Cladue Code/family-finance/guide/index.html`（CSS 在第 8–105 行）、`/Users/linyenchu/Cladue Code/family-finance/tools/build_lite.py`、`/Users/linyenchu/Cladue Code/family-finance/tools/v7_check.py`、`/Users/linyenchu/Cladue Code/family-finance/wip/v63-review/layout-audit-structure.md`（另一份結構稽核，與本報告互補）。截圖在 `/private/tmp/claude-501/-Users-linyenchu-Cladue-Code/5bd6c053-40da-443a-9c76-3bc78e880185/scratchpad/ae_v_*.png` 與 `ae_fig3.png`、`ae_s7tail.png`。