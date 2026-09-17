# 施工計畫：按功能分七組（給 builder）

對應給作者看的文件：`wip/v61-2026-09-17/restructure/recommended-structure.md`（下稱「推薦文件」）。
數字與字串是 2026-09-17 從工作區的 `guide/index.html` 掃出來的，當時另一條工作流的改動還沒提交。**動手前先重掃一次**，對不上就停下來回報，不要猜。

---

## 0. 前提、範圍與硬規則

**開工前**
1. 另一條工作流（firstmonth 搬移、目錄分組、withdraw 改名、D10 列印）已經提交，`python3 tools/build_lite.py` 全綠。
2. 作者已經回答推薦文件第六節的三題，也核准第七節列的新文字。本計畫以「第 1 題選 A、第 2 題選 A、第 3 題選 A」為主線寫；選 B／C 時照第 3 節的選做批次追加。
3. `git add -A && git commit`，再 `cp guide/index.html guide/index.v61-restructure.backup.html`。

**範圍（主線）**
- 搬節：只搬整個 `<section class="part" id="…">…</section>`。卡片一張都不跨節搬。
- 顯示節號：**第 1–14 節一個都不變**，不需要重編號。
- 新增 4 個分組節：`group-plan`、`group-situations`、`group-life`、`group-ref`。改寫 2 個：`group-core`、`group-howto`。
- 目錄改成 7 組可收合；封面加任務入口，閱讀方式框改兩句並收成摺疊。
- 加 18 個錨點（第 8 節）。

**硬規則（違反就停）**
- section id 一律不改。新分組節的 id 一律用 `group-` 開頭。`class` 保持 `class="part"` 原樣：舊腳本與掃描器用 `<section class="part" id=` 精確比對，不要加第二個 class。
- 不碰：`div.story`（黃框）、`mark.key`、`lite/facts.txt` 裡的句子、`details[data-lite-alt="plan-blank"]`、`details[data-lite-alt="lookup-tables"]`、`div[data-lite-alt="ch4-drill"]`、`#ten div.warning`、`#annual ol.checklist`（含「儲蓄率：」那一張，工作表第 3 頁的指紋來源）。
- 錨點不得加在上面這些區塊裡面，也不得改動它們的起始標籤。要連到這些區塊時，在它們**前面**插一個空的 `<span id="…"></span>`。
- 主線做完以後，`alt` 哨兵要**零 stamp** 就全綠。只要有任何短稿要 `--stamp`，就表示碰到了受保護區塊：還原那一筆，不准 stamp。

---

## 1. 新順序總表

「顯示」欄是 h2 裡 `span.num` 的數字（不變），「—」表示沒有節號。

| # | id | 組 | 顯示 | 動作 |
|---|---|---|---|---|
| 1 | ten | 開始之前 | — | 不動 |
| 2 | why | 開始之前 | — | 不動 |
| 3 | start | 開始之前 | — | 不動 |
| 4 | glossary | 開始之前 | — | 不動 |
| 5 | **group-core** | 先搞懂 | — | 原地改寫成組地圖（§6.1） |
| 6–15 | s1 … s10 | 先搞懂 | 1–10 | 不動；只在 s2、s5、s6、s8、s10 加錨點（§8） |
| 16 | **group-plan** | 寫計畫 | — | **新增**，插在 s10 與 s11 之間（§6.2） |
| 17 | s11 | 寫計畫 | 11 | 不動；加 `plan-table` 錨點、在 ch4-drill 前插 `<span id="drill">` |
| 18 | cases | 寫計畫 | 12 | 不動；加 `case-chen` 錨點 |
| 19 | s12 | 寫計畫 | 13 | 不動；加 `s12-paths` 錨點（給 products 的指路句） |
| 20 | **group-situations** | 遇到狀況 | — | **新增**，插在 s12 與 s13 之間（§6.3，含狀況索引） |
| 21 | s13 | 遇到狀況 | 14 | 不動（位置沒變）；加 6 個群組錨點 |
| 22 | sidepaths | 遇到狀況 | — | **搬**：從 lifecycle 與 annual 之間，搬到 s13 後面；改一處「（上一節）」（§9） |
| 23 | **group-howto** | 動手做 | — | 原地改寫成組地圖（§6.4）。搬完 sidepaths 以後，它就在 sidepaths 正後方 |
| 24 | firstmonth | 動手做 | — | **搬**：從 steps 後面搬到 steps 前面 |
| 25 | steps | 動手做 | — | 不動 |
| 26 | products | 動手做 | — | 不動；第 2 題選 A 時加一句指路（§9） |
| 27 | costs | 動手做 | — | 不動；加 `costs-four` 錨點 |
| 28 | **group-life** | 隨人生調整 | — | **新增**，插在 costs 後面（§6.5） |
| 29 | annual | 隨人生調整 | — | **搬**：排到 lifecycle 前面 |
| 30 | lifecycle | 隨人生調整 | — | **搬**：排到 withdraw 前面 |
| 31 | withdraw | 隨人生調整 | — | **搬**：排到 lifecycle 後面；節名沿用「用錢前的準備與家庭交接」，不再改名 |
| 32 | **group-ref** | 查資料 | — | **新增**，插在 toolbox 前面（§6.6） |
| 33 | toolbox | 查資料 | — | 不動 |
| 34 | methods | 查資料 | — | 不動 |

**目前工作區的順序**（供對照）：ten, why, start, glossary, group-core, s1…s10, s11, cases, s12, s13, group-howto, steps, firstmonth, products, costs, withdraw, lifecycle, sidepaths, annual, toolbox, methods。

**實際搬動只有 4 次**：sidepaths 往前、firstmonth 和 steps 互換、withdraw 往後、annual 往前。其餘都是插入新節或原地改寫。

搬節做法：用程式以 `re.search(r'<section class="part" id="X">.*?</section>\n*', h, re.S)` 切出整塊，照上表重新串接（切之前先確認每塊裡沒有巢狀的 `</section>`，現況沒有）。搬完立刻跑第 10 節的 `order` 檢查。

---

## 2. 每一節的動作清單（沒列到的節＝完全不動）

