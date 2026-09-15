export const meta = {
  name: 'family-finance-front-and-action',
  description: '研究檔同步修正 ＋ 導讀（含先看重點）與總行動清單撰寫、裁判、修正',
  phases: [
    { title: 'Sync', detail: 'applier 把章節裡已核對的數字同步回研究檔與大綱' },
    { title: 'Write', detail: '寫第 00 章導讀與第 16 章總行動清單' },
    { title: 'Judge', detail: '每章一位裁判（語氣版面＋數字）' },
    { title: 'Fix', detail: '修正與複驗' },
  ],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'
const TODAY = '2026-09-07'

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
    checkerErrors: { type: 'number' }, chars: { type: 'number' },
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
const BUILD_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' }, chars: { type: 'number' }, checkerErrors: { type: 'number' },
    checkerWarnings: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' },
  },
  required: ['file', 'chars', 'checkerErrors'],
}
const SYNC_SCHEMA = {
  type: 'object',
  properties: {
    done: { type: 'array', items: { type: 'string' } },
    skipped: { type: 'array', items: { type: 'object', properties: { item: { type: 'string' }, reason: { type: 'string' } }, required: ['item', 'reason'] } },
  },
  required: ['done', 'skipped'],
}

const SYNC_PROMPT = `
你是 applier，把章節檔裡已經被裁判逐字核對過的數字與等級，同步回研究檔與大綱。真相來源是各章 <ol class="sources"> 裡的條目。只改下面列出的項目，不改其他內容，不動 chapters/。每一項改完在該處加一行「（2026-09-07 依第 N 章來源同步）」。
1. ${ROOT}/research/tw-tax-bank.md 第 7 條（114 年度綜所稅級距）：最高級距門檻 500 萬 → 498 萬（4,980,001 元以上）、累進差額 913,700 → 911,700，信心等級升 verified。依據 ${ROOT}/chapters/11-tax.html 的 src-11-4、src-11-5。
2. ${ROOT}/outline.md §5 第 1 條括號內「59／133／266／500 萬與 41,300／147,700／413,700／913,700」→「59／133／266／498 萬與 41,300／147,700／413,700／911,700」。
3. ${ROOT}/research/tw-social-insurance.md「補 13」：補充保費獎金的計費，由「單次」改為「全年累計超過當月投保金額 4 倍的部分」，依全民健康保險法第 31 條；依據 chapters/11-tax.html 的 src-11-24。
4. ${ROOT}/research/tw-social-insurance.md §2.1、§2.3：補上勞工退休金條例第 14 條（雇主 6%、自提 6%）、第 24 條（請領年齡與年資）全國法規資料庫網址，§2.3 升 verified；依據 chapters/02-balance-sheet.html 的 src-02-1、src-02-3。
5. ${ROOT}/research/budget-behavior-family.md「補 1」：在 CFPB「500 到 1,000 美元起點」那句後加註「查證錯誤：裁判實際開啟頁面無此數字，不得引用」；依據 ${ROOT}/tools/state/judge-04.json 裡 facts 鏡頭的 blocker。
6. ${ROOT}/research/tw-tax-bank.md 第 23 條：「為近 5 年最低」加註「未見於原文；逐年比較依據見第 7 章 src-07-7（2021–2025：1.97／2.95／2.49／2.18／1.66）」。
7. ${ROOT}/research/tw-tax-bank.md 第 12 條的法條項次與第 14 條（證券交易稅條例第 2 條之 1，FL006079）的網址與信心等級，依據 chapters/09-rules-card.html 的來源條目修正。
8. ${ROOT}/research/investing-evidence.md 5.1 的期間與超額報酬描述、10.3 的美國遺產稅 40% 稅率：40% 回推不到出處，標 unverified 並註明「第 9 章正文已刪除稅率」。
9. ${ROOT}/research/ch-14.md 第 62、66、67 條：依 chapters/14-legacy.html 的 src-14-3、src-14-19、src-14-24 升 verified 並補網址。
10. ${ROOT}/outline.md §3「### 06-insurance」keyPoints 提到利變型保單「2027 年」新制之處，改成「2025-02-11 修正、2026-01-01 生效（verified）；第二波 2027 年為規劃中（likely）」。
做不到的項目寫進 skipped 並說明理由。回傳 StructuredOutput：done、skipped。
`

