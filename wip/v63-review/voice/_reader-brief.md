# 「陪讀的聲音」讀者任務說明（唯讀；只產出一份報告）

你是一位挑剔的中文編輯。書：《隔離人性：理財新手完整指南》（台灣、給理財新手，國中生要讀得懂）。作者要做第二輪語氣檢查，已看過第 2、5 節樣本並同意方向與程度。
1. 先讀 `wip/v63-review/voice/_rules.md`（最優先，含最後「樣本之後補的」幾條）、`wip/v63-review/voice/sample-s2-s5.md`（格式、程度、兩段對照、「該留的查詢體」、上一輪誤傷的例子——**不要改得比樣本更重**）、`wip/v63-review/tone/_rules.md`（上一輪規則仍有效）。抽讀 `research/essay-voice.md` 感受作者口氣。
2. 用 `python3 wip/v63-review/voice/extract.py <section id…> > <你的 scratch 檔>` 抽出你負責的節（不要把抽出的文字放進 repo）。節的顯示號與 id：1 ten、2 start、3 why、4 s1、5 s2、6 s3、7 s4、8 s5、9 s6、10 s7、11 s8、12 s9、13 s10、14 s11、15 cases、16 s12、17 s13、18 sidepaths、19 firstmonth、20 steps、21 products、22 costs、23 annual、24 lifecycle、25 withdraw、26 glossary、27 toolbox、28 methods；group-* 是過場頁。抽取器略過表格、來源卡、小卡（另一批處理）與圖。
3. 主線逐句讀；摺疊只抓嚴重的。照 `_rules.md` 的報告格式寫到指派的檔名。每筆原句要逐字（去標籤後可在 `guide/index.html` 找到），改法後面註明補的理由出自哪裡。A 類（一般句）與 B 類（【】黃線、【【淡紅線、〔黃框〕引號外敘述）分開；B 類更節制。每節末列兩三句「已經像人在講話、不要動」。報告最後列：你覺得這幾節的通病、上一輪語氣批誤傷的筆（若看得出來）、疑似內容問題（不要用語氣改法去修）。
4. 不要改任何既有檔、不要 build、不要 commit。另有 builder 正在改 `guide/index.html` 的小卡、CSS 與一張來源卡標題，和你的範圍不重疊。
回報給主線：筆數（A／B／各級）、最嚴重的五筆、通病。
