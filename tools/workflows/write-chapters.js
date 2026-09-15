export const meta = {
  name: 'family-finance-write-chapters',
  description: '家庭理財文件第 1–15 章：分章補查 → 撰寫 HTML 片段 → 雙鏡頭對抗驗證（數字／語氣版面）→ 修正 → 複驗',
  phases: [
    { title: 'Research', detail: '各章缺口補查（法條逐字、官方頁面）' },
    { title: 'Write', detail: '依大綱與元件契約撰寫章節片段' },
    { title: 'Judge', detail: '兩位裁判：數字與來源／語氣與版面' },
    { title: 'Fix', detail: '套用兩位裁判的修正' },
    { title: 'Recheck', detail: '複驗 blocker 與 major 是否真的修掉' },
  ],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'
const TODAY = '2026-09-07'

const CHAPTERS = [
  { id: '01-why-and-order', num: 1, stage: 1, title: '理財到底在解決什麼問題（以及錢該怎麼排隊）', gaps: [76], files: ['budget-behavior-family.md', 'tw-tax-bank.md'] },
  { id: '02-balance-sheet', num: 2, stage: 1, title: '先照一張全家福：家庭資產負債表', gaps: [], files: ['budget-behavior-family.md', 'tw-tax-bank.md', 'tw-social-insurance.md'] },
  { id: '03-cash-flow', num: 3, stage: 1, title: '再看一段錄影：現金流、記帳與自動分流', gaps: [74], files: ['budget-behavior-family.md'] },
  { id: '04-emergency-fund', num: 4, stage: 2, title: '緊急預備金：家裡的滅火器', gaps: [3, 77], files: ['budget-behavior-family.md', 'tw-tax-bank.md'] },
  { id: '05-debt', num: 5, stage: 2, title: '債務：先把會漏水的地方補起來', gaps: [4, 5, 7, 9], files: ['insurance-debt-scam.md', 'tw-tax-bank.md'] },
  { id: '06-insurance', num: 6, stage: 2, title: '保險：先看已經有的，再補賠不起的', gaps: [11, 12, 14, 15, 16, 17, 18, 19, 20, 21], files: ['insurance-debt-scam.md', 'tw-social-insurance.md'] },
  { id: '07-time-inflation-compounding', num: 7, stage: 3, title: '投資第一課：時間、通膨、複利，還有報酬從哪裡來', gaps: [22, 23, 27, 28], files: ['investing-evidence.md', 'tw-tax-bank.md'] },
  { id: '08-risk-diversification-cost', num: 8, stage: 3, title: '投資第二課：風險、分散、費用，以及「買下平均」是什麼意思', gaps: [25, 26, 29, 30, 31, 32], files: ['investing-evidence.md'] },
  { id: '09-rules-card', num: 9, stage: 3, title: '投資第三課：把投資變成制度——分桶、路徑、投入方式、規則卡', gaps: [], files: ['investing-evidence.md', 'budget-behavior-family.md'] },
  { id: '10-retirement', num: 10, stage: 4, title: '退休：先查出你已經有的，再算差多少', gaps: [34, 35, 36, 37, 40], files: ['tw-social-insurance.md', 'investing-evidence.md', 'tw-tax-bank.md'] },
  { id: '11-tax', num: 11, stage: 4, title: '稅：看懂它怎麼算，比背數字有用', gaps: [42, 43, 44, 45, 46, 47], files: ['tw-tax-bank.md', 'tw-social-insurance.md'] },
  { id: '12-housing', num: 12, stage: 4, title: '房子：租與買，把兩邊的帳都算出來', gaps: [48, 49, 50, 51, 52, 53, 54], files: ['insurance-debt-scam.md', 'tw-tax-bank.md'] },
  { id: '13-family', num: 13, stage: 5, title: '家裡不只你一個人：伴侶、小孩、父母、長照', gaps: [55, 56, 57, 58, 59, 60], files: ['budget-behavior-family.md', 'tw-tax-bank.md'] },
  { id: '14-legacy', num: 14, stage: 5, title: '萬一：受益人、失能、繼承', gaps: [61, 62, 63, 64, 65, 66, 67, 68], files: ['budget-behavior-family.md', 'insurance-debt-scam.md', 'tw-tax-bank.md', 'tw-social-insurance.md'] },
  { id: '15-scams', num: 15, stage: 6, title: '陷阱與詐騙：三個問題篩掉九成', gaps: [69, 70, 71, 72, 73, 33], files: ['insurance-debt-scam.md', 'investing-evidence.md'] },
]

const RULINGS = `
作者已拍板（outline.md §6 五題）：
1. 商品費用揭露頁網址可以出現在來源清單（至少兩家、加註「僅作費用區間之證據，非推薦」）；正文、框、表、圖一律不點名。
2. 115 年度綜所稅級距已由補查以官方 PDF 逐字核對（門檻 61／138／277／519 萬；累進差額 0／42,700／153,100／430,100／949,100），可用；同時列 114 年度（2026 年 5 月申報用），兩者都標年度。詳見 tw-tax-bank.md「補查」節。
3. 提領率研究放進第 10 章，只作對照卡，標明「美國資料、前提、不可直接套用」。
4. 長照費用只寫量級並附 1966 入口；若本章補查拿到官方數字才可放，標年度。
5. Mind the Gap 引用，但同一頁寫出方法論質疑。
另：outline.md §5 的 15 條事實衝突裁定一律照做（例如 SPIVA 台灣百分比不用、勞退基金 8.58% 不是新制勞退專屬、台股峰谷點位未經證交所 API 重算前不寫具體點位）。
`

const FACTS_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' }, summary: { type: 'string' },
    facts: { type: 'array', items: { type: 'object', properties: {
      item: { type: 'string' }, claim: { type: 'string' }, value: { type: 'string' }, source: { type: 'string' }, url: { type: 'string' },
      confidence: { type: 'string', enum: ['verified', 'likely', 'unverified'] }, note: { type: 'string' },
    }, required: ['item', 'claim', 'source', 'confidence'] } },
  },
  required: ['file', 'summary', 'facts'],
}