function frontPrompt() {
  return `
你是寫手，負責「家庭理財白話說明文件」第 00 章《怎麼用這份文件（先讀這頁，三分鐘）》。今天是 ${TODAY}。
必讀：${ROOT}/outline.md（§0、§1 版面規格、§2 語氣規範、§3 的「### 00-how-to-use」全部欄位——注意其中「作者 2026-09-07 追加」的『先看重點』要求）、${ROOT}/components.md、${ROOT}/design-brief.md 的「導讀與附錄的額外元素」一節（keypoints、checkup-table、q-index、triage、routes、manifesto 的 class 與結構）、以及 ${ROOT}/chapters/01 到 15 的每一章（至少讀每章的 <header> 與 <footer>：三個問題、讀完你做得到、時間列、你手上多了什麼、今天的一件事）。
產出 ${ROOT}/chapters/00-how-to-use.html，一個 <section class="chapter" id="ch-00" data-num="0" data-stage="0">，章首章尾照契約（三個問題用 outline 的原句；「今天的一件事」＝選一條路線並把準備物拍照存進手機）。正文順序固定：
1. 「這份文件不是什麼」：<div class="manifesto">，≤20 行白話清單，含：不是投資建議、不推薦商品、不做個人化投資／稅務／法律建議、作者是醫師不是金融從業人員、未收取任何金融機構報酬、未使用推薦連結、數字有查證日期但會過期、重大決定請找有執照的專業人員並先問對方怎麼收費、發現任何一條數字有誤請回報。
2. 「先看重點」：<div class="keypoints"><h3>先看重點</h3><ol>…</ol></div>，10 到 14 條，每條一句 ≤30 字、白話、只講事實與取捨、不下指令，句尾 <a href="#ch-NN">第 N 章</a>（可連多章）。順序照章節。這一段要讓人只讀它就抓到全書骨架。
3. 「你要花多少時間」三條路線：<div class="routes"> 用 .cards 三張（30 分鐘急救版／一個週末完整版／每週一章版約四個月），六欄照對照卡模板；只用時間描述，不帶價值判斷。
4. 「我現在最想解決哪一題」：<div class="triage"> 三題分流用 ol.steps（有沒有年利率高的債／有沒有半年內能動用的現金／有沒有人靠你的收入生活 → 第 5、4、6 章）。
5. 「從問題進來」：<ul class="q-index">，把 15 章的三個問題原句全部列出（45 句），每句連到該章。
6. 「健檢進度表」：<table class="checkup-table">，四欄：章名（必須是 <a href="#ch-NN">…</a>）｜大約幾分鐘（抄各章時間列）｜這章要產出的東西（抄各章「你手上多了什麼」第一條）｜完成（留空格，JS 會放勾選框）。00 到 17 都列（16、17 的產出寫「總清單與行事曆」「名詞表與來源」）。
7. 「章節怎麼互相依賴」：用 ol.steps 寫七個階段，每階段一句話說明會用到前面什麼。
8. 「現在先準備」：動手框（✍️ 動手，ul.checks）：最近三個月銀行對帳單與信用卡帳單、所有保單或保險存摺、勞保局行動服務 App 或自然人憑證、手機網銀。沒有也可以先讀。
9. 一句話說明術語點一下會展開、附錄有名詞表與會過期的數字一覽表。
語氣：像朋友把書遞給你時說的話；作者身分（想把事情講清楚的朋友、醫師、非金融從業人員）只在這裡出現一次。正文（不含 keypoints、q-index、checkup-table）約 1,200 字。
不引用任何制度數字（本章沒有來源清單也可以）。交件前執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/00-how-to-use.html" --loose，必須 0 錯誤，但章首章尾仍要完整。回傳 StructuredOutput：file、chars、checkerErrors、checkerWarnings、notes。
`
}

