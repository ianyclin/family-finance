# v7.0 預覽：CN——格式一致性（格式檢查員 2026-09-28 掃十類後的機械修正；主線裁定）

依據 `wip/v63-review/format-audit-2026-09-28.md`（格式檢查員報告全文）。**只動標點、標記、排版、標題前綴、來源卡的標題／備註格式；不動任何句子的意思，不寫新句（詞彙表「交割戶」那一句除外，內容取自第 10 節既有 tooltip）。黃框、h2、lede 不動。** 行號以 `1ffde47` 為準（報告的行號），用特徵字串定位；每處替換前 assert。凡是動到帶 `data-lite` 的行或工作表短稿，改完看 build_lite 哨兵、必要時 `--stamp`；改到 SVG 的一律改產圖腳本再 `essay_charts.py --guide`，不直接改 guide 裡的 SVG。

## A. 讀者看得到
1. **來源卡補 `div.sources-grid`**（9 張：start L354、s2 L754、s5 L2698、s6 L2793、s7 L2863、s8 L2930、s11 L3436、annual L3848、withdraw L4079）：把 `<details class="source-card">` 內、summary 之後的所有 `a.source-link` 包進一個 `<div class="sources-grid">…</div>`（照其他 15 張的結構）；s12 L3599 落在 grid 外的那一筆移進 grid。宣告數不變。
2. **純文字「第 N 節」補 xref**：L843 s3「第 4 節」→`第 <a class="xref" href="#s1">4</a> 節`；L2874 s8「第 8 節」→`#s5`；L3161 s11 圖說「第 14 節計畫表」→`第 <a class="xref" href="#s11">14</a> 節計畫表`；L2698 來源註「第 10 節」→`#s7`；L3750 來源註「第 17 節」×2→`#s13`。（圖說與來源註裡放 xref 全書已有先例；若 `xrefs` 哨兵對來源卡內的 xref 有意見，回報。）
3. **「□」後不空格**：主文件 19 處（L356 ×2、L2795 ×2、L2933 ×3、L3156 ×7、L3346 ×3、L3349 ×2）「□ 」→「□」；工作表 `lite/alt/*.html` 對應的 10 處（L248 ×7、L255 ×3 在 lite/index.html，找回對應短稿）同改，補 note、stamp、仍 6 頁。
4. **「＿」長度**：L355、L356 ×2、L1588 的 6 格「＿＿＿＿＿＿」→4 格「＿＿＿＿」；L3346「先等＿天」→「先等＿＿天」；L3346「誠實寫：＿＿＿」與「＿＿＿（例：」的 3 格→4 格。
5. **第 27 節書目**：版次移到出版社年份後——「《綠角的基金8堂課》2016 補課增修版，綠角，經濟日報 2016。」→「《綠角的基金8堂課》綠角，經濟日報 2016 補課增修版。」；「《鄉民的提早退休計畫》觀念版，Bogleheads 三位作者，樂金 2021。」→「《鄉民的提早退休計畫》Bogleheads 三位作者，樂金 2021 觀念版。」；「《投資金律》新版，William Bernstein，臉譜 2024。」→「《投資金律》William Bernstein，臉譜 2024 新版。」；「《致富心態》Morgan Housel，天下文化 2020（2026 有增訂版）。」→「《致富心態》Morgan Housel，天下文化 2020，2026 增訂版。」。「《一年投資5分鐘》陳逸朴（小資YP）」→「小資YP（陳逸朴）」（pn 照包）。Podcast 條目改成和另外兩段同型：`<li><strong><span class="pn">老人</span></strong>：<a …>《人生不難 Life Lab》</a>。中文 Podcast；…</li>`。「退休」段「《退休研究室》」→「退休研究室」（其他站名都沒書名號）。「證券營業員。書見上。」→「證券營業員；書見上。」。自稱：L4151「本書的立場相近但更保守」→「這本書的立場相近但更保守」；L4149「這篇只夠帶你開始」→「這本書只夠帶你開始」；L4138 詞彙表「這篇」→「這本書」。「小資YP」3 處包 `span.pn`。
6. **摺疊標題**：L3355「展開小安填好的全表」→「想深入：小安填好的全表」；L3501「展開陳大哥怎麼算出四成…」→「想深入：陳大哥怎麼算出四成…」（後半照原文）。圖表資料 summary 的「與」改「和」：L2779「樣本、官方原圖與版權」→「樣本、官方原圖和版權」；L2927「口徑、官方原圖與版權」→「口徑、官方原圖和版權」。
7. **SVG**：61 個連字號負號「-」→「−」（s5 L1603–1801、L2326–2437 那兩張圖）、6 個「1000 萬」「1500 萬」→「1,000 萬」「1,500 萬」（s2 L540、L569；s7 L2810、L2812、L2832、L2834）——找到產這幾張圖的腳本（`tools/essay_charts.py`、`tools/v7_g*.py`、`tools/v63_g*.py`）改格式函式，跑 `--guide`，確認第二次 0 ⚠。日期區間：L2863 s7、L2927 s8 的「～」→「到」；L4158 methods「至」→「到」。
8. **來源卡標題與備註**：日期格式 C／D 改成 B「機構：標題（YYYY-MM-DD）」——L2698 s5 ×7「…，YYYY 年 M 月 D 日」、L3603「FAPA…」、L4067「Ben Felix, …, 2022-12-22」→尾巴改「（2022-12-22）」；「Author (年)：Title」→「Author (年), Title」7 筆（L3555、L4067 ×4、L4079 ×2）；L3137 s10 ×4 半形括號內的中文改全形「（1995；連結為 1993 年 NBER 工作論文版）」；同一網址不同標題 12 組統一成較完整的那個（元大 0050、富邦 006208、Vanguard VT、J.P. Morgan Guide to Retirement、Fed History 1929、證交所交易制度、Schwab、Vanguard cost averaging、e添富收益分配、Barber 2014、勞退條例第 7 條、證期局詐騙提醒、投信投顧公會），逐組列出改前改後；L3750 sidepaths 備註多餘句號刪；L3821 costs 重複的 165 警政署那筆刪一筆（宣告數 −1）。
9. **詞彙表**：g-scope、g-circle 的所有 `a.term` title 改成和 dd 第一句逐字相同（列出改前改後）；L3650 那個較短的 g-circle title 一併對齊。「交割戶」：詞彙表 `dt id="g-settle"`「交割、T+2」→「交割、T+2、交割戶」，dd 句末補「交割戶就是綁在證券戶上的銀行帳戶，買股票從這裡扣錢、賣股票的錢匯進這裡。」（取自第 10 節 tooltip，不是新事實）。

