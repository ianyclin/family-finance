# v7.0 設計的工程衝擊地圖（偵查，2026-09-19）

只讀不改的偵查結果。對照 `wip/v63-review/design-v7.md`、`docs/handoff-guide-2026-09-16.md`、`docs/core-edition/specs/lite-format.md` §9／§11。
每一筆都給「檔案:行號」；`guide/index.html` 是壓過的長行（3,299 行 / 1.1 MB），一行可能有很多內容。
標記：**〔確定〕**＝字串比對找到；**〔疑似〕**＝靠命名或程式邏輯推論，附依據。

---

## 1. 新元素 `div.planstep`、`p.planstep-title`、`details.more`

### 1-1 現有 CSS 在哪（`<style>` = guide/index.html 第 8–62 行）

| 東西 | 位置 | 原文 |
|---|---|---|
| 全域 details 間距 | `guide/index.html:10` | `details{margin:14px 0}` |
| 全域 summary | `guide/index.html:10` | `summary{cursor:pointer;font-weight:800;color:var(--green)}` |
| 卡片共用盒子 | `guide/index.html:10` | `.data-card,.source-card,.story,.decision,.warning{margin:22px 0;border-radius:16px;padding:18px 20px}` |
| 白話版 | `guide/index.html:10` | `.explain{padding:14px 16px;background:var(--green2);border-radius:16px}`、`.plain-title{...}` |
| 行動框 | `guide/index.html:10`、`:33` | `.decision{border:2px solid var(--green);font-weight:700}`／`.decision::before{content:"本節行動";...}`（第 33 行是後面再寫一次 `content`） |
| 黃框 | `guide/index.html:10` | `.story{background:var(--amber2);border-left:5px solid var(--amber)}`＋`.story::before{content:"作者的做法紀錄…"}` |
| 小字 | `guide/index.html:10` | `.small{font-size:.84rem;color:var(--muted)}` |
| 深色模式卡片 | `guide/index.html:40` | `.data-card{background:#19251f;…}` `.source-card{…}` `.warning{…}`（**沒有 .story／.decision**） |
| 目錄的 details | `guide/index.html:12–24` | `.toc details.toc-part…`（和主線 details 不同套） |
| 圖內 details | `guide/index.html:59` | `figure.chart details.orig …`（目前沒有東西套用，核准的例外） |

〔確定〕`details.more` 不加任何 CSS 也會長得跟現有摺疊一樣（`details{margin:14px 0}`＋`summary{...}` 是 tag 選擇器）。
〔確定〕`div.planstep` 沒有任何現成樣式可繼承；要新增一條 CSS。若要外觀貼近既有卡片，最省事是把 `.planstep` 併進 `guide/index.html:10` 那條 `.data-card,.source-card,.story,.decision,.warning{…}` 的選擇器清單，並在 `:40`（深色）與 `:41`（列印）兩處各加一次 —— 不加的話深色模式與紙本會少掉底色／`break-inside:avoid`。

### 1-2 列印

| 事項 | 位置 | 原文／行為 |
|---|---|---|
| 網頁列印時展開摺疊 | `guide/index.html:105` | `window.addEventListener('beforeprint',…querySelectorAll('details[data-print]')…` —— 只展開帶 `data-print` 的 |
| PDF 產生時展開摺疊 | `tools/build_lite.py:811-819` `open_details()` | 完整版 `only_marked=True`：`re.sub(r'<details\b(?=[^>]*\sdata-print=)(?![^>]*\sopen\b)', '<details open', s)`；工作表全部展開 |
| **「紙本未印」字樣的產生處** | `tools/build_lite.py:557-559`（`FULL_PRINT_CSS`） | `@media print{details:not([open])>summary::after{content:"（紙本未印，網頁版可展開）"…}` `#annual details:not([open])>summary::after{content:"（紙本未印）"}` |
| 目錄／read-how 的列印例外 | `guide/index.html:24` | `details.read-how[open]>summary{display:none}`、`details[data-print]:not([open])::details-content{content-visibility:visible;display:block}` |
| 分頁摺疊 | `guide/index.html:41` | `details[data-print="page"]{break-before:page;break-after:page;break-inside:avoid}` |
| 現況 | — | `data-print="open"` 35 處、`data-print="page"` 3 處 |

〔確定〕設計第 1 節規則 6（`details.more` 不印、印「紙本未印，網頁版可展開」）**不需要改任何程式**：`FULL_PRINT_CSS` 是對所有沒展開的 details 生效的通則。要改的只有「別誤加 `data-print`」。
〔疑似〕若 `details.more` 數量暴增（每節一兩個），完整版 PDF 每個未展開摺疊都多一行提示字，頁數會往上飄；`blank_pages`（>3 頁近乎空白才 WARN）與 `tail_flows` 的接排邏輯（`tools/build_lite.py:873`、`make_pdfs` 最多四輪）都會跟著重跑，但不會 FAIL。依據：這兩支都是 WARN／自動處理，沒有硬上限。

