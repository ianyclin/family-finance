# 交班：《隔離人性：理財新手完整指南》（2026-09-19｜v6.3.1 已發布、v7.0 預覽完工待作者看）

這一份取代 `docs/handoff-guide-2026-09-16.md` 成為**接手第一份要讀的文件**。舊那份留著當版本歷史（v4.x–v6.3 每一輪改了什麼、歷次拍板）。這一份只寫「現在是什麼樣子、怎麼動手、還欠什麼」。

---

## 接手先讀這段（三分鐘）

1. **這個專案在做什麼**：幫投資新手的一本書。作者是「指數三寶飯」。作者原話：「其實我的粉專不是重點，重點是我要用這份資料幫助投資新手」。
2. **只有一個原文檔**：`guide/index.html`（1.1 MB）。其他能讀到的 HTML／PDF **全部是程式產生的**，不要手改。
3. **現在有兩條線**：`main` ＝已發布的 v6.3.1；`v7-preview` ＝重寫過的 v7.0 預覽，**還沒合併、還沒上正式網址**。等作者看。見下一節。
4. **改完一定跑**：`python3 tools/build_lite.py`（exit 0＋`SENTINELS OK` 才算做完）＋ `tools/v7_check.py` 四支。**哨兵紅了不要繞過**，照 `docs/core-edition/specs/lite-format.md` 第 9 節那一欄處理；也不要為了變綠而放寬哨兵語意。
5. **這個資料夾是獨立的本機 git repo**（無遠端）。根目錄 `life-journal` 是公開 GitHub 倉庫，已 gitignore 本資料夾；**永遠不要把 family-finance 加進 life-journal**。動手前先 commit，改完先給作者看 diff。
6. **作者的鐵律**：教學段不推薦商品（代號只准出現在黃框 `div.story`）；黃框「」裡的引句一個字都不能改；文件不替讀者下結論；每個數字要有來源。
7. **派子代理照 `CLAUDE.md` 的分流**：跑腳本 runner、找位置 scout、套改動 applier、建造 builder、驗收 judge（決策與思考用 Fable，其餘派 Opus）。主線不要自己寫長篇。

---

## 兩條線的現況

| | `main`（commit 3f7008a） | `v7-preview`（commit 3bb111e） |
|---|---|---|
| 版本字樣 | v6.3.1／2026-09-19 | v7.0 預覽／2026-09-19 |
| 完整版 PDF | 175 頁 | **152 頁** |
| 可列印工作表 | 4 頁（兩張紙） | **6 頁（三張紙）** |
| 主線字數 | 61,621 | **46,103** |
| 主線＋看得到的小字 | 81,172 | **51,690** |
| 摺疊／`planstep` 小卡／圖 | 38／0／24 | 99／10／24 |
| 發布狀態 | 已在正式網址 | 只發私人預覽，正式網址停在 v6.3.1 |

**正式網址（更新時一定要帶 `url`，否則會開一個新的）**

- 完整指南：https://claude.ai/code/artifact/19dbae25-66c1-404d-8219-8f9e19d586a4 （第 55 版＝v6.3.1）
- 可列印工作表：https://claude.ai/artifact/492iv4AuQeSHVPRN2XEC1E （第 8 版＝v6.3.1）
- **外部讀者看到的是 Share 選單裡「釘選」的那一版**。發了新版不等於讀者看得到，要作者自己去 Share 改釘選。

**v7.0 預覽網址**：完整指南 https://claude.ai/artifact/9WawELoGewi9ecKK32YcfU ；工作表 https://claude.ai/artifact/SyGNXbzfPAXVeundB33Wb4 （2026-09-19 各第 1 版；更新時帶這兩個 `url`，不要覆蓋正式版）

**規矩**：作者說「我會先看」。**作者看過、同意之前，不要把 v7 發到正式網址、不要合併回 `main`。**

---

## 作者這一輪的指示（逐字引）

- 「針對『架構』『可閱讀性』最完整的檢視跟安排。我想要他是**容易閱讀的、引人入勝的、有教育性的**。」
- 「**你直接完成到最後吧。記得 eli5 的初衷，文字必須容易理解。**」
- 「**大部分的新手只想要『告訴我模糊的正確』不需要『十分精準』或是『作者把所有例外寫出來』，新手無法消化。**」
- 「**可列印工作表也需要採用 eli5**（目前好像不容易閱讀）。」
- 「**我希望你不要順著使用者說，而是應該思考、與我討論我說的話。**」

