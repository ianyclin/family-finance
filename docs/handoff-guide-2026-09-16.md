# 交班：《隔離人性：理財新手完整指南》（2026-09-16，v6.1）

這一份取代 `docs/handoff-guide-2026-09-13.md` 成為**接手第一份要讀的文件**。舊那份留著當版本歷史（v4.x–v6.0 每一輪改了什麼、2026-09-15 的查證結果、作者當時的拍板），這一份只寫「現在是什麼樣子、怎麼動手、還欠什麼」。

---

## 接手先讀這段（三分鐘）

1. **這個專案在做什麼**：幫投資新手的一本書。作者是「指數三寶飯」。作者原話：「其實我的粉專不是重點，重點是我要用這份資料幫助投資新手」「內容的正確性、教育性、啟發性、閱讀性很重要，不能很難啃」。
2. **只有一個原文檔**：`guide/index.html`（約 0.9 MB）。其他能讀到的 HTML／PDF **全部是程式產生的**，不要手改。
3. **改完一定跑**：`python3 tools/build_lite.py`。它會產生兩份 HTML、兩份 PDF、兩份發布片段，最後跑約 24 類哨兵。**exit 0＋`SENTINELS OK` 才算做完。**
4. **哨兵紅了不要繞過**，照 `docs/core-edition/specs/lite-format.md` 第 9 節那一欄處理；也不要為了變綠而放寬哨兵語意。
5. **這個資料夾是獨立的本機 git repo**（無遠端）。根目錄 `life-journal` 是公開 GitHub 倉庫，已 gitignore 本資料夾；**永遠不要把 family-finance 加進 life-journal**。動手前先 commit，改完先給作者看 diff 再提交。
6. **作者的鐵律**：教學段不推薦商品（商品代號只准出現在作者黃框 `div.story`）；黃框「」裡的引句一個字都不能改；文件不替讀者下結論；每個數字要有來源。
7. **派子代理照 `CLAUDE.md` 的分流**：跑腳本 runner、找位置 scout、套已核准的改動 applier、建造 builder、驗收 judge（fable xhigh）。主線不要自己寫長篇。

---

## 現況（2026-09-16）

- **版本**：完整版 v6.1。`guide/index.html` 是唯一原文。
- **發布網址（更新時一定要帶 `url`，否則會開一個新的）**
  - 完整指南：https://claude.ai/code/artifact/19dbae25-66c1-404d-8219-8f9e19d586a4 （短網址同一份：https://claude.ai/artifact/4CCVbRjiv3jaP4GNGZx6vw ，2026-09-16 發到第 48 版）
  - 可列印工作表（原新手實作版，同一個網址覆蓋過去）：https://claude.ai/artifact/492iv4AuQeSHVPRN2XEC1E （第 2 版）
- **發布用片段**：`output/guide.html`、`output/lite.html`（`build_lite.py` 自動產生並由 `fragments` 哨兵把關，不要手做）。
- **匯出**：`export/` 只留最新版的四個檔（完整版 HTML＋PDF、工作表 HTML＋PDF）。
- **備份**：改大檔前先 `cp guide/index.html guide/index.vX.backup.html`（`*.backup.html` 已 gitignore）。
- **第三方原始資料檔不進 repo**（`research/pdf/`、`research/orig/`、`research/data/damodaran_histret.xls`）。要重算 `asset_rotation` 的人照 `research/data/README.md` 自己下載，並 `pip install xlrd`。

## 這一版（v6.1）和 v6.0 的差別

作者 2026-09-16 的方向：「我認為新手實作版反而複雜，我偏好以完整指南為主」「重要概念可以套用圖表，才不會文字比例太高閱讀疲累」。四批改動：

1. **第一批**：MSCI 數字全部改成粗略說法（條款不准散布）；「另外三個人」編成第 12 節（節號重編，見下面的陷阱）；封面改成以完整指南為主；十二條機械修正。
2. **第二批**：放進五張早就寫好但沒用到的圖（SPIVA、平滑對鋸齒、五個人、錯過最好的幾天、三桶）。
3. **第三批**：照審查修那五張圖的圖說；**把六張嵌入的第三方原圖全部拿掉**（改成一行出處＋外連），檔案 1.72 MB → 0.89 MB。
4. **第四批**：新增控制地圖（做得到／部分／做不到三層）與圖、第 6 節「等匯率，和等股價是同一個問題」、台股跌兩成以上七次的回本圖、四類資產逐年輪換圖（2004–2025）。複審後又修了一輪：輪換圖圖說改成事實（四類都當過第一名，也有連四年同一名）、控制地圖圖說改成不依賴版面方位（手機版是上中下）、控制不了那一層補「要不要曝險是你選的」但書、回本圖補第 4 節 25–34 年的邊界、第 5 節補「猜不到的是匯率會怎麼走，不是換匯本身」。