### 1-3 會不會撞到檢查

- 〔確定〕**沒有任何「區塊順序」檢查**。`tools/guidetools.py:54-78` `check()` 只驗：標籤開合（`TAGS`，`tools/guidetools.py:14`）、id 重複、壞 href、`<a>` 巢狀、term 連結不在 `div.story` 內、term 不在 `<strong>` 內。「來源→黃框→行動」「p.decision 必須最後」只寫在交班文件 `docs/handoff-guide-2026-09-16.md:94` 的表格裡，**程式沒有實作**。
- 〔確定〕**沒有 class 白名單**。`tools/lite_sentinels.py` 全檔沒有允許 class 清單；只有 `part_maps`（`:257-320`）、`toc_order`（`:188-227`）針對特定 class 做結構比對。新增 `planstep`／`more` 兩個 class 不會紅。
- 〔確定〕`tools/guidetools.py:74-75` 的 `check` 統計行會印 `details` 數量；`tools/test_guidetools.py:48-52` 只比較「同一份檔案加上 data-lite 屬性前後」的計數是否相同，不是和歷史基準比 → 新增 details 不會讓測試紅。
- 〔確定〕`tools/test_guidetools.py:34` 會對每個 `<details` 注入 `data-lite="ch9"` 再跑 `to_text` 比對；`details.more` 一樣走得過（`open_tag()` 容許額外屬性）。
- 〔注意，確定〕`tools/guidetools.py:14` 的 `TAGS` 有 `div`、`p`、`details`：新卡片若少一個 `</div>` 會被 `check` 抓到，這是好事。
- 〔確定〕`tools/build_lite.py:977-979` `FRAGMENT_TAGS` 也含 `div`／`p`／`details`，發布片段的標籤平衡照樣把關。
- 〔確定〕`div.planstep` 若放在 `div.story` 裡會觸發 term 連結檢查嗎？不會——除非裡面有 `a.term`。設計把 planstep 放在黃框「之後」，不在黃框內，安全。
- 〔確定〕**`stories` 哨兵**（`tools/lite_sentinels.py:717-735`）比對黃框純文字；planstep 插在黃框後面不影響，插進黃框內就會 FAIL。
- 〔疑似〕`alt` 指紋：`lite/alt/*.html` 的 `src` 選擇器指向帶 `data-lite-alt` 的元素（例如 `ch4-drill.html:4` `src: [data-lite-alt~="ch4-drill"]:nth(1) sha256=266a8991…`）。在這些元素**內部**加 planstep 會讓 sha256 變 → `alt` FAIL，要人重看短稿再 `--stamp`。放在外面就沒事。依據：`lite-format.md:322` 的 `alt` 規則。

**結論**：第 1 項是本輪最便宜的一項。要動的檔只有 `guide/index.html` 的 `<style>`（第 10／40／41 行三處各加一個選擇器），程式與哨兵零改動。不要為了樣式去改 `build_lite.py` 的 `FULL_PRINT_CSS`（那會影響全書所有摺疊）。

---

## 2. 節順序改動（start 提前到 why 前；glossary 搬到 group-ref／toolbox 前）

### 2-1 現況（`guide/index.html`）

| 東西 | 行 | 原文（節錄） |
|---|---|---|
| 封面入口 `nav.tasks` | `:72-82` | `:74` `<li><a href="#ten">只有十分鐘，先抓重點</a></li>`／`:75` `<li><a href="#start">先確認能不能開始投資（預備金、卡債、保單）</a></li>`／`:82` `看不懂的詞，翻「<a class="xref" href="#glossary">先認識這些詞</a>」；想從頭讀，往下看<a href="#toc">目錄</a>。` |
| 「預設讀法」文字 | `:83`（`details.promise.read-how`） | `<strong>預設讀法（一條路）：</strong>「…#ten…」→「…#start…」→「…#glossary…」的前十四個 → 第 …#s1… 節起，照目錄往下讀。`；同行前面另有「看到不懂的詞，先翻「#glossary」。」 |
| 目錄「開始之前」組 | `:87-88` | `:88` `<ul><li><a href="#ten">…</a></li><li><a href="#why">為什麼選指數化…</a></li><li><a href="#start">投資前的安全順序</a></li><li><a href="#glossary">先認識這些詞</a></li></ul></details>` |
| 目錄「查資料」組 | `:99-100` | `:100` `<ul><li><a href="#toolbox">去哪查：官方入口與延伸閱讀</a></li><li><a href="#methods">資料口徑與來源</a></li></ul></details>` |
| 正文 why | `:118` | `<section class="part" id="why"><h2>為什麼選指數化：得到什麼、要接受什麼</h2><p class="lede">這一頁是全篇的地圖…</p>` |
| 正文 start | `:248` | `<section class="part" id="start"><h2>投資前的安全順序</h2><p class="lede">先打地基，再蓋樓；投資是樓上的事。</p>` |
| 正文 glossary | `:310` | `<section class="part" id="glossary"><h2>先認識這些詞</h2><p class="lede">前後各節都會用到，看不懂的時候回來查。</p>` |
| group-ref 分組節 | `:3264-3267` | `:3264` `<section class="part" id="group-ref"><h2>查資料</h2><p class="lede">官方網站、延伸閱讀…</p>`；`:3265` `<ol class="part-map">`；`:3266`／`:3267` 兩個 `li` |
| toolbox | `:3272` | `<section class="part" id="toolbox">…` |