**閱讀情境**（Fable 建議、作者未反對）：主線為手機設計；填表與查資料給桌機與紙本。
**真人試讀**：作者找得到 3–5 位新手，**但作者要自己先看過**才找人。

---

## v7 改了什麼

| # | 改動 | 落在哪 |
|---|---|---|
| 1 | **兩層結構**：主線（第一次讀的人）／`<details class="more"><summary>想深入：…</summary>`（精確但書、口徑、第二份以後的證據）。針對特定讀者的摺疊，摘要改寫成「如果你…：」 | 全書。`details.more` 82 個、「想深入：」71 個、「如果你…：」11 個 |
| 2 | **每節骨架三問**：① 這一節的答案／現在先做什麼 → ② 為什麼大致合理（一個畫面、一個機制、一兩個數字）→ ③ 什麼情況才要停下來重想（＝安全但書的固定位置） | 全書 |
| 3 | **取捨問題**（每一段都用它篩）：「拿掉這個細節，新手會做出明顯不合適的決定嗎？還是只是專業讀者覺得不夠完整？」前者留主線，後者移層 | 寫作規則 |
| 4 | **起步版六行**：用途與年份／預備金債務保障／每月投多少哪天扣／買哪一類股票幾成／下跌時怎麼做／什麼情況才賣。`#plan-starter`，邊讀邊填 | s11 開頭＋工作表第 1 頁 |
| 5 | **10 張 `div.planstep`** 小卡（start、s2、s4、s5×2、s6、s7、s8、s10×2），每張只問一件事，小安示範一行 | 8 個節 |
| 6 | **F 區三格跌幅收成一格**：「照常投入，什麼都不改（預設）／我另有規則＿」。`mark.key` 跟著改 | s11＋全書 25 處同步 |
| 7 | **演練改有限結論**：「這次演練沒有發現做不到的地方」；所有人的第一份比例一律寫「暫定」 | s11、cases、工作表 |
| 8 | **`#plan-panic` 兩條路**：有計畫→拿出那張紙照做；沒計畫→今天只做三件事。封面入口、狀況索引、ten、s5 都直連過去 | s11 |
| 9 | **節順序**：ten → start → why（先做得到的事，再講理由）；`glossary` 搬到「查資料」組（`group-ref` 之後、`toolbox` 之前） | 正文＋目錄 |
| 10 | **第 14 節改名改定位**：「三十二種常見情境」→「常見情境：我在怕什麼？」，每題收成「發生什麼事 → 先檢查什麼 → 今天做哪一步 → 何時再看」（「今天：」出現 29 次） | s13（顯示 14） |
| 11 | **工作表三張紙六頁**：①正 起步版六行＋跌的那一天／①背 四個立即停止＋大跌演練／②正 完整版計畫表（欄位名白話）／②背 查表頁三步／③正 年檢問句版／③背 5/25。`pages`／`worksheet` 哨兵改新規格（規格寫在 `docs/core-edition/specs/spec-v61-worksheet.md` 末尾「v7：三張紙」） | `lite/manifest.json`＋`lite/alt/` |
| 12 | **新工具 `tools/v7_check.py`**：`mainline`／`numbers`／`budget`／`planstep`／`anchors` 五個子命令，預算檔 `wip/v63-review/budget-v7.json`、允許丟數字的清單 `wip/v63-review/numbers-allow-all.json` | `tools/` |

**驗收**：`judge-v7-1`（簡化過頭）、`judge-v7-2`（規則一致性）、`readers-v7`（三位手機讀者）三份報告存在 `wip/v63-review/`；must 全部照 `spec-v7-final-fix.md` 修完（commit 3bb111e）。

---

## v7 的寫作規則（之後改書都要守）

