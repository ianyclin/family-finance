# v7.0 預覽：CU——兩張指路圖（主線 2026-09-28 晚定；作者裁定「都照你建議，開工」）

原則：圖是產線內的 SVG（腳本產、桌機／手機兩版、重疊量測、字從書裡同一句取並由哨兵比對），不是產線外的圖。**圖只指路，不下規則；圖上每一句都必須逐字存在於 guide 內文**（腳本 compute() 讀 guide/index.html 斷言每個標籤字串存在；缺就 raise）。ChatGPT 的六站漏「先走完安全順序」與「開戶」，照書畫。急救卡對「借錢買的」只有「今天正在跌」一條路，圖不補路。

## 圖一：「跌了，先看哪裡」（data-chart="panic-map"）
- 放：第 14 節急救卡 `#plan-panic`「跌的那一天先看這裡」卡**開頭**（卡的三件事之前）；group-situations「正在跌、很慌」那格文字不動（已指到急救卡）。
- 結構（依 scout 地圖，來源全在急救卡 L3189 與 s13-drop20）：頂端「帳面跌了，很慌」→ 四個分岔＋一條主路：
  1. 「這筆錢五年內要用的」→ 第 8 節「跌的時候、很久沒漲的時候，記得這幾句」第一條（`#s5-remember`）
  2. 「借錢買的」→「年齡、槓桿與退休」的「已經借錢投資、今天正在跌」（`#lifecycle-q2-today`）
  3. 「手上是以前買的個股」→ 第 17 節「處理套牢的舊部位」（`#s13-loss`）
  4. 主路「照這本書做長期、分散投資的」→「今天先做三件事：不賣、不加碼、關掉 app 的漲跌推播」→ 再分：「已經寫好計畫的：把那張紙拿出來，照『市場下跌時』那一行做」／「還沒寫過計畫的：今天不是寫規則的日子…挑一個平靜的日子回來，填下面的六行」（`#plan-starter`）
- 標籤字串逐字取自急救卡原句（可截短成子字串，但子字串必須逐字存在）；箭頭上不寫新字。桌機橫向樹、手機直向樹。
- 圖說（figcaption，只指路）：「先找自己是哪一種錢，再看那一格；圖上的每一條路，急救卡下面都有原文。」；note：不要（卡本身就是說明）。
- SVG 裡的節號連結：SVG 內文字不能是 xref；圖只標名稱，不標「第 N 節」（避免 xref 哨兵與純文字節號）。

## 圖二：「從今天到第一筆投資」（data-chart="first-route"）
- 放：第 19 節 firstmonth「從第一週到第一年：一頁時間表」開頭（lede 之後、白話版之後、「第一週」之前），當「用到再翻」那一部的地圖。
- 七站（依書順序，ChatGPT 的六站加兩站）：
  1. 「投資前的安全順序」（第 2 節，五項）
  2. 「每月投多少」（第 5 節儲蓄率；標籤用起步版第 3 行原字「每月投多少？」）
  3. 「股票放幾成」＋「驗算一次」（第 8 節小卡）
  4. 「起步版六行」（第 14 節 `#plan-starter`；標籤「起步版：六行，填完就可以開始」可截短）
  5. 「到合法券商開證券戶和交割戶」（第 19 節第一週第 4 項／第 20 節第 4 步「選通路與產品」）
  6. 「用小金額完成第一次」（第 20 節第 5 步）
  7. 「設成自動，留好紀錄」（第 20 節第 6 步）→ 尾巴「每年一次的檢查表」（第 23 節）
- 標籤逐字取自各站標題或起步版行名；圖說：「七站照這個順序走；每一站的細節在括號裡那一節。」（括號裡的節號放 figcaption 用 xref，不放 SVG。）
- 桌機一列七站、手機兩列或直向。

## 產線
- 新腳本 `tools/v7_g12_route_maps.py`：`compute()` 讀 `guide/index.html`，對兩張圖的每個標籤 `assert label in guide_text`（去標籤後的可見文字；急救卡在 details 內也算），回傳結構；`chart_panic()`、`chart_route()` 仿 `v63_g01_plan_flow.py`（`E.L('d')`／`E.L('m')` 兩版、`E.text`、`E.note`）。
- `tools/essay_charts.py`：加 wrapper 與 `do_guide()` 的 `funcs["panic-map"]`、`funcs["first-route"]`；`guide/index.html` 先放兩個空殼 `<figure class="chart" data-chart="…">`。
- `tools/calc_core.py`：若 compute 不需要 calc-results 就不加鍵；但把標籤斷言也接進 calc_core 的「引用缺漏」機制（或在 v7_check 加一支 `routes` 檢查）——擇一，回報。
- 重疊量測：`tools/v7_money_age_measure.py` 寫死 money-age；改成接受 `--chart NAME`（預設 money-age，維持既有行為與輸出），對兩張新圖各量一次：文字框互不重疊、不出 viewBox、桌機 1024／手機 375。
- 第 28 節「N 張圖」那句（`v7_layout_check` 會對）：28→30，同步改；`guidetools check` 的 data-chart 28→30 若有測試釘住就回報。
- 圖說是可見文字，budget 照實測 `_comment_cu`。

## 檢查
essay_charts 兩次（0 ⚠、等冪）、layout、money_age_measure（三張）、budget、numbers 兩基準（round58）、anchors、xrefs、planstep、guidetools check、兩支測試、calc_core、build_lite（PDF 頁數前後；工作表不受影響）。驗證員：圖上每一條路對到急救卡原句與錨點、沒有多路少路、沒有新字；七站順序與書一致；SVG 文字在 375 不重疊。