### 2-2 會紅的哨兵與各自的改法

**`order`（`tools/lite_sentinels.py:188-227` `check_toc_order`）**〔確定〕
- 規則：`nav#toc` 裡所有 `<a href="#id">` 的順序，必須逐一等於正文 `section.part[id]`（排除 `group-*`）的順序，每節剛好一次（`:198-211`）。
- 另一條：每個 `details.toc-part[data-group=X]`，`X` 必須是正文裡「緊接在該組第一節前面」的那個 section（`:212-225`）。
- 改法：**只改 `guide/index.html`，不動哨兵**。（a）正文 `start`（:248）搬到 `why`（:118）前面，目錄 `:88` 的 `<li>` 跟著調成 ten→start→why。（b）glossary 的 `<li>` 從 `:88` 移到 `:100`，正文 glossary 區塊搬到 `#group-ref`（:3264）之後、`#toolbox`（:3272）之前。
- **陷阱（確定）**：把 glossary 放成 group-ref 組的第一條時，`data-group` 那條規則要求正文裡 glossary 的前一個 section 必須是 `group-ref`。所以 glossary 必須「緊接在 group-ref 分組節後面」，不能插在 toolbox 和 methods 中間。若要放在 toolbox 之後，目錄該組的 `<li>` 順序也得一致（toolbox→glossary→methods），這樣 `data-group` 檢查看的是第一條 toolbox，反而更安全。

**`part_maps`（`tools/lite_sentinels.py:257-320` `check_part_maps`）**〔確定〕
- 逐字比的是四件事：組地圖 `li` 的連結文字 ＝ 目標節 h2 去掉 `span.num` 後的文字（`:300-303`）；`span.map-lede` ＝ 目標節 `p.lede` 的文字（`:304-308`）；`span.map-num` ＝ 目標節 `span.num`（沒節號就不准有 map-num，`:309-314`）；`li` 的 href 順序 ＝ 目錄同組的連結順序（`:315-316`）。另外分組節自己的 `p.lede` 要等於目錄該組的 `toc-part-desc`（`:285-287`）。
- 改法：在 `guide/index.html:3265` 的 `<ol class="part-map">` 裡加一個 `li`：連結文字必須逐字是「先認識這些詞」，`map-lede` 必須逐字是「前後各節都會用到，看不懂的時候回來查。」，**不可以有 map-num**（glossary 的 h2 沒有 `span.num`）。若同時改了 glossary 的 h2 或 lede，三個地方（正文、組地圖、目錄 `li` 文字）要一起改。
- 「開始之前」那一組（`:87-88`）**沒有 `data-group`、也沒有對應的 `group-*` 分組節**，所以 start／why 對調只動目錄與正文，`part_maps` 不受影響。

**`xref_num`（`tools/lite_sentinels.py:230-254`）**〔確定〕不受節順序影響（只看顯示節號），但 start／why／glossary 都沒有節號，全書指向它們的連結用的是節名而非數字，安全。

**封面入口與預設讀法**〔確定〕：`:75`（start）與 `:82`（glossary）的連結不會壞（id 不動），但語意要跟著改；設計第 5 節已點名「預設讀法裡『先讀前十四個詞』那句拿掉」＝ `guide/index.html:83`。同一行還有一句「看到不懂的詞，先翻『先認識這些詞』」，以及底下「另外兩條路線」的摺疊也提到 ten／start，一起讀過再改。

**`lite/manifest.json`**〔確定〕**完全沒有引用這三節**。全檔只有兩個 `src`：`#ten div.warning`、`#rebalance-525`（`lite/manifest.json` 的 `cards` 章）。節順序改動對工作表零影響。

