export const meta = {
  name: 'v61-w3-charts-and-g11-research',
  description: '隔離人性 v61：三張新圖（G8 G9 G10）的計算與畫圖＋G11「在歷史高點買進」的研究，不碰原文檔',
  phases: [
    { title: 'Build', detail: '三張圖各一個 builder，寫在獨立模組；G11 研究三路並行' },
    { title: 'Integrate', detail: '一個代理把三個模組接進 calc_core 與 essay_charts' },
    { title: 'Verify', detail: '每張圖一位裁判從原始資料獨立重算；G11 研究綜整' },
  ],
}

const REPO = '/Users/linyenchu/Cladue Code/family-finance'
const SCR = args.scratch
const COMMON = `專案：${REPO}（獨立本機 git repo）。
先讀：${REPO}/docs/core-edition/specs/spec-v61-remaining.md（本輪規格）、${REPO}/docs/core-edition/specs/v61-decisions.md 的 G 組、${REPO}/docs/handoff-guide-2026-09-16.md 的「工具」一節（essay_charts 的規矩）。
看現成範例：tools/essay_charts.py 的 taiex_recovery()、asset_rotation()（新圖照同樣結構：回傳 dict(title, sub, svgs=[桌面 640 寬 L("d")、手機 360 寬 L("m")], extras=legend()+note(), caption)），tools/calc_core.py 的 damodaran_annual()、taiex_drawdowns()、asset_rotation 區塊。
**絕對不准**：修改 guide/index.html、執行 tools/build_lite.py、執行 tools/essay_charts.py --guide、修改 tools/calc_core.py 或 tools/essay_charts.py（整合由下一個階段統一做）、git commit。
設計系統：只用 essay_charts 已定義的顏色常數（TEAL、MUTED、AMBER、ACCENT、BLUE、INK、LINE）與既有 helper（L、svg_open、text、rect、poly、dot、hline、grid、legend、note）；字級沿用既有圖；手機版減少標籤密度，不能超出 360 寬。
圖說與 note 規矩：只寫圖上看得到的事實；不替讀者下結論（例如不能讓人讀成「跌了一定會回來」「任何時候買都可以」）；口徑（名目、含息、年度或月資料、哪個市場、期間、沒扣費用稅）寫進 note；歷史不是保證。所有數字都要能從你的 compute() 結果讀到，四捨五入用 half-up（不要用 Python round）。`

const BUILD_SCHEMA = {
  type: 'object',
  properties: {
    chart_id: { type: 'string' },
    module: { type: 'string' },
    calc_key: { type: 'string' },
    placement: { type: 'string', description: '建議放在哪一節、哪一段之後（節 id＋一小段原文）' },
    lead_sentence: { type: 'string', description: '圖前引導句草稿（放進指南的正文，一兩句）' },
    caption: { type: 'string' },
    key_numbers: { type: 'array', items: { type: 'string' } },
    caveats: { type: 'array', items: { type: 'string' } },
    preview_png: { type: 'string' },
    notes: { type: 'string' },
  },
  required: ['chart_id', 'module', 'calc_key', 'placement', 'lead_sentence', 'caption', 'key_numbers', 'caveats', 'preview_png', 'notes'],
}