- `ten`：在 `<div class="warning" data-lite="ch1">` 前面插 `<span id="ten-stop"></span>`。警告框本身不動；頁尾本節行動不動。
- `s2`：`<h3>前幾年像沒在長：先有心理準備</h3>` → `<h3 id="s2-slow">…</h3>`
- `s5`：`<h3>跌的時候、很久沒漲的時候，記得這幾句</h3>` → `id="s5-remember"`；圖說裡沒連結的「第 4 節」補連結（第 0 批，§10.3）
- `s6`：`<h3>等匯率，和等股價是同一個問題</h3>` → `id="s6-fx"`；`<h3>現在是歷史新高，會不會太高了？</h3>` → `id="s6-ath"`
- `s8`：`<h3>高股息 ETF：先看四件事</h3>` → `id="s8-dividend"`
- `s10`：`<ul class="checklist"><li><strong>冷卻期</strong>` 的那個 `<li>` → `<li id="s10-cooling">`（冷卻期那段是共同事實，只加屬性，文字一字不動）
- `s11`：`<h3>把答案寫成一張紙：我的投資計畫</h3>` → `id="plan-table"`；在 `<div class="data-card" data-lite-alt="ch4-drill">` 前面插 `<span id="drill"></span>`
- `cases`：`<h3>陳大哥：五年後退休</h3>` → `id="case-chen"`
- `s12`：`<h3>三條新手路徑：去哪裡買、各付什麼代價</h3>` → `id="s12-paths"`
- `s13`：`<h3>怕錯過（1 題）</h3>` → `id="s13-miss"`；`怕賠（14 題）` → `s13-loss`；`怕輸人（4 題）` → `s13-envy`；`無聊（1 題）` → `s13-bored`；`想控制（7 題）` → `s13-control`；`<h3>家人推銷時：守住自己的規則，不必說服對方</h3>` → `s13-family`。s13 的篩選腳本用 h3 的 textContent 找群組，加 id 不影響，改完手動點一次篩選按鈕確認。
- `sidepaths`：搬位置；改「（上一節）」（§9.1）
- `firstmonth`：搬位置。導言已經是「動作散在全書各節」，不用改
- `products`：第 2 題選 A 時加指路句（§9.3）
- `costs`：`<h3>四種出事，哪一種會讓錢真的不見</h3>` → `id="costs-four"`（這張卡有 `data-lite-alt="ch5-risk"`，是已退場的短稿，現在不驗指紋；交班文件記一筆「回復實作版時 ch5-risk 要重看」）
- `annual`、`lifecycle`、`withdraw`：只搬位置。withdraw 裡指向 lifecycle 第三題的引用本來就用節名，搬完變成往回指，不用改
- `group-core`、`group-howto`：改寫（§6）
- 新增 `group-plan`、`group-situations`、`group-life`、`group-ref`（§6）
- 封面：§7
- 目錄：§5

---

## 3. 跨節搬卡片

**主線：0 張。** 下面兩個選做批次，只在作者選了對應選項時才做。

### 3.1 選做批次 P（第 2 題選 B）：挑產品三張卡 s12 → products

搬的卡（依原順序，放在 products 白話版之後、`<h3>選 ETF 時逐項查看</h3>` 那張卡之前）：
1. `挑產品前三題`
2. `三條新手路徑：去哪裡買、各付什麼代價`（連同卡裡的摺疊「三條路徑的完整比較」）
3. `挑產品前先知道三件事`

**不搬**：`「買整個世界」長什麼樣`。why ×2、s4、s13 都用「第 13 節那張卡」指它。

**卡內要改**
- 三條新手路徑卡的小字「作者自己用哪幾檔，寫在本節最後的作者做法紀錄（黃框）」→「……寫在第 <a class="xref" href="#s12">13</a> 節最後的作者做法紀錄（黃框）」。黃框留在 s12，因為 s2 還指著「第 13 節那張七條清單」。這句前面的「本指南的做法」標籤不動，`labels` 哨兵要照樣綠。
- 卡內原本寫「下面『挑產品前先知道三件事』第 2 條」的地方：三張卡順序不變，方位仍成立，不用改。
- s12 的「直接來源」卡要拆：逐條找它被哪張卡引用。已知 IRS NRA withholding、元大 0050、富邦 006208 官方頁跟產品卡有關，搬到 products 的「文中商品的官方資料」；Vanguard 投資原則、全球 ETF 國家比重兩列、Vanguard 2021／2022 兩列留在 s12；iShares CBU0 要查它在哪張卡被用到。商品代號只准出現在允許的位置，`tickers` 哨兵要綠。

**全書要改指的連結**（都是人工判斷，不能用程式批次換）

| 在哪 | 現在 | 改成 |
|---|---|---|
| why「在台灣買全球型有三種摩擦」 | 第 13 節的三條路徑表 | 「挑商品…」節名連結到 `#s12-paths` 新位置（搬完 id 跟著卡走） |
| s11 C 區欄位「走哪條路、總費用率」 | 第 13 節的三條路徑表 | 同上 |
| **s11 lookup-tables 區塊**「先回第 13 節的三條路徑表看一次費用」 | `#s12` 13 | 改節名連結；**要作者同意**（工作表第 2 頁）；改完人工重看 `lite/alt/lookup-tables.html`，同步改短稿那一句，再 `--stamp lookup-tables` |
| cases「註冊地怎麼比看下一節（第 13 節）」 | 下一節＋`#s12` | 「註冊地怎麼比，看『挑商品…』的『挑產品前三題』」 |
| steps「先回第 13 節的三條路徑表看一次費用」 | `#s12` | 節名連結 |
| steps「第 13 節『挑產品前三題』那張卡有整理」 | `#s12` | 節名連結 |
| firstmonth「C 區的路徑和總費用率，等下面挑好路徑再補（第 11、13 節）」 | `#s12` | 「第 11 節、『挑商品…』」 |
| firstmonth「挑產品：先看『挑產品前三題』、選一條新手路徑（第 13 節），再用『ETF 與債券檢查表』逐項看」 | `#s12`＋舊節名 | 改成同一節內的順序說法 |
| sidepaths「約 57%，第 13 節」 | `#s12` | 節名連結（57% 在「三件事」那張卡） |
| annual「用複委託或海外券商買……第 13 節」 | `#s12` | 節名連結 |

**改名（要作者核准）**：s12 →「新手的起點：四個原則與七個問題」；products →「挑商品：三條新手路徑與 ETF、債券檢查表」。之後全書以節名當錨文字的連結、目錄、封面、組地圖都要改。products 約 13 處，用 `grep 'href="#products"'` 列全；ten 的 `details[data-lite-alt="ch1-six"]` 已退場，可以改。
**另外**：products 裡「註冊地」會連講四次，照 D9 的方式在第二、三次改成一句指路，或收進摺疊；不准刪內容。
**驗收**：`alt` 只有 lookup-tables 需要 stamp（而且是人工重看過後）；`facts`、`labels`、`tickers` 綠；兩節的數字用 `guidetools numbers` 檢查，只准搬家，不准遺失。

### 3.2 選做批次 N（第 1 題選 C）：第 14 節移到動手做後面，拿掉節號

- 組順序改成：…寫計畫 → 動手做 → 遇到狀況 → 隨人生調整 → 查資料。
- s13 的 h2 拿掉 `<span class="num">14</span>`。
- 全書 10 個 `href="#s13"` 的數字錨文字改成節名「三十一種常見情境」，並人工順句：封面、start 黃框（**要作者核准例外**）、group-core（已改寫，不再有）、s8「照第 14 節的問題處理」、s10「看第 14 節那一題」、s12 七問表「第 8、11、14 節」、firstmonth「先算第 14 節那三個數」、sidepaths「怎麼算要不要解在第 14 節」、annual 兩處（其中一處在 `#annual ol.checklist` 裡，改完要重看 `lite/alt/app-a-checklist.html` 並 `--stamp app-a-checklist`）。主線新加的 group-situations（清單的 `map-num` 14、狀況索引裡 8 個錨文字「14」、收尾句）也要一起改成節名；`part_maps` 哨兵的 map-num 規則會提醒。
- 更新 `stories` 的核對：start 黃框文字有變，一次性的黃框逐字比對（§11.2）要把這一格列成「核准的改動」。