**`build_lite.py` 有沒有寫死節順序／頁碼**〔確定〕**沒有**：
- 目錄頁碼是動態的：`make_pdfs`（`tools/build_lite.py:941-960`）從 `nav.toc` 正則抓 `toc_order`，`print_with_toc`（`:845-859`）最多印四次直到頁碼不變。
- 節尾接排：`tail_flows`（`:873`）＋`flow_css`（`:888`）用的是 `toc_order` 與實測頁面字數，不是寫死的節。
- 頁數上限只有工作表那邊：`pages` 哨兵 `tools/lite_sentinels.py:517`（`page_limit`，manifest 寫 5）、`:544-546`（plan 必須奇數頁、lookup 緊接下一頁）、`worksheet` 哨兵 `:784`（PDF 剛好 4 頁，常數 `WORKSHEET_PAGES=4` 在 `:17`）。**完整版沒有頁數上限**，只有 `blank_pages` 在近乎空白頁 >3 時 WARN（`:590`）。
- 唯一的奇偶頁假設在工作表第 1／2 頁，和節順序無關。

---

## 3. F 區三格收成一格：所有要同步的位置

搜尋法：對 `guide/index.html`、`lite/alt/*.html`、`lite/facts.txt`、`lite/case-checks.json`、`tools/calc_core.py`、`tools/essay_charts.py`、`tools/v63_g01_plan_flow.py`、`lite/manifest.json` 掃 `跌 10`／`10%／20%／30%`／`三種跌幅`／`三格`／`20%、30%`／`照常投入`／`F 區`。`lite/alt/retired/` 依指示不計。

### 3-1 `guide/index.html`（**確定**，共 13 筆直接寫到三格／三種跌幅）

| 行 | 節 id | 逐字引句（去標籤） |
|---|---|---|
| 113 | ten | 「定好股債比，寫進「我的投資計畫」。**股票那一塊從最近高點跌 10%、20%、30% 以上各做什麼**，要在平靜的時候先寫好」（ten 第 5 條） |
| 115 | ten | 「大跌時恐慌賣。**股票那一塊從最近高點跌 10%、20%、30% 以上各做什麼**，在平靜的時候先寫好」（六個最貴的錯，`details[data-lite-alt="ch1-six"]`） |
| 2291 | s9 | 「所以呢：少買賣。**F 區三格都寫照常投入**，這三塊錢就省下來了。」 |
| 2441 | s10 | 「新的比例寫多少、跟著要改的規則是什麼（D 區重查一次表、E 區重算大跌少多少、**F 區三格重寫**；計畫表在第 11 節）」（冷卻期四問第四題） |
| 2459 | s11 | `#plan-panic`：「翻到 F 區…**股票那一塊跌 10%、20%、30% 以上各做什麼**；什麼情況才可以賣…」 |
| 2459 | s11 | 白話版／八區說明：「F 規則：股票那一塊從最近高點跌 10%、20%、30% 以上各做什麼、什麼情況才賣、冷卻期、多久看一次。**最不用臨場判斷的答案是三種跌幅都寫「照常投入，什麼都不改」。**」（**這句就是 `mark.key`**） |
| 2512 | s11 | plan-flow 圖 SVG（桌機版）`<text …>跌 10%／20%／30% 以上各做什麼、什麼情況才賣、冷卻期</text>` |
| 2572 | s11 | plan-flow 圖 SVG（手機版）`<text …>跌 10%／20%／30% 各做什麼</text>` |
| 2585 | s11 | plan-flow 的 `p.note`：「**F 區跌 10%、20%、30% 三格量的是股票那一塊**，從最近的高點算，算法在同一節。」 |
| 2588 | s11 | 欄位表第 19–20 格：「…**20 股票那一塊跌 10%、20%、30% 以上各寫一句。**再從這二選一…」；同一行第 19 格是「F 跌幅跟什麼比」的口徑句 |
| 2589 | s11 | 一頁空白版（`details[data-lite-alt="plan-blank"][data-print="page"]`）：「F 規則　跌幅：股票那一塊從最近高點算（新存入、領出的錢不算）**跌 10%＿＿　跌 20%＿＿　跌 30% 以上＿＿**大跌時：□只用新錢補　□年檢照門檻動防守…」 |
| 2640 | s11 | 兩把尺 `data-card[data-lite-alt="ch4-steps"]` 小字：「這裡的「能忍的跌幅」是整體帳面少幾成，和 **F 區三格量的「股票那一塊跌幾成」**不是同一把尺」 |
| 2646 | s11 | 小安全表 F 區：「跌幅怎麼算：股票那一塊，從最近的高點算…**股票那一塊跌 10%、20%、30% 以上：照常投入**（兩筆自動扣都不改金額、不停扣）；跌 20% 時把當下想做的事寫在紙背面，不動手。」 |