1. **一句一件事，講大方向就好。** 不在同一句裡補口徑、邊界、反例。
2. **但書分三種**：安全但書（照字面做會出事）留主線、只在動手的那個位置講一次；精確但書（口徑、邊界、少數人的例外、推導）移進「想深入」；防禦性但書（不是建議／不是預測／不是保證）每節最多一次。
3. **模糊不等於錯。** 簡化後的句子單獨拿出來仍要成立，不得滑成承諾（「長期一定賺」「跌了都會回來」「放五年就安全」）。
4. **移層優先於刪除。** 查證過、有來源的內容不刪；來源跟著數字一起移。直接刪的只有重複句與多餘的防禦性但書。
5. **不要用補但書修問題。** 修法順序：①把句子改寫成本身就成立的說法 →②把安全但書移回「什麼情況要重想」的位置，同時拿掉一句別的抵字數 →③真的需要才新增。
6. **新寫的句子比移層更容易出錯（裁判①的結論）**：這一版真正會出事的兩處都不是講得太模糊，是**新寫的句子把規則寫窄了**（「只有三種情況才賣」vs 書上自己的四種）、**新造的載體漏帶了地板**（起步版卡叫人寫股票比例，卻沒有尺、沒有「五年內的錢不放股票」）。新增的絕對句（「只有／一定／都」）、新做的卡片與表，一律要帶地板。
7. **看得到的小字每節 ≤350 字**（`p.small`／`span.small`／`p.note`／`figcaption`），只留緊貼數字的一句出處；小字在手機上一樣佔版面，移到小字不算減重。
8. **主線必要跳轉＝0**：主線句不准有「先看第 N 節才懂」的依賴；指路句一節最多一句，放最後。
9. **預設做法不等於替讀者下結論**：主線給一個預設、標「本指南的做法」、旁邊留一格「我另有規則」。（這是 Fable 的解讀，待作者確認，見「還沒做的事」。）
10. **不能動**：黃框 `div.story` 全文、所有既有 `id`、來源卡的引文與連結、圖的資料；不新增事實、數字、研究、來源。

---

## 作者的原則（不能違反）

- **目的是幫助投資新手，粉專不是重點。** 取捨時先問「新手讀得懂、照做不會出錯嗎」。
- 四個標準一起看：**正確性、教育性、啟發性、閱讀性**。為了完全正確一直補細節而變難讀，也算失敗。
- 真實性優先；每個數字要有來源；不推薦商品、不做個人化建議；**文件不替讀者下結論**（圖說最容易犯）。
- 教學內容不混入作者做法。作者做法只在黃框 `div.story`，黃框裡「」內的引句一字不改。
- 作者持股比例：台股一成、全球七成、因子兩成。再平衡：年底 5/25 門檻，平時投入偏離到門檻兩倍才賣；賣出只有提領期、用錢、再平衡三種情況。第 11、12 節與年檢三處要一起改。
- ELI5：國中生讀得懂，但不讓大人覺得被當小孩；先畫面、再道理、最後數字。寫法在 `docs/core-edition/specs/eli5-rules.md`（v7 放寬的地方見上一節）。

## 文件裡的標記系統（改文字時要維持）

| 東西 | 寫法 | 規則 |
|---|---|---|
| 節號連結 | `第 <a class="xref" href="#s4">4</a> 節` | 內文出現「第 N 節」一律要連 |
| 名詞連結 | `<a class="term" href="#g-xxx" title="一句解釋">詞</a>` | 每節只標第一次；不標在標題、白話版、黃框、strong、其他連結裡。目前 105 處 |
| 重點句 | `<mark class="key">句子</mark>` | 14 句（清單見下）。一節最多一句，單獨看得懂，是行動或結論 |
| 先跳過 | `<span class="later">先跳過也可以…</span>` | 13 處 |
| 白話版 | `<p class="explain"><span class="plain-title">白話版</span><br>比喻</p>` | 每節都有；要是比喻，不可以直接講答案 |
| 想深入 | `<details class="more"><summary>想深入：〈具體講什麼〉</summary>` | 摘要要具體。針對某一種人的用「如果你…：」 |
| 計畫小卡 | `<div class="planstep" data-plan="C10">` | 標題「你的計畫・第 N 行：〈白話問題〉」；放在黃框之後、`p.decision` 之前，**不要放進黃框或帶 `data-lite-alt` 的區塊裡** |
| 卡片順序 | 每節：h2 → lede → 白話版 → 內容 → 圖 → 想深入 → 來源 → 黃框 → planstep → `p.decision` | 程式沒有把關，靠人 |
| 圖 | `<figure class="chart" data-chart="圖id">` | 由 `tools/essay_charts.py --guide` 產生，見下面的警告 |

### 節 id ≠ 顯示的節號（陷阱）