---

## 4. 「第 N 節」自動重編（主線不用；留給以後）

主線不改任何顯示節號，**這一節只在以後重編號時照做**。

**做法**
1. 依正文順序，凡是 `<h2>` 裡有 `<span class="num">` 的節，重新給 1..N，同時改 h2 的 span 與目錄裡 `ol` 的 counter 起點（§5）。
2. 建 `num_of[id]`，再建 `anchor_sec[任意 id] = 所在節 id`。卡片錨點如 `lifecycle-q2`、`s5-remember` 都算進它所在的節。
3. 所有 `<a class="xref" href="#X">數字</a>`，數字改成 `num_of[anchor_sec[X]]`。
4. 找列舉：`第 <a…>A</a>、<a…>B</a> 節` 這種，重編後要照新數字由小到大重排（旅程方案實測有 18 組會亂序）。
5. 跑 §10.2 的 `xref_num` 哨兵確認。

**程式改不到、要人工處理的地方**
- 黃框裡的節號連結：`#start` 黃框 →`#s13`、`#s12` 黃框 →`#s11`。要作者核准才能改。
- 受保護區塊裡的節號連結：lookup-tables →`#s1`、`#s12`、`#s2`；ch4-drill →`#s10`；`#annual ol.checklist` →`#s2`、`#s11`、`#s13`、`#s9`、`#s10`（外加兩個節名連結 withdraw、costs）。改完要重看短稿再 stamp。
- 短稿檔頭 note 與短稿內文：`lite/alt/lookup-tables.html`（「第 13 節」）、`lite/alt/ch4-drill.html`（「第 10 節」）。
- `lite/manifest.json` 封面接話的國字「第十一節」（接話不准用阿拉伯數字，程式抓不到）。
- 沒有連結的「第 N 節」：s5 圖說「第 4 節」、methods「第 5 節的比例」、`tools/essay_charts.py` 第 742 行的預設圖說「第 4 節」。第 0 批會先把前兩處補上連結、第三處同步。
- `guidetools numbers` 會被節號變動灌滿，重編那一輪要另外寫一支「排除 xref 數字」的比對。

---

## 5. 目錄：新的 HTML、CSS、JS

### 5.1 HTML（整個取代現在的 `<nav class="toc" id="toc" …>…</nav>`）

```html
<nav class="toc" id="toc" aria-label="目錄"><h2>目錄</h2>
<p class="small toc-hint">點組名展開；想從頭讀，從「開始之前」往下。</p>
<details class="toc-part" data-print="open" open><summary><span class="toc-part-name">開始之前</span><span class="toc-part-desc">先抓重點，確認自己的錢能不能開始；看不懂的詞在這裡查。</span></summary>
<ul><li><a href="#ten">十分鐘看完：新手先記住這七件事</a></li><li><a href="#why">一眼看懂：為什麼指數化投資、好在哪、限制在哪</a></li><li><a href="#start">投資前的安全順序</a></li><li><a href="#glossary">先認識這些詞</a></li></ul></details>
<details class="toc-part" data-print="open" data-group="group-core"><summary><span class="toc-part-name">先搞懂：為什麼這樣做</span><span class="toc-part-range">第 1–10 節</span><span class="toc-part-desc">十個新手最常問的問題，一節回答一個；計畫表每一格的理由都在這裡。</span></summary>
<ol class="toc-from-1"><li><a href="#s1">投資賺的是誰的錢？</a></li><li><a href="#s2">現在開始會不會太晚？</a></li><li><a href="#s3">為什麼不請人幫我挑？</a></li><li><a href="#s4">為什麼不只買最會漲的？</a></li><li><a href="#s5">帳面跌了兩成，是出事了嗎？</a></li><li><a href="#s6">要不要等跌下來再買？</a></li><li><a href="#s7">買在幾號、多久買一次？</a></li><li><a href="#s8">漲了要不要先賣一些？</a></li><li><a href="#s9">買一樣的東西，結果為什麼不同？</a></li><li><a href="#s10">明明知道，為什麼還是想動手？</a></li></ol></details>
<details class="toc-part" data-print="open" data-group="group-plan"><summary><span class="toc-part-name">寫下自己的計畫</span><span class="toc-part-range">第 11–13 節</span><span class="toc-part-desc">把理由填成一張紙：這筆錢什麼時候用、股票放幾成、跌了怎麼做；再看另外三個人怎麼填。</span></summary>
<ol class="toc-from-11"><li><a href="#s11">把答案寫成一張紙：我的投資計畫</a></li><li><a href="#cases">另外三個人：同樣做指數化，股票比例為什麼差這麼多？</a></li><li><a href="#s12">把前面組起來：新手的起點怎麼定</a></li></ol></details>
<details class="toc-part" data-print="open" data-group="group-situations"><summary><span class="toc-part-name">遇到狀況時翻：怕跌、想賣、有人推銷</span><span class="toc-part-desc">心裡在怕、手癢想動、有人推薦東西的時候，先在這裡找該翻哪一頁。</span></summary>
<ol class="toc-from-14"><li><a href="#s13">三十一種常見情境：我在怕什麼？</a></li></ol><ul><li><a href="#sidepaths">常見的岔路：為什麼不是核心</a></li></ul></details>
<details class="toc-part" data-print="open" data-group="group-howto"><summary><span class="toc-part-name">動手做：開戶、挑商品、第一年</span><span class="toc-part-desc">計畫寫好以後照順序做；做到哪一步，翻哪一節。</span></summary>
<ul><li><a href="#firstmonth">從第一週到第一年：一頁時間表</a></li><li><a href="#steps">第一次投資的七個步驟</a></li><li><a href="#products">ETF 與債券檢查表</a></li><li><a href="#costs">費用、稅務與帳戶安全</a></li></ul></details>
<details class="toc-part" data-print="open" data-group="group-life"><summary><span class="toc-part-name">隨人生調整：每年檢查、年紀變了、快要用錢</span><span class="toc-part-desc">一年檢查一次；年紀、收入、用錢的日子改變時，回來重算。</span></summary>
<ul><li><a href="#annual">每年一次的檢查表</a></li><li><a href="#lifecycle">年齡、槓桿與退休：三個常被問的問題</a></li><li><a href="#withdraw">用錢前的準備與家庭交接</a></li></ul></details>
<details class="toc-part" data-print="open" data-group="group-ref"><summary><span class="toc-part-name">查資料</span><span class="toc-part-desc">官方網站、延伸閱讀，和全書數字怎麼算出來。</span></summary>
<ul><li><a href="#toolbox">去哪查：官方入口與延伸閱讀</a></li><li><a href="#methods">資料口徑與來源</a></li></ul></details>
</nav>
```