function actionPrompt() {
  return `
你是寫手，負責「家庭理財白話說明文件」第 16 章《總行動清單與一年的節奏》。今天是 ${TODAY}。
必讀：${ROOT}/outline.md（§1、§2、§3 的「### 16-action-list」全部欄位、§1 第 16 條行動清單三層）、${ROOT}/components.md、${ROOT}/design-brief.md 的「導讀與附錄的額外元素」（master-list、pair 的 class）、以及 ${ROOT}/chapters/01 到 15 每章的 <footer>（今天的一件事、你手上多了什麼、還沒解決）。研究檔在 ${ROOT}/research/：任何日期或制度事實（例如綜所稅申報月份、勞保局寄發通知、保單年度）都要能在研究檔找到 verified／likely 的來源並照契約列進本章來源清單；找不到就不寫成事實。
產出 ${ROOT}/chapters/16-action-list.html，<section class="chapter" id="ch-16" data-num="16" data-stage="7">，章首章尾照契約。內容：
1. 「第一週五件事」：全是查資料、列清單，各 ≤30 分鐘，從 15 章的「今天的一件事」裡挑並排序，寫成 ul.checks；每件標來自第幾章。
2. 「十二個月的節奏」：穩定期與緊縮期兩版並列（用兩張對照卡或兩欄表，表格 ≤3 欄：月份｜穩定期做什麼｜緊縮期做什麼），每月一件事，寫成「查什麼、算什麼、填哪張表、跟誰談」，不寫「買什麼」。
3. 「人生事件觸發表」：結婚、生小孩、換工作、買房、離婚、父母需要照顧、繼承、收入中斷——各列要重看哪幾章、重填哪幾張表（表格 ≤3 欄）。
4. 「年度健檢表（工作表⑫）」：動手框 id="ws-12"，worksheet 表格：淨值（第 2 章）、必要月支出（第 3 章）、緊急金月數（第 4 章）、債務總額與最高利率（第 5 章）、保額缺口（第 6 章）、投資規則卡是否照做（第 9 章）、勞保與勞退數字（第 10 章）、受益人是否更新（第 14 章），各一列，填寫日期在右上角。
5. 「家庭財務健檢總清單」：<div class="master-list"> 三段 <h4>：先做／再做／有餘力再做，每項 ul.checks，附章節連結 <a href="#ch-NN">，需要另一半一起做的項目加 <span class="pair">👥</span>。所有行動寫成動作，不放需要下判斷的項目。
6. 結尾：「現在就能做的三件事」（不花錢、不做任何投資決定），不勵志。
字數約 2,500（不含表格）。框 ≤7、動手框 ≤2。交件前執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/16-action-list.html"（若沒有任何引用則加 --loose），必須 0 錯誤。回傳 StructuredOutput：file、chars、checkerErrors、checkerWarnings、notes。
`
}

function judgePrompt(id, num, title, loose) {
  return `
你是裁判，對「家庭理財白話說明文件」第 ${num} 章《${title}》做對抗性驗證（語氣、版面、數字三合一）。任務是「試著推翻」。你只讀不改。
讀：${ROOT}/chapters/${id}.html、${ROOT}/outline.md（§1、§2、§3 該章全部欄位含 pitfalls）、${ROOT}/components.md、${ROOT}/design-brief.md「導讀與附錄的額外元素」。先執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${id}.html"${loose ? ' --loose' : ''}。
檢查：
1. 零基礎讀者測試：讀不懂的句子、術語未解釋、>40 字的句子、>4 句的段落。作者交代版面和語氣必須容易閱讀，這一項嚴格。
2. 語氣規範 12 條：禁用字眼、隱含指令（「你應該」「盡量」「一定要」）、恐嚇或勵志、預設處境。
3. 交叉一致：本章引用到的其他章內容（三個問題原句、今天的一件事、產出、章名、章號）要逐一對照 ${ROOT}/chapters/ 裡的實際檔案，抄錯就是 major；連結 #ch-NN 必須存在（00 到 17）。
4. 任何日期或制度事實都要有來源條目且在研究檔可回推；沒有就是 blocker。
5. 元件契約與額外元素的 class 用法；表格欄數（checkup-table 例外四欄）；框數。
${num === 0 ? '6. 「先看重點」：10–14 條、每條 ≤30 字、每條有章節連結、只講事實與取捨不下指令；健檢進度表章名欄是否為 <a href="#ch-NN">；45 句問題是否與各章原句一致。' : '6. 行動是否全是「查、算、填、談」而不是「買」；第一週五件事是否各 ≤30 分鐘；人生事件表是否覆蓋 outline 列出的事件。'}
回傳 StructuredOutput：verdict、issues（severity、where 原文逐字、problem、fix 可直接套用）、strengths。找不到就誠實 pass。
`
}