const CHARTS = [
  { id: 'recovery-by-mix', g: 'G8', mod: 'tools/v61_g8_recovery_by_mix.py',
    task: `G8「不同股債比，從谷底爬回來各要多久」。資料：research/data/damodaran_histret.xls（美國 S&P 500 含息、10 年期公債，年度、名目、美元；讀法照 calc_core.damodaran_annual()）。
算：股票 100%、80%、60%、40%（其餘放 10 年期公債）、每年年底再平衡的組合，1928–2025 逐年淨值；找出每一段從前高跌下去再回到前高的過程，至少算出：每種比例的「最深年度跌幅」「最久要幾年回到前高」，以及幾個大家叫得出名字的段落（1929 起、1973–74、2000–02、2008、2022）各比例的跌幅與回本年數。
畫：一張讀者三秒看得懂的圖，訊息是「股票放越多，跌得越深、爬回來也越久」——前提是資料真的支持；如果某一段不支持（例如 2022 股債一起跌），圖或 note 要誠實呈現。支撐指南第 11 節「股票放幾成」。
一定要寫進 note 的口徑：年度資料會低估年內真正的最深跌幅；美國一個市場；名目、沒扣費用稅；每年再平衡；歷史不是保證。` },
  { id: 'country-recovery', g: 'G9', mod: 'tools/v61_g9_country_recovery.py',
    task: `G9 替代方案 A：把指南第 4 節那張「高點到再創高」表畫成三條時間軸長條。資料就是那張表（用 python 從 guide/index.html 的 #s4 讀出表格核對，不要自己改數字）：美國 1929-09 → 1954-11 約 25 年（聯準會歷史頁，道瓊價格）；日本 1989-12-29 → 2024-02-22 34 年 2 個月（日經官方；含息版 2021 年先過高點）；台灣 1990-02 → 2020-07 約 30 年（證交所；含息版沒有官方數字，會早很多年）。
畫：共用一條年份軸（約 1925–2030），三條長條各自從高點畫到再創高，標出年數。訊息是「單押一個國家，可能要等很久」，接回第 4 節「核心放全球」。note 要寫：都是價格指數（不含息），含息版會早一些（日本 2021 年先過）；這三段是挑出來的著名例子，不是平均。
calc_key 用 country_recovery，compute() 回傳這三筆的起訖日期、年數、口徑、來源。` },
  { id: 'rebalance-drift', g: 'G10', mod: 'tools/v61_g10_rebalance_drift.py',
    task: `G10「不再平衡的話，股債比會漂成什麼樣」。資料：research/data/damodaran_histret.xls（美國 S&P 500 含息、10 年期公債，年度、名目）。
算：從某一年開始股票八成、債券兩成（指南第 11 節用八二當例子），之後完全不再平衡，每年年底股票占比變多少；對照每年再平衡（永遠 80%）。起點年份自己選一個有代表性的，並另外算幾個不同起點（例如 1990、2000、2009）的漂移範圍放進 compute() 結果，讓裁判能檢查挑的起點有沒有挑櫻桃。
再算 5/25 規則（指南第 11 節：差超過 5 個百分點或超過原本比例的四分之一，取較小者；八二的股票那邊是 ±5 個百分點，債券那邊 20% 的四分之一是 5 個百分點）：不再平衡的那條線第一次超出門檻是哪一年。
畫：一條股票占比的線＋80% 的目標線＋門檻帶（75%–85%），讀者看得出「不管它，比例會自己跑掉」。note 寫明口徑與「示意：只用美國一個市場、一個起點」。` },
]

phase('Build')
const builds = CHARTS.map(c => agent(
`${COMMON}

你的任務：${c.task}

交付：
1. 模組檔 ${c.mod}，裡面兩個函式：
   - compute()：只用標準庫＋xlrd，讀原始資料、回傳可 JSON 化的 dict（口徑、來源、每一個會印在圖上的數字、以及裁判需要的中間結果）。
   - chart(res)：吃 compute() 的結果，回傳和 essay_charts 其他圖一樣的 dict(title, sub, svgs, extras, caption)。essay_charts 的 helper 在函式內 lazy import（import essay_charts as E），避免循環 import。
   檔頭註解寫清楚資料來源、口徑、演算法。
2. 自測：寫一個 ${SCR}/w3/test_${c.g}.py，呼叫 compute() 與 chart()，把 figure HTML 包進一個最小頁面（含 essay_charts 產出的 figure CSS 或從 guide/index.html 抽出 figure.chart 相關 CSS），存到 ${SCR}/w3/${c.id}.html，並用 Chrome headless 或 PyMuPDF 以外的方式截圖成 PNG（例如 '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' --headless --screenshot=... --window-size=900,900，手機版再截一張 --window-size=400,900）。自己看截圖確認沒有文字重疊、沒有超出框。
3. 回傳結構化摘要：placement（建議放在指南哪一節哪一段後面）、lead_sentence（圖前引導句草稿）、caption（圖說草稿）、key_numbers、caveats、preview_png（桌面版截圖路徑）。`,
  { label: `build:${c.g}`, phase: 'Build', schema: BUILD_SCHEMA, model: 'opus', effort: 'high' }))