**要點**
- 每一個 `details.toc-part` 都要帶 `data-print`。`open_details(only_marked=True)` 只展開帶這個屬性的摺疊；少了它，PDF 目錄會印成收合的，`toc` 哨兵讀不到頁碼。
- 目錄連結維持 `<a href="#id">節名</a>`（不加 class、不加屬性）。`build_lite.py` 第 943 行和 `lite_sentinels.py` 第 430 行都用 `<a href="#([\w-]+)">` 精確比對。
- 節名前面不准加任何字：`toc_printed_numbers` 要求連結文字以節名的前 6 個字開頭。選做的〔要動筆〕記號要放在 `<a>` 裡、節名**後面**：`<a href="#s11">把答案寫成一張紙：我的投資計畫<span class="toc-tag">要動筆</span></a>`。建置時頁碼 span 會接在它後面，結尾仍是數字。
- 分組節（group-*）**不進目錄**（沿用核准的例外 4）。組名放在 `summary` 裡，不做成連結。
- 目錄連結順序必須等於正文順序：`tail_flows` 用目錄順序判斷近乎空白頁（§10.2 `order` 哨兵）。

### 5.2 CSS（加在 `<style>` 裡現有 `.toc` 規則後面）

現在的 `.toc ol{counter-reset:toc}` 讓每個 `ol` 從 01 開始，所以要給後面兩組設起點。

```css
.toc .toc-hint{margin:.2em 0 .6em}
.toc details.toc-part{border-top:1px solid var(--line);padding:.15em 0}
.toc details.toc-part>summary{list-style:none;cursor:pointer;display:flex;flex-wrap:wrap;align-items:baseline;gap:.1em .6em;padding:.55em 0}
.toc details.toc-part>summary::-webkit-details-marker{display:none}
.toc details.toc-part>summary::before{content:"▸";color:var(--muted);width:1em}
.toc details.toc-part[open]>summary::before{content:"▾"}
.toc .toc-part-name{font-weight:700}
.toc .toc-part-range{font-size:.8em;color:var(--muted)}
.toc .toc-part-desc{flex-basis:100%;font-size:.84em;color:var(--muted);padding-left:1.6em}
.toc ol.toc-from-11{counter-reset:toc 10}
.toc ol.toc-from-14{counter-reset:toc 13}
.toc .toc-tag{margin-left:.5em;font-size:.75em;color:var(--muted);border:1px solid var(--line);border-radius:6px;padding:0 .35em}
@media print{.toc details.toc-part>summary::before{content:none}.toc .toc-part-desc{padding-left:0}}
```

### 5.3 JS（寬螢幕自動展開；放在 `</nav>` 後面，選做但建議做）

```html
<script>
(function(){if(!window.matchMedia||!window.matchMedia('(min-width: 760px)').matches)return;
document.querySelectorAll('#toc details.toc-part, details.read-how').forEach(function(d){d.open=true;});})();
</script>
```

---

## 6. 分組節（組地圖）

### 6.0 共通結構

```html
<section class="part" id="group-XXX"><h2>組名</h2><p class="lede">一行說明（和目錄 summary 的說明逐字相同）</p>
<ol class="part-map">
<li><span class="map-num">11</span><a class="xref" href="#s11">節名（和 h2 去掉 span.num 後逐字相同）</a><span class="map-lede">那一節的 p.lede（逐字相同）</span></li>
…
</ol>
<p class="small">一兩句「什麼時候可以跳、什麼不能跳」</p>
<a class="back" href="#toc">回目錄</a></section>
```

- 沒節號的節，`li` 裡省略 `span.map-num`。
- 清單的節名與 lede 只准照抄。由 §10.2 的 `part_maps` 哨兵比對，不一致就紅。
- 不要白話版、不要本節行動（沿用核准的例外 4，交班文件要把範圍改成「所有 group-* 分組節」）。
- CSS：
```css
.part-map{list-style:none;margin:.6em 0;padding:0}
.part-map li{padding:.45em 0;border-top:1px solid var(--line)}
.part-map .map-num{display:inline-block;min-width:1.9em;color:var(--muted);font-variant-numeric:tabular-nums}
.part-map .map-lede{display:block;font-size:.88em;color:var(--muted);padding-left:1.9em}
```
- 內文出現「第 N 節」一律要連（`第 <a class="xref" href="#sN">N</a> 節`）。下面草稿都照這條寫。

### 6.1 group-core（原地改寫）

```html
<section class="part" id="group-core"><h2>先搞懂：為什麼這樣做</h2><p class="lede">十個新手最常問的問題，一節回答一個；計畫表每一格的理由都在這裡。</p>
<ol class="part-map">
<li><span class="map-num">1</span><a class="xref" href="#s1">投資賺的是誰的錢？</a><span class="map-lede">先找付款的人，再看可能拿到多少。</span></li>
<li><span class="map-num">2</span><a class="xref" href="#s2">現在開始會不會太晚？</a><span class="map-lede">金額可以慢慢加，已經過去的年份加不回來。</span></li>
<li><span class="map-num">3</span><a class="xref" href="#s3">為什麼不請人幫我挑？</a><span class="map-lede">未來報酬不知道，費用卻會照表收。</span></li>
<li><span class="map-num">4</span><a class="xref" href="#s4">為什麼不只買最會漲的？</a><span class="map-lede">分散不保證多賺，但一家公司或一個國家出事，不會拖垮全部。</span></li>
<li><span class="map-num">5</span><a class="xref" href="#s5">帳面跌了兩成，是出事了嗎？</a><span class="map-lede">先分清楚是價格在晃，還是資產真的壞掉。</span></li>
<li><span class="map-num">6</span><a class="xref" href="#s6">要不要等跌下來再買？</a><span class="map-lede">猜低點要猜對兩次，等待也有代價。</span></li>
<li><span class="map-num">7</span><a class="xref" href="#s7">買在幾號、多久買一次？</a><span class="map-lede">買在哪一天確實有差，但這個差通常小於費用、遲遲不進場和恐慌賣出帶來的影響。</span></li>
<li><span class="map-num">8</span><a class="xref" href="#s8">漲了要不要先賣一些？</a><span class="map-lede">賣出會降低市場曝險；之後若再買回，就多了一次時點判斷。</span></li>
<li><span class="map-num">9</span><a class="xref" href="#s9">買一樣的東西，結果為什麼不同？</a><span class="map-lede">差別常在中途的買賣，不只在最初買了什麼。</span></li>
<li><span class="map-num">10</span><a class="xref" href="#s10">明明知道，為什麼還是想動手？</a><span class="map-lede">想動手不代表不夠聰明；大腦本來就會走捷徑。</span></li>
</ol>
<p class="small">可以照順序讀，也可以挑最想問的先讀；要寫計畫的人，至少先讀第 <a class="xref" href="#s5">5</a> 節和第 <a class="xref" href="#s10">10</a> 節。每一節的順序都一樣：先白話版，再數字和來源，最後一句「本節行動」。</p>
<a class="back" href="#toc">回目錄</a></section>
```
（最後一句「每一節的順序都一樣……」沿用現在 group-core 的原句。）