另有**間接相關**（沒寫三格，但講 F 區「跌幾成那一格」）〔確定〕：
- `guide/index.html:2643` `#drill` 第 3 步：「抄下計畫表 F 區，跌幅最接近那天的那一格寫的：＿＿＿。」＋小字「F 區量的也是股票那一塊，不用換算：這一步的股票跌 50%，直接看 **F 區「跌 30% 以上」那一格**。」——收成一格後這兩句都失效。
- `guide/index.html:2588` 第 21 格「可以賣」與 F 選項五種（「F 的選項其實只有五種：照常投入、照常投入並額外加碼股票、照再平衡規則處理、不看、賣」）。
- `guide/index.html:2757`（cases 阿凱）「八成約 487 萬…寫出來是「先賣一些」，和 F 區不一樣，沒通過…六成…寫得出「照常投入、不賣」，和 F 區一樣，通過」。
- `guide/index.html:2788`（cases 小芸阿哲）「2056 年約 724 萬、跌 50% 少 290 萬，他們寫得出「照常投入」，通過」。
- `guide/index.html:2874-2879`（s12，顯示 13）「什麼時候賣（F 區）」「多久看一次（F 區）」「再平衡由平台做的，F 區就寫「照常投入，不自己動」」。
- `guide/index.html:2896`（group-situations 狀況索引）「先打開自己計畫表的 F 區照做」「把跌了做什麼寫進 F 區」。
- `guide/index.html:2930`（s13，顯示 14，`#s13-drop20`）「市場下跌 20%…再照**規則卡上「跌 20%」那一格**做；跌幅看股票那一塊，從最近的高點算。」←**收成一格後這句一定要改**。
- `guide/index.html:3239`（lifecycle 提領）「門檻用計畫表 F 區自己那一把尺」。
- `guide/index.html:3295`（methods 版本紀錄）「v6.3（2026-09-18）：…**F 區改用股票跌幅**…」。

### 3-2 `lite/alt/`（工作表四頁的來源）〔確定〕

- `lite/alt/plan-blank.html:23`（第 1 頁計畫表空白版本體，F 區三行手寫線）——收一格後**整個 F 區區塊要重排**，並重新 `--stamp`。
- `lite/alt/plan-blank.html:6,9,16,17,18,20,21` 檔頭 note 逐條記了 F 區歷次改動（`:9`「F 區三種跌幅、G 區各占一整行」、`:20`「F 區跌幅口徑改成…；工作表專有：F 區三行手寫線加高（完整版空白版維持一行三格）」）。note 是給人看的，不影響哨兵，但要補一條新 note 說明這次收一格。
- `lite/alt/ch4-drill.html:12` 第 3 步「直接看 F 區『跌 30% 以上』那一格」＋檔頭 `:9,:10` 的 note。
- `lite/alt/app-a-checklist.html:11` 的「三格」是**年檢勾選欄的三格（沒問題／不適用／尚未確認）**，與 F 區無關，不要誤改。
- `lite/alt/lookup-tables.html`：沒有 F 區跌幅字樣。

### 3-3 其他檔

- `lite/facts.txt`〔確定〕**沒有任何 F 區跌幅的行**；唯一和 F 區沾邊的是 `:33`「跑掉一點點不用管。常見的尺叫 5/25：差超過 5 個百分點…」（5/25 門檻，兩份逐字比）。收一格若動到 `#rebalance-525` 那段就會 FAIL。
- `lite/case-checks.json`〔確定〕只剩一條（查表頁扣費算例，`:3-8`），**與 F 區無關**。
- `tools/calc_core.py`〔確定〕
  - `:234` `'八成「先賣一些」沒通過 → 七成「想停扣」沒通過 → 六成「照常投入」通過（虛構的回答，不是算出來的）'`（阿凱演練 story 字串）。
  - `quotes`（`:1047` 起）中會被 F 區改動牽動的：`:1087-1089` 三條 D04 欄位表第 20 格的例子——`'股票跌一半以後股票剩 40 萬、總共剩 60 萬，股票占 66.7%'`、`'從防守搬 8 萬去買股票（防守從 20 萬剩 12 萬）'`、`'要再投入 40 萬新錢才回得到八成'`；以及 `'2046 年約 203 萬、跌 50% 少 81 萬'`（演練，若演練仍用跌 50% 就不動）。刪掉書上的句子而沒同步 quotes → `引用缺漏`（`calc_core` 末段 `:1112` 的比對）。
  - `R['rebalance_after_crash_d04']`（`:658-662`）是這三句的算處，數字本身不必改。
- `tools/essay_charts.py`〔確定〕本身沒有 F 區三格字樣；圖是委派的：`:811-813` `def plan_flow(): import v63_g01_plan_flow as _g01`，`:922` `funcs["plan-flow"] = plan_flow`。
- `tools/v63_g01_plan_flow.py`〔確定〕**三筆**：
  - `:33` `('box', 'F', '規則', '跌 10%／20%／30% 以上各做什麼、什麼情況才賣、冷卻期', '跌 10%／20%／30% 各做什麼'),`（桌機／手機兩種文字，就是 guide `:2512`／`:2572` 的來源）
  - `:52` `'numbers_on_chart': '只有區名裡本來就有的 4%（B 區高利率債的粗尺）與 10%／20%／30%（F 區三格）',`
  - `:135` `'F 區跌 10%、20%、30% 三格量的是股票那一塊，從最近的高點算，算法在同一節。'`（p.note，就是 guide `:2585`）
  - **只改 guide 沒用**：`essay_charts.py --guide` 會整塊重建 `figure.chart`（交班文件 `docs/handoff-guide-2026-09-16.md:138-140`），p.note 會被蓋回腳本版並印 `⚠`。

