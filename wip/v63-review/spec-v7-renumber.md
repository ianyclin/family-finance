# v7.0 預覽：全書連號＋手機表格提示＋電腦版目錄（作者 2026-09-20 同意）

作者原話：「我還是喜歡全部連號，讓每一節都有個號碼歸屬，也比較容易溝通」「全部依你的建議」。分兩個 commit 做：先 A（小），再 B（大）。

## A. 小改動

A1 **「← 表格可左右滑動 →」只在真的能滑的表上顯示**。現況：`@media(max-width:660px){.table-wrap::before{content:…}}` 對每張表都顯示；Fable 在 375px 實測（摺疊全開）：44 張表、40 張有提示、其中 28 張根本滑不動。改法：CSS 提示改成只對 `.table-wrap.is-scrollable::before` 生效；在現有的行內 `<script>` 裡加一小段：載入、`resize`、任何 `<details>` 的 `toggle` 事件後，對每個 `.table-wrap` 量 `scrollWidth > clientWidth + 2`，成立才加 `is-scrollable`（不成立就移除）。程式沒跑起來時的結果是「沒有提示」，可以接受。既有對特定表關掉提示的規則（`content:none`）保留。工作表 `lite` 那份樣式是複製指南的 `<style>`，確認一起生效或不受影響（工作表沒有 script 就讓它沒有提示）。
A2 **三張只超出一點點的表，調到不用滑**（375px 實測超出量：`why` 那張對照表 6px、`s10` 一張 6px、`s12` 一張 16px）：用縮欄內距或允許換行處理，不改內容、不縮字級到難讀。其餘 9 張真的要滑的（s2×2、s5×1、s11×2、cases×3、s12×1）這一批不動，列清單回報（每張：節 id、表的標題或第一列、幾欄、超出幾 px），之後作者逐張決定。
A3 **電腦版目錄預設也收起**，兩個例外：網址是 `#toc`（讀者按了「回目錄」）時自動全部展開；列印照舊全開（`data-print="open"` 機制不動）。做法：現有那段 `matchMedia('(min-width: 760px)')` 的 script——`details.read-how` 在寬螢幕仍自動展開（六條短條列，不擋路）；`#toc details.toc-part` 改成只在 `location.hash==='#toc'` 時展開，並監聽 `hashchange`（同頁按「回目錄」要即時展開）。手機也適用同一條（按回目錄 → 全開）。
A4 手機目錄說明文字的 CSS（上一批加的）照舊。

## B. 全書連號（28 節）

| 新號 | id | | 新號 | id |
|---|---|---|---|---|
| 1 | ten | | 15 | cases |
| 2 | start | | 16 | s12 |
| 3 | why | | 17 | s13 |
| 4–13 | s1–s10 | | 18 | sidepaths |
| 14 | s11 | | 19–22 | firstmonth、steps、products、costs |
| | | | 23–25 | annual、lifecycle、withdraw |
| | | | 26–28 | glossary、toolbox、methods |

原本有號的 14 節一律「舊號＋3」。**所有 `id` 不動**（外部連結、manifest、短稿 src 都靠 id）。