5. **拍板 L8＝A：《新手實作版》縮成《可列印工作表》**（見下一節）。

`data-chart` 現在 15 張。完整版 A4 152 頁、工作表 4 頁；近乎空白頁與頁數以 `build_lite.py` 每次的輸出為準，不要抄舊數字。

## 可列印工作表（原《新手實作版》）

作者：「新手實作版反而複雜。」它不再是第二本書，只留下無可取代的東西：印出來可以手寫的表。

| 頁 | 內容 | 來源 |
|---|---|---|
| 1（奇數） | 窄橫幅（書名、v6.1／2026-09-16、一句指路）＋我的投資計畫 A–H 區空白版 | `alt:plan-blank` |
| 2 | 查表頁（表一、表二、表三） | `alt:lookup-tables` |
| 3 | 每年一次的檢查表 | `alt:app-a-checklist` |
| 4 | 四個立即停止＋大跌演練卡 | `src:#ten div.warning`＋`alt:ch4-drill` |

第 1、2 頁雙面印剛好是同一張紙的正反面（`pages` 哨兵在把關）。

- 十二章與附錄 B 退場。**36 份短稿沒有刪**，搬到 `lite/alt/retired/`；完整版裡的 `data-lite` 標記也留著。要回復實作版：把 manifest 的章搬回來、短稿搬回 `lite/alt/`，**每一份都要先逐份對完整版原文重看再 `--stamp`**（退場期間它們不再被指紋檢查）。規則寫在 `lite-format.md` 第 11 節。
- `lite/facts.txt` 新增 `full-only:` 前綴：16 條兩份逐字比對，11 條隨十二章退場、只查完整版。`lite/case-checks.json` 只留查表頁那一條，其餘在 `lite/case-checks.retired-v60.json`。
- **工作表模式**（`worksheet_mode()`：manifest 沒有任何 `label`、也沒有 `toc`）：`toc`／`appendix_b`／`chapter_refs`／`unused_marks`／`fiction` 五支印 SKIP＋理由，十二章一回來自動復活；新增 `worksheet` 哨兵接手把關（四塊各一頁、PDF 剛好 4 頁、每塊要有 `src`／`alt` 來源、全文不得出現「第 N 章」與「附錄 X」）。
- 已知：第 4 頁下半頁是空白（塞得下第三張卡，規格只列兩張）；`lite/manifest.partA.json`／`partB.json` 現在跑不起來（引用的短稿已退場），它們只是第二階段的測試檔。
- 踩過的雷：`build_lite.py --manifest <沒寫 fragment paths 的 manifest>` 會覆蓋正式的 `output/guide.html`、`output/lite.html`。用實驗用 manifest 前先確認 `paths`，用完重跑一次正式 build。

---

## 作者的原則（不能違反）

- **目的是幫助投資新手，粉專不是重點。** 判斷取捨時先問「新手讀得懂、照做不會出錯嗎」。
- 四個標準一起看：**正確性、教育性、啟發性、閱讀性**。為了「完全正確」一直補細節而變難讀，也算失敗。
- 真實性優先；每個數字要有來源；不推薦商品、不做個人化建議；**文件不替讀者下結論**（圖說尤其容易犯，例如「跌了都會回來」）。
- 教學內容不能混入作者做法。作者做法只在黃框 `div.story`（標題「作者的做法紀錄（個人過程，不是教學內容）」），黃框裡「」內的引句一字不改。
- 作者持股比例：台股一成、全球七成、因子兩成。再平衡：年底 5/25 門檻，平時投入偏離到門檻兩倍才賣；賣出只有三種情況（提領期、用錢、再平衡）。第 11、13 節與年檢三處要一起改。
- ELI5：國中生讀得懂，但不讓大人覺得被當小孩；先畫面、再道理、最後數字；一句一件事；比喻不能說錯；推導與但書放小字。寫法在 `docs/core-edition/specs/eli5-rules.md`。

## 文件裡的標記系統（改文字時要維持）

| 東西 | 寫法 | 規則 |
|---|---|---|
| 節號連結 | `第 <a class="xref" href="#s4">4</a> 節` | 內文出現「第 N 節」一律要連。節名引用用 `「<a class="xref" href="#start">投資前的安全順序</a>」`。 |
| 名詞連結 | `<a class="term" href="#g-xxx" title="一句解釋">詞</a>` | 每節只標第一次；不標在標題、白話版、黃框、strong、其他連結裡。新名詞先加詞彙表 `<dt id="g-…">` 再標。目前 106 處。 |
| 重點句 | `<mark class="key">句子</mark>` | 目前 14 句（清單見下）。一節最多一句，單獨看得懂，是行動或結論。 |
| 先跳過 | `<span class="later">先跳過也可以…</span>` | 12 處。 |
| 白話版 | `<p class="explain"><span class="plain-title">白話版</span><br>比喻</p>` | 每節都有；要是比喻，不可以直接講答案；裡面不放名詞連結。 |
| 卡片 | `data-card`／`source-card`／`story`／`warning`／`p.decision` | 每節順序：h2 → lede → 白話版 → 內容 → 來源 → 黃框 → 行動。 |
| 圖 | `<figure class="chart" data-chart="圖id">` | 圖由 `tools/essay_charts.py --guide` 產生，見下面的警告。 |

