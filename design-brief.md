# 外殼設計簡報（給外殼 builder；版面規格全文見 outline.md §1）

頁面名稱：`<title>家庭理財白話手冊</title>`。單一 HTML 檔，讀者主要用手機看，也要能列印。

## 主題感

像一本「家計簿＋存摺」：淡冷灰的紙面、藍黑的墨字、朱紅印章色只用在少數強調處（章節眉標、警語框、目前所在的導覽項）。青綠色留給「動手」與「今天的一件事」。避免奶油底＋橘紅、避免大面積漸層、避免圓角卡片到處貼。

## 色票（CSS 變數，三種主題狀態都要定義；元件只透過變數取色）

| 變數 | 淺色 | 深色 | 用途 |
|---|---|---|---|
| --paper | #F4F6F8 | #121820 | body 背景（一定要明寫） |
| --surface | #FFFFFF | #1A222B | 框、卡片、側欄底 |
| --ink | #1B2733 | #E6EAEE | 正文 |
| --muted | #5C6B78 | #9AA7B2 | 次要文字、dt 標籤、來源清單 |
| --line | #CBD3DA | #33404B | 框線、表格線、分隔線 |
| --fill | #E8EDF1 | #222C36 | 算式框、pre、徽章底 |
| --accent | #B33A2E | #E2685A | 眉標、警語框、目前章節、進度條已達段 |
| --accent-soft | #F6E4E1 | #3A2320 | 警語框底 |
| --teal | #1E7B6C | #4FB8A5 | 動手框、今天的一件事、連結 |
| --teal-soft | #DDEFEA | #173129 | 動手框底、勾選完成 |
| --amber | #9A6B12 | #D9A441 | 年度徽章文字 |
| --amber-soft | #F5EBD3 | #3A2E12 | 年度徽章底 |

主題規則：`:root` 定義完整淺色；`@media (prefers-color-scheme: dark)` 內以 `:root:not([data-theme="light"])` 重定義；`:root[data-theme="dark"]` 再定義一次。所有顏色都只寫在這三個區塊，元件樣式只用變數。

## 字型

- 標題與一句話：`"Noto Serif TC"`, `"Songti TC"`, `"PMingLiU"`, serif（600／700）
- 內文：`"Noto Sans TC"`, `"PingFang TC"`, `"Microsoft JhengHei"`, sans-serif（400／500／700）
- 數字、算式、徽章、來源清單的年份：`"IBM Plex Mono"`, `"SF Mono"`, Menlo, monospace（400／500）
- Google Fonts：`https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@600;700&family=Noto+Sans+TC:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap`
- 字級：正文 17px／行高 1.8；h2 1.9rem 宋體；.lede 1.3rem 宋體、`text-wrap: balance`；h3 1.2rem 黑體 700；h4 1rem 700；眉標 0.8rem、字距 0.08em、accent 色；來源清單 0.85rem；.num 等寬、`font-variant-numeric: tabular-nums`。

## 版面

- 內文欄寬上限 42rem，置中；≥1024px 時左側 260px 固定側欄（章節導覽，依七個階段分組，標示目前章節、每章可打勾「完成」）。
- <1024px：頂端固定列，左邊書名、中間「第 N 章／共 18」（捲動時用 IntersectionObserver 更新）、右邊「目錄」按鈕開抽屜式導覽。
- 每章 `<header class="ch-head">` 前面，由組裝腳本插入八段進度條（0 導讀｜1 看清楚｜2 止血與撐住｜3 長大｜4 制度｜5 家庭與交棒｜6 守住｜7 例行化；附錄 data-stage=8 顯示全滿），目前階段用 accent 填色、其餘用 line；段下有小字標籤，手機上只顯示目前階段的標籤。
- 每個階段第一章之前插入區隔頁 `<div class="stage-divider">`：階段名＋「這一區做完你會多出什麼」一句（文字由組裝腳本的設定表提供，見下）。
- 框：fact 左邊 3px ink 線、surface 底；formula fill 底、1px line 框、pre 等寬不換行可橫捲；tradeoff 1px line 框，.cols 兩欄 grid（<640px 堆疊），.bottom 宋體、muted；warning 1.5px accent 框、accent-soft 底；myth 左邊 3px muted 線，dt 為小標；action 1.5px 虛線 teal 框，`ul.checks li` 前面由 JS 加真正的 checkbox 並記到 localStorage（try/catch），`td.blank` 設 contenteditable 並記到 localStorage、螢幕上顯示虛底線、列印時顯示空格線。
- 對照卡 `.cards`：grid `repeat(auto-fit, minmax(240px, 1fr))`；卡片 1px line 框、surface 底；dt 小字 muted、dd 正文；同一列卡片等高。
- `.table-wrap` overflow-x auto；表格 1px line；th 左對齊 muted。
- `dfn`：虛底線；點擊在原地展開一個小浮層，內容來自附錄名詞表（`dl.glossary` 的 `dt[id="term-XXX"]` 與其後的 dd）；找不到就不加互動。Esc 或再點關閉。
- `details`：summary 用 teal、前面一個小三角；列印時全部展開。
- `figure.chart svg`：寬 100%、高自動；顏色靠 CSS 變數；`figcaption` 0.9rem muted。
- 徽章 `.badge`：等寬 0.75rem、amber 字、amber-soft 底、圓角 3px。
- `sup.cite a`：0.7rem、teal、無底線。
- 章尾 `.ch-foot`：上方一條 1px line；.today 用 teal-soft 底 + teal 左線；.sources li 0.85rem、行高 1.6。
- 動態：只有抽屜開合與浮層淡入；`prefers-reduced-motion` 時全關。鍵盤焦點有可見外框。
- 列印：隱藏側欄、頂端列、進度條互動；每章 `page-break-before`；連結不印網址（來源清單本來就有網址文字）。