function fixPrompt(id, num, title, issues, loose) {
  return `
你是修稿者，處理第 ${num} 章《${title}》。檔案：${ROOT}/chapters/${id}.html。契約：${ROOT}/components.md；規範：${ROOT}/outline.md §1、§2。研究檔在 ${ROOT}/research/。
處理下面全部問題：blocker 與 major 必須修，minor 盡量修，修不了寫進 skipped 說明理由。不動其他檔案。改完的句子要更白話、更短。
${JSON.stringify(issues, null, 1)}
修完執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${id}.html"${loose ? ' --loose' : ''}，必須 0 錯誤。回傳 StructuredOutput：file、applied、skipped、checkerErrors、chars。
`
}

function recheckPrompt(id, issues, loose) {
  return `
你是複驗員。檔案：${ROOT}/chapters/${id}.html。先執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${id}.html"${loose ? ' --loose' : ''}。逐條確認下面 blocker／major 是否真的修掉。你只讀不改。
${JSON.stringify(issues.filter(i => i.severity !== 'minor'), null, 1)}
回傳 StructuredOutput：ok、checkerErrors、remaining。
`
}

const CH = [
  { id: '00-how-to-use', num: 0, title: '怎麼用這份文件（先讀這頁，三分鐘）', loose: true, prompt: frontPrompt() },
  { id: '16-action-list', num: 16, title: '總行動清單與一年的節奏', loose: false, prompt: actionPrompt() },
]

phase('Sync')
const syncP = agent(SYNC_PROMPT, { label: 'sync:research-files', phase: 'Sync', model: 'sonnet', effort: 'medium', schema: SYNC_SCHEMA })

const chapters = await pipeline(
  CH,
  async (ch) => {
    const build = await agent(ch.prompt, { label: `write:${ch.id}`, phase: 'Write', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
    return { build }
  },
  async (prev, ch) => {
    if (!prev.build) return { ...prev, judge: null }
    const judge = await agent(judgePrompt(ch.id, ch.num, ch.title, ch.loose), { label: `judge:${ch.id}`, phase: 'Judge', model: 'fable', effort: 'xhigh', schema: ISSUES_SCHEMA })
    log(`${ch.id}：裁判 ${judge ? judge.verdict : '無'}（${judge ? judge.issues.length : 0} 條）`)
    return { ...prev, judge }
  },
  async (prev, ch) => {
    if (!prev.judge || !prev.judge.issues.length) return { ...prev, fix: null, recheck: null }
    let issues = prev.judge.issues, fix = null, recheck = null
    for (let round = 1; round <= 2; round++) {
      if (!issues.length) break
      fix = await agent(fixPrompt(ch.id, ch.num, ch.title, issues, ch.loose), { label: `fix${round}:${ch.id}`, phase: 'Fix', model: 'opus', effort: 'medium', schema: FIX_SCHEMA })
      if (!issues.some(i => i.severity !== 'minor')) { recheck = { ok: true, remaining: [] }; break }
      recheck = await agent(recheckPrompt(ch.id, issues, ch.loose), { label: `recheck${round}:${ch.id}`, phase: 'Fix', model: 'sonnet', effort: 'low', schema: RECHECK_SCHEMA })
      if (!recheck || recheck.ok) break
      issues = recheck.remaining
    }
    return { ...prev, fix, recheck }
  },
)

const sync = await syncP
return {
  sync,
  chapters: CH.map((ch, i) => {
    const r = chapters[i] || {}
    return { id: ch.id, built: !!r.build, chars: r.fix ? r.fix.chars : (r.build && r.build.chars), issues: r.judge ? r.judge.issues.length : null, applied: r.fix && r.fix.applied, skipped: r.fix && r.fix.skipped, remaining: r.recheck && r.recheck.remaining, notes: r.build && r.build.notes }
  }),
}