const G11_SCHEMA = {
  type: 'object',
  properties: {
    lane: { type: 'string' },
    findings: { type: 'array', items: { type: 'object', properties: {
      claim: { type: 'string' }, numbers: { type: 'string' }, source: { type: 'string' }, url: { type: 'string' },
      tier: { type: 'string', description: '一手研究／官方資料／自算／業者報告／部落格' }, license_note: { type: 'string' } },
      required: ['claim', 'numbers', 'source', 'url', 'tier', 'license_note'] } },
    boundaries: { type: 'array', items: { type: 'string' } },
    files: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
  required: ['lane', 'findings', 'boundaries', 'files', 'notes'],
}
const G11_LANES = [
  { lane: 'web-research', model: 'opus', effort: 'high', prompt: `上網查「在歷史新高附近買進股票，之後的報酬有沒有比較差」的一手或權威來源：學術論文、J.P. Morgan Guide to the Markets／Guide to Retirement 相關頁、Vanguard、Morningstar、Dimensional、AQR、Of Dollars And Data（Nick Maggiulli）、A Wealth of Common Sense（Ben Carlson）等。每一條要有：結論、數字、期間與口徑、網址、來源等級。特別注意版權與條款（本書慣例：只引用數字、自己重畫，不轉載圖；若條款禁止再散布數字，要標出）。也要找反例與限制（例如 1929、2000、日本 1989 都是在高點附近）。` },
  { lane: 'compute-us', model: 'opus', effort: 'high', prompt: `自己算美國：用 research/data/shiller_sp_monthly.csv（Shiller 月資料；含息月指數照 tools/calc_core.py 的 shiller_tr()：月報酬＝(P_t＋D_t/12)÷P_{t−1}，股利欄截止就停）。定義「在歷史新高買進」＝該月含息指數創下到當月為止的新高（也算一個「距新高 5% 以內」的版本）。算之後 1、3、5、10 年的年化報酬分布（中位數、四分位、正報酬比例），和「所有月份」比較。也算價格指數版（不含息）對照。視窗重疊要註明。程式寫到 ${SCR}/w3/g11_us.py，結果存 ${SCR}/w3/g11_us.json。注意 Shiller 用的是月平均價，不是月底價，要寫進 boundaries。` },
  { lane: 'compute-tw', model: 'opus', effort: 'high', prompt: `自己算台灣：用 tools/calc_core.py 的 taiex_series()（證交所發行量加權股價報酬指數，含息、逐日，2003-01-02 到 2025-12-31）。定義「在歷史新高買進」＝收盤創下到當天為止的新高。算之後 1、3、5、10 年（日曆視窗，照 calc_core 的 rolling 規則：滿 N 年同一天，沒開盤取前一個交易日）的年化報酬分布與正報酬比例，和「所有交易日」比較。程式寫到 ${SCR}/w3/g11_tw.py（import calc_core 的函式時小心它 import 時會重算全部並寫檔——請改成自己讀 CSV，讀法照 taiex_series()），結果存 ${SCR}/w3/g11_tw.json。boundaries 寫清楚：23 年、起點在 2000–2002 大跌之後、視窗重疊、10 年視窗樣本很少。` },
]
const g11 = G11_LANES.map(l => agent(
`${COMMON}

G11 研究（本階段只研究與計算，不寫指南文字）。${l.prompt}
回傳 findings（每條含來源等級與條款注意）、boundaries（這個證據不能推到哪裡）、files（你產出的檔案路徑）。`,
  { label: `g11:${l.lane}`, phase: 'Build', schema: G11_SCHEMA, model: l.model, effort: l.effort }))

const built = (await Promise.all(builds)).filter(Boolean)
log('三張圖建好：' + built.map(b => `${b.chart_id}→${b.module}`).join('、'))

phase('Integrate')
const integ = await agent(
`專案：${REPO}。三個新圖模組已經寫好：
${built.map(b => `- ${b.chart_id}：${b.module}（calc key：${b.calc_key}）`).join('\n')}
任務：把它們接進既有流程，不改任何既有圖、不改 guide/index.html、不跑 build_lite.py、不跑 essay_charts.py --guide、不 commit。
1. tools/calc_core.py：在 asset_rotation 區塊之後，import 三個模組並寫入 R[calc_key] = module.compute()；跑 python3 tools/calc_core.py，確認最後印「引用缺漏: []」，且 lite/calc-results.json 其他既有 key 的值完全沒變（先備份舊 json 到 ${SCR}/w3/calc-results.before.json，再用 python 逐 key 比對，新 key 以外必須相等）。
2. tools/essay_charts.py：在 funcs["asset-rotation"] = asset_rotation 那一段後面，註冊三個 id（"recovery-by-mix"、"country-recovery"、"rebalance-drift"），函式呼叫各模組的 chart(calc()[calc_key])，註解「只在指南」。確認 --guide 模式下，指南裡沒有這三個 data-chart 空殼時不會報錯（看既有邏輯）。
3. 跑 python3 -c 匯入 essay_charts 並呼叫三個 funcs，確認都回傳完整 dict、SVG 字串非空。
回傳：改了哪幾行（檔名:行號）、比對結果、任何問題。`,
  { label: 'integrate', phase: 'Integrate', model: 'sonnet', effort: 'medium' })

phase('Verify')
const VERDICT = {
  type: 'object',
  properties: {
    chart_id: { type: 'string' },
    verdict: { type: 'string', enum: ['pass', 'fix_needed', 'reject'] },
    findings: { type: 'array', items: { type: 'object', properties: {
      severity: { type: 'string', enum: ['must', 'should', 'note'] }, location: { type: 'string' }, problem: { type: 'string' }, suggestion: { type: 'string' } },
      required: ['severity', 'location', 'problem', 'suggestion'] } },
  },
  required: ['chart_id', 'verdict', 'findings'],
}
const verifs = await parallel(built.map(b => () => agent(
`你是裁判，對抗性驗證一張新圖；只讀不改（可以在 ${SCR}/w3/judge-${b.chart_id}/ 寫自己的重算程式）。專案：${REPO}。
圖：${b.chart_id}，模組 ${b.module}，calc key ${b.calc_key}，預覽 ${b.preview_png}（用 Read 看圖）。
起草者的圖說：${JSON.stringify(b.caption)}
圖前引導句：${JSON.stringify(b.lead_sentence)}
建議位置：${b.placement}
關鍵數字：${JSON.stringify(b.key_numbers)}
口徑與限制：${JSON.stringify(b.caveats)}

逐項查：
1. **獨立重算**：不要 import 起草者的模組，自己從 research/data 原始檔（Damodaran xls 用 xlrd；或指南 #s4 的表）重算每一個印在圖上與圖說裡的數字，四捨五入 half-up。對不上就是 must。
2. 演算法有沒有挑櫻桃（起點、門檻、段落定義）或會誤導的選擇。
3. 圖說、引導句、note 有沒有寫圖上看不到的事、有沒有替讀者下結論、口徑有沒有漏（年度資料低估跌幅、名目、單一市場、沒扣費用稅、價格 vs 含息）。
4. 圖本身：桌面與手機兩版 SVG 有沒有文字重疊、超框、標籤錯位（把模組的 chart() 輸出存成 HTML 用 Chrome headless 截圖看）；顏色只用設計系統常數。
5. 和指南現有內容有沒有衝突（grep guide/index.html 的相關段落：第 4 節回本表、第 11 節股票放幾成與 5/25、年度跌幅表等）。
must＝錯誤或誤導；should＝明顯可以更好；note＝小事。`,
  { label: `verify:${b.chart_id}`, phase: 'Verify', schema: VERDICT, model: 'fable', effort: 'xhigh' })))

const g11res = (await Promise.all(g11)).filter(Boolean)
const synth = await agent(
`你是 G11 研究的綜整者（fable，嚴格查證）。專案：${REPO}。三路研究結果如下（JSON）：
${JSON.stringify(g11res)}
請：(1) 抽查最重要的 3–5 條數字：打開網址或重跑 ${SCR}/w3/ 底下的程式核對；(2) 寫一份內容簡報到 ${REPO}/docs/core-edition/specs/g11-brief.md：結論能說到哪裡、不能說到哪裡、建議放在指南哪一節（先 grep 第 6 節「要不要等跌下來再買？」與第 14 節情境題）、建議用哪幾個自算數字（附程式路徑與口徑）、哪些外部來源可以引用數字（條款）、必須寫的但書（1929／2000／日本 1989 等反例、視窗重疊、月平均價）、以及「不能寫成隨時進場都可以」的具體寫法建議；(3) 如果自算程式可靠，把它們複製到 ${REPO}/tools/v61_g11_ath.py（合併成一個模組，compute() 回傳台美兩邊結果，不要接進 calc_core）。
回傳：簡報路徑、模組路徑、你核對後推翻或修正了哪些數字。`,
  { label: 'g11:synthesize', phase: 'Verify', model: 'fable', effort: 'xhigh' })

return { built, integ, verifs: verifs.filter(Boolean), g11: g11res.map(r => ({ lane: r.lane, n: r.findings.length, boundaries: r.boundaries, files: r.files })), synth }
