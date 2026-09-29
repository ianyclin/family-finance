# v7.0：DE——版本字樣改「v7.0／2026-09-29」拿掉「預覽」、插畫句併進分工卡（作者 2026-09-29 下午；主線裁定）

作者原話：「版本應該可以更新 預覽可以拿掉」「插畫可以整合至上面的分工」。基準 HEAD 01035b5。

## 1. 版本字樣（源頭是 `lite/manifest.json`）
- `lite/manifest.json`：`"version": "v7.0 預覽"` → `"v7.0"`；`"date": "2026-09-27"` → `"2026-09-29"`。
- `guide/index.html` L211 eyebrow：「給新手的長期投資與行為紀律指南・v7.0 預覽／2026-09-27」→「…・v7.0／2026-09-29」。
- `lite/index.html` 的 `<title>`、`p.lite-version`，以及指南書末附錄的 `p.lite-version`，都由 build_lite 從 manifest 產生——確認 build 後三處都變成「v7.0／2026-09-29」、title「隔離人性｜可列印工作表 v7.0」；若 title 是寫死在 build_lite 的樣板裡就改樣板。
- 匯出檔名 `export/…-v7.0 預覽.pdf` 會變 `…-v7.0.pdf`（若檔名樣板從 manifest 取）：舊的兩份「v7.0 預覽」PDF 留在 export/（gitignore），交班註明。
- 全 repo grep「v7.0 預覽」「2026-09-27」（排除 backup、work/、calc-results、export/、docs 歷史紀錄、wip 歷史紀錄）：guide、lite、tools、`docs/core-edition/specs/lite-format.md`、`lite/facts.txt` 若有就同改；`docs/handoff-guide-2026-09-19.md` 只在「換 session 交班」段標題與固定流程加一句「2026-09-29 起版本字樣是 v7.0／2026-09-29，不再叫預覽」，歷史段落不改。
- 頁尾「資料檢查日期：2026-09-23」不動（那是資料核對日，不是版本日）。
- numbers 哨兵：cover 的「27」會 LOST → 開 `numbers-allow-round60.json`（round59＋這一條，理由「版本日期 09-27→09-29」），兩基準 LOST 0。

## 2. 插畫句併進分工卡（第 28 節 `#methods`，L4412–4417）
- 把卡外那段 `<p>插畫：書封與十幅章節插畫（第 8 節兩幅一組）由 AI 影像模型生成（OpenAI 的圖像生成工具，2026-09-28；書封 2026-09-29），構圖與修改由作者決定，圖說由 AI 起草、作者核定；插畫只做比喻與休息，不承載任何數字或規則。</p>` 刪掉，改成卡裡第三個 `<li>`，放在「AI（Anthropic 的 Claude）」那條之後、「讀者要知道的」之前：`<li><strong>插畫</strong>：書封與十幅章節插畫（第 8 節兩幅一組）由 AI 影像模型生成（OpenAI 的圖像生成工具，2026-09-28；書封 2026-09-29），構圖與修改由作者決定，圖說由 AI 起草、作者核定；插畫只做比喻與休息，不承載任何數字或規則。</li>`（用字一字不改；粗體樣式比照前兩條——先看前兩條的 strong 用法照抄）。
- 卡外沒有別的東西跟著動；來源卡不動。

## 檢查
全套（numbers 兩基準 round60；anchors；budget——methods 主線可能因 li 歸類變動，照實測 `_comment_de`；planstep；xrefs；guidetools check；兩支測試；essay_charts ×2；calc_core；layout；build_lite ×2 等冪；lite_sentinels 含 [version]／[appendix]／[stale]；embed_illus --check）；grep 確認「v7.0 預覽」在 guide、lite、tools、output 為 0；PDF 第 2 頁眉標與附錄第一頁版本行；截圖第 28 節分工卡（375）。不 commit。