`cases` 顯示第 12 節，所以 **id `s12` 顯示成第 13 節、id `s13` 顯示成第 14 節**。id 一律不動。另有六個沒有節號的分組節 `group-core`／`group-plan`／`group-situations`／`group-howto`／`group-life`／`group-ref`（組地圖，`part_maps` 哨兵逐字比對）。`start`、`why`、`glossary` 沒有節號。

### 核准的例外（不是錯誤，不要「順手修好」）

1. `lifecycle` 的三個黃框嵌在三個問題中間（刻意的）；`methods` 沒有「本節行動」（它是查證附錄）；工作表的接話與動作框不回填完整版。
2. `group-*` 分組節沒有節號、沒有白話版、目錄裡不列成連結；`figure.chart details.orig` 那幾條 CSS 現在沒有東西套用，沒有刪。
3. 工作表演練卡刻意不和完整版 `#drill` 同步（第一張紙要自足），差異寫在 `lite/alt/ch4-drill.html` 檔頭 note。
4. 查表頁算例用 0.2% 費用（全書其他算例 0.5%）：換掉會踩到表二沒有那一列的邊界。

### 目前 14 句重點（mark.key，從 `guide/index.html` 實抽）

why 它是一套寫得下來的步驟，不是一種本事。／s1 上面的歷史數字是過去，不是預測。／s3 簡單不是妥協，是把所有會扣分的動作拿掉以後剩下的東西。／s4 核心放全球市值型，台股大盤可以是裡面的一塊。／s5 波動會在兩種情況變成真的傷害：第一，錢很快要用，被迫低價賣；第二，比例超過心理承受度，自己在低點賣。／s6 有錢可投、計畫也允許的時候，就照規則投進去。／s7 挑一個固定的日子就好。／s9 熱門時加碼、下跌時退出，會讓投資人的錢放在較差的時段。／**s11 最不用臨場判斷的答案是「不管跌多少，照常投入，什麼都不改」。**（v7 改過）／s13 照卡做，不用說服對方。／steps 買進前先讓交割帳戶有足夠資金，避免違約交割／annual 自己的年化和指數差很多時，先找原因，不先換商品。／lifecycle 借的錢有固定利息，投資報酬沒有。／withdraw 市值型配置加一張規則卡，是最容易交接的組合

---

## 改完後的固定流程

```bash
cd "/Users/linyenchu/Cladue Code/family-finance"
git add -A && git commit -m "…"                       # 0. 動手前先把現狀存起來
cp guide/index.html guide/index.vX.backup.html        # 1. 大檔先備份（*.backup.html 已 gitignore）
# 2. 只改 guide/index.html（Edit，或寫一次性 python 做整段替換；不要整檔 Write）
python3 tools/essay_charts.py --guide                 # 3. 只有動到圖才跑，一定要帶 --guide
BASE=wip/v63-review/_baseline_v631.html               # 4. v7 的四個檢查
python3 tools/v7_check.py numbers $BASE guide/index.html --allow-file wip/v63-review/numbers-allow-all.json
python3 tools/v7_check.py anchors $BASE guide/index.html
python3 tools/v7_check.py budget guide/index.html wip/v63-review/budget-v7.json
python3 tools/v7_check.py planstep guide/index.html
python3 tools/build_lite.py                           # 5. 兩份 HTML＋兩份 PDF＋約 28 類哨兵（exit 0 才算過）
python3 tools/guidetools.py check guide/index.html
python3 tools/test_guidetools.py tools guide/index.html && python3 tools/test_v7_check.py
python3 tools/calc_core.py                            # 「引用缺漏 []」才過
```

`tools/v7_check.py mainline guide/index.html` 是看數字用的（逐節 mainline／small／source／摺疊）。**主線預算在 `wip/v63-review/budget-v7.json`：要加主線字就要同步調預算，並在 `_comment` 寫為什麼、抵掉了什麼。** 預算不是建議值，是這一版唯一擋得住「越改越厚」的東西。

發布：用 Artifact 工具發 `output/guide.html`（帶完整版 `url`）與 `output/lite.html`（帶工作表 `url`）。**發布交給子代理做**——`output/guide.html` 1.1 MB，主線自己用 Artifact read 會把整份灌進上下文。

### worktree 平行施工（v7 用過，會再用）