B1 每個 `section` 的 h2 都有 `span.num`（沒有的補上），數字照上表。`group-*` 六個分組節仍然沒有節號。
B2 全書 `a.xref` 的數字錨文字依 `href` 目標重寫成新號（寫一支一次性腳本，依目標 id 查表；不要用「舊字串 +3」的文字取代）。形如「第 5、11 節」「第 1–10 節」的連號與範圍都要對。`xref_num` 哨兵最後逐條驗。
B3 **用節名指路的地方維持用節名**（「投資前的安全順序」那一節），不必改成數字；但節名前後若寫了「沒有節號」之類的說明要拿掉。
B4 目錄：七組照舊；加兩個小標題把七組分成「第一部分：照順序讀（第 1–16 節）」與「第二部分：用到再翻（第 17–28 節）」（不另編一層號碼）；`toc-part-range` 改成新範圍（開始之前 第 1–3 節／先搞懂 第 4–13 節／寫下自己的計畫 第 14–16 節／遇到狀況時翻 第 17–18 節／動手做 第 19–22 節／隨人生調整 第 23–25 節／查資料 第 26–28 節）；目錄清單的 CSS 計數器（`toc-from-11`、`toc-from-14` 那一套）改成和新號一致。`order`、`toc`、`part_maps` 哨兵：`part_maps` 原本規定沒有節號的節（glossary 等）不得有 `map-num`——現在每一節都有號，組地圖每一行都要有 `map-num` 且等於目標的 `span.num`；需要調整哨兵規則時，保持「地圖上的號碼＝目標節的號碼、節名與 lede 逐字一致」這個語意，不得放寬。
B5 圖裡的節號：`tools/v63_g0*.py`、`tools/essay_charts.py` 等腳本裡寫死的「第 N 節」與站點對節號的對照全部改新號，重跑 `python3 tools/essay_charts.py --guide`（0 個 ⚠）。
B6 **黃框 `div.story` 裡的節號數字**：作者已同意只改數字（其餘一字不動，「」裡的引句不碰）。黃框裡的節號若是 `a.xref`，由 B2 的腳本一併處理；若是純文字，手改並逐處列進回報。`stories` 哨兵比的是完整版與原文一致，確認不受影響。
B7 工作表與短稿：`lite/alt/*.html`、`lite/manifest.json` 的接合文字裡用國字或數字寫的節號（「完整指南第十一節」「第十節四題」…）改新號（第十四節、第十三節…）；`xref` 在工作表會展開成節名的機制不動。逐份看過再 `--stamp`。
B8 `calc_core.py` 的 quotes、`lite/facts.txt`、`lite/case-checks.json`、`lite/labels.json` 若含節號，同步，逐條列進回報；`python3 tools/calc_core.py` 引用缺漏要是空的。
B9 `methods` 版本紀錄：舊條目裡的節號不改（那是當時的號碼），在 v7.0 預覽那一條加一句：「v7.0 起全書 28 節連號：原第 N 節＝現在的第 N＋3 節；原本沒有節號的各節也都有號。」
B10 文內所有非連結的「第 N 節」純文字（圖說、表格、摘要、`title` 屬性、`details` 摘要、planstep、`#plan-starter` 對照表「在哪一節填過」…）全集 grep 一次，逐處核對改新號；`a.term` 的 `title` 裡若有節號也要改。
B11 `numbers` 檢查會因節號改變出現大量 LOST／ADDED：這一批請改用「重編前的 guide（B 開工前那個 commit 的 `guide/index.html`，存成 `wip/v63-review/_baseline_v7_prerenumber.html`，記得加進 .gitignore）」當基準，先用腳本把基準檔的節號同樣映射一次再比，或者另寫一支一次性檢查：除了節號以外的數字 token 多重集合改前改後完全相同。回報你選的方法與結果。之後 `_baseline_v631` 對現況的 `numbers` 檢查會永久帶著這批差異——請把它們整理進一個新的 allow 檔 `wip/v63-review/numbers-allow-renumber.json`（或提出更乾淨的做法），不要手動塞幾百條。
B12 文件：`docs/handoff-guide-2026-09-19.md` 的「節 id ≠ 顯示的節號」一節改寫成新對照表（id → 新號），14 句 `mark.key` 清單前的節 id 照舊；`wip/v63-review/changes-for-author-v7.md` 加一項「全書 28 節連號」。

## 交件

每個 commit 前：`build_lite.py` exit 0＋SENTINELS OK、`guidetools.py check`、`test_guidetools.py`、`test_v7_check.py`、`v7_check.py anchors／budget／planstep`、`calc_core.py` 引用缺漏空、`essay_charts.py --guide` 0 ⚠。B 另外：全書 grep 舊的範圍字樣（「第 1–10 節」「第 11–13 節」「第 11 節」…）逐一確認是新號還是版本紀錄裡的歷史條目；完整版 PDF 目錄頁與任兩張含節號的圖轉 PNG 用 Read 看過。回報：A 的 9 張表清單；B 每一類（B1–B10）改了幾處、純文字手改的逐處清單、黃框改了哪幾個數字、哨兵規則調整的新舊對照、你選的 numbers 驗證法與結果、沒做的與原因、你不同意的地方。
