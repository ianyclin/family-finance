export const meta = {
  name: 'family-finance-finish-chapters',
  description: '補完第 2–15 章缺的關卡：缺的裁判補派、已有裁判結果的直接修正、修完複驗',
  phases: [
    { title: 'Judge', detail: '只補派缺的裁判（數字／語氣）' },
    { title: 'Fix', detail: '合併第一輪與新裁判的問題後修正' },
    { title: 'Recheck', detail: '複驗 blocker 與 major' },
  ],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'
const two = n => String(n).padStart(2, '0')

// state：facts／voice 為 true 表示第一輪裁判結果已存在 tools/state/judge-NN.json
const CHAPTERS = [
  { id: '02-balance-sheet', num: 2, title: '先照一張全家福：家庭資產負債表', files: ['budget-behavior-family.md', 'tw-tax-bank.md', 'tw-social-insurance.md'], facts: true, voice: true },
  { id: '04-emergency-fund', num: 4, title: '緊急預備金：家裡的滅火器', files: ['budget-behavior-family.md', 'tw-tax-bank.md'], facts: true, voice: true },
  { id: '05-debt', num: 5, title: '債務：先把會漏水的地方補起來', files: ['insurance-debt-scam.md', 'tw-tax-bank.md'], facts: false, voice: false },
  { id: '06-insurance', num: 6, title: '保險：先看已經有的，再補賠不起的', files: ['insurance-debt-scam.md', 'tw-social-insurance.md'], facts: false, voice: false },
  { id: '07-time-inflation-compounding', num: 7, title: '投資第一課：時間、通膨、複利，還有報酬從哪裡來', files: ['investing-evidence.md', 'tw-tax-bank.md'], facts: false, voice: true },
  { id: '08-risk-diversification-cost', num: 8, title: '投資第二課：風險、分散、費用，以及「買下平均」是什麼意思', files: ['investing-evidence.md'], facts: false, voice: false },
  { id: '09-rules-card', num: 9, title: '投資第三課：把投資變成制度——分桶、路徑、投入方式、規則卡', files: ['investing-evidence.md', 'budget-behavior-family.md'], facts: true, voice: true },
  { id: '10-retirement', num: 10, title: '退休：先查出你已經有的，再算差多少', files: ['tw-social-insurance.md', 'investing-evidence.md', 'tw-tax-bank.md'], facts: true, voice: true },
  { id: '11-tax', num: 11, title: '稅：看懂它怎麼算，比背數字有用', files: ['tw-tax-bank.md', 'tw-social-insurance.md'], facts: false, voice: false },
  { id: '12-housing', num: 12, title: '房子：租與買，把兩邊的帳都算出來', files: ['insurance-debt-scam.md', 'tw-tax-bank.md'], facts: true, voice: false },
  { id: '13-family', num: 13, title: '家裡不只你一個人：伴侶、小孩、父母、長照', files: ['budget-behavior-family.md', 'tw-tax-bank.md'], facts: false, voice: false },
  { id: '14-legacy', num: 14, title: '萬一：受益人、失能、繼承', files: ['budget-behavior-family.md', 'insurance-debt-scam.md', 'tw-tax-bank.md', 'tw-social-insurance.md'], facts: false, voice: false },
  { id: '15-scams', num: 15, title: '陷阱與詐騙：三個問題篩掉九成', files: ['insurance-debt-scam.md', 'investing-evidence.md'], facts: false, voice: false },
]

const skip = new Set((args && args.skip) || [])

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

function judgeFactsPrompt(ch) {
  return `
你是數字與來源裁判，對「家庭理財白話說明文件」第 ${ch.num} 章《${ch.title}》做對抗性驗證。你的任務是「試著推翻」，不是找優點。你只讀不改：不得修改任何檔案。
讀：${ROOT}/chapters/${ch.id}.html、${ROOT}/outline.md（§3 該章、§5 事實衝突、§6 拍板）、研究檔 ${ch.files.map(f => ROOT + '/research/' + f).join('、')}、${ROOT}/research/ch-${two(ch.num)}.md（若存在）、${ROOT}/research/gap-fill.md。
逐項檢查：
1. 正文每個帶數字的句子：回研究檔找到同一個數字與來源；數字、年度、機構、網址、等級符號（●◐◑○）任何一項對不上就是 blocker。研究檔標 likely 的，來源條目必須有「（轉引，待官方原檔核對）」；標 unverified 的不得以事實語氣出現。
2. 所有算式用 Bash 跑 Python 重算，差一位數就是 blocker。
3. 挑 3 到 5 個最高風險的網址（法條、稅、給付、利率）用 WebFetch 實際打開（先 ToolSearch select:WebFetch），核對數字仍然有效；打不開就記錄，不算錯。
4. §5 事實衝突的 15 條裁定與 §6 拍板有沒有被違反。
5. 有沒有沒附來源的數字、「本文自算」沒標○、隱含預測（「長期會漲」）。
6. 有沒有任何商品名、代號、公司名、平台名。
7. 報酬率／年化／未來金額的同一框或小節有沒有「這是假設，不是承諾」。
回傳 StructuredOutput：verdict（pass／fix／rewrite）、issues（每條 severity、where＝原文逐字引述、problem、fix＝可以直接套用的替換文字或明確指令）、strengths 一句。找不到問題就誠實回 pass。
`
}
function judgeVoicePrompt(ch) {
  return `
你是語氣與版面裁判，對「家庭理財白話說明文件」第 ${ch.num} 章《${ch.title}》做對抗性驗證。任務是「試著推翻」。你只讀不改：不得修改任何檔案。
讀：${ROOT}/chapters/${ch.id}.html、${ROOT}/outline.md（§1 版面規格、§2 語氣規範、§3 該章全部欄位含 pitfalls）、${ROOT}/components.md。先執行
  python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${ch.id}.html"
把錯誤與警告納入 issues。
逐項檢查：
1. 零基礎讀者測試：把自己當成完全沒基礎的朋友逐段讀，列出讀不懂的句子、沒解釋就用的術語、超過 40 字的句子、超過 4 句的段落、一段塞太多概念的地方。作者特別交代：版面和語氣必須容易閱讀，這一項請嚴格。
2. 語氣規範 12 條逐條對照：禁用字眼、隱含推薦（「多數人選擇」「聰明的做法」也算）、恐嚇或勵志、評價過去、預設雙薪有房有小孩、「老公／老婆」、驚嘆號、表情符號。
3. 不替讀者下結論：每個取捨框有沒有偷偷把一邊寫得比較好；底句有沒有填成具體內容；outline 該章 pitfalls 列的錯誤有沒有犯。
4. 章首五件、章尾五件順序與內容；三個問題是否照抄 outline 原句；「今天的一件事」是否 ≤10 分鐘、手機可完成、有完成判準。
5. 元件契約：只用允許的元素與 class；框 ≤7、動手框 ≤2；表格 ≤3 欄；對照卡六欄；術語 dfn 格式與「比喻哪裡不成立」；圖有 figcaption 與「示意・非承諾」。
6. 字數是否在 outline targetLength ±15% 內；小節數 3–7；每章比喻 ≤3、醫療類比 ≤1。
回傳 StructuredOutput：verdict、issues（severity、where＝原文逐字引述、problem、fix＝可直接套用的替換文字）、strengths 一句。找不到問題就誠實回 pass。
`
}
function fixPrompt(ch, newIssues, hasState, round) {
  return `
你是修稿者，處理「家庭理財白話說明文件」第 ${ch.num} 章《${ch.title}》${round > 1 ? '（第二輪）' : ''}。
檔案：${ROOT}/chapters/${ch.id}.html。契約：${ROOT}/components.md。語氣與版面規範：${ROOT}/outline.md §1、§2。研究檔在 ${ROOT}/research/。
問題來源有兩處，全部處理：
${hasState ? `(a) 第一輪裁判結果檔 ${ROOT}/tools/state/judge-${two(ch.num)}.json（讀它的 issues 陣列；注意檔案可能已被小幅修改，where 的引文找不到時用語意定位）。` : '(a) 無第一輪結果。'}
(b) 本輪新裁判的問題（下方 JSON）。
規則：blocker 與 major 必須修；minor 盡量修，修不了要在 skipped 說明理由。修 blocker 時若需要數字，只能用研究檔裡 verified／likely 的數字；沒有就改成質性描述。不要改動沒被點到的段落，字數維持在 outline targetLength ±15%。作者特別交代：版面和語氣必須容易閱讀，改完的句子要比原本更白話、更短。
本輪新問題：
${JSON.stringify(newIssues, null, 1)}
修完執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${ch.id}.html"，必須 0 個錯誤。不要動其他檔案。
回傳 StructuredOutput：file、applied、skipped（哪條、為什麼）、checkerErrors、checkerWarnings、chars。
`
}
function recheckPrompt(ch, newIssues, hasState) {
  return `
你是複驗員。檔案：${ROOT}/chapters/${ch.id}.html。先執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${ch.id}.html"。
然後逐條確認 blocker 與 major 問題是否真的修掉：問題清單來自 ${hasState ? `${ROOT}/tools/state/judge-${two(ch.num)}.json 的 issues（只看 severity 為 blocker／major 的）以及` : ''}下方 JSON。在檔案裡找到修改後的文字，確認符合 fix 的要求，且沒有引入新的禁用字眼或商品名。你只讀不改。
${JSON.stringify(newIssues.filter(i => i.severity !== 'minor'), null, 1)}
回傳 StructuredOutput：ok（全部修掉且哨兵 0 錯誤才 true）、checkerErrors、remaining（還沒修好的，附 severity、where、problem、fix）。
`
}

const todo = CHAPTERS.filter(ch => !skip.has(ch.id))
log(`補完 ${todo.length} 章`)

const results = await pipeline(
  todo,
  // 1 缺的裁判
  async (ch) => {
    const jobs = []
    if (!ch.facts) jobs.push(() => agent(judgeFactsPrompt(ch), { label: `judge-facts:${ch.id}`, phase: 'Judge', model: 'fable', effort: 'xhigh', schema: ISSUES_SCHEMA }).then(r => ({ lens: 'facts', r })))
    if (!ch.voice) jobs.push(() => agent(judgeVoicePrompt(ch), { label: `judge-voice:${ch.id}`, phase: 'Judge', model: 'fable', effort: 'high', schema: ISSUES_SCHEMA }).then(r => ({ lens: 'voice', r })))
    const out = jobs.length ? (await parallel(jobs)).filter(Boolean) : []
    const newIssues = out.flatMap(o => ((o.r && o.r.issues) || []).map(i => ({ ...i, lens: o.lens })))
    const failed = jobs.length - out.filter(o => o.r).length
    log(`${ch.id}：新裁判 ${out.length} 位，新問題 ${newIssues.length} 條${failed ? `，${failed} 位失敗` : ''}`)
    return { newIssues, judgesFailed: failed }
  },
  // 2 修正 ＋ 3 複驗（最多兩輪）
  async (prev, ch) => {
    const hasState = ch.facts || ch.voice
    let issues = prev.newIssues
    let fix = null, recheck = null
    for (let round = 1; round <= 2; round++) {
      if (round === 1 && !hasState && !issues.length) break
      if (round === 2 && !issues.length) break
      fix = await agent(fixPrompt(ch, issues, hasState && round === 1, round), { label: `fix${round}:${ch.id}`, phase: 'Fix', model: 'opus', effort: 'medium', schema: FIX_SCHEMA })
      recheck = await agent(recheckPrompt(ch, issues, hasState && round === 1), { label: `recheck${round}:${ch.id}`, phase: 'Recheck', model: 'sonnet', effort: 'low', schema: RECHECK_SCHEMA })
      if (!recheck || recheck.ok) break
      issues = recheck.remaining
      log(`${ch.id}：複驗仍有 ${issues.length} 條，進第二輪`)
    }
    return { ...prev, fix, recheck }
  },
)

return todo.map((ch, i) => {
  const r = results[i]
  if (!r) return { id: ch.id, status: 'dropped' }
  return {
    id: ch.id,
    status: r.fix ? (r.recheck && r.recheck.ok === false ? 'unresolved' : 'fixed') : 'no-fix',
    newIssues: r.newIssues.length, judgesFailed: r.judgesFailed,
    applied: r.fix && r.fix.applied, skipped: r.fix && r.fix.skipped, chars: r.fix && r.fix.chars,
    checkerErrors: r.fix && r.fix.checkerErrors, remaining: r.recheck && r.recheck.remaining,
  }
})