- 每批一個 `git worktree`，只准改自己那幾節；`<style>`、封面、目錄、`group-*` 組地圖、`tools/` 不要動；**`h2` 與 `p.lede` 不要改**（會讓 `part_maps` 紅）。
- **gitignore 的檔不在 worktree 裡**：基準檔請用絕對路徑 `/Users/linyenchu/Cladue Code/family-finance/wip/v63-review/_baseline_v631.html`；build 缺檔就從主工作目錄複製，**不要 commit 它們**。
- commit 只加來源檔（`guide/index.html`、`lite/alt`、`lite/facts.txt`、`lite/case-checks.json`、`tools/*.py`）；`output/`、`lite/index.html`、`lite/work/`、`lite/calc-results.json` 是產生的，**不要 commit**（`git checkout -- output lite/index.html lite/work`），合併後統一重建一次。
- `.claude/` 已 gitignore，所以 `.claude/worktrees/` 裡的工作目錄不會被誤提交。

### 工具

**手改的檔只有這幾種**：`guide/index.html`、`lite/manifest.json`、`lite/alt/*.html`、`lite/facts.txt`／`case-checks.json`／`tickers.json`／`labels.json`、`tools/*.py`。`lite/index.html`、`output/*`、`export/*` 都是產生的。

- `tools/guidetools.py`：`apply`（補丁 JSON，每筆 old 必須唯一）、`check`、`text`、`diff`、`numbers`。**不要用 `apply` 搬節或做有重疊的補丁**（`str.replace` 會換掉所有出現處，理由見 `wip/v63-review/engineering-impact.md` 第 6 節）。測試 `tools/test_guidetools.py`、`tools/test_v7_check.py`。
- `tools/calc_core.py` → `lite/calc-results.json`：書裡所有數字的唯一算處。末尾 `quotes` 是「書裡應該找得到的句子」，刪書上的句子要一起刪。
- `tools/essay_charts.py --guide`：重畫 24 張圖。**不要跑不帶 `--guide` 的版本**（會改到專篇）。它會整塊重建每個 `figure.chart`，只保留指南的 `<figcaption>`；手改過的 `p.note` 會被蓋回腳本版並印 `⚠`。**圖說與 `p.note` 在指南和腳本（含 `tools/v63_g0*.py`）各一份，兩邊一起改。**
- `tools/build_lite.py`：抽區塊、套短稿、排版、印 PDF、跑哨兵。參數 `--fingerprint`、`--stamp <短稿id>`、`--manifest`。需要 Google Chrome 與 PyMuPDF；整趟約 1–3 分鐘。
- `tools/lite_sentinels.py`：約 28 類檢查。

### 哨兵排錯速查

| 紅的 | 多半是什麼 | 怎麼辦 |
|---|---|---|
| `alt` 指紋不符 | 完整版原文改了，短稿沒跟著看 | 人看過短稿還對不對，再 `--stamp <id>` |
| `glue` 有數字 | 接合文字寫了阿拉伯數字 | 數字留在原文區塊裡，接話只講方向 |
| `facts` | 兩份共同事實不再逐字一致 | 改回一致，或調 `lite/facts.txt` |
| `cases` | 案例數字和 `calc-results.json` 對不上 | 先確認是不是 `calc_core.py` 該改 |
| `tickers` | 商品代號跑出黃框外 | 教學段一律不准出現代號 |
| `labels` | 「本指南的做法」不是那七件事之一 | 白名單在 `lite/labels.json`（「本指南的預設」不受它管） |
| `pages` | 工作表頁數或正反面配對不對 | 新規則：第 1–2、3–4、5–6 成對，奇數頁是正面；頁數是奇數就補一塊或加 `blank_page` |
| `worksheet` | 塊數／頁數／來源／出現章號 | 新規則：塊數＋留白頁數＝總頁數，落在 5–6 |
| `toc`／`order` | 目錄頁碼或順序≠正文 | 搬節時目錄要一起搬 |
| `part_maps` | 組地圖和目標節的 h2／lede／節號不一致 | 逐字同步（改 h2 或 lede 就會紅） |
| `xref_num` | 「第 N 節」錨文字≠目標節顯示節號 | 照目標節的 `span.num` 改（id≠節號陷阱） |
| `fragments` | `output/*.html` 和產出對不上 | 重跑 build |
| `引用缺漏` | `calc_core.py` 的 `quotes` 和書不同步 | 兩邊挑一邊改 |

