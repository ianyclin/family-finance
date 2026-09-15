export const meta = {
  name: 'family-finance-research-outline',
  description: '家庭理財白話說明文件：五路查證數字來源 ＋ 三角度大綱提案 ＋ 裁判整合定案大綱',
  phases: [
    { title: 'Research', detail: '五位研究員各自查證一個領域的數字與權威來源，寫進 research/*.md' },
    { title: 'Outline', detail: '三位提案人從不同角度擬完整大綱' },
    { title: 'Judge', detail: '裁判整合成定案大綱，並列出研究缺口' },
    { title: 'GapFill', detail: '補查裁判點名的缺口' },
  ],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'
const TODAY = '2026-09-07'

const COMMON = `
你在替一份「家庭理財白話說明文件」做前置查證。讀者是完全沒有理財基礎的台灣成年人；作者要求每個數字都要能回推到權威來源。
今天是 ${TODAY}。凡是會逐年變動的數字（免稅額、投保薪資上限、利率上限、費用率等），一律找「目前有效」或「最新公告」的版本，並標註「以哪一年度／哪一日為準」。
工具：請用 WebSearch 與 WebFetch 查證（若工具尚未載入，先用 ToolSearch 載入 select:WebSearch,WebFetch）。優先直接讀官方頁面：政府機關（.gov.tw）、金管會、勞動部／勞保局、財政部／國稅局、中央銀行、主計總處、中央存保、健保署、投信投顧公會、證交所、以及原始研究（S&P SPIVA、Vanguard、Morningstar、Bengen／Trinity Study、CFPB、FINRA、學術論文）。
鐵律：
1. 不准捏造網址。每一條事實都要附「你實際打開過」的網址；只在搜尋摘要看到而沒打開的，confidence 標 likely；查不到的標 unverified 並照實說。
2. 數字要抄原文，不要自己換算後只給結果；需要換算時同時給原始數字與換算式。
3. 把結果寫成 Markdown 檔（路徑見下），格式：每條事實一個小節：「事實／數字／來源機構／網址／以…為準／信心等級／備註（含原文引述一句）」。
4. 最後用 StructuredOutput 回傳同一份清單的結構化版本，file 欄位填你寫的檔案完整路徑。
5. 你是研究員不是作者：不要寫教學文字，只回報事實與來源。
`

const RESEARCH = [
  { key: 'tw-social-insurance', title: '台灣社會保險與退休制度', prompt: `
領域：台灣的社會保險與退休制度。要查證的清單：
- 勞保老年給付：請領年齡（含逐年延後到 65 歲的時程）、年金計算公式（平均月投保薪資 × 年資 × 1.55%）、目前月投保薪資上限（45,800？請確認現行）、勞保基金財務狀況（精算報告預估用罄年份與政府撥補金額）。
- 勞退新制：雇主提繳 6%、勞工自願提繳最高 6%、自提金額不計入當年度薪資所得課稅的法源、提繳工資分級表上限、勞退基金歷年平均收益率、保證收益（不低於二年定存）、請領年齡 60 歲、月退與一次退的條件（年資 15 年）。
- 國民年金：對象與大致保費。
- 全民健保：一般保費費率（現行 %）、補充保費費率、部分負擔的概念（不用細表）。
- 勞保與勞退的差別（一句話能講清楚的官方定義）。
輸出檔案：${ROOT}/research/tw-social-insurance.md` },
  { key: 'tw-tax-bank', title: '台灣稅務、銀行與物價', prompt: `
領域：台灣的所得稅、銀行存款保障與物價。要查證的清單：
- 綜合所得稅（2026 年申報 2025 年度所得，以及若已公告的 2026 年度）：免稅額、標準扣除額（單身／有配偶）、薪資特別扣除額、儲蓄投資特別扣除額 27 萬、幼兒學前特別扣除額、長照特別扣除額、基本生活費、稅率級距表（5%～40% 各級距金額）。
- 股利所得課稅兩種方式（合併計稅 8.5% 抵減、上限 8 萬；或分開計稅 28%）。
- 證券交易稅 0.3%、ETF 0.1%；證券交易所得免稅；海外所得 100 萬以上要計入最低稅負制、基本所得額免稅額（750 萬？請確認現行）。
- 存款保險：每人每家金融機構最高保額 300 萬（確認現行）與中央存保的官方說法。
- 信用卡循環信用利率法定上限（銀行法 47-1 條，15%）、信用卡最低應繳金額規範、現金卡。
- 中央銀行重貼現率現行值；主要銀行一年期定存利率大約區間；活期存款利率大約區間（以央行或五大銀行平均利率為準）。
- 主計總處 CPI：近 10 年與近 20 年的年平均通膨率（請給資料來源與計算依據），2025 全年 CPI 年增率。
- 通膨 2% 對購買力的影響（用官方數字自己算一個 20 年、30 年的例子，附算式）。
輸出檔案：${ROOT}/research/tw-tax-bank.md` },
  { key: 'investing-evidence', title: '投資的證據與工具', prompt: `
領域：投資的實證證據與台灣可用的工具。要查證的清單：
- 長期報酬：台灣加權股價報酬指數（含息）自 2003 年編製以來的年化報酬；S&P 500 長期（1926 或 1957 起）年化總報酬；全球股票（MSCI ACWI）長期年化報酬。給來源與計算區間。
- 主動 vs 被動：S&P SPIVA 最新報告中，10 年、15 年、20 年期輸給指數的主動基金比例（美國大型股；若有台灣或亞洲版本也給）。
- 費用的影響：Morningstar「費用是最可靠的報酬預測指標」研究；Vanguard 或 SEC 對 1% 費用長期侵蝕的示例。
- 行為落差：Morningstar「Mind the Gap」最新版投資人實際報酬落後基金報酬的幅度；或 DALBAR。
- 定期定額 vs 單筆：Vanguard 2012 或後續研究的結論（單筆約 2/3 時間勝出）。
- 提領率：Bengen 1994 的 4% 法則與 Trinity Study 的原始結論、以及近年下修（Morningstar 3.7%～4%）的討論。
- 台灣工具：0050、006208、0056、00878 的經理費與保管費、總費用率（投信官網）；VT、VTI、VOO、BND 的費用率（Vanguard 官網）；台灣券商複委託手續費一般區間；海外券商的稅務注意（美國非居民股息預扣稅 30%、遺產稅門檻 6 萬美元）。
- 複利：用 72 法則與實際算式各算一個例子（每月 5,000、年化 6%、30 年 = ？ 給算式）。
- 風險：股市最大回撤的歷史例子（2008 金融海嘯 S&P 500 跌幅、台股 2008 跌幅、2020 疫情），以及後續復原花了多久，要有來源。
輸出檔案：${ROOT}/research/investing-evidence.md` },
  { key: 'insurance-debt-scam', title: '保險、債務、房貸與詐騙', prompt: `
領域：保險原則、債務、房貸與詐騙。要查證的清單：
- 保險：金管會或壽險公會對「先保障後儲蓄」「保額應為年收入若干倍」的官方說法；保險法上受益人與要保人的定義；台灣人壽保險投保率與平均保額（保發中心或壽險公會統計，顯示「保單多但保額低」）。
- 儲蓄險：如何計算 IRR（內部報酬率）、金管會對儲蓄型保單宣告利率與解約金的規範、投資型保單的費用結構（前置費用、危險保費）。
- 實支實付醫療險、意外險、失能險、定期壽險、癌症險、重大傷病險的白話定義（可引官方或公會說明）。
- 債務利率排序：信用卡循環（上限 15%）、信貸（一般區間）、車貸、學貸（目前利率與利息補貼規則）、房貸（目前五大銀行新承作房貸平均利率）。
- 房貸：央行現行選擇性信用管制重點（第幾戶成數）、金管會或央行對房貸負擔率的計算方式、寬限期的意思、新青安貸款的重點條件、房貸壽險。
- 租買比較：年租金報酬率（租金／房價）的台灣大致數字（內政部或民間統計）、持有成本項目（房屋稅、地價稅、管理費、修繕）。
- 詐騙：165 反詐騙、警政署統計 2025 年詐騙財損金額與最常見手法（假投資）、金管會「投資詐騙五大特徵」或類似警語、如何查證合法業者（金管會核准名單、投信投顧公會）。
- 消費者求助：金融消費評議中心、投保中心（投資人保護中心）的功能。
輸出檔案：${ROOT}/research/insurance-debt-scam.md` },
  { key: 'budget-behavior-family', title: '預算、行為與家庭', prompt: `
領域：預算方法、行為財務與家庭層面的證據。要查證的清單：
- 50/30/20 法則的出處（Elizabeth Warren《All Your Worth》2005）與內容；台灣主計總處家庭收支調查中，平均每戶消費支出結構（食、住、交通等比例）與儲蓄率。
- 緊急預備金 3～6 個月的來源（CFPB、Vanguard、FINRA 的說法）與台灣版本（金管會金融教育或銀行公會）。
- 行為財務：Kahneman 與 Tversky 的損失趨避（損失痛感約為獲利的 2 倍，來源）、Thaler 的心理帳戶、Save More Tomorrow 的實驗結果、Benartzi。
- 台灣的金融素養調查：金管會或 OECD/INFE 台灣得分、以及「多少比例的人沒有記帳／沒有預備金」之類的官方或大型民調數字。
- 家庭：台灣民法夫妻法定財產制的重點（剩餘財產分配請求權）、遺產稅免稅額與稅率（現行）、贈與稅免稅額（每年 244 萬？確認現行）、子女教育費用大致估算（教育部或主計總處）、長照費用大致行情。
- 教孩子理財：官方或學術資源（金管會校園金融教育、CFPB 的 Money as You Grow 里程碑）。
- 記帳工具的原則（不推薦特定商品，只記錄官方或大型機構建議的做法）。
輸出檔案：${ROOT}/research/budget-behavior-family.md` },
]

const FACTS_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    summary: { type: 'string' },
    facts: { type: 'array', items: { type: 'object', properties: {
      claim: { type: 'string' }, value: { type: 'string' }, source: { type: 'string' }, url: { type: 'string' }, asOf: { type: 'string' },
      confidence: { type: 'string', enum: ['verified', 'likely', 'unverified'] }, note: { type: 'string' },
    }, required: ['claim', 'source', 'confidence'] } },
    gaps: { type: 'array', items: { type: 'string' } },
  },
  required: ['file', 'summary', 'facts'],
}

