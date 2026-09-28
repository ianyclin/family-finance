# 批 CN 驗證員報告（judge／opus xhigh，2026-09-28；唯讀）

總判：機械項目 A1、A3–A9、B10 全部落地；A2 部分完成（3／6，另 3 處規格本身做不到）；沒有越界改字；budget 紅（+23，詞彙表交割戶那句）。

## 越界檢查
含空白的 word-diff 共 240 個字元級改動：SVG 61 個（「-」→「−」，改在 tools/essay_charts.py 的 minus() 與刻度 "{:,} 萬"，記憶體內重跑 do_guide 與現檔逐字相同），其餘 179 個每一條都對得到 A1–A9 或 B10。刪字都是規格點名的。黃框 26、h2 35、lede 34、warning 6、p.decision 27、p.explain 28、.key 111 逐 byte 相同。立場句清單 12 主題只碰到《舉債致富》那句（見下）。「不動」清單：xref 文字只多 3 個；「×」95、「 × 」57、「＝」58、「 ＝ 」10 不變；本節／這一節／這一頁／本文／本指南計數不變；warning 開頭、span.later 13、methods 無 p.decision、工作表 h1 不變。

## 發現（依嚴重度）
1. budget FAILED：_total_max 59603／59580；1ffde47 是 OK。逐節 glossary +41、toolbox −12、start −6、s4 −2、s11 +3、firstmonth −1。→ 主線處置：上限照實測調，寫 _comment_cn。
2. A2 未做的 3 處（L2698、L3750×2）都在 a.source-link > span.source-note 內，補 xref 成 a 套 a；全書 source-link 內 xref 為 0，規格援引的先例不成立。→ 不做，記處置。
3. L4151「這本書的立場相近但更保守」字面合規格（與 47c8047 只差「本書」→「這本書」），但位置緊接 Anderson 書的描述，易被讀成指《舉債致富》。→ 主線改「本文」。
4. g-circle 7 個 title 對齊 dd 第一句後少了「圈外」那句（dd 第二句仍有）。→ 維持。
5. cases 5 個 h5→h4 後層級倒掛：卡片標題 h4 → h5「和小安差在哪」→ details 內 h4；在 .data-card 內吃 1.06rem，比旁邊 h5 大。→ 主線退回 h5。
6. s7 卡與 s5 第二個 grid 各只 1 筆，桌機佔半欄。→ 維持。
7. methods 卡兩筆統一後由中文變英文標題；Ben Felix 尾巴「（YouTube）（2022-12-22）」括號相連。→ 前者維持，後者合併。
8. 刪掉的 165 重複筆帶唯一的通話費備註；正文 4 句不涉通話費。→ 維持。

## 逐條落地表
A1 完成（9 張補 grid：start 2、s2 6、s5 36+1 分兩個 grid、s6 3、s7 1、s8 3、s11 6、annual 2、withdraw 6；s12 grid 內 17→18；27 張宣告數＝實際數；全書 240 筆）。A2 部分（L843 改在 v63_g04_fee_gap.py raw=True、L3161 改在 v63_g01_plan_flow.py 並給 figure() 加 sub_html、L2874 直接改）。A3 完成（guide「□ 」19→0；lite/index.html 10→0；plan-starter 7、ch4-drill 3）。A4 完成（「＿」長度分佈 {1:100,2:19,3:2,4:22,6:4}→{1:99,2:20,4:28}）。A5 完成。A6 完成（「展開」開頭 summary 0、「與版權」0）。A7 完成（U+2212 94→155；千分位 6；「～」「至」→「到」3）。A8 完成（C 型 8＋D 型 1 改 B 型；「(年)：」7→0；L3137×4；13 組同網址統一，剩 UBS、SPIVA 兩組不在規格內；L3750 句號刪；costs 18→17）。A9 完成（g-scope 7、g-circle 7 含 L3650 對齊；交割戶 dt 與 dd 逐字合規格）。B10 完成（h3 拆兩個 pn；5 個 h5→h4〔後由主線退回〕；fm-three 改 h4、冒號與 br 拿掉）。

## 半成品／工作表
標籤開關全部平衡、a 套 a 為 0、詞彙表 title 無新舊混雜；guidetools check OK。lite/index.html 4 行＝2 行替換（plan-starter、ch4-drill 輸出），只有 10 個「□ 」；app-a-checklist 只有 note 與 stamp；8 個 src 的 sha256 用 build_lite --fingerprint 重算相符。

## 驗證員自己跑過的
xrefs OK（514）、anchors 對 1ffde47 OK、planstep OK、numbers（round57）兩基準 LOST 0、calc_core 封鎖寫檔 exec 全過且引用缺漏 []、money_age TOTAL OK。沒跑（會寫檔）：build_lite 全建、layout、兩支測試——由 runner 另跑，全綠。沒開瀏覽器看 9 張 grid 兩欄與 cases h4 外觀。