注意：`span.map-num` 裡的數字不是 xref，重編號時要一起更新。§10.2 的 `part_maps` 哨兵要檢查 map-num 等於那一節 h2 的 `span.num`。

### 6.2 group-plan（新增，插在 s10 後、s11 前）

清單：s11、cases、s12 三行（lede 照抄，見推薦文件樣張 A）。收尾小字：
```html
<p class="small">填 E 區（風險）和 F 區（跌了做什麼）以前，先讀第 <a class="xref" href="#s5">5</a> 節（壓力測試用的跌幅）和第 <a class="xref" href="#s10">10</a> 節（改計畫前的冷卻期）。要印出來手寫，另有《可列印工作表》。</p>
```
（與推薦文件樣張 A 的收尾句逐字相同。）

### 6.3 group-situations（新增，插在 s12 後、s13 前）

```html
<section class="part" id="group-situations"><h2>遇到狀況時翻：怕跌、想賣、有人推銷</h2><p class="lede">心裡在怕、手癢想動、有人推薦東西的時候，先在這裡找該翻哪一頁。</p>
<p>動手之前先看一遍也好：先知道自己可能會怕什麼，遇到時比較不慌。</p>
<div class="table-wrap"><table class="compact text situations"><thead><tr><th>遇到的狀況</th><th>先翻這裡</th></tr></thead><tbody>
<tr><td>帳面跌了一兩成、新聞說要崩盤，很想賣</td><td>先打開自己<a class="xref" href="#plan-table">計畫表</a>的 F 區照做；再看第 <a class="xref" href="#s5-remember">5</a> 節「跌的時候、很久沒漲的時候，記得這幾句」、第 <a class="xref" href="#drill">11</a> 節「大跌演練」、第 <a class="xref" href="#s13-loss">14</a> 節「怕賠」</td></tr>
<tr><td>投了好幾年，好像都沒在長</td><td>第 <a class="xref" href="#s2-slow">2</a> 節「前幾年像沒在長」、第 <a class="xref" href="#s5-remember">5</a> 節同一張卡、第 <a class="xref" href="#s13-bored">14</a> 節「無聊」</td></tr>
<tr><td>漲很多，想先賣掉一些</td><td>第 <a class="xref" href="#s8">8</a> 節、第 <a class="xref" href="#s13-miss">14</a> 節「怕錯過」</td></tr>
<tr><td>手上有錢，想等跌下來，或覺得現在太高</td><td>第 <a class="xref" href="#s6">6</a> 節（含「<a class="xref" href="#s6-ath">現在是歷史新高，會不會太高了？</a>」）、第 <a class="xref" href="#s13-loss">14</a> 節「怕賠」</td></tr>
<tr><td>台幣升值，海外資產縮水</td><td>第 <a class="xref" href="#s6-fx">6</a> 節「等匯率，和等股價是同一個問題」、第 <a class="xref" href="#s13-loss">14</a> 節「怕賠」最後一題</td></tr>
<tr><td>想改計畫、想調高股票比例、想加碼攤平</td><td>第 <a class="xref" href="#s10-cooling">10</a> 節「冷卻期」、第 <a class="xref" href="#s13-control">14</a> 節「想控制」</td></tr>
<tr><td>朋友集中一檔賺很多，覺得自己輸了</td><td>第 <a class="xref" href="#s13-envy">14</a> 節「怕輸人」</td></tr>
<tr><td>有人推薦高股息、月配、儲蓄險、正 2、主題型，或家人一直推銷</td><td>「<a class="xref" href="#sidepaths">常見的岔路</a>」、第 <a class="xref" href="#s8-dividend">8</a> 節「高股息 ETF：先看四件事」、第 <a class="xref" href="#s13-family">14</a> 節「家人推銷時」</td></tr>
<tr><td>想借錢投資（信貸、質押、融資）</td><td>「<a class="xref" href="#lifecycle-q2">年齡、槓桿與退休</a>」第二題、「<a class="xref" href="#sidepaths">常見的岔路</a>」</td></tr>
<tr><td>LINE 老師、保證獲利、要你匯款或給驗證碼</td><td>「<a class="xref" href="#ten-stop">十分鐘看完</a>」的四個立即停止（已經匯了，打 165）、「<a class="xref" href="#costs-four">費用、稅務與帳戶安全</a>」的「四種出事」</td></tr>
</tbody></table></div>
<ol class="part-map">
<li><span class="map-num">14</span><a class="xref" href="#s13">三十一種常見情境：我在怕什麼？</a><span class="map-lede">先辨認困難，再回前面的章節找完整方法。</span></li>
<li><a class="xref" href="#sidepaths">常見的岔路：為什麼不是核心</a><span class="map-lede">每一條你都會遇到；這裡只回答一件事：為什麼它不是核心。</span></li>
</ol>
<p class="small">表上找不到，就往下翻第 <a class="xref" href="#s13">14</a> 節，31 題照六種感受分組。</p>
<a class="back" href="#toc">回目錄</a></section>
```

- 表格 class 沿用全書現有的 `compact text`（文字表格）。手機 400px 下，表格要在 `.table-wrap` 裡捲，頁面本身不能橫捲。
- 「已經匯了，打 165」出自 ten 警告框原文，不是新事實。
- **裁判逐列核對**：每一格指到的卡片，真的回答了那一列的狀況（§12 第 2 批）。

### 6.4 group-howto（原地改寫）

h2「動手做：開戶、挑商品、第一年」，lede 用一行說明。清單：firstmonth、steps、products、costs 四行，lede 照抄。收尾小字：
```html
<p class="small">還沒寫計畫表的人，先回第 <a class="xref" href="#s11">11</a> 節。不必從頭讀：做到哪一步，就翻哪一節。</p>
```
（「不必從頭讀：做到哪一步，就翻哪一節。」沿用現在 group-howto 的原句。）

### 6.5 group-life（新增，插在 costs 後、annual 前）

清單：annual、lifecycle、withdraw 三行，lede 照抄。lifecycle 那一行的 `map-lede` 後面另起一個 `span.small`，列出三個子連結：`<a class="xref" href="#lifecycle-q1">第一題</a>　年齡該不該影響比例／<a class="xref" href="#lifecycle-q2">第二題</a>　年輕時借錢投資／<a class="xref" href="#lifecycle-q3">第三題</a>　退休要存多少`。`part_maps` 哨兵只比對 `map-lede`，所以子連結要放在它**外面**。

收尾小字：
```html
<p class="small">離退休只剩幾年的人，可以對照第 <a class="xref" href="#case-chen">12</a> 節的陳大哥（五年後退休，附填好的全表）。</p>
```

### 6.6 group-ref（新增，插在 toolbox 前）

清單：toolbox、methods 兩行，lede 照抄。收尾小字：
```html
<p class="small">看不懂的詞，在最前面的「<a class="xref" href="#glossary">先認識這些詞</a>」；正文裡點詞也會跳過去。</p>
```

---

## 7. 封面

### 7.1 任務入口（插在最後一個 `<p class="subtitle">` 之後、`<div class="promise">` 之前）