### 節 id ≠ 顯示的節號（v6.1 起的陷阱）

「另外三個人」（id `cases`）移到第 11 節後面、編成**第 12 節**，所以 **id `s12` 顯示成第 13 節、id `s13` 顯示成第 14 節**。id 一律不動（manifest、短稿、既有連結都靠 id）。改內文時看到 `href="#s12"`，錨文字要寫 13；`href="#s13"` 要寫 14。另有兩個沒有節號的分組標題 `group-core`、`group-howto`。

### 核准的例外（不是錯誤，不要「順手修好」）

1. `lifecycle` 的三個黃框嵌在三個問題中間（刻意的），其餘各節一律「來源 → 黃框 → 行動」。
2. `methods`（資料口徑與來源）沒有「本節行動」——它是查證附錄。
3. 工作表的接話、動作框不回填完整版（那是為了分頁存在的過場）。
4. `group-core`、`group-howto` 沒有節號、沒有白話版、不在目錄裡。
5. `figure.chart details.orig` 那幾條 CSS 現在沒有東西套用（原圖已全部移除），沒有刪。

### 目前 14 句重點（mark.key）

why 它是一套寫得下來的步驟，不是一種本事。／s1 上面的歷史數字是過去，不是預測。／s3 簡單不是妥協…／s4 核心放全球市值型，台股大盤可以是裡面的一塊。／s5 波動會在兩種情況變成真的傷害…／s6 有錢可投、計畫也允許的時候，就照規則投進去。／s7 挑一個固定的日子就好。／s9 熱門時加碼、下跌時退出…／s11 最不用臨場判斷的答案是三種跌幅都寫「照常投入…」／s13 照卡做，不用說服對方。／steps 買進前先讓交割帳戶有足夠資金…／withdraw 市值型配置加一張規則卡，是最容易交接的組合／lifecycle 借的錢有固定利息，投資報酬沒有。／annual 自己的年化和指數差很多時，先找原因，不先換商品。

---

## 改完後的固定流程

```bash
cd "/Users/linyenchu/Cladue Code/family-finance"
git add -A && git commit -m "…"                      # 0. 動手前先把現狀存起來
cp guide/index.html guide/index.vX.backup.html       # 1. 大檔先備份
# 2. 只改 guide/index.html（用 Edit 或 tools/guidetools.py apply，不要整檔 Write）
python3 tools/essay_charts.py --guide                # 3. 只有動到圖才要跑
python3 tools/build_lite.py                          # 4. 產出兩份 HTML＋兩份 PDF＋跑哨兵（exit 0 才算過）
python3 tools/guidetools.py check guide/index.html   # 5. 原文結構檢查
python3 tools/test_guidetools.py tools guide/index.html
```

然後用 Artifact 工具發布 `output/guide.html`（帶完整版 `url`）與 `output/lite.html`（帶工作表 `url`）。

### 手改的檔只有這幾種

`guide/index.html`（原文與 `data-lite*` 標記）、`lite/manifest.json`、`lite/alt/*.html`（短稿）、`lite/facts.txt`／`lite/case-checks.json`／`lite/tickers.json`／`lite/labels.json`（檢查用清單）、`tools/*.py`。`lite/index.html`、`output/*`、`export/*` 都是產生的。

### 工具

- `tools/guidetools.py`：`apply`（補丁 JSON，每筆 old 必須唯一）、`check`、`text`、`diff`、`numbers`。測試 `tools/test_guidetools.py`（15 個）。
- `tools/calc_core.py` → `lite/calc-results.json`：書裡所有數字的唯一算處（含 `sweet_satisfy`、`rolling`、`taiex_drawdowns`、`asset_rotation`）。改數字先改這裡、重跑、再改書。末尾的 `quotes` 清單是「書裡應該找得到的句子」，刪書上的句子時要一起刪，否則「引用缺漏」會跳出來。
- `tools/essay_charts.py --guide`：重畫指南全部 15 張圖。**它會整塊重建每一個 `figure.chart`，只保留指南自己的 `<figcaption>`**（所以 figcaption 裡不能放需要保留的 `p.note`，但可以放連結）。要加新圖：在指南放空殼 `<figure class="chart" data-chart="圖id"><figcaption>圖說</figcaption></figure>`，再跑一次。
  - **警告**：指南裡手改過的 `p.note`（圖下說明）會被腳本蓋回腳本版。腳本跑完會比對並印 `⚠`；看到警告要自己判斷哪一版對，對的那版要寫回腳本，不要只在指南改。
  - 圖說（figcaption）在指南和腳本各有一份（腳本那份是新圖的預設值）。**改圖說時兩邊一起改**，否則下一個人重跑腳本會以為腳本那份才是正典。
