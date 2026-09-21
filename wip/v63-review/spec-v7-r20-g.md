# v7.0 預覽第 20 版：收尾 G（作者 2026-09-21 指示＋Fable 對上一批回報的裁示）

先讀 `v7-builder-rules.md`。一個 commit、具名 add、不 amend、不發布、不跑無頭瀏覽器。allow 檔 `numbers-allow-round17.json`。

1. **第 2 節樓梯圖（`figure.chart[data-chart="safety-steps"]`，腳本 `tools/v63_g05_safety_steps.py`）**——作者：「這幾句感覺都可以拿掉」。
   - `chart-sub`：「示意：階梯高低只表示先後順序，不表示難易或金額」→「示意圖：只表示先後順序」。
   - 圖下 `p.note`（「示意圖，沒有新數字：…在下面那五點裡。」）：拿掉。
   - `figcaption`（「由低到高五階：…最上面那一階才是投資。」）：不再顯示。螢幕閱讀器已有 SVG 的 `aria-label`（同樣列了五階）；若框架／哨兵要求每張圖都有 `figcaption` 或 `p.note`，優先做法是讓框架允許「純示意圖」省略（在腳本加一個明確的旗標，例如 `illustration_only=True`，並在 `essay_charts.py` 的檢查裡認這個旗標），次選是保留 `figcaption` 但加上既有的視覺隱藏 class（全書若已有 `.sr-only` 類的樣式就用，沒有就新增一條標準的 visually-hidden CSS）。不要為了過哨兵而放寬別張圖的檢查。改腳本那一邊並重跑 `essay_charts.py --guide`（跑兩次，確認 0 ⚠、別張圖的 p.note 沒被蓋）。工作表／短稿若含這張圖，同步。
   - 另外**只列清單不動手**：全書 25 張圖裡，`chart-sub` 與 `p.note` 講同一件事、或 `figcaption` 只是重複緊鄰內文的，逐張列出（圖名、三句原文、你的判斷）；有數字的圖口徑說明不算重複。寫到 `wip/v63-review/figure-caption-audit.md`。
2. **第 24 節作者黃框**（作者已同意）：「我自己的目標提領率用 2.5%，也就是 40 倍，比研究保守；」→「我自己的目標提領率用 2.5%，也就是 40 倍，比 4% 那幾份研究保守；」其餘不動；stories 哨兵指紋照正規做法更新。
3. **第 16 節「本指南的做法」**：退回兩段（上一批併成一段後同一段出現兩次標籤），兩段都不加 `<strong>`，文字不變。
4. 第 16 節主線 B：「美國掛牌的內扣費用最低，但…」→「美國掛牌裡最便宜的，內扣費用最低，但…」。新摺疊「股息被扣的稅」那一段的口徑小字（或段末括號）補一句：「三種的股息率資料日期不同（美國註冊的用 2026 年 8 月的官方頁，另外兩種用到 2023 年的長期資料），所以只看量級。」
5. `wip/v63-review/author-readthrough.md`：補第五批之後的條目（九件事／九個錯、辯證後的修正與裁判後修正、樓梯圖三句、黃框「比 4% 那幾份研究保守」），標已做＋commit。待辦加一條：「2.7%（Ben Felix 2022 影片；同一批作者改用全球分散組合另跑的結果）——等換到沒有 TLS 攔截的網路，核對影片說明或 PWL 原文後，才決定要不要補在第 24 節 2.31% 那句後面；查證紀錄 `debate/verify-ben-felix-2p7.md`」。`docs/handoff-guide-2026-09-19.md` 最上面現況段同步這條待辦與「第 19、20 版因本機網路（醫院 TLS 攔截 *.frame.claudeusercontent.com）尚未發到預覽網址；`release/` 兩個副本是最新的，換網路後直接發」。把 `debate/verify-ben-felix-2p7.md` 一起 add。
交件：全套檢查；更新 `release/` 兩個副本（含 `release/index.html`）；回報每條改前改後、框架怎麼處理純示意圖、全套輸出。