const OUTLINE_COMMON = `
你要替一份「家庭理財完整說明文件」擬大綱。背景：作者是台灣的醫師，跟朋友聊投資時發現朋友完全沒有理財基礎，想做一份白話、淺顯、版面清楚、註記附權威來源的說明文件給朋友看。作者的價值觀：真實性優先於教育性，文件不替讀者下結論，只把事實、取捨與後果講清楚，讓讀者自己決定；不推薦特定商品、不做個人化投資建議。
讀者：台灣成年人，有工作與家庭，零基礎，會看手機。用語：台灣繁體中文，白話，避免術語，術語第一次出現要用生活比喻解釋。
範圍：家庭理財的全貌，至少涵蓋：為什麼要理財、家庭資產負債表與現金流、記帳與預算、緊急預備金、債務、保險、投資基礎（複利、通膨、風險、分散、指數化、費用）、退休（勞保、勞退、自提）、稅、房子租買、家庭層面（夫妻財務、小孩、父母、遺產與受益人）、常見陷阱與詐騙、行動清單、名詞表。你可以增減與重排。
每章請給：標題、這章要讓讀者「做得到」什麼、關鍵訊息 3～6 條、可用的生活比喻、適合的版面元素（表格、對照卡、流程圖、警語框、算式框、檢核清單…）、這章最容易講錯或誤導的地方。
另外給整份文件的版面規格建議（章節導覽、每章開頭「一句話」、重點框、註記格式、名詞表、行動清單）與語氣規範。
不要寫正文，只寫大綱。用 StructuredOutput 回傳。
`

