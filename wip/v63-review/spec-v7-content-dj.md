# v7.0：批 DJ —— 第 24 節「要不要自提」（正式規格；2026-10-11）

依據：作者 2026-10-11 問勞退自提；兩位裁判查證（勞保局、勞退條例 14/23/24/29、所得稅法 4-1/5/14/15/100、所得基本稅額條例 12/13、財政部 115 年度公告、勞動基金運用局表 2、盈虧分配辦法第 8、9 條）；作者拍板：固定 60 歲一次領比、熱圖進書、折線進工具收合、工具取代 Google 試算表、「級距數字減 5」粗規則加但書進書。**設計與文字已由作者核定，照做、逐字。**記憶：memory/laotui-self-contribution.md。本檔取代草稿 `spec-v7-content-dj-draft.md`（已刪）。

不在本批：`tools/laotui/`（試算工具）與 `tools/v7_g13_laotui.py` 的路徑整理由另一個代理同時進行，本批不動，只 import `v7_g13_laotui` 的 `compute()`／`chart()`／`CAPTION`。工具發布成 Artifact 不在本批。

## A. 第 24 節既有句子改字（guide/index.html，先 grep 原句，一字不差才改）

1. 卡 `#pension` 勞退新制那條：「要不要自提，比兩件事：現在少繳的稅（看你的<a class="term" href="#g-bracket" …>級距</a>），對上錢鎖到 60 歲。」→「要不要自提，看四件事：現在少繳的稅（看你的<a class="term" href="#g-bracket" …>級距</a>）、這筆錢本來會拿去做什麼、離 60 歲還有幾年、打算怎麼領；下一張卡有整理。」（term 連結保留原樣。）
2. 同條「你可以再自提最多 6%」→「你可以再自提最多 6%（月薪上限 15 萬，所以每月最多 9,000 元）」。
3. 「想深入」摺疊「勞退基金的保證收益、自提的稅怎麼算」：「少繳的稅是延後不是免掉：60 歲領出時算退職所得，落在所得稅法第 14 條第九類的免稅額度內才不用再繳。」→「60 歲領出時算退職所得，雇主提的和自提的合在一起算：一次領每年資 20.6 萬內（115 年度）、按月領每年 89.4 萬內不用繳，超過才課；多數人實際上不用再繳。」
4. 同段：「基金收益保證不低於兩年期定存利率，不足由國庫補。」→「請領時，累積收益若低於用二年期定存利率（單利）算的收益，由國庫補足；中間某一年帳上可以是負的（2022 年 −6.67%）。」

**實際**：四句原句全書各只出現一次，與規格逐字相同，全部照改。A4 的原句在段中，前面接「自提的報酬跟著勞退基金走；」，該前半句保留，所以改後是「自提的報酬跟著勞退基金走；請領時，…由國庫補足。中間某一年…」（A4 規格原文是「；」，主線刻意改成「。」：一句兩個分號太碎）。

## B. 新卡（緊接在 `#pension` 卡之後、`#pension-lump` 卡之前）

```
<div class="data-card" id="pension-self"><h4>要不要自提，先看你是哪種人</h4><span class="later">開始工作、公司問你要不要自提那一天再看</span>
<p>自提是用今年少繳的稅，換一筆鎖到 60 歲、跟著勞退基金長的錢。少繳的稅是確定的，鎖住的代價是確定的，少賺的報酬差是不確定的。</p>
<ul>
<li>級距 5%、12%，離 60 歲還有二十年以上，錢本來會照計畫投指數：先不自提。</li>
<li>級距 20% 以上，離 60 歲十五年以內：自提多半划算；級距 30% 以上，二十五年以內都算。</li>
<li>本來只會放定存，或知道自己大跌會賣的人：自提。它贏定存、有保底，而且拿不出來。</li>
<li>不管哪種人，只拿 60 歲前確定用不到的錢自提；年資滿 15 年選按月領，多半不用再繳稅。</li>
</ul>
<p><strong>粗規則：離 60 歲的年數，不超過你的級距數字減 5，自提多半划算。</strong>（12% 級距七年內、20% 十五年內、30% 二十五年內、40% 幾乎都是。）</p>
<p class="small">這是用勞退 4.65%（2006–2025 年化）、自己投台股 ETF 年化 7.5%、每月提薪水的 6%、25 歲開始工作、60 歲一次領算的。改用不配息 ETF 的人，年數再扣 5 年；自己投的報酬若高於 7.5%，年數也要再縮；勞退報酬若只有最差十年的 2.1%，這條規則不適用，直接看線上工具。</p>
<p>另外一件算不出來的事：想要一份自己和別人都動不到的錢，自提是少數做得到的工具，代價就是報酬差，願不願意付是你的事。</p>
<p>兩個例子：小安月薪 4 萬，級距 5%，自提 6% 是每月 2,400 元，一年最多少繳 1,440 元的稅。另一位月薪 15 萬、年終一個月以上，級距 20%，自提到上限 9,000 元，一年最多少繳 21,600 元。小安離 60 歲還有三十五年，照粗規則先不自提；月薪 15 萬那位若離 60 歲十年，在十五年內，自提多半划算。</p>
<figure class="chart" data-chart="laotui-heatmap"></figure>
<p>要不要補繳稅，會差多少：圖上已經把 60 歲一次領要補的稅算進去。5% 級距不受影響，12% 最多差 3 個百分點；20% 以上的人，完全不用補最多再好幾個百分點，免稅額和級距若一直不調，存越久差越多，最多差兩成。會因此改變輸贏的，只有本來領先不到一成的格子，和 40% 級距存 30 年以上那幾格。誰要補、每一格差多少，<a href="https://claude.ai/artifact/PF21JSy8748skZ8wieZELz" target="_blank" rel="noopener">線上工具</a>的「補繳的稅差多少」有圖。改按月領多半零稅，但錢留在基金裡，用的是基金的報酬。</p>
</div>
```