```html
<nav class="tasks" aria-label="我現在想"><p class="tasks-title"><strong>我現在想……</strong></p>
<ul>
<li><a href="#ten">只有十分鐘，先抓重點</a></li>
<li><a href="#start">先確認能不能開始投資（預備金、卡債、保單）</a></li>
<li><a href="#group-plan">寫下自己的比例和規則</a></li>
<li><a href="#group-howto">開戶、挑商品、下第一單</a></li>
<li><a href="#group-situations">大跌很慌、想賣，或有人推銷</a></li>
<li><a href="#annual">年底了，做一年一次的檢查</a></li>
<li><a href="#group-life">自己或爸媽快退休、快要用錢</a></li>
</ul>
<p class="small">看不懂的詞，翻「<a class="xref" href="#glossary">先認識這些詞</a>」；想從頭讀，往下看<a href="#toc">目錄</a>。</p></nav>
```

```css
.tasks ul{list-style:none;margin:.4em 0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}
.tasks li a{display:block;height:100%;padding:.6em .8em;border:1px solid var(--line);border-radius:12px;background:var(--surface);text-decoration:none;line-height:1.4}
@media print{.tasks{display:none}}
```

**危險**：`toc_printed_numbers` 會把封面上連結文字「以某節節名前 6 個字開頭」的連結當成目錄項，要求結尾有頁碼，沒有就紅。入口文字一律不准以節名開頭：不能寫「投資前的安全順序」「十分鐘看完：…」「每年一次的檢查表」。上面七個已經逐一避開了。列印時整塊隱藏，這個風險只剩網頁版，但保險起見照樣避開。

### 7.2 閱讀方式框

1. 外殼 `<div class="promise">…</div>` 改成 `<details class="promise read-how" data-print="open"><summary><strong>怎麼讀這本書</strong>：綠框、黃框、標籤、四十分鐘讀法</summary>…原內容…</details>`。原內容開頭的 `<strong>閱讀方式：</strong>` 保留。
2. 兩句替換（其他一字不動）：

**舊 1**
```
只有十分鐘的人，先讀「<a class="xref" href="#ten">十分鐘看完</a>」；多一點時間，再讀「開始前」的其他三節（一眼看懂、投資前的安全順序、先認識這些詞）加第 <a class="xref" href="#s11">11</a>、<a class="xref" href="#s12">13</a> 節，大約四十分鐘。
```
**新 1**
```
只有十分鐘的人，先讀「<a class="xref" href="#ten">十分鐘看完</a>」和「<a class="xref" href="#start">投資前的安全順序</a>」；多一點時間，再讀「<a class="xref" href="#why">一眼看懂</a>」、第 <a class="xref" href="#plan-table">11</a> 節的計畫表（白話版、兩把尺、壓力測試、三問）、第 <a class="xref" href="#s12">13</a> 節的四個原則和七個問題，最後看「<a class="xref" href="#firstmonth">從第一週到第一年</a>」，大約四十分鐘，讀完就知道這個星期做什麼。
```
（`#plan-table` 在 s11 裡，錨文字 11 對得上 `xref_num`。若嫌卡片錨點太細，改回 `#s11` 也可以。）

**舊 2**
```
心裡正在怕某一件事的時候，直接翻第 <a class="xref" href="#s13">14</a> 節；要開戶、下單、對帳、每年檢查的時候，翻後面的實作附錄（從第一週到第一年的時間表也在那裡）。
```
**新 2**
```
心裡正在怕某一件事的時候，翻「<a class="xref" href="#group-situations">遇到狀況時翻</a>」；要開戶、下單、對帳的時候，翻「<a class="xref" href="#group-howto">動手做</a>」；每年檢查、年紀變了、快要用錢的時候，翻「<a class="xref" href="#group-life">隨人生調整</a>」。
```

3. 閱讀方式框前面那句定位（「這一份是主體……《可列印工作表》」）、eyebrow 版本字串、chips 都不動（`version` 哨兵看 eyebrow）。

---

## 8. 錨點清單（18 個）

| id | 所在節 | 放在哪 | 誰會連 |
|---|---|---|---|
| ten-stop | ten | `<span>`，插在 `<div class="warning" data-lite="ch1">` 前 | 狀況索引 |
| s2-slow | s2 | h3「前幾年像沒在長：先有心理準備」 | 狀況索引 |
| s5-remember | s5 | h3「跌的時候、很久沒漲的時候，記得這幾句」 | 狀況索引 ×2 |
| s6-ath | s6 | h3「現在是歷史新高，會不會太高了？」 | 狀況索引 |
| s6-fx | s6 | h3「等匯率，和等股價是同一個問題」 | 狀況索引 |
| s8-dividend | s8 | h3「高股息 ETF：先看四件事」 | 狀況索引 |
| s10-cooling | s10 | `<li>`（冷卻期） | 狀況索引 |
| plan-table | s11 | h3「把答案寫成一張紙：我的投資計畫」 | 狀況索引、封面 |
| drill | s11 | `<span>`，插在 `<div class="data-card" data-lite-alt="ch4-drill">` 前 | 狀況索引 |
| case-chen | cases | h3「陳大哥：五年後退休」 | group-life |
| s12-paths | s12 | h3「三條新手路徑：去哪裡買、各付什麼代價」 | products 指路句 |
| s13-miss／s13-loss／s13-envy／s13-bored／s13-control／s13-family | s13 | 各 h3 | 狀況索引 |
| costs-four | costs | h3「四種出事，哪一種會讓錢真的不見」 | 狀況索引 |

現有可沿用：`lifecycle-q1`、`lifecycle-q2`、`lifecycle-q3`、`pension`、`control-map`。

`guidetools check` 會抓重複 id 與斷掉的連結，不用另寫錨點哨兵。錨點「還在、但卡片內容換了」是哨兵擋不住的：交班文件記下這 18 個錨點與用途，以後搬卡、改卡名時要一起看。

---

## 9. 方位詞與固定文字（人工）

### 9.1 sidepaths（必改）
舊：`<li><strong>正 2、反 1：</strong>官方寫「不宜長期持有」；它是單日工具（上一節）。</li>`
新：`<li><strong>正 2、反 1：</strong>官方寫「不宜長期持有」；它是單日工具（「<a class="xref" href="#lifecycle-q2">年齡、槓桿與退休</a>」第二題）。</li>`
（「正 2 ETF：官方寫它不宜長期持有……」在 lifecycle 第二題底下的「台灣三種常見的借法」卡片裡，錨點用第二題的 h3。）

### 9.2 已掃過、搬完仍然成立、**不要改**的方位詞
- cases「註冊地怎麼比看下一節（第 13 節）」：cases 後面仍是 s12。
- s12 導言「配上前面已經寫好的那張」、s12 白話版「前面十一節是零件」、s12 h3「四個原則，各對應前面的節」：s11 仍在前面。
- s13 導言「再回前面的章節找完整方法」：第 1–13 節仍在前面。
- s1「前面『先認識這些詞』有解釋」、glossary「前後各節都會用到」與白話版：glossary 位置不動。
- firstmonth 導言「動作散在全書各節」：另一條工作流已改好。
- withdraw「傷得比後面幾年才跌多」、lifecycle「B 是後面幾年才跌」：講時間，不是版面位置。
- 其餘約 90 處「上面／下面」都是節內指卡片或表格，不受搬節影響（`judge-cost/directional.txt` 有全表）。