**哨兵擋不住的三條路**（每輪仍要人工對）：國字寫的新事實、短稿換用來源裡另一個數字、沒有數字的新規則。

---

## 還沒做的事

### (a) 等作者看預覽後的決定（最優先）

1. **要不要採用 v7。** 不採用就把 `main` 的 v6.3.1 繼續往下做。
2. **三個 Fable 自己拿的主意，請作者特別看**：① F 區三格跌幅收成一格＋重點句改字（`mark.key` 是作者語氣所在）；② 詞彙表搬到書末「查資料」組；③ `start` 提到 `why` 前面。
3. **「預設做法 vs 不替讀者下結論」的解讀**：Fable 判斷「主線給一個預設、標本指南的做法、留一格我另有規則」不算替讀者下結論。作者若不同意，F 區、冷卻期、5/25 三處要一起退回。
4. 第 8 節**收益平準金**的比喻現在是「班上分餅乾」版，另一個候選是班費版，請作者挑。
5. **填表順序圖**（s11）與**人力資本那段**（s2）現在收進「想深入」摺疊，作者若覺得該留主線，字數要從同節別處抵。
6. 第 14 節改名「常見情境：我在怕什麼？」。

### (b) 真人任務測試（作者先看過才找人）

3–5 位新手，題目見 `wip/v63-review/decisions-2026-09-19.md` 末節：說出哪些錢不能投、找到今天該做的事、填出必要欄位、區分「恐慌停扣」與「失業依規則暫停」、在情境中找到對應行動。
**成功指標**：讀十分鐘後問「**這個星期你會做哪一件事？**」，答得出具體一步才算過。
**陷阱題**：「**放五年以上就安全了嗎？**」——要看有沒有人把簡化句讀成保證；有的話，那個位置把安全但書放回主線。
**另外四個觀察點**（v7 第三輪 B5 加的，每一位都看）：
1. 能不能說出**自己今天可以做什麼**（不是「以後要做什麼」）。
2. 能不能**完成起步版六行而不必一直回翻**前面各節。
3. 遇到**收入中斷**或**市場下跌**，找不找得到適用的做法（該翻哪一頁、照哪一行做）。
4. 能不能坦白說「**我不知道**」，而不覺得自己不適合投資——三問第 2 題與大跌演練的「不知道」出口就是為這件事寫的。

**這一輪之後停止 AI 審閱擴充修改清單**：v7 預覽的修改清單到第三輪 B 為止。下一輪改什麼，由真人測試的結果決定，不再由 AI 評閱自行加項。

### (c) v6.3 時代的已知未做

- S29 Morningstar Mind the Gap **2026 版**要下載 PDF 核對。
- 台灣上市家數：書上 1,094 家（證交所開放資料，出表日 2026-09-17）和證期局的 971 家對不上，原因沒查完。（舊交班寫「差 11 家」，和這兩個數字算不起來，一併待查。）
- S60（陳大哥錢不夠的情境）沒做。
- `<title>` 與 PDF 檔名仍是「理財新手完整指南」（和封面書名不一致）；`output/essay.html`、`output/eli5.html` 是舊口徑。
- `lite/manifest.partA.json`／`partB.json` 跑不起來（引用的短稿已退場），只是第二階段測試檔。
- 夫妻財務分工：作者 2026-09-18 說先不管。

### (d) 最終修正批回報的「順帶看到」（各一行，沒動手）

- `tools/calc_core.py:375` 陳大哥演練的死字串仍寫「通過」（`drill_2031_low.story`），和「有限結論」規則不一致；它不進書，只在 JSON 裡。
- `cases` 那個摺疊可以改成「如果你是接案／收入不固定」開頭，和 C2 的「如果你…：」規則一致。
- `lite/alt/plan-blank.html` 的 F 區少一句完整版有的說明（收一格後的「我另有規則」那行）。

### (e) 沒跟上的分支產物

專篇 `essay/sections/*.html` 與小朋友版沒跟 v6.2 以後的任何一輪；專篇仍嵌第三方原圖 base64。

### (f) 清掉 worktree 與已合併的分支（**指令列在這裡，不要現在執行**）