const BUILD_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' }, chars: { type: 'number' },
    questions: { type: 'array', items: { type: 'string' } },
    today: { type: 'object', properties: { do: { type: 'string' }, crit: { type: 'string' }, est: { type: 'string' } }, required: ['do', 'crit'] },
    gain: { type: 'array', items: { type: 'string' } },
    worksheet: { type: 'string' },
    terms: { type: 'array', items: { type: 'string' } },
    sourcesCount: { type: 'number' },
    omittedForLackOfSource: { type: 'array', items: { type: 'string' } },
    checkerWarnings: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
  required: ['file', 'chars', 'questions', 'today', 'terms', 'sourcesCount'],
}

const ISSUES_SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['pass', 'fix', 'rewrite'] },
    issues: { type: 'array', items: { type: 'object', properties: {
      severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
      where: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' },
    }, required: ['severity', 'where', 'problem', 'fix'] } },
    strengths: { type: 'string' },
  },
  required: ['verdict', 'issues'],
}

const FIX_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' }, applied: { type: 'number' },
    skipped: { type: 'array', items: { type: 'object', properties: { issue: { type: 'string' }, reason: { type: 'string' } }, required: ['issue', 'reason'] } },
    checkerErrors: { type: 'number' }, checkerWarnings: { type: 'number' }, chars: { type: 'number' },
  },
  required: ['file', 'applied', 'skipped', 'checkerErrors'],
}

const RECHECK_SCHEMA = {
  type: 'object',
  properties: {
    ok: { type: 'boolean' }, checkerErrors: { type: 'number' },
    remaining: { type: 'array', items: { type: 'object', properties: {
      severity: { type: 'string', enum: ['blocker', 'major', 'minor'] }, where: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' },
    }, required: ['severity', 'where', 'problem', 'fix'] } },
  },
  required: ['ok', 'checkerErrors', 'remaining'],
}

const two = n => String(n).padStart(2, '0')

function researchPrompt(ch) {
  return `
你是查證員，替「家庭理財白話說明文件」第 ${ch.num} 章《${ch.title}》補查研究缺口。今天是 ${TODAY}。
先讀：${ROOT}/outline.md 的「## 4. 研究缺口」一節（只看編號 ${ch.gaps.join('、')} 這幾條）與 ${ROOT}/research/gap-fill.md（看哪些已完成、哪些網域抓不到）。再讀 ${ch.files.map(f => ROOT + '/research/' + f).join('、')} 裡跟本章相關的小節，避免重查。
工具：用 WebFetch／WebSearch（若尚未載入，先 ToolSearch select:WebFetch,WebSearch）。法條一律開全國法規資料庫（law.moj.gov.tw）逐條抄現行條文；政府 PDF 可用 WebFetch 取得後存到 ${ROOT}/research/pdf/ 再讀。已知 nhi.gov.tw、spglobal.com、morningstar.com 對 WebFetch 回 403，這類改找同機關其他頁面或標 unverified，不要硬耗；整體最多約 25 次抓取。
鐵律：不捏造網址；沒實際打開的只能標 likely；查不到就標 unverified 並寫搜尋過程。數字抄原文，附原文引述一句。
輸出：寫成 Markdown 存到 ${ROOT}/research/ch-${two(ch.num)}.md（每條：缺口編號／事實／數字／來源機構／網址／以…為準／信心等級／原文引述），並用 StructuredOutput 回傳同一份清單（item 填缺口編號）。你是查證員不是作者，不寫教學文字。
`
}