### 9.3 products 指路句（第 2 題選 A 才加）
放在 products 白話版 `</p>` 之後、`<div class="data-card">`（選 ETF 時逐項查看）之前：
```html
<p>還沒決定去哪裡買，先看第 <a class="xref" href="#s12-paths">13</a> 節「三條新手路徑：去哪裡買、各付什麼代價」。</p>
```

### 9.4 group-core、group-howto、封面
照 §6.1、§6.4、§7 整段替換。

---

## 10. 工具修改

### 10.1 列印：分組節不另起新頁（`tools/build_lite.py` 第 561 行）
舊：`'@media print{section.part#group-core,section.part#group-howto{break-before:auto!important;page-break-before:auto!important}}\n'`
新：`'@media print{section.part[id^="group-"]{break-before:auto!important;page-break-before:auto!important}}\n'`
另外在同一個 FULL_PRINT_CSS 補一條：分組節印成色帶（淺底、上下細線），`break-inside:avoid`，但 `part-map` 很長時允許斷頁（group-core 有 10 行，不能強制不斷）。註解一併改成「所有 group-* 分組節」。

### 10.2 新哨兵（加在 `tools/lite_sentinels.py`，完整版專用，工作表模式也要跑）

1. **`order`**：`nav.toc` 裡 `<a href="#id">` 的順序 ＝ 正文 `section.part` 的順序（排除 `group-*`），而且每節剛好出現一次。每個 `details.toc-part[data-group=X]`，X 必須是正文中緊接在該組第一節前面的那個 section。
2. **`xref_num`**：所有 `<a class="xref" href="#X">純數字</a>`，數字 ＝ `X` 所在節（卡片錨點算所屬節）h2 的 `span.num`；X 所在節沒有節號就紅。
3. **`part_maps`**：每個 `group-*` 節的 `ol.part-map`：
   - `li` 的 href 順序 ＝ 目錄同組的 href 順序；
   - 連結文字 ＝ 目標節 h2 去掉 `span.num` 的文字；
   - `span.map-lede` ＝ 目標節 `p.lede` 的文字；
   - `span.map-num` ＝ 目標節的 `span.num`，沒有節號的就不准出現。
   - 分組節的 `p.lede` ＝ 目錄同組 `span.toc-part-desc`。

三支都照現有哨兵的 `R.ok／R.fail` 寫，**第 0 批先在原文不動的情況下讓 1、2 綠**。3 在第 1 批加入分組節以後才啟用；第 0 批沒有 `part-map` 時印 SKIP＋理由。

### 10.3 兩處沒連結的節號（第 0 批順手修）
- s5 圖說「第 4 節那張表裡，也有等 25 到 34 年的例子」→ `第 <a class="xref" href="#s4">4</a> 節`。**`tools/essay_charts.py` 第 742 行的預設圖說同步改**（交班文件：圖說兩邊一起改）。改完不用重畫圖，但要確認 `essay_charts.py --guide` 下次跑時不會蓋回舊字。
- methods「『任選一天』那一欄就是第 5 節的比例」→ `第 <a class="xref" href="#s5">5</a> 節`。

### 10.4 不做
- 不寫主題索引哨兵（沒有主題索引）。
- 不在原文寫每節的麵包屑／下一步按鈕。以後要做，改在 `build_lite.py` 產出時依目錄分組自動注入，不寫進 `guide/index.html`。

---

## 11. 列印與各哨兵要注意的地方

### 11.1 逐支

| 哨兵／檢查 | 這次會怎樣 | 怎麼處理 |
|---|---|---|
| `toc` | 目錄結構換了，頁碼會全部重算 | 必須綠。紅的話先查：某個 `details.toc-part` 少了 `data-print`；某條連結文字前面多了字；封面入口文字以節名開頭（§7.1） |
| `alt`（指紋） | **應該零變化** | 只要紅，就是碰到了受保護區塊。還原那一筆，不准 `--stamp`。選做批次 P、N 例外，照 §3 人工重看後才 stamp |
| `worksheet`／`pages` | 工作表 4 頁不受影響 | 照樣綠；頁數不准變 |
| `facts` | 只加屬性、只搬節，文字不變 | 照樣綠 |
| `stories` | 它拿原文比自己產生的輸出，**抓不到黃框被改** | 另跑 §11.2 的一次性比對 |
| `labels`／`tickers` | 新文字裡沒有「本指南的做法」、沒有商品代號 | 照樣綠。新文字若出現代號（例如「0050」）會紅，改寫 |
| `blank_pages` | 分組節接在上一節後面印，頁數可能 ±0–4 | 記下前後的 WARN 數與總頁數，寫進回報。新增近乎空白頁超過 2 頁，就調色帶的斷頁規則，不改哨兵門檻 |
| `s13_filter` | s13 加 id | 照樣綠；另外手動點篩選按鈕確認 |
| `check`（guidetools） | 新 id、新連結 | 必須 `CHECK OK`：沒有重複 id、沒有斷連結、`<a>` 沒有巢狀 |
| `stale`／`fragments` | 原文改了 | 重跑 `build_lite.py` 就好 |
| `version` | 沒動 eyebrow | 照樣綠 |
| 新增的 `order`／`xref_num`／`part_maps` | — | 必須綠 |

### 11.2 一次性比對（每批都跑，結果貼進回報）

```python
# 用法：python3 compare_protected.py <舊版 html> guide/index.html
import re, sys
from collections import Counter
def blocks(h, tag, cls):
    out = []
    for m in re.finditer(r'<%s\b[^>]*class="%s"[^>]*>' % (tag, cls), h):
        d = 0
        for t in re.finditer(r'<%s\b[^>]*>|</%s>' % (tag, tag), h[m.start():]):
            d += -1 if t.group(0).startswith('</') else 1
            if d == 0:
                out.append(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h[m.start():m.start()+t.end()])).strip()); break
    return out
old, new = (open(p, encoding='utf-8').read() for p in sys.argv[1:3])
for tag, cls in [('div', 'story'), ('mark', 'key'), ('div', 'warning')]:
    a, b = Counter(blocks(old, tag, cls)), Counter(blocks(new, tag, cls))
    print(tag, cls, 'OK' if a == b else ('LOST %s / ADDED %s' % (a - b, b - a)))
```
舊版用 `git show HEAD:guide/index.html > /tmp/old.html` 取得。
另外跑：
- `guidetools numbers old new`：只准在新分組節、封面、目錄出現 ADDED，任何一節都不准有 LOST。
- `guidetools diff old new out.txt`：給作者看的差異。
- 名詞連結數維持 106（新文字裡不准加名詞連結）。`mark.key` 數、`details` 數（封面多 1、目錄多 7）、`data-chart` 數，前後對照。