### 3-4 `lite/manifest.json`
〔確定〕不含跌幅字樣；但 `cards` 章抽 `#rebalance-525` 與 `alt: ch4-drill`，兩者都會被這次改動碰到。

**筆數**：直接寫「三格／三種跌幅／10%、20%、30%」的位置 —— guide 13 筆、plan-flow 模組 3 筆、`lite/alt/plan-blank.html` 1 筆本體＋7 條 note、`lite/alt/ch4-drill.html` 1 筆本體＋2 條 note＝**確定 25 筆**；間接（講 F 區某一格、演練結論）另有 **確定 11 處**。

---

## 4. `mark.key` 改字：誰記了那 14 句

- 〔確定〕**程式裡沒有任何地方存那 14 句的文字。** 全庫掃「最不用臨場判斷」只命中：`docs/handoff-guide-2026-09-16.md:111`（14 句清單）、`lite/work/patch-step0.json:136-137`（歷史補丁）、`lite/work/full-v60.txt:1360`（build 自動 dump 的純文字，會自己重生）。
- 〔確定〕`tools/guidetools.py:74` 的 `check` 只印 `marks <數量>`，不比內容、不 FAIL；`tools/test_guidetools.py:82-83` 只測「加一個 mark 計數 +1」。
- 〔確定〕`tools/lite_sentinels.py` 完全沒有 mark.key 檢查（`unused_marks` 指的是 `data-lite` 標記，`:631-641`，不同東西）。
- 〔確定〕`lite/facts.txt` 沒有這句；`tools/calc_core.py` 的 `quotes` 也沒有這句。
- 要改的只有**文件**：`docs/handoff-guide-2026-09-16.md:111` 的清單、以及 `:91` 的「目前 14 句」數量。若 s1 等節在減重時砍掉 mark.key，數量也要改。
- 〔疑似〕「一節最多一句」是紙上規則，沒有程式把關。依據：`check()` 只數總量，沒有 per-section 統計。

---

## 5. 數字保全檢查：`guidetools.py numbers` 夠不夠用

**用法**〔確定〕：`python3 tools/guidetools.py numbers <old.html> <new.html>`（`tools/guidetools.py:8`、`:133`）。

**它做什麼**（`tools/guidetools.py:114-123`）：
1. 兩份各跑 `to_text()`（`:88-103`）轉純文字；
2. `sections()`（`:105-112`）用 `\n## `（＝`<h2>`）切段，**以 h2 標題文字當 key**；
3. 每段用 `re.findall(r'\d+(?:[.,]\d+)*')` 做 `Counter`，印出 `## 標題` ＋ `LOST: {...}` / `ADDED: {...}`。

**它涵蓋什麼**〔確定，實測 `to_text` 輸出）：
- **含**摺疊（`details` 內文全留，`<summary>` 變成「【摺疊】」）、`p.small`／`span.small`（變「〈小字〉」）、表格（`<td>` 變 `|`）、`mark.key`、`figcaption`、`a.term`。
- **不含來源卡**：`to_text` 預設 `keep_sources=False`，`strip_div(h,'source-card')`（`:91`）整塊刪掉 → **來源卡裡的年份、頁碼、數字不在比較範圍**。這正是設計第 1 節規則 3「來源卡跟著數字走」要盯的地方，`numbers` 幫不上忙。
- **不含 SVG**（`:93` 移除 `<svg>…</svg>`）→ 圖上的數字不比。
- **不含黃框**：`sections()` 會丟掉以「【黃框】」開頭的行（`:110`）。實測全書 25 個 `div.story` **每一個都是單一文字區塊**，所以黃框數字整塊被排除（〔確定〕，用 `div_blocks` 逐個檢查過）。黃框本來就不准改，可接受。
- **不含國字數字**（「三成」「一半」「十四個」）——`\d` 只抓阿拉伯數字。這正好是 `lite-format.md:347-350` 說的「哨兵擋不住的三條路」之一。

**能不能拿來做「每節改前改後阿拉伯數字集合比較（含摺疊與小字）」**
〔確定〕**可以，而且正是為此寫的**，但有四個缺口：