const ANGLES = [
  { key: 'sequence', angle: '教學循序：從零開始，每一章只依賴前面的章，讀完能一步步建立自己的家庭財務系統', model: 'opus', effort: 'high' },
  { key: 'pain', angle: '讀者痛點：從零基礎朋友最可能問的問題與最常見的誤解出發（例如「要不要買儲蓄險」「現在進場會不會太晚」「房貸先還完再投資？」），每章解決一組疑問', model: 'opus', effort: 'high' },
  { key: 'action', angle: '行動導向：每章結尾都有一件當天就能做的事，整份文件讀完等於做完一次家庭財務健檢；重視檢核清單與表格', model: 'opus', effort: 'high' },
]

const OUTLINE_SCHEMA = {
  type: 'object',
  properties: {
    angle: { type: 'string' },
    tone: { type: 'string' },
    globalLayout: { type: 'array', items: { type: 'string' } },
    chapters: { type: 'array', items: { type: 'object', properties: {
      title: { type: 'string' }, goal: { type: 'string' },
      keyPoints: { type: 'array', items: { type: 'string' } },
      analogies: { type: 'array', items: { type: 'string' } },
      layoutElements: { type: 'array', items: { type: 'string' } },
      pitfalls: { type: 'array', items: { type: 'string' } },
    }, required: ['title', 'goal', 'keyPoints'] } },
  },
  required: ['angle', 'chapters'],
}

const FINAL_SCHEMA = {
  type: 'object',
  properties: {
    outlineFile: { type: 'string' },
    rationale: { type: 'string' },
    tone: { type: 'string' },
    layoutSpec: { type: 'array', items: { type: 'string' } },
    chapters: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, title: { type: 'string' }, goal: { type: 'string' },
      keyPoints: { type: 'array', items: { type: 'string' } },
      factsNeeded: { type: 'array', items: { type: 'string' } },
      layoutElements: { type: 'array', items: { type: 'string' } },
      pitfalls: { type: 'array', items: { type: 'string' } },
      targetLength: { type: 'string' },
    }, required: ['id', 'title', 'goal', 'keyPoints'] } },
    researchGaps: { type: 'array', items: { type: 'string' } },
    factConflicts: { type: 'array', items: { type: 'string' } },
  },
  required: ['outlineFile', 'chapters'],
}