### 11.3 PDF 要人眼看的地方
- 目錄頁：七組的組名和說明是否清楚、兩欄排版有沒有被 `summary` 打亂、頁碼有沒有對齊。
- 四個新分組節和兩個改寫的分組節：色帶有沒有接在上一節後面、`part-map` 有沒有被硬切成孤行。
- 封面：`.tasks` 沒印出來；閱讀方式框整段印出，沒有「（紙本未印）」字樣。
- PDF 書籤會多出 4 個分組節的 h2，可以接受。

### 11.4 手機（400px）要實際看
用 `mcp__Claude_Browser__*` 開 `output/full-v60-out.html`（或發布前的 `output/guide.html`），`resize_window` 設 400×860：
- 封面入口兩欄不溢出；閱讀方式框預設收合。
- 目錄預設只開「開始之前」，其他六組收合；點開正常；寬螢幕（≥760px）全部打開。
- 狀況索引表在 `.table-wrap` 裡捲，頁面本身不橫捲。
- 從封面「大跌很慌」→ 狀況索引 → 點 `s5-remember`，會跳到卡片標題而不是節的開頭。
- 看完把 viewport 設回 `desktop`。

---

## 12. 分批與驗收

每一批：動手前 commit → 改 → `python3 tools/build_lite.py`（exit 0＋`SENTINELS OK`）→ `python3 tools/guidetools.py check guide/index.html` → `python3 tools/test_guidetools.py tools guide/index.html` → §11.2 比對 → 裁判 → 給作者 diff → commit。

### 第 0 批：保險（工具，半輪內；原文只補 §10.3 兩個連結）
- §10.1 列印規則通用化；§10.2 的 `order`、`xref_num`（`part_maps` 先 SKIP）；§10.3。
- **驗收**：建置全綠；故意把一個 xref 數字改錯、把目錄兩條對調，確認新哨兵會紅，再還原。

### 第 1 批：換骨架（一輪）
- §1 搬節（4 次搬動）；新增四個分組節、改寫兩個（§6）；§5 目錄（HTML＋CSS＋JS）；§9.1 sidepaths；§7.2 閱讀方式框的兩句與 details 外殼。
- 這一批先不加狀況索引表格（group-situations 先只放 lede、「動手之前先看一遍也好」那句與清單；「表上找不到……」那句等第 2 批有表格再加），也先不加錨點；新 1 那句的 `#plan-table` 暫時用 `#s11`；group-life 的陳大哥句等第 2 批有 `case-chen` 再加。
- `part_maps` 哨兵啟用。
- **驗收**：
  - 建置全綠，`alt` 零 stamp。
  - §11.2 的黃框、重點句、警告框三項 OK；`numbers` 沒有 LOST。
  - `order`、`xref_num`、`part_maps` 綠。
  - PDF 頁數、`blank_pages` WARN 數前後對照。
  - 裁判（judge／fable xhigh）：從頭讀一遍新順序，確認沒有新的「先用後解釋」與方位錯誤，組地圖清單和原文逐字相同。

### 第 2 批：找東西的工具（一輪）
- §8 錨點；§6.3 狀況索引表；§7.1 封面入口；新 1 改回 `#plan-table`；§6.5 陳大哥句；§9.3 products 指路句（第 2 題選 A）；選做的〔要動筆〕記號（作者點頭才加）。
- **驗收**：
  - 建置全綠，`alt` 零 stamp，`check` OK。
  - 裁判（fable xhigh）逐列核對狀況索引：每個連結跳到的卡片確實回答那一列；沒有新事實、新數字；「大跌」那一列沒有指到詐騙警告。
  - 新手走查（sonnet，國中程度、400px）：五個任務（要不要開始、填計畫表、大跌怎麼辦、年底檢查、爸媽快退休），每個任務記錄點了幾下、有沒有迷路。
  - §11.4 手機檢查截圖附在回報裡。

### 第 3 批：收尾（半輪）
- §11.3 PDF 人眼檢查；修色帶與斷頁。
- 更新 `docs/handoff-guide-2026-09-16.md`（或寫新的交班文件）：
  - 核准的例外 4 改成「所有 `group-*` 分組節沒有節號、沒有白話版、不在目錄裡，組名在目錄 `summary`」；
  - 目錄結構與 `data-print` 規則；
  - 新哨兵三支；18 個錨點與用途；
  - 「封面入口文字不准以節名開頭」；
  - `ch5-risk` 那張卡加了 id。
- 發布：`output/guide.html` 用完整版 `url` 更新（交班文件列的網址），不要開新的。工作表沒有變，不用重發。

### 選做批次
- **P**（第 2 題選 B）：§3.1，約一輪，排在第 3 批之後。
- **N**（第 1 題選 C）：§3.2，約半輪。需要作者先核准 start 黃框的例外。

---

## 13. 和另一條工作流：保留或推翻

| 另一條工作流做的事 | 本計畫 | 說明 |
|---|---|---|
| firstmonth 從「開始前」移出 | **保留** | — |
| firstmonth 排在 steps **後面** | **推翻**（改排 steps 前面） | 它是時間表，第一週的開戶就是七個步驟第 4 步；三位裁判中兩位指出順序反了 |
| 目錄小標不帶數量 | **保留** | 新組名一樣不帶數量；「第 1–10 節」是範圍標示，不是分組名 |
| 三組各加一行說明 | **保留做法，換文字** | 說明搬進 `summary` 的 `toc-part-desc` |
| 「先看懂，再決定」一組 14 節 | **推翻** | 拆成「先搞懂」「寫下自己的計畫」「遇到狀況時翻」三組 |
| 「實作附錄」一組，內分四小群（開始做／人生階段／維護／查證） | **推翻** | 改成三個平行的組（動手做／隨人生調整／查資料），岔路移到「遇到狀況時翻」 |
| 「人生階段」排在「維護」前，withdraw 在 lifecycle 前 | **推翻** | 改成 annual → lifecycle → withdraw（四份方案一致） |
| withdraw 改名「用錢前的準備與家庭交接」 | **保留** | 不再改名，免得年檢勾選表再重看一次 |
| group-core／group-howto 的新 h2 與內文 | **推翻** | 改寫成組地圖 |
| D10：列印只展開帶 `data-print` 的摺疊 | **保留** | 目錄與閱讀方式框的 details 都要帶 `data-print` |
| group-core／group-howto 列印不另起新頁 | **保留並擴大** | 改成 `section.part[id^="group-"]` |
| 封面定位句「這一份是主體……《可列印工作表》」 | **保留** | — |
| 封面「翻後面的實作附錄（從第一週到第一年的時間表也在那裡）」 | **推翻** | 見 §7.2 新 2 |
| 第一批 D1–D11、L 系列等內容改動 | **全部保留** | 本計畫不碰內容 |

---

## 14. 回退

每一批一個 commit。任何一批驗收不過、又不能在同一批修好，就 `git revert` 那一個 commit，回到上一批的綠色狀態。第 1 批和第 2 批互相獨立：第 2 批只加錨點與表格，退掉它不影響骨架。