data-card 的標籤、class、`<span class="later">` 比照同節既有卡；p.small 是全書既有小字寫法；「線上工具」用正文外連的既有寫法（`<a href target="_blank" rel="noopener">`，不用 source-link）。

**實際（與上面的差異只有一處）**：「小安」「陳大哥」四處包 `<span class="pn">…</span>`（全書虛構人物名的體例，批 CR 補過漏網的；字一個沒改）。去掉 pn 標籤後與上面逐字元相同（腳本比對 True）。

## C. 熱圖登記

`tools/essay_charts.py`：照其他「只在指南」圖的寫法，加 module-level 函式並登記：
```python
def laotui_heatmap():
    import v7_g13_laotui as _g13
    return _g13.chart(_g13.compute())
...
    funcs["laotui-heatmap"] = laotui_heatmap          # 只在指南
```
圖說：指南是空殼、沒有 figcaption，`build()` 用 `chart()` 回傳的 `caption`（＝`v7_g13_laotui.CAPTION`）；`p.note` 是 v7_g13 的 `FLIP_NOTE`。跑 `python3 tools/essay_charts.py --guide`：換了 31 張圖，git diff 只有這一張由空殼變實圖，其他 30 張逐字不變；腳本印的「laotui-heatmap 的圖下說明和指南原本的不一樣（指南原本：沒有）」是空殼第一次填入的正常訊息。

## D. 「去哪查」（#toolbox「退休與保險」）

加第 5 筆（放在該卡最後，金管會保險局之後），summary 4→5；全書沒有總筆數宣告句，不用同步：
`<a class="source-link" href="https://claude.ai/artifact/PF21JSy8748skZ8wieZELz" target="_blank" rel="noopener"><span>本書附：要不要自提試算工具</span><span class="source-note">勞退報酬 × 自己投的報酬，五個級距、離 60 歲年數的熱圖與翻盤年</span></a>`

## E. 第 24 節來源卡（直接來源 32→36 筆，加在卡末）

1. https://www.mof.gov.tw/singlehtml/384fb3077bb349ea973e7fc6f13b6974?cntId=34b463dc8f1b49f29d440d92a6fd5139 — 財政部：115 年度綜合所得稅免稅額、扣除額、課稅級距與退職所得定額免稅金額 — 「一次領每年資 20.6 萬免稅、41.4 萬半數；按月領 89.4 萬；級距」
2. https://www.blf.gov.tw/media/ch3lc5dv/2-新制勞工退休基金經營概況.pdf — 勞動部勞動基金運用局：新制勞工退休基金經營概況（表 2） — 「2006–2025 年化 4.65%；2022 年 −6.67%」
3. https://www.bli.gov.tw/0108501.html — 勞保局：個人自願提繳退休金 — 「自提上限 6%、月薪上限 15 萬」
4. https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=N0030030 — 勞工退休金條例退休基金監理及盈虧分配辦法 — 「第 8、9 條：保證收益怎麼算、國庫補足」

URL 對照 scratchpad `laotui/tool6.html` 頁尾：1–3 三個網址與 tool6 逐字相同；第 4 筆 tool6 沒有，用本單的。全書 19 張來源卡宣告數與 source-link 實數全部相符。

## F. 「想深入：提領率與 25 倍怎麼算」摺疊

summary 下那句「…自提的稅、三步的算法…」不動；A3、A4 改完後摺疊裡講自提的稅那段與正文、新卡有無矛盾，列在交班與回報，不自己改。

## G. 檢查

numbers（兩基準；新開 `numbers-allow-round61.json`＝round60 的 706 條＋1 條 lifecycle「14」）、anchors、planstep、xrefs、budget（照實測調，`_comment_dj`）、guidetools check、test_guidetools／test_v7_check（本機 python3 沒有 pytest 模組，照交班慣例以腳本直接跑）、calc_core、embed_illus --check、v7_g12_route_maps、`v7_g13_laotui.py --check-proto <scratchpad>/laotui/tool6-data.json`、v7_layout_check、build_lite、lite_sentinels。截圖 `wip/v63-review/dj-1024.png`、`dj-375.png`、`dj-dark-1024.png`、`dj-dark-375.png`（只截 #pension 與新卡；用指南原 `<style>` 的摘錄頁，深色把 `@media(prefers-color-scheme:dark)` 改成 `@media all`；375 用 iframe 量寬，避開 headless 最小視窗寬）。

## H. 文件

本檔；交班檔尾「批 DJ」＋「立場句清單」加新卡四條條件句、粗規則句、第五件事句；`changes-for-author-v7.md`「一之一百一十二」。

## 預算（實測）

lifecycle 主線 5185→5951（+766：A1＋A2 +48、新卡 +718）、小字 726→971（+245：新卡 p.small 110＋熱圖 figcaption 106＋p.note 29）、folded 3531→3595（A3、A4 +64）；全書主線 62621→63387、看得到的字 69963→70974。budget：lifecycle 5187→5953、lifecycle 小字放行 726→971、`_total_max` 63389、`_visible_total_max` 70976。

**裁判後最新（2026-10-11 深夜）**：lifecycle 主線實測 5995、小字 998、全書主線 63431、看得到的字 71045。budget：lifecycle 5997、lifecycle 小字放行 998、`_total_max` 63433、`_visible_total_max` 71047。中途值（5982／971／63418／71005）已作廢。
