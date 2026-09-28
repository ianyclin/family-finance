# v7.0 預覽：CT——八張繪本插畫內嵌＋封面圖（主線 2026-09-28 晚定；作者裁定「都照你建議，開工」）

來源：作者用 ChatGPT imagegen 生成的八張插畫（`/Users/linyenchu/Documents/Codex/2026-09-17/new-chat/output/finance-picturebook-latest/*.png`，1536×1024），已由 runner 縮成 WebP 寬 1400、品質 80，放在 scratchpad `illus/NN-name.webp`（合計 1.12MB）。主線判斷：三張幫理解（罐子、蛋糕、晴雨）、五張讓眼睛休息；價值在「讀得下去」，不在「讀得懂」。

## 一、放哪（每節最多一張；第 14 節計畫表區不放）
| 圖 | 檔 | 位置 | 圖說（作者可改；不寫數字、不寫規則） | alt |
|---|---|---|---|---|
| 1 罐子 | 01-money-by-purpose | 第 2 節 start：五項安全順序清單**之前**、白話版之後 | 急用的錢、近期要用的錢、長期不用的錢，各有自己的位置。 | 三個罐子分別貼著 OK 繃、月曆、嫩芽，一隻手把硬幣放進第一個 |
| 7 拼布 | 07-small-steps-quilt | 第 5 節 s2：「前幾年像沒在長」那段之後（十桶金摺疊之前） | 前幾年，先看自己有沒有照計畫投入。許多改變，是一點一點累積的。 | 一個人坐在沙發上縫拼布被 |
| 6 步調 | 06-own-pace | 第 7 節 s4：「分散的代價」那段附近（黃線之後） | 別人走得快，不代表你要換路。照自己的用途和步調走。 | 一個人沿河邊小路散步，遠處有人騎單車 |
| 3 晴雨 | 03-calm-plan-rain | 第 8 節 s5：資料卡第 6 條「想打開 app 的時候，先打開你的計畫」附近（卡之後） | 把重要決定留在平靜的時候。慌張時，先拿出原本寫好的計畫。 | 左邊晴天一個人在桌前畫地圖，右邊雨天同一個人撐傘照著地圖走 |
| 2 蛋糕 | 02-dividend-cake | 第 11 節 s8：黃線「高配息不等於高總報酬」那段之後 | 配息像把蛋糕切一片拿出來。手上多了一片，原來的蛋糕就少了一片；切開這個動作沒有讓蛋糕變大。 | 一個切成六片的蛋糕，右邊同一個蛋糕少了一片，那一片在旁邊的小盤子上 |
| 5 停一下 | 05-pause-before-action | 第 13 節 s10：冷卻期那段之前或之後 | 想動手的念頭來了，先停一下，再看原本寫好的規則。 | 一個人端著杯子看窗外，手放在桌上的手機上 |
| 8 一起看 | 08-shared-plan-v2 | 第 17 節 s13：「伴侶不同意」那題附近 | 一起談這筆錢要做什麼、跌了怎麼辦，把兩個人的想法寫進計畫。 | 兩個人在餐桌前一起看同一張計畫 |
| 4 散步 | 04-time-for-life | **封面**：書名與副標之後、「我只有十分鐘」等按鈕之前；無圖說 | （無） | 三代人在河邊小路散步 |
- 圖說裡不給人物取名（不是小安）。
- 圖說是可見文字，算該節小字；照實測調 `_visible_small_overrides` 與總量，`_comment_ct`。