## 導讀與附錄的額外元素（00、16、17 章會用到，樣式要先備好）

- `<table class="checkup-table">`：健檢進度表（章名｜分鐘｜產出｜完成），四欄是導讀的例外；「完成」欄由 JS 放 checkbox 並與側欄的打勾同步。
- `<div class="keypoints">`：導讀最前面的「先看重點」，內容是 `<ol>`，每項末尾一個 `<a href="#ch-NN">第 N 章</a>`；視覺上要比其他入口更醒目（宋體、字級略大、每項之間留白），但不是卡片。
- `<div class="author-route">`：導讀最後的「如果你想照作者的路走」單頁：`<h3>`＋`<p class="route-intro">`（標示這是作者自己的路，不是文件結論）＋`<ol>` 七條（每條 `<strong>` 一句原則＋理由＋代價＋章節連結）＋`<p class="route-note">`（連到第 9 章的作者規則卡）。視覺：teal 左線、surface 底、宋體標題；列印時獨立一頁。
- `<ul class="q-index">`：30 句問題索引，每項 `<a href="#ch-NN">`。
- `<div class="triage">`：三題分流，內容用 `ol.steps`。
- `<div class="routes">`：三條路線，內容用 `.cards`。
- `<div class="manifesto">`：「這份文件不是什麼」清單，1px accent 框、不用底色。
- `<dl class="glossary">`：名詞表，`dt id="term-XXX"`。
- `<div class="table-wrap wide"><p class="swipe-hint">可左右滑動</p><table class="expiry">`：會過期的數字一覽表（5 欄）。
- `<table class="revisions">`：修訂紀錄。
- `<div class="master-list">`：總清單，三段 `<h4>` 先做／再做／有餘力再做，項目用 `ul.checks`，「需要另一半一起做」用 `<span class="pair">👥</span>`。
- `<p class="version-line">`：頁尾「本版完成日／下次建議重查」。

## 組裝腳本（tools/assemble.py）

輸入：`shell/style.css`、`shell/app.js`、`chapters/*.html`（依檔名數字排序，00 到 17）、腳本內的階段設定表。輸出：`output/index.html`（CSS 與 JS 內嵌，字型用 Google Fonts 連結；不含 `<!doctype>` `<html>` `<head>` `<body>` 標籤，因為發佈端會包外層——但要能被瀏覽器直接開，所以檔案開頭放 `<title>`、`<meta charset>`、`<style>`，再放內容與 `<script>`）。
腳本要做：插入頂端列與側欄（從各章 h2、eyebrow、data-stage 生成目錄）、插入進度條、插入區隔頁、把名詞表轉成 JSON 內嵌供浮層使用、檢查所有 `#src-` `#ch-` `#ws-` `#term-` `#def-` 錨點都存在、檢查 id 不重複、印出每章字數統計。缺章時照樣組裝並在終端列出缺哪些。

階段設定表（區隔頁文字）：
0. 導讀：「先花三分鐘決定從哪裡開始。」
1. 看清楚：「這一區做完，你會有一張家庭資產負債表、一張現金流表，和一個寫了金額與年份的目標。」
2. 止血與撐住：「這一區做完，你會知道自己撐得過幾個月、哪筆債先還、哪些保障已經有了、哪些賠不起。」
3. 長大：「這一區做完，你會看懂報酬從哪裡來、費用怎麼吃掉它，並且把投資寫成一張自己的規則卡。」
4. 制度：「這一區做完，你會查出自己退休時已經有的、看懂稅怎麼算，並把租與買兩邊的帳攤開。」
5. 家庭與交棒：「這一區做完，你會有一張全家一頁資訊表，受益人與文件位置都填好。」
6. 守住：「這一區做完，你會有三個問題，先把多數陷阱篩掉。」
7. 例行化：「這一區做完，你會有一份一年的節奏表，知道每年幾月要重查什麼。」