## B. 原始碼層
10. L3476 cases h3「小芸與阿哲」拆成兩個 `span.pn`；cases 摺疊內 5 個 h5（L3455、L3484、L3490、L3502、L3510）→h4；L3788 firstmonth 卡片的 `<strong>` 標題→`<h4>`。

## 不動（作者定或刻意）
指路用數字或節名（作者拍板中）；工作表怎麼稱呼主文件與節號國字（作者拍板中）；「×／＝」空格（會動到驗算腳本釘住的句子）；「本節／這一節／這一頁」；warning 開頭標點；`span.later` 兩型；methods 沒有 p.decision；工作表第一張正面的 h1。

## 檢查
全套（budget；numbers 兩基準 `_baseline_v631.html` 與 `1ffde47`，掉 token 開 round57 寫理由——來源標題改格式會掉日期 token；anchors；xrefs；planstep；guidetools check；兩支測試；calc_core 引用缺漏 []；essay_charts 兩次；layout；money_age；build_lite 6 頁）；來源卡 27 張宣告數＝實際數（costs −1）。桌機 1024px 看 9 張補了 grid 的來源卡是兩欄。不 commit。

## 處置（主線 2026-09-28，驗收後）
- A2 只做 3 處（L843、L2874、L3161）。L2698「第 10 節」、L3750「第 17 節」×2 不做：三處都在 `a.source-link > span.source-note` 裡，補 xref 會變成 a 套 a，HTML 不允許，瀏覽器會切斷外層來源連結。規格說「來源註裡放 xref 全書已有先例」不成立——有 xref 的 why 卡是散文卡、沒有 source-link。
- A5 自稱：L4151「本書」→「這本書」會被讀成指《舉債致富》本身（緊接在描述 Anderson 那句之後），改為全書主流自稱「本文的立場相近但更保守」。此句在立場句清單「借錢投資」那條，其餘字與 47c8047 逐 byte 相同。
- B10 cases 的 5 個 h5→h4 退回 h5：那 5 個小標在 data-card 裡的 details 內，卡裡 h4 是卡片標題層級（.data-card h4 1.06rem），改 h4 會比同層的 h5「和小安差在哪」大、和卡片標題同級；s5、lifecycle 的先例不在 data-card 裡。firstmonth 的 strong→h4 維持。
- A8 Ben Felix 那筆統一標題後尾巴「（YouTube）（2022-12-22）」兩組括號相連，合成「（YouTube，2022-12-22）」。
- budget：_total_max 59,580→59,602（詞彙表交割戶那句 +41、其他 −19，含驗收後「本書」→「本文」−1），寫入 `_comment_cn`；numbers 用 `numbers-allow-round57.json` 對兩基準 LOST 0。
- 維持現狀不改：s7 與 s5 第二個 grid 只有一筆、桌機佔半欄（結構一致優先）；methods 卡「Vanguard 2023：Cost averaging（官方 PDF）」與「Charles Schwab：Does Market Timing Work?」是統一成全書已有的較完整標題；g-circle 滑過說明對齊 dd 第一句後少了「圈外」那句（dd 第二句仍有）；被刪的 165 重複筆帶的通話費備註，正文 4 句提到 165 都不涉通話費。
- 驗證員報告：`wip/v63-review/judge-cn.md`。