- `tools/build_lite.py`：從 `guide/index.html` 依 manifest 抽區塊、套短稿、排版、印 PDF、跑哨兵。參數：`--fingerprint "選擇器"`、`--stamp <短稿id>`、`--manifest`。
- `tools/lite_sentinels.py`：約 24 類檢查。

### 哨兵排錯速查

| 紅的 | 多半是什麼 | 怎麼辦 |
|---|---|---|
| `alt` 指紋不符 | 完整版原文改了，短稿沒跟著看 | 人看過短稿還對不對，再 `--stamp <id>` |
| `glue` 有數字 | 接合文字寫了阿拉伯數字 | 數字一律留在原文區塊裡，接話只講方向 |
| `facts` | 兩份共同事實不再逐字一致 | 改回一致，或到 `lite/facts.txt` 調整清單 |
| `cases` | 案例數字和 `calc-results.json` 對不上 | 先確認是不是 `calc_core.py` 該改 |
| `tickers` | 商品代號跑出黃框外 | 教學段一律不准出現代號 |
| `labels` | 「本指南的做法」不是那七件事之一 | 標籤白名單在 `lite/labels.json` |
| `pages` | 頁數或奇偶頁不對 | 版面問題，不要用改上限硬過 |
| `toc` | 目錄頁碼≠連結目標≠書籤 | 重跑 build，還是不對就看 manifest 的章順序 |
| `fragments` | `output/*.html` 和產出對不上 | 重跑 build（片段是自動產生的） |
| `引用缺漏` | `calc_core.py` 的 `quotes` 和書不同步 | 兩邊挑一邊改 |

**哨兵擋不住的三條路**（每輪仍要人工對）：國字寫的新事實、短稿換用來源裡另一個數字、沒有數字的新規則。

---

## 還沒做的事（接手可以直接往下做）

拍板清單在 `docs/core-edition/specs/v61-decisions.md`（424 行，每條都有白話問題＋選項＋建議）。作者已拍板但**還沒實作**的：

- **二、刪減與合併 D1–D11**：重複的觀念散在多處（費用怎麼算進試算 10 處、「錢不夠時要多存」6 次、「五年內要用的錢不放股票」4 處…）。全部刪完只省約 1,100 字（1.8%），真正的體積在第 11 節與「另外三個人」。**D10（列印時強制展開所有摺疊區要不要改）是紙本頁數的最大變因**，建議 A（只展開要動筆的）。
- **三、L1–L7**（L8 已完成）：實作版真正獨有的內容幾乎是空集合（短稿都標著來源），所以這一組是「實作版把同一件事講得更好，要不要換回完整版」。**十二章退場後，這些寫法只剩在 `lite/alt/retired/` 的短稿裡，沒有人會再看到**，值得趁還記得時決定。四條零風險的（作者還沒拍板）：L2 補一句「能忍跌 20%，股票最多放四成：股票跌一半時，四成股票剛好少兩成」（不新增數字）、L3 兩句白話就地解釋（配息像從存錢筒拿錢、年化＝平均一年長多少）、L4 冷卻期與儲蓄險解約照實作版分段編號（一個字不改）、L7 命名與標題化三條。L1（年檢「自己的報酬」用 581 字短版）與 L5（年檢十條歸成七組）動得比較大，L6 建議**不要**合併兩張表。
- **四、剩下的圖**：G8（不同股債比從谷底爬回來要多久）、G10（不再平衡會漂成什麼樣）、G11（在歷史高點附近買進）。G9（各國逐年拼布表）做不出來——資料全被商業機構鎖住，替代方案見清單。
- **S5–S9**：結構與編排的剩餘項。
- 專篇 `essay/sections/*.html` 與小朋友版沒跟這幾輪改（共用 `essay_charts.py` 的圖，文字不同步）。專篇裡仍嵌著第三方原圖 base64。
- 早先未決：藍字密度（第 8 節 9 處、費用節 8 處）等作者看過；「自己的報酬」減重方案（作者選擇先不做）。

## 給下一個 session 的第一句話

> 接手《隔離人性》理財指南，先讀 `docs/handoff-guide-2026-09-16.md`，再讀 `docs/core-edition/specs/v61-decisions.md` 裡還沒做的 D、L、G、S 四組，然後問我要先做哪一組。