```bash
git worktree list                      # 現在有 7 個在 .claude/worktrees/
git worktree remove .claude/worktrees/agent-XXXXXXXX          # agent-abc584ad35e8c2831 是 locked，要先 git worktree unlock
git worktree prune
git branch -D worktree-agent-a31a9a6a9666cfa26 worktree-agent-a4ce74154aaf9f9e3 worktree-agent-a53bf6642f7cb9ab4 worktree-agent-abc584ad35e8c2831 worktree-agent-ad3556328bdab2d7e worktree-agent-ae66bf2b0088bdd51 worktree-agent-af6191a3d8959af1f
```

七個分支的內容都已經合併進 `v7-preview`（見 `git log --oneline main..v7-preview` 的 Merge 紀錄）。**等作者決定 v7 的去留之後再清**，現在刪掉就沒有逐批的施工紀錄可以對。

---

## 這一輪結束時的狀態

- **第二輪驗收（同一天稍晚）**：最終修正批（3bb111e）之後補派裁判③只驗那一批的新句子（`wip/v63-review/judge-v7-3.md`）——又驗出 2 條 must，同一種錯：工作表第一張背面的演練卡算不出第一個數字（第一張紙沒有金額欄）；起步版第 6 行把「已經影響睡眠」掛在「才賣」底下、沒有幅度出口。另外 Fable 在 375px 實測：平滑捲動讓「正在跌」入口要花兩秒刷過整本書；`#plan-starter` 三欄表在手機上擠到不能讀。全部照 `spec-v7-final-fix-2.md` 修完（f27fd34、071dcda）：演練卡改用「每月投入 × 12 × 年數，二十年以上再乘一倍半」粗估（依據：表二 3.6%／20 年 35.1 ÷ 本金 24 ≈ 1.46；30 年實際是 1.80，所以長年期略偏鬆，但工作表版不換算物價、整體仍比完整版偏嚴）；第 6 行第三項改成「→ 把股票比例長期調低（怎麼調看第 10 節）」，第 8 節主線同步；拿掉 `scroll-behavior:smooth`；六行卡 ≤660px 直排。**教訓寫進寫作規則第 10 條的精神：每一批「新寫的句子」都要再驗一次，機械檢查全綠不代表沒有把規則寫窄。** 這一批之後沒有再派裁判（約二十處，Fable 逐條讀過 builder 的改前改後）。
- **第三輪（同一天，ChatGPT 讀完預覽第 2 版後的評閱）**：A 部分（不改規則：小安前後一致、下市不等於歸零、稅表列名、朋友那題、急救卡與第 5 行的適用範圍、四處移層）＋B 部分（改規則：演練三步三出口含「不知道」、完整版改成第一次年檢用到才補、六行加「其餘放哪裡／每年幾月檢查」、急救卡適用條件前置）。規格 `spec-v7-round3-A.md`、`spec-v7-round3-B.md`；commit 18c2583、199ff23、3919a02。作者尚未逐項確認，全部列在 `changes-for-author-v7.md`「一之二」，每項可單獨退回。**B 部分之後沒有再派裁判**（Fable 讀過演練卡、急救卡、對照表的改後全文）；下一個 session 若要動這幾張卡，先派一位裁判只驗 199ff23 的新句子。
- 現在的數字：主線 45,915、主線＋看得到的小字 51,510、完整版 PDF 154 頁、工作表 6 頁。`v7-preview` HEAD 見 `git log`（071dcda 之後只有文件）。
- **還沒驗的**：claude.ai 的 artifact 外框裡，點頁內連結再按上一頁會不會回到原位（本機測是會；預覽網址要登入，Fable 不能代登）。請作者用手機開預覽時順手試。
- 3bb111e 當時的全綠紀錄：`numbers` LOST 0、`anchors` OK、`budget` OK、`planstep` OK、`build_lite` SENTINELS OK（工作表 6 頁）、`guidetools check` OK、兩支測試 ALL PASS、`calc_core` 引用缺漏 []、`essay_charts` 0 ⚠。
- 作者用公司網路，每小時要重連一次；發布或長時間工作流遇到 network error，等作者重連後重試即可。

## 給下一個 session 的第一句話

> 接手《隔離人性》理財指南，先讀 `docs/handoff-guide-2026-09-19.md`：`main` 是已發布的 v6.3.1，`v7-preview` 是做完但還沒發正式網址的 v7.0 預覽。**在作者說他看過預覽、也同意之前，不要合併回 `main`、不要換正式網址的釘選版本。** 先問我：作者看了沒、他怎麼說。分工：決策與思考用 Fable，其餘派 Opus。
