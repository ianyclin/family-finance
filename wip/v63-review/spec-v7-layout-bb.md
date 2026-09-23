# v7.0 預覽：BB——版面收斂第二段（皮）：容器收成四種、字級梯度與小字升級

作者 2026-09-23 拍板（拍板 1、2）。在 BA（結構）之後做。依據 `layout-audit-visual.md` 3-A～3-C、3-G、四、以及 P3 死樣式。只動 guide/index.html 的 `<style>`（唯一例外：紅框補標籤字用 CSS `::before`，不改 DOM；`.promise` 讀者手冊補一句介紹紅框與資料卡要改 DOM——先起草標「待作者定」）。guide 的 `<style>` 是 lite 的來源，每次改完跑 build_lite 看頁數與哨兵。分 BB-1（容器＋字級）、BB-2（660px 規則簡化＋死樣式清理）。

## BB-1 容器收成四種 ＋ 字級梯度
容器：
- ① 主線卡 `.data-card`：底 `var(--surface)`、1px `var(--line)`、圓角 12px、內距 16/14（手機）18/20（桌機）、外距 `var(--gap-l)`。**卡內的 `.table-wrap`、`figure.chart`（BA 後應已無）、`.col-card` 不再自帶框線與底色**：`.data-card .table-wrap{border:0;background:transparent}`。
- ② 提示框 `.explain`、`.warning`、`.decision`、`.planstep`：**無底色**、左 4px 色棒（explain 綠、warning 紅 `var(--red)`、decision 綠、planstep 綠虛線 `border-left-style:dashed`）、圓角 0、內距 14/16、外距 `var(--gap-l)`。標籤字：explain 已有 `span.plain-title`；decision 已有 `::before` 本節行動；planstep 已有；**warning 新增 `.warning::before{content:"注意";…}`**（樣式比照 `.story::before`，紅色）。
- ③ 作者聲音 `.story`：保留 `var(--amber2)` 底＋左 4px amber（原 5px 改 4px），圓角 12px；`::before` 不變。**全書唯一有底色的框。**
- ④ 摺疊 `details.more`、`details.source-card`：無框無底（source-card 的米色底與棕框拿掉），左 2px `var(--line)`，summary 一律 .94rem／700／`var(--muted)`；箭頭沿用 AY。來源卡 summary 顏色改 muted（原綠）。
- 左緣對齊：四種容器的「框線＋內距」總和統一為 **18px**（例如 1px＋17、4px＋14、2px＋16），目標 `v7_layout_check` 的 375 正文左緣種類數從 18 降到 ≤8。
- 深色模式：四種容器的 token 覆寫同步（`.data-card`、`.warning`、`.source-card`、`thead` 原本硬寫色，改用 token）。
字級梯度（只留四級＋表格例外）：h2 1.55rem；h3 1.2rem；正文 1rem；小字 **.85rem（14.4px）**：`figcaption`、`.small`、`.note`、`.chart-sub`、`.source-link`、`span.small`、`p.small`、`summary` 用 .94rem；表格 `td/th` .85rem，`tight-mobile` 例外 .78rem。中間級（16、16.37、14.96、14.72、13.44、12.8、12.6、11.84）全部映射掉。行高只留 1.78（正文）、1.6（小字）、1.35（標題）。
列印：`@media print` 若因容器改動變頁，工作表 6 頁不變、完整版 ±3 頁內；超過就在 print 區塊補覆寫。

## BB-2 660px 規則簡化 ＋ 死樣式
- 16 個 660px 區塊合併成一個 `@media (max-width:660px)`；`pointer:coarse` 只留觸控熱區；`.wide{min-width:520px}` 在手機取消；`.table-wrap` 提示字只留 `.is-scrollable::before` 一條（AY 已做，確認）。
- `figure.chart` 負邊距：只留 section 直接子元素那一條（BA-3 後）；`.data-card` 內距改用 `--pad-card` 變數。
- 死樣式：`.audit-*`、`.bars*`、`.chip`、`.tasks`、`.toc-tag`、`.caveat`、`.ok`、`.fix`、`.rules`、`figure.chart details.orig`、`.label-principle/.label-practice`——**逐條先 grep guide/index.html、lite/index.html、output/*.html、tools/*.py 確認 0 使用才刪**（`.lite-plan` 是反例：guide 沒用、lite 在用，不能刪）。
- 320px：`tight-mobile` 再壓一級或接受橫捲，至少讓 375 維持只有 1 張表橫捲。

## 交件
每批回報：容器樣式表（四種的最終宣告）、字級與行高的最終值域、`v7_layout_check` 375／1024 各項、PDF 頁數、深色模式抽查（四種容器對比 ≥3:1）、刪掉的規則清單與 grep 證據。不發布；主線截圖。