## 二、檔案與標記
- 八張 WebP 進 repo：`guide/illus/NN-name.webp`（追蹤）。新腳本 `tools/embed_illus.py`：讀 `guide/illus/*.webp` 轉 base64，替換 `guide/index.html` 裡 `<img data-illus="NN-name" src="…">` 的 src（等冪：重跑結果不變）；HTML 裡保留 `data-illus` 屬性當鍵。這樣圖有單一來源，改圖只重跑腳本。
- 標記：`<figure class="illus"><img data-illus="…" src="data:image/webp;base64,…" alt="…" width="1400" height="933" loading="lazy" decoding="async"><figcaption>…</figcaption></figure>`。**不用** `class="chart"`、不加 `data-chart`，避免被 28 張圖表的哨兵、`essay_charts` 替換邏輯與量測腳本認到；先看 `guidetools.py check`／`test_guidetools.py`／`build_lite.py` 對 `<figure>`／`<img>` 有沒有計數或抽取，必要時在 `to_text` 排除 `figure.illus`（figcaption 要留給讀者，但工作表短稿不抽）。
- CSS：`figure.illus{margin:1.4em 0}figure.illus img{display:block;width:100%;height:auto;border-radius:10px}figure.illus figcaption{…用既有 figcaption 樣式…}`；封面圖 `img.cover-art{max-height:44vh;object-fit:cover}`（手機不超過半屏）；列印：`figure.illus img{max-height:70mm;width:auto;margin:0 auto}`、封面圖 `max-height:90mm`，避免 PDF 暴增。
- 深色模式：圖不反轉；可加 `filter:brightness(.92)` 讓米白底不刺眼（builder 看效果決定）。

## 三、誠實標示
第 28 節 methods「資料口徑與來源」加一段（主線文字）：「插畫：封面圖與八張章節插畫由 AI 影像模型生成（ChatGPT，2026-09-28），構圖、修改與圖說由作者決定；插畫只做比喻與休息，不承載任何數字或規則。」

## 四、檢查
essay_charts 兩次（不能碰到 figure.illus；記憶體模擬也要）、budget 照實測（`_comment_ct`）、numbers 兩基準（round58；圖說沒有數字）、anchors、xrefs、planstep、guidetools check、兩支測試、calc_core、layout（375／1024 無溢出、圖不撐寬）、money_age、build_lite（工作表 6 頁不變；完整版 PDF 頁數與檔案大小前後回報；插畫在 PDF 裡要出現、封面圖要出現）；`git diff --stat` 裡 guide/index.html 的增量大部分是 base64（回報字元數）；線上 Artifact 上限 16MB，發布前確認 `output/guide.html` 大小。
`tools/embed_illus.py` 加一個 `--check` 模式：確認每個 `data-illus` 的 src 與檔案一致（哨兵），並把它加進交班檔的檢查清單。

## 五、不做
不做資訊圖（另批 CU）；不動任何內文句子；封面版面不換成 ChatGPT 的 A4 樣稿。

## 六、封面與前後頁（作者 2026-09-28 晚拍板，併入 CT）
1. **封面放筆名**：副標／封面兩段話之下、按鈕之上，小字一行「指數三寶飯｜家庭理財陪跑」（用既有 `span.pn` 包筆名；不放本名）。與封面圖（第 4 張）的相對位置：書名 → 副標 → 封面兩段話 → 封面圖 → 筆名 → 按鈕；手機上按鈕不超過第二屏。
2. **「後記：初衷與感謝」前兩段搬到前面**：原第一段「寫這份指南的初衷很單純…」與第二段「這份指南只是開始…我推薦的書放在第 27 節。」**一字不改**搬到封面按鈕之後、「怎麼讀這本書」之前，加標題「為什麼寫這本書」（作者 2026-09-28 深夜拍板；主線理由：全書節名習慣用讀者會問的話）（h3 或既有的封面小標樣式，看封面現有結構）；第 27 節的 xref 保留。書尾只留第三段（感謝）與署名，標題改「後記：感謝」。搬動後 anchors／xrefs／budget（cover 主線會增加，照實測 `_comment_ct`；methods 減少）照跑；`to_text` 抽取順序改變會讓 lite/work 文字檔變動，屬預期。驗證員要逐字比對搬前搬後兩段相同。