function buildPrompt(ch, research) {
  const extra = research && research.file ? `、${research.file}（本章補查結果）` : ''
  return `
你是寫手，負責「家庭理財白話說明文件」第 ${ch.num} 章《${ch.title}》。今天是 ${TODAY}。
必讀（照順序）：
1. ${ROOT}/outline.md：§0 整合說明、§1 版面規格（18 條）、§2 語氣規範（12 條）、§3 裡「### ${ch.id}」那一章的全部欄位、§5 事實衝突。
2. ${ROOT}/components.md：HTML 片段契約，只能用裡面列的元素與 class。
3. 研究檔：${ch.files.map(f => ROOT + '/research/' + f).join('、')}${extra}。只能引用研究檔裡 verified 或 likely 的事實；unverified 的改成質性描述或不寫；絕不自己補數字、絕不捏造來源。
${RULINGS}
寫作要求：
- 讀者是完全沒有理財基礎的台灣成年人，像跟朋友講話。每個術語第一次出現照契約格式（白話說法＋術語＋比喻＋比喻哪裡不成立）。
- 章首「這章回答你的三個問題」直接抄 outline 該章的讀者原句。
- 三段式呈現取捨：事實 → 做法 → 各自代價與適合誰 → 底句「這一題沒有標準答案，只有你知道＿＿＿」（＿＿＿填具體內容）。全篇不出現「你應該」「建議你」「推薦」。
- 目標字數見 outline 的 targetLength，允許 ±15%。框合計 ≤7、動手框 ≤2；工作表編號照契約。
- 所有算式先用 Bash 跑 Python 算過再寫；有報酬率／年化的框或小節一定有「這是假設，不是承諾」。
- 圖只在 outline 該章 layoutElements 有要求時畫，SVG 座標用 Python 算，並照契約用 CSS 變數。
- 章末來源清單：每條六段、有等級符號、有查證日期；每條都被正文引用、每個引用都有對應條目。
- 不出現任何商品名、代號、公司、平台、App（政府 App 除外）。
產出：寫到 ${ROOT}/chapters/${ch.id}.html（只有一個 <section>）。寫完執行
  python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${ch.id}.html"
必須 0 個錯誤；警告逐條處理或在 notes 說明。不要動其他檔案。
最後用 StructuredOutput 回傳：file、chars（哨兵統計的 chars）、questions（三個問題原句）、today（do／crit／est）、gain、worksheet（如「工作表④ 緊急金試算」，沒有填空字串）、terms（本章 dfn 的術語）、sourcesCount、omittedForLackOfSource（因為沒來源而放棄的數字）、checkerWarnings、notes。
`
}