log('研究員與大綱提案人同時出發')
const [research, outlines] = await parallel([
  () => parallel(RESEARCH.map(r => () =>
    agent(COMMON + r.prompt, { label: `research:${r.key}`, phase: 'Research', model: 'sonnet', effort: 'medium', schema: FACTS_SCHEMA }))),
  () => parallel(ANGLES.map(a => () =>
    agent(OUTLINE_COMMON + `\n你的角度：${a.angle}`, { label: `outline:${a.key}`, phase: 'Outline', model: a.model, effort: a.effort, schema: OUTLINE_SCHEMA }))),
])

const researchOk = (research || []).filter(Boolean)
const outlinesOk = (outlines || []).filter(Boolean)
log(`研究完成 ${researchOk.length}/${RESEARCH.length}，大綱提案 ${outlinesOk.length}/${ANGLES.length}`)

phase('Judge')
const judgePrompt = `
你是裁判兼總編輯。手上有三份從不同角度擬的大綱，以及五份查證後的事實清單（檔案在 ${ROOT}/research/，請全部讀完）。
任務：
1. 整合成一份定案大綱：吸收三份提案各自最好的部分（不是投票選一份），章節順序要讓零基礎讀者能循序理解，同時每章保留「一句話重點」與「今天可以做的一件事」。章數建議 12～16 章，加名詞表與總行動清單。每章給 id（兩位數字-英文 slug）、title、goal、keyPoints、factsNeeded（指向研究檔裡哪些事實，寫成「檔名：事實標題」）、layoutElements、pitfalls、targetLength（中文字數）。
2. 定整份文件的 layoutSpec（版面規格）與 tone（語氣規範），要具體到寫手照做即可：例如每章結構、重點框種類、註記怎麼寫（文內上標編號＋章末來源列表，含機構、標題、日期、網址）、表格何時用、比喻怎麼用、哪些字眼禁用（推薦、保證、必賺…）、如何呈現「取捨」而不是替讀者下結論。
3. 列出 researchGaps：定案大綱需要、但五份研究檔沒有查到或標了 unverified 的事實，寫成可以直接派人去查的句子。
4. 列出 factConflicts：研究檔之間或與你的常識明顯矛盾、需要再確認的數字。
5. 把定案大綱寫成 Markdown 存到 ${ROOT}/outline.md（含 layoutSpec 與 tone），outlineFile 填該路徑。
作者價值觀：真實性優先；不替讀者下結論；不推薦商品；不做個人化建議；每個數字要有來源。
三份提案：
${JSON.stringify(outlinesOk, null, 1)}
五份研究摘要（完整內容請讀檔）：
${JSON.stringify(researchOk.map(r => ({ file: r.file, summary: r.summary, gaps: r.gaps, factCount: (r.facts || []).length })), null, 1)}
`
const final = await agent(judgePrompt, { label: 'judge:outline', phase: 'Judge', model: 'fable', effort: 'xhigh', schema: FINAL_SCHEMA })

let gapFill = null
const gaps = [...((final && final.researchGaps) || []), ...((final && final.factConflicts) || [])]
if (gaps.length) {
  phase('GapFill')
  log(`補查 ${gaps.length} 個缺口／矛盾`)
  gapFill = await agent(COMMON + `
領域：補查。以下是總編輯點名「大綱需要但尚未查到」或「數字互相矛盾」的項目，請逐條查證，並在對應的既有研究檔（${ROOT}/research/）末尾追加一節「## 補查 ${TODAY}」寫入結果；若不屬於任何既有檔案，寫到 ${ROOT}/research/gap-fill.md。file 欄位填 gap-fill.md 或你主要更新的檔案。
項目：
${gaps.map((g, i) => `${i + 1}. ${g}`).join('\n')}
`, { label: 'research:gap-fill', phase: 'GapFill', model: 'sonnet', effort: 'high', schema: FACTS_SCHEMA })
}

return {
  final,
  gapFill,
  research: researchOk.map(r => ({ file: r.file, summary: r.summary, gaps: r.gaps, unverified: (r.facts || []).filter(f => f.confidence !== 'verified').map(f => f.claim) })),
  outlineAngles: outlinesOk.map(o => ({ angle: o.angle, chapterTitles: (o.chapters || []).map(c => c.title) })),
}