1. **來源卡被整塊排除** → 移層時把數字搬進來源卡、或把來源卡刪掉，`numbers` 都看不到。缺的是一個 `keep_sources=True` 的開關（函式已經有參數，`to_text(path, keep_sources=False)`，CLI 沒有暴露 → **改一行 argv 即可**）。
2. **靠 h2 標題當 key**：本輪設計允許改 h2 嗎？`design-v7.md:23` 說 h2 節名不能動（除非點名），所以大致安全；但**一旦某節 h2 改字，那一節會被判成「整節 LOST ＋ 新節 ADDED」**，輸出爆量、不可讀。實測目前 36 個 h2 chunk、無重名。缺的是「用 section id 當 key」。
3. **只比多重集、不比位置**：同一個數字從主線搬到 `details.more` 不會被發現（這是設計要的），但同一個數字被「改掉又在別處新增同值」也看不出來。
4. **沒有 exit code**：`numbers()` 只 print，永遠 return None → 不能當 CI 關卡，只能人看。要進「每批必跑」的流程得自己包一層判 `LOST` 非空。

〔疑似〕封面（第一個 h2 之前的內容）會落在 `sections()` 的第一個 key（`\n` 開頭那段）裡，key 是空字串或首行文字；封面改動的數字可能報在一個看不懂的標題下。依據：`re.split(r'\n## ', '\n'+text)` 的第一塊沒有 h2。

---

## 6. `guidetools.py apply` 的補丁格式與限制

**格式**（`tools/guidetools.py:9`）：`[{"section": "...", "old": "...", "new": "...", "why": "..."}]`，可一次給多個檔：`apply <base.html> <out.html> <patch1.json> [patch2.json ...]`（`:4`、`:127`）。

**限制**〔確定，`tools/guidetools.py:35-52`〕：
1. `old` 在**整個檔**必須剛好出現一次（`h.count(x['old']) != 1` → `APPLY FAILED`，`:40-42`）。`section` 欄位只是標籤，**程式完全不用它縮小搜尋範圍**。
2. 會檢查各補丁命中的區間不重疊（`:44-47`）。
3. **長度沒有上限**：`old` 可以是幾萬字的整個 section，只要逐字相同（含空白、換行、屬性順序）。實務難點是 SVG 圖與壓行的 HTML 很難逐字抄對。
4. **致命細節**：實際替換用 `h.replace(x['old'], x['new'])`（`:50`），`str.replace` 會換掉**所有**出現處。唯一性只在替換「之前」用原始 `h` 驗過一次。**若某個補丁的 `new` 產生的文字，剛好等於另一個尚未套用的補丁的 `old`，那個 `old` 會被替換兩次且不報錯。** 搬移整個 section（＝一個補丁刪、一個補丁插）正好是最容易踩到的情境。
5. 沒有備份、沒有 dry-run；輸出寫到另一個檔（`out.html`），所以流程上是「套到副本 → 檢查 → 再覆蓋」。

**搬移整個 section 比較安全的做法**（依上述限制推導，〔疑似〕但有程式依據）：
- **首選：一個補丁涵蓋「兩節之間的整段」。** 例如 start 提到 why 前：`old` ＝ `<section … id="why">…</section>\n…\n<section … id="start">…</section>` 整塊（guide 第 118–309 行），`new` ＝ 同樣內容前後對調。只有一個補丁、沒有重複字串風險。缺點：`old` 很長（約 200 行、數萬字），要用程式從原檔切出來，不能手抄。
- **次選：兩個補丁（挖除＋插入），但插入點必須在挖除點之外，且互相檢查「A 的 new 不包含 B 的 old、B 的 new 不包含 A 的 old」。** 這條檢查程式沒做，得人工／腳本自己確認。
- **不要用**：以節首一行當 `old`、只搬標題那種做法（會留下孤兒內容，`check` 的標籤平衡會抓到，但 diff 很難看）。
- 套完一定接 `python3 tools/guidetools.py check`（標籤平衡＋id 重複＋壞 href）與 `diff` 產出純文字 diff 給人看（`:130-132`）。

---

## 7. build 一次要多久、需要什麼外部程式

**外部相依**〔確定〕：
- **Google Chrome**（不是 Chromium、不是 Playwright）：`tools/build_lite.py:18` `CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'`，`chrome_pdf()`（`:820-831`）用 `--headless=new --disable-gpu --no-pdf-header-footer --generate-pdf-document-outline --virtual-time-budget=8000 --print-to-pdf=…`，單次列印硬逾時 300 秒（`:828`）。註解另記：**加 `--user-data-dir` 會讓 headless 卡住不出檔**（`:821`）。
- **PyMuPDF（`import fitz`）**：`tools/build_lite.py:834, 866, 896, 909, 1048`，以及哨兵讀頁數／書籤。
- 其他都是標準庫（`sys, os, re, json, hashlib, unicodedata, subprocess, shutil, argparse, time`，`:15`）。`tools/essay_charts.py` 另外才需要資料相依。
- 〔確定〕**沒有 playwright、沒有 chromium 套件**。