function judgeFactsPrompt(ch) {
  return `
你是數字與來源裁判，對「家庭理財白話說明文件」第 ${ch.num} 章《${ch.title}》做對抗性驗證。你的任務是「試著推翻」，不是找優點。你只讀不改：不得修改任何檔案。
讀：${ROOT}/chapters/${ch.id}.html、${ROOT}/outline.md（§3 該章、§5 事實衝突、§6 拍板）、研究檔 ${ch.files.map(f => ROOT + '/research/' + f).join('、')}、${ROOT}/research/ch-${two(ch.num)}.md（若存在）、${ROOT}/research/gap-fill.md。
逐項檢查：
1. 正文每個帶數字的句子：回研究檔找到同一個數字與來源；數字、年度、機構、網址、等級符號（●◐◑○）任何一項對不上就是 blocker。研究檔標 likely 的，來源條目必須有「（轉引，待官方原檔核對）」；標 unverified 的不得以事實語氣出現。
2. 所有算式用 Bash 跑 Python 重算（複利、購買力、級距、乘法），差一位數就是 blocker。
3. 挑 3 到 5 個最高風險的網址（法條、稅、給付、利率）用 WebFetch 實際打開（先 ToolSearch select:WebFetch），核對數字仍然有效；打不開就記錄，不算錯。
4. §5 事實衝突的 15 條裁定與 §6 拍板有沒有被違反（例如台股具體點位、SPIVA 台灣百分比、勞退基金 8.58% 歸屬、Mind the Gap 沒附質疑）。
5. 有沒有沒附來源的數字、有沒有「本文自算」沒標○、有沒有隱含預測（「長期會漲」）。
6. 有沒有任何商品名、代號、公司名、平台名。
7. 報酬率／年化／未來金額的同一框或小節有沒有「這是假設，不是承諾」。
回傳 StructuredOutput：verdict（pass／fix／rewrite）、issues（每條 severity、where＝原文逐字引述、problem、fix＝可以直接套用的替換文字或明確指令）、strengths 一句。找不到問題就誠實回 pass，不要硬湊。
`
}

function judgeVoicePrompt(ch) {
  return `
你是語氣與版面裁判，對「家庭理財白話說明文件」第 ${ch.num} 章《${ch.title}》做對抗性驗證。任務是「試著推翻」。你只讀不改：不得修改任何檔案。
讀：${ROOT}/chapters/${ch.id}.html、${ROOT}/outline.md（§1 版面規格、§2 語氣規範、§3 該章全部欄位含 pitfalls）、${ROOT}/components.md。先執行
  python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${ch.id}.html"
把錯誤與警告納入 issues。
逐項檢查：
1. 零基礎讀者測試：把自己當成完全沒基礎的朋友逐段讀，列出讀不懂的句子、沒解釋就用的術語、超過 40 字的句子、超過 4 句的段落、一段裡塞太多概念的地方。
2. 語氣規範 12 條逐條對照：禁用字眼、隱含推薦（「多數人選擇」「聰明的做法」也算）、恐嚇或勵志、評價過去、預設雙薪有房有小孩、「老公／老婆」、驚嘆號、表情符號。
3. 不替讀者下結論：每個取捨框有沒有偷偷把一邊寫得比較好；底句有沒有填成具體內容；outline 該章 pitfalls 列的錯誤有沒有犯。
4. 章首五件、章尾五件順序與內容；三個問題是否照抄 outline 原句；「今天的一件事」是否 ≤10 分鐘、手機可完成、有完成判準；「讀完你做得到」是否動詞開頭可驗證。
5. 元件契約：只用允許的元素與 class；框 ≤7、動手框 ≤2；表格 ≤3 欄；對照卡六欄；術語 dfn 格式與「比喻哪裡不成立」；圖有 figcaption「這張圖在說什麼」與「示意・非承諾」。
6. 字數是否在 targetLength ±15% 內；小節數 3–7；每章比喻 ≤3、醫療類比 ≤1。
回傳 StructuredOutput：verdict、issues（severity、where＝原文逐字引述、problem、fix＝可直接套用的替換文字）、strengths 一句。找不到問題就誠實回 pass。
`
}

function fixPrompt(ch, issues, round) {
  return `
你是修稿者，處理「家庭理財白話說明文件」第 ${ch.num} 章《${ch.title}》${round > 1 ? '（第二輪）' : ''}。
檔案：${ROOT}/chapters/${ch.id}.html。契約：${ROOT}/components.md。語氣與版面規範：${ROOT}/outline.md §1、§2。研究檔在 ${ROOT}/research/。
下面是裁判列出的問題，全部處理：blocker 與 major 必須修；minor 盡量修，修不了要在 skipped 說明理由。修 blocker 時若需要數字，只能用研究檔裡 verified／likely 的數字；沒有就改成質性描述。不要改動沒被點到的段落，不要讓字數偏離 ±15%。
問題清單：
${JSON.stringify(issues, null, 1)}
修完執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${ch.id}.html"，必須 0 個錯誤。不要動其他檔案。
回傳 StructuredOutput：file、applied（處理了幾條）、skipped（哪條、為什麼）、checkerErrors、checkerWarnings、chars。
`
}

