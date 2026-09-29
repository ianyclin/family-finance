# v7.0 預覽：CY——書封放全書第一頁、副標改句號、三代人插畫搬到第 1 節（作者 2026-09-29 早上；主線裁定）

作者：ChatGPT（Codex imagegen）做的書封「可用？」→ 主線建議無字版，作者改出 v3（無告示牌、副標句號、三個小孩）並說「也許這張可以放在最前面，其他的不用動」；副標標點作者問「冒號怪怪的」→ 主線改判句號；作者問「原本第一頁散步插圖還有需要嗎」→ 主線建議搬到第 1 節。基準：批 CX 之後的 HEAD。**只動下面列的；黃框、h2、lede、mark.key、p.decision、warning 不動。**

## 1. 書封（新插畫 00）
- 來源檔 `/private/tmp/claude-501/-Users-linyenchu-Cladue-Code/4d496a8a-af22-4959-894e-8aa2d8792c49/scratchpad/cover/d-0857-final.png`（1024×1536，sha256 04e767f0…；原檔在 `~/Documents/Codex/2026-09-17/new-chat/output/cover-plan-and-life/cover-family-five-period.png`）。轉成 `guide/illus/00-book-cover.webp`（照 CT 的做法：長邊不放大，品質與其他十張同；記錄尺寸與位元組數），`embed_illus.py` 不帶 --check 跑一次嵌入。
- 放在 `<header class="cover" id="top">` 的**第一個子元素**（eyebrow 之前）：
  `<figure class="illus book-cover" id="book-cover"><img data-illus="00-book-cover" alt="書封：一家五口從敞開的木門走向山湖邊的小路；門內桌上留著一張打勾的計畫紙、一支筆、一杯茶和一支朝下放的手機。" width="1024" height="1536" loading="eager"></figure>`（alt 先用 Read 看圖核對每個物件都在）。書封沒有圖說。
- 螢幕：置中、`max-width:min(100%,560px)`、圓角與陰影沿用 `.illus img`；375 寬時滿版；書封和 eyebrow 之間留一段距離（約 40px），讓書名頁像翻頁後的第二頁。
- 列印：書封自成第 1 頁：`@media print{figure.book-cover{break-after:page;margin:0;} figure.book-cover img{max-height:none;width:auto;height:calc(297mm - 32mm);max-width:100%;margin:0 auto;display:block}}`（A4 高減上下邊界 16mm×2；要是撐不滿或溢出到第 2 頁，改用 fitz 量過的實際值），CT 那條 `figure.illus img{max-height:55mm}` 不可以套到它（用更具體的選擇器覆蓋）。PDF 第 1 頁只有書封、第 2 頁從 eyebrow／h1 開始（fitz 驗）。書籤：書封沒有標題，不產書籤。
- 目錄、進度條（posmenu／posrail）不列書封。

## 2. 副標改句號
`<p class="subtitle">早點開始規劃，穩穩地投資：把現在的薪水，慢慢換成以後的選擇權。</p>` → `…穩穩地投資。把現在的薪水…`（只換那一個標點）。`<meta name="description"` 若含這句同改；`lite/index.html` 若由 build_lite 從這句產生也會跟著變（回報）。

## 3. 三代人插畫 04 從書名頁搬到第 1 節
- 刪掉 header 裡的 `<figure class="illus cover-illus">…04-time-for-life…</figure>`（整塊；批 CX 已把署名移到它上方，署名留著）。
- 第 1 節 `#ten`：在含「陪小孩長大、陪父母」那一項的 `ol.checklist[data-lite-alt="ch1-six"]` 的 `</ol>` **之後**（不進 li、不進 data-lite 範圍）插入
  `<figure class="illus"><img data-illus="04-time-for-life" alt="（沿用原 alt）" width="1400" height="933" loading="lazy"><figcaption>有些體驗有期限：陪小孩長大、陪父母，過了就買不回來。</figcaption></figure>`（圖說是第 1 節那句的截短，不新增字；`.cover-art` class 拿掉，樣式同其他九張）。第 1 節的 lite 短稿指紋若因此變動，只 `--stamp` 不改本體並回報。
- `embed_illus.py --check`：11 張。

## 4. 第 28 節那句
「插畫：封面圖與九幅章節插畫（第 8 節兩幅一組）由 AI 影像模型生成（OpenAI 的圖像生成工具，2026-09-28）…」→「插畫：書封、封面圖與九幅章節插畫（第 8 節兩幅一組）由 AI 影像模型生成（OpenAI 的圖像生成工具，2026-09-28、書封 09-29）…」；後半「構圖與修改由作者決定，圖說由 AI 起草、作者核定；插畫只做比喻與休息，不承載任何數字或規則。」不動。**書封上有字**（書名、副標、署名），「不承載任何數字或規則」仍成立；不用改。

## 檢查
全套（numbers 兩基準 round59 LOST 0；anchors；budget——ten 節多一句圖說小字、cover 少 0（書封無字）、methods +N，照實測寫 `_comment_cy`；planstep；xrefs；guidetools check；兩支測試；essay_charts --guide ×2 0 ⚠；calc_core；layout（書封在 375／1024 不溢出）；build_lite 兩次等冪；lite_sentinels；embed_illus --check 11 張）；PDF：p1 只有書封（fitz：文字 0 字、圖 1 張、圖佔頁面高度 ≥ 85%）、p2 從書名頁開始、總頁數、書籤數、大小 ≤ 12MiB（書封 webp 不可以超過 600KB，超過就降品質）；375／1024 各截圖：書封→書名頁、第 1 節那張圖。不 commit。

## 補（作者 2026-09-29 提醒「檢查是否有其他地方重複使用這張圖」，主線已查）
- `04-time-for-life` 全倉庫只在 `guide/index.html` 一處（書名頁），`lite/`、`tools/`、`docs/` 沒有引用；`output/*.html` 是產生檔會跟著變。搬到第 1 節後，全書仍只出現一次（`embed_illus --check` 的 11 張各一）。
- 孤兒樣式：`figure.illus img.cover-art{max-height:44vh;…}`（L166）搬圖後沒有元素使用——刪掉，書封用自己的 `figure.book-cover img` 規則；`lite/index.html` 那份由 build_lite 從指南 CSS 複製，會自動跟著。