**耗時**〔疑似，用檔案 mtime 推估，程式沒有任何計時器 —— `time` 只用在 `:1040` 印時間戳〕：
- 最近一次 build（2026-09-19）：`lite/index.html`／`output/guide.html`／`output/lite.html` 05:07:44 → 工作表 PDF 05:07:48（約 4 秒）→ `lite/work/print/print-full.html` 05:08:13 → 完整版 PDF 與 export 05:08:21。
- 即 **HTML 階段幾秒、工作表 PDF 約 4 秒、完整版 PDF 約 33 秒**（176 頁、24 張 SVG，`print_with_toc` 最多 4 次列印 × 最多 4 輪 `tail_flows` 重排，`:950-958`）；之後還要跑約 27 類哨兵（要再開 PDF 讀每頁文字）。
- 〔疑似〕**整趟 `python3 tools/build_lite.py` 約 1–3 分鐘**；歷史紀錄 `lite/work/build.log:27-28` 顯示 v6.0 時「完整版 134 頁、印 6 次」，頁數與列印次數都比現在少，所以取上緣比較保險。v7 若頁數再長、摺疊變多，列印輪數可能增加。

---

## 8. `#drill`（指南）vs `lite/alt/ch4-drill.html`：逐段 diff

方法：從 `guide/index.html` 抓 `<span id="drill"></span>` 到該 `div` 結束（第 2643 行），與 `lite/alt/ch4-drill.html:12` 去標籤後逐 `<li>`／`<br>` 比對。

**結論〔確定〕：兩份是同樣的 6 個步驟，字數幾乎相同；沒有任何一份多出整段。前一位偵查「工作表版多三段」的說法不成立。**

唯一的兩處差異都是「填寫格」的排版，不是內容：

| 步 | 指南 `guide/index.html:2643` | 工作表 `lite/alt/ch4-drill.html:12` |
|---|---|---|
| 第 2 步 | `想像那天打開 app，看到這個數字。寫下你真的會想做的事：＿＿＿（賣掉、停扣、加碼、刪 app……）。` | `想像那天打開 app，看到這個數字。寫下你真的會想做的事（賣掉、停扣、加碼、刪 app……）：` ＋ 一條加高的手寫線 `div.lite-line` |
| 第 3 步 | `抄下計畫表 F 區，跌幅最接近那天的那一格寫的：＿＿＿。` ＋ `<br>` 後接小字 | 同一句，`＿＿＿` 換成手寫線；小字**逐字相同**：`F 區量的也是股票那一塊，不用換算：這一步的股票跌 50%，直接看 F 區「跌 30% 以上」那一格。` |

其餘完全逐字相同，包括你在指南裡讀到的那兩段：
- 「F 區量的也是股票那一塊，不用換算…」→ 兩份都有（指南第 3 步小字、短稿第 3 步小字）。
- 「年檢時比例掉出門檻，規則會要你把防守的錢移去買股票…只用新錢補，不動防守」→ **兩份都有，都是第 5 步**。
- 第 4 步三條路（降一成／降到兩成還是做不到／比例改了怎麼記）兩份都有。
- 唯一 HTML 層的差異：指南第 4 步的「（要不要過冷卻期，看第 10 節）」包在 `<span data-lite="skip">` 裡（抽取實作版時會被拿掉），短稿把它寫成明文 —— 見 `lite/alt/ch4-drill.html:5-6` 的 note。顯示文字相同。

〔確定〕短稿指紋 `sha256=266a8991d54593de2f3154d72646331201401fab35b46bdf60e0190b9773eec8`（`lite/alt/ch4-drill.html:4`）盯的是指南那張卡；F 區收一格時兩份都要改，改完要 `python3 tools/build_lite.py --stamp ch4-drill`，而且照 `lite-format.md:322` 必須**人先逐字看過**再 stamp。

---

## 順帶看到（與本任務無關，各一行）

- `guide/index.html:33` 的 `.decision::before{content:"本節行動"}` 和 `:10` 裡同一條規則重複，第 33 行少了顏色與字級（後者覆蓋前者的 content，其餘靠繼承），看起來是歷次壓行留下的殘件。
- `guide/index.html:40`（深色模式）沒有覆寫 `.story`、`.decision`，`:41`（列印）才把它們改成白底。
- `tools/guidetools.py` 的 `numbers` 沒有 exit code，無法當關卡；`apply` 的 `section` 欄位程式從不使用。
- `lite/manifest.partA.json`／`partB.json` 依交班文件仍跑不起來（引用已退場短稿）。
- 封面入口 `guide/index.html:78` 的「大跌很慌、想賣」現在連 `#group-situations`，設計第 6 節要求改連 `#plan-panic`。