function recheckPrompt(ch, issues) {
  return `
你是複驗員。檔案：${ROOT}/chapters/${ch.id}.html。先執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${ch.id}.html"。
然後逐條確認下面 blocker 與 major 問題是否真的修掉（在檔案裡找到修改後的文字，確認新文字符合 fix 的要求，而且沒有引入新的禁用字眼或商品名）。你只讀不改。
${JSON.stringify(issues.filter(i => i.severity !== 'minor'), null, 1)}
回傳 StructuredOutput：ok（全部修掉且哨兵 0 錯誤才 true）、checkerErrors、remaining（還沒修好的，附 severity、where、problem、fix）。
`
}

log(`開始 ${CHAPTERS.length} 章：補查 → 撰寫 → 雙裁判 → 修正 → 複驗`)

const results = await pipeline(
  CHAPTERS,
  // 1 補查
  async (ch) => {
    if (!ch.gaps.length) return { research: null }
    const r = await agent(researchPrompt(ch), { label: `research:${ch.id}`, phase: 'Research', model: 'sonnet', effort: 'high', schema: FACTS_SCHEMA })
    return { research: r }
  },
  // 2 撰寫
  async (prev, ch) => {
    const build = await agent(buildPrompt(ch, prev && prev.research), { label: `write:${ch.id}`, phase: 'Write', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
    return { ...prev, build }
  },
  // 3 雙裁判
  async (prev, ch) => {
    if (!prev.build) return { ...prev, judges: null }
    const [facts, voice] = await parallel([
      () => agent(judgeFactsPrompt(ch), { label: `judge-facts:${ch.id}`, phase: 'Judge', model: 'fable', effort: 'xhigh', schema: ISSUES_SCHEMA }),
      () => agent(judgeVoicePrompt(ch), { label: `judge-voice:${ch.id}`, phase: 'Judge', model: 'fable', effort: 'high', schema: ISSUES_SCHEMA }),
    ])
    const issues = [...((facts && facts.issues) || []).map(i => ({ ...i, lens: 'facts' })), ...((voice && voice.issues) || []).map(i => ({ ...i, lens: 'voice' }))]
    log(`${ch.id}：數字裁判 ${facts ? facts.verdict : '無'}（${facts ? facts.issues.length : 0} 條）、語氣裁判 ${voice ? voice.verdict : '無'}（${voice ? voice.issues.length : 0} 條）`)
    return { ...prev, judges: { facts, voice }, issues }
  },
  // 4 修正 ＋ 5 複驗（最多兩輪）
  async (prev, ch) => {
    if (!prev.build || !prev.issues) return { ...prev, fix: null, recheck: null }
    let issues = prev.issues
    let fix = null, recheck = null
    for (let round = 1; round <= 2; round++) {
      if (!issues.length) break
      fix = await agent(fixPrompt(ch, issues, round), { label: `fix${round}:${ch.id}`, phase: 'Fix', model: 'opus', effort: 'medium', schema: FIX_SCHEMA })
      const serious = issues.filter(i => i.severity !== 'minor')
      if (!serious.length) { recheck = { ok: true, checkerErrors: fix ? fix.checkerErrors : -1, remaining: [] }; break }
      recheck = await agent(recheckPrompt(ch, issues), { label: `recheck${round}:${ch.id}`, phase: 'Recheck', model: 'sonnet', effort: 'low', schema: RECHECK_SCHEMA })
      if (!recheck || recheck.ok) break
      issues = recheck.remaining
      log(`${ch.id}：複驗仍有 ${issues.length} 條，進第二輪`)
    }
    return { ...prev, fix, recheck }
  },
)

const summary = CHAPTERS.map((ch, i) => {
  const r = results[i]
  if (!r) return { id: ch.id, status: 'dropped' }
  const b = r.build || {}
  return {
    id: ch.id,
    status: r.build ? (r.recheck && r.recheck.ok === false ? 'unresolved' : 'done') : 'no-build',
    chars: (r.fix && r.fix.chars) || b.chars,
    questions: b.questions, today: b.today, gain: b.gain, worksheet: b.worksheet, terms: b.terms,
    sources: b.sourcesCount, omitted: b.omittedForLackOfSource,
    issueCounts: r.issues ? { total: r.issues.length, blocker: r.issues.filter(x => x.severity === 'blocker').length, major: r.issues.filter(x => x.severity === 'major').length } : null,
    fixSkipped: r.fix && r.fix.skipped, remaining: r.recheck && r.recheck.remaining,
    researchUnverified: r.research ? (r.research.facts || []).filter(f => f.confidence === 'unverified').map(f => f.item + ' ' + f.claim) : [],
  }
})
return summary
