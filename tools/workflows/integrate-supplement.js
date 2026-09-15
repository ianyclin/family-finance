export const meta = {
  name: 'family-finance-integrate-supplement',
  description: '把裁定通過的補充素材與作者七條原則整合進 01、07、08、09、10、15 章（整合→雙裁判→修正→複驗），再寫第 17 章附錄並驗證',
  phases: [
    { title: 'Integrate', detail: '依 supplement-plan.md 把改寫句、表、圖加進六章' },
    { title: 'Judge', detail: '數字與來源／語氣與版面兩位裁判' },
    { title: 'Fix', detail: '修正與複驗' },
    { title: 'Appendix', detail: '第 17 章名詞表、會過期的數字、待查清單、修訂紀錄' },
  ],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'
const TODAY = '2026-09-07'
const two = n => String(n).padStart(2, '0')

const TARGETS = [
  { id: '01-why-and-order', num: 1, title: '理財到底在解決什麼問題（以及錢該怎麼排隊）', chars: 3289, claims: 'C9（滿足點，正文一段＋事實框三篇論文）、C10（多存 vs 現在花取捨框＋113 年五等分位事實框）、C12／C20（摩根三欄一句引用，表在第 10 章）', files: ['supp-happiness-humancapital.md', 'supp-dgbas-quintile.md', 'supp-taiwan-lifetable-jpm.md', 'budget-behavior-family.md'] },
  { id: '07-time-inflation-compounding', num: 7, title: '投資第一課：時間、通膨、複利，還有報酬從哪裡來', chars: 3371, claims: 'C9（甜蜜點算式框，依 research/author-principles.md 的算術）、C2／C18（每筆錢有自己的日期，正文一段；不畫新圖）、C3（歷史上多數期間：DMS 數字事實框＋四次回撤與日本台灣反例）、C19（每年投入 1 萬美元、7% 的里程碑改成表，標幣別）、C11／C28（四個人比較：用 Python 自算台幣版對照表，並引 JPM 為存在性來源）、C17（既有鋸齒圖保留，補圖說）', files: ['supp-market-history.md', 'supp-taiwan-lifetable-jpm.md', 'supp-author-sources.md', 'investing-evidence.md', 'author-principles.md'] },
  { id: '08-risk-diversification-cost', num: 8, title: '投資第二課：風險、分散、費用，以及「買下平均」是什麼意思', chars: 4364, claims: 'C6（SPIVA 2024 年底 10／15／20 年與存活率，升 verified；台灣機構版報告不引，只寫「台灣沒有公開版本」）、C7／C24／C32（單一市場 vs 全球取捨框；輪替沒有時鐘：MSCI 官方 10 年數字＋DMS「美國是例外」＋Hartford 2019 預測失準，合併成一個事實框或誤解框）、C22／C26／C16（年內最大跌幅 vs 全年報酬：JPM 最新版 14.2%／35 of 46 加台股自算版；持有期間區間收窄要換 1950–2018 版並附日本台灣反例；四次大回撤回本年數；合併成一個事實框＋一張三欄表）、C23（輪動表改正文一段，不放表）、C14／C15（賣出理由千百種：誤解框，附 2009 起算的選樣效果說明）', files: ['supp-spiva.md', 'supp-market-history.md', 'supp-timing-dca.md', 'supp-taiwan-dca-compute.md', 'investing-evidence.md', 'author-principles.md'] },
  { id: '09-rules-card', num: 9, title: '投資第三課：把投資變成制度——分桶、路徑、投入方式、規則卡', chars: 3679, claims: 'C4／C5（台股自算：買在月高／收盤／月低三情境，與七種頻率；先重跑 tools/twse_dca.py 與 tools/twse_dca_freq.py 核對數字再寫；一個算式框＋一張三欄表）、C13／C25（擇時的證據兩面：Schwab 五人＋Vanguard 單筆 vs 分批＋錯過最好與最差日子並列；一個事實框，Maggiulli 只列存在性線索與書名）、C27（分桶：既有圖保留，正文補「一種常見分法」）、C8 與作者七條原則（依 research/author-principles.md 寫「作者自己的做法（不是推薦）」框：<aside class="box fact author">，每條附代價，商品名只在這框內並註明「同類商品很多檔，列名不是推薦」）', files: ['supp-taiwan-dca-compute.md', 'supp-timing-dca.md', 'supp-author-sources.md', 'investing-evidence.md', 'author-principles.md'] },
  { id: '10-retirement', num: 10, title: '退休：先查出你已經有的，再算差多少', chars: 4363, claims: 'C20（摩根六面向三欄表，事實）、C31（台灣 113 年簡易生命表自算：65 歲活到 75／80／85 的機率，男女與夫妻至少一人，三欄表，標○本文自算與●內政部資料）、C21／C30 已 drop 不放', files: ['supp-taiwan-lifetable-jpm.md', 'tw-social-insurance.md', 'investing-evidence.md'] },
  { id: '15-scams', num: 15, title: '陷阱與詐騙：先問三個問題', chars: 3448, claims: 'C1（報酬／時間／風險三樣只拿得到兩樣：警語框改寫句＋可選一張三圓示意圖標「示意・非承諾」，附「用時間換低風險也有例外」）', files: ['supp-market-history.md', 'supp-timing-dca.md', 'insurance-debt-scam.md'] },
]

const BUILD_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' }, chars: { type: 'number' }, checkerErrors: { type: 'number' },
    added: { type: 'array', items: { type: 'string' } }, replaced: { type: 'array', items: { type: 'string' } },
    omitted: { type: 'array', items: { type: 'string' } }, newTerms: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' },
  },
  required: ['file', 'chars', 'checkerErrors', 'added'],
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

function integratePrompt(t) {
  const limit = Math.round(t.chars * 1.2)
  return `
你是寫手，負責把作者補充的素材整合進「家庭理財白話說明文件」第 ${t.num} 章《${t.title}》。今天是 ${TODAY}。
必讀（照順序）：
1. ${ROOT}/supplement-plan.md：§0 總表、§1 裡本章負責的條目（${t.claims}）、§2 factErrors、§3 unresolved、§4 本章的框預算與合併建議、§5。裁定是 rewrite 的一律用它給的 rewritten 句為底（可再白話化，不可改變意思）；drop 的不放。
2. ${ROOT}/chapters/${t.id}.html（現有章節，已通過兩位裁判）、${ROOT}/components.md、${ROOT}/outline.md §1 §2。
3. 研究檔：${t.files.map(f => ROOT + '/research/' + f).join('、')}。只能引用 verified／likely 的事實；每個新數字都要加來源條目（six 段格式、等級符號、查證日期），likely 要註明轉引；本文自算標○並附算式。
主線決定：
- 台灣 SPIVA 機構版報告不引。
- 每章最多新增一張圖；其他用三欄表或對照卡；框總數仍 ≤7、動手框 ≤2（依 §4 的合併建議，必要時把既有的框合併或改成表）。
- 字數上限 ${limit} 字（現在 ${t.chars}）。優先「替換」寫得弱或重複的段落，而不是純加。作者一再交代：版面和語氣必須容易閱讀，新增的每一句都要比原本的平均句更短更白。
- 不下指令、不預測；「歷史上多數期間」「影響很小：數字」「這一題沒有標準答案，只有你知道＿＿＿」句式。
- 第 9 章：作者自己的做法框只在第 9 章出現一次，用 <aside class="box fact author">，內容依 research/author-principles.md，每條附代價；商品名只在這個框內。
- 引用 tools/twse_dca.py、tools/twse_dca_freq.py 的自算數字前，先用 Bash 重跑腳本（若需要網路且失敗，改用 research/data/ 裡既有 CSV 並註明），數字對得上才寫。
- 章首章尾結構不動（三個問題、今天的一件事保持原樣）；「還沒解決」與來源清單可以增修。
- 術語：新引入的術語若已在其他章有 dfn（用 grep -l 'def-術語' chapters/ 檢查），本章不再包 dfn。
產出：覆寫 ${ROOT}/chapters/${t.id}.html。完成後執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${t.id}.html"，必須 0 錯誤。不要動其他檔案。
回傳 StructuredOutput：file、chars、checkerErrors、added（加了哪些元件，一行一個）、replaced（替換掉哪些段落）、omitted（裁定可用但你沒放的，附理由）、newTerms、notes。
`
}

function judgeFactsPrompt(t) {
  return `
你是數字與來源裁判，對第 ${t.num} 章《${t.title}》（剛整合完補充素材）做對抗性驗證。你只讀不改。
讀：${ROOT}/chapters/${t.id}.html、${ROOT}/supplement-plan.md（本章條目與 §2 factErrors）、研究檔 ${t.files.map(f => ROOT + '/research/' + f).join('、')}、${ROOT}/research/ch-${two(t.num)}.md（若存在）。
檢查：每個帶數字的句子回研究檔或 supplement 檔找到同一個數字、年度、機構、網址、等級；自算數字用 Bash 重跑 Python（或重跑 tools/twse_dca*.py）核對；裁定為 drop 的內容不得出現；SPIVA 台灣機構版不得引用；rewrite 條目的意思不得被改回指令或預測；商品名只允許在 <aside class="box fact author"> 內（且只在第 9 章）；每個新來源都被引用、每個引用都有條目；有報酬率處有「這是假設，不是承諾」。
回傳 StructuredOutput：verdict、issues（severity、where 逐字、problem、fix 可直接套用）、strengths。找不到就誠實 pass。
`
}
function judgeVoicePrompt(t) {
  const limit = Math.round(t.chars * 1.2)
  return `
你是語氣與版面裁判，對第 ${t.num} 章《${t.title}》（剛整合完補充素材）做對抗性驗證。你只讀不改。
讀：${ROOT}/chapters/${t.id}.html、${ROOT}/outline.md §1 §2 與 §3 該章 pitfalls、${ROOT}/components.md、${ROOT}/supplement-plan.md §4。先執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${t.id}.html"。
檢查：1) 零基礎讀者測試，新加的段落是否比原本更難讀（>40 字句、>4 句段、術語未解釋）——作者交代版面和語氣必須容易閱讀，嚴格；2) 語氣 12 條，特別是新段落有沒有把 rewrite 句改回「你應該」「Hold」「盡量」「長期會漲」；3) 框 ≤7、動手框 ≤2、圖 ≤ 原有＋1、表 ≤3 欄、對照卡六欄；4) 字數是否 ≤ ${limit}；5) 新舊段落是否重複講同一件事（重複就是 major，指出該刪哪一段）；6) 章首章尾未被破壞；7) 第 9 章作者框是否標「不是推薦」、每條附代價。
回傳 StructuredOutput：verdict、issues、strengths。
`
}
function fixPrompt(t, issues, round) {
  return `
你是修稿者，處理第 ${t.num} 章《${t.title}》${round > 1 ? '（第二輪）' : ''}。檔案：${ROOT}/chapters/${t.id}.html。契約：${ROOT}/components.md；規範：${ROOT}/outline.md §1 §2；素材裁定：${ROOT}/supplement-plan.md；研究檔在 ${ROOT}/research/。
處理下面全部問題：blocker 與 major 必須修，minor 盡量修，修不了寫進 skipped 說明理由。修出來的句子要更短更白。不動其他檔案。
${JSON.stringify(issues, null, 1)}
修完執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${t.id}.html"，必須 0 錯誤。回傳 StructuredOutput：file、applied、skipped、checkerErrors、chars。
`
}
function recheckPrompt(t, issues) {
  return `
你是複驗員。檔案：${ROOT}/chapters/${t.id}.html。先執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${t.id}.html"。逐條確認下面 blocker／major 是否真的修掉，且沒有引入禁用字眼或商品名（作者框除外）。你只讀不改。
${JSON.stringify(issues.filter(i => i.severity !== 'minor'), null, 1)}
回傳 StructuredOutput：ok、checkerErrors、remaining。
`
}

const results = await pipeline(
  TARGETS,
  async (t) => ({ build: await agent(integratePrompt(t), { label: `integrate:${t.id}`, phase: 'Integrate', model: 'opus', effort: 'high', schema: BUILD_SCHEMA }) }),
  async (prev, t) => {
    if (!prev.build) return { ...prev, issues: null }
    const [facts, voice] = await parallel([
      () => agent(judgeFactsPrompt(t), { label: `judge-facts:${t.id}`, phase: 'Judge', model: 'fable', effort: 'xhigh', schema: ISSUES_SCHEMA }),
      () => agent(judgeVoicePrompt(t), { label: `judge-voice:${t.id}`, phase: 'Judge', model: 'fable', effort: 'high', schema: ISSUES_SCHEMA }),
    ])
    const issues = [...((facts && facts.issues) || []).map(i => ({ ...i, lens: 'facts' })), ...((voice && voice.issues) || []).map(i => ({ ...i, lens: 'voice' }))]
    log(`${t.id}：數字 ${facts ? facts.verdict : '失敗'}（${facts ? facts.issues.length : 0}）、語氣 ${voice ? voice.verdict : '失敗'}（${voice ? voice.issues.length : 0}）`)
    return { ...prev, issues, judgesFailed: (facts ? 0 : 1) + (voice ? 0 : 1) }
  },
  async (prev, t) => {
    if (!prev.issues || !prev.issues.length) return { ...prev, fix: null, recheck: null }
    let issues = prev.issues, fix = null, recheck = null
    for (let round = 1; round <= 2; round++) {
      if (!issues.length) break
      fix = await agent(fixPrompt(t, issues, round), { label: `fix${round}:${t.id}`, phase: 'Fix', model: 'opus', effort: 'medium', schema: FIX_SCHEMA })
      if (!issues.some(i => i.severity !== 'minor')) { recheck = { ok: true, remaining: [] }; break }
      recheck = await agent(recheckPrompt(t, issues), { label: `recheck${round}:${t.id}`, phase: 'Fix', model: 'sonnet', effort: 'low', schema: RECHECK_SCHEMA })
      if (!recheck || recheck.ok) break
      issues = recheck.remaining
    }
    return { ...prev, fix, recheck }
  },
)

phase('Appendix')
const appendixPrompt = `
你是寫手，負責「家庭理財白話說明文件」第 17 章《附錄：名詞表、來源清單、會過期的數字、空白工作表》。今天是 ${TODAY}。
必讀：${ROOT}/outline.md（§1 第 7、8、10、17、18 條與 §3「### 17-glossary-sources」）、${ROOT}/components.md、${ROOT}/design-brief.md「導讀與附錄的額外元素」（glossary、expiry、revisions、swipe-hint、wide、version-line 的 class）、${ROOT}/supplement-plan.md §3 unresolved、${ROOT}/research/gap-fill.md。然後掃描全部章節：
  grep -o 'data-term="[^"]*"' "${ROOT}"/chapters/*.html | sort | uniq -c
  grep -o '<span class="badge">[^<]*</span>' "${ROOT}"/chapters/*.html | sort | uniq -c
  grep -n '轉引，待官方原檔核對' "${ROOT}"/chapters/*.html
產出 ${ROOT}/chapters/17-glossary-sources.html，<section class="chapter" id="ch-17" data-num="17" data-stage="8">，章首照契約（三個問題：「這個詞是什麼意思？」「這個數字還對嗎？」「哪些東西還沒查到？」；讀完你做得到：查任何一個詞、知道哪個數字幾月要重查、找到空白工作表），章尾照契約（今天的一件事：把「會過期的數字一覽表」的下次重查月份加進手機行事曆；來源清單可只列本章引用的官方入口，沒有就用 --loose）。內容順序：
1. 名詞表 <dl class="glossary">：每個 data-term 一條，<dt id="term-＜術語＞">術語</dt><dd>白話定義一到兩句＋「第 N 章」連結</dd>；定義要跟該章 dfn 所在句一致（讀那一句）。依筆畫或注音排序皆可，但同類的放一起。約 60 條以內。
2. 來源怎麼讀：四級符號說明（●◐◑○）與「轉引」的意思，三到五句。
3. 會過期的數字一覽表：<div class="table-wrap wide"><p class="swipe-hint">可左右滑動</p><table class="expiry"> 五欄：數字｜適用年度｜上次確認日｜官方查證連結｜建議重查月份。從各章事實框裡把「制度性、每年會變」的數字全部收進來（免稅額與扣除額、級距、投保薪資分級表、勞退提繳、健保費率與補充保費、存款保險額度、循環利率上限、遺產贈與稅免稅額、房貸管制、房地合一、就學貸款利率、五大銀行利率、CPI 年增率、勞保基金精算），連結用該章來源條目的網址，建議重查月份依制度公告習慣（例如所得稅每年 12 月與 5 月、投保薪資每年 1 月）。
4. 待查清單：把各章來源條目裡標「轉引，待官方原檔核對」的、研究檔 unverified 的、supplement-plan §3 需要作者提供的，整理成三欄表（項目｜目前依據｜要去哪裡查），供作者或下一版處理。
5. 空白工作表：十二張工作表的清單，每項連到 #ws-1 … #ws-12（不重印）。
6. 修訂紀錄 <table class="revisions">：版本 1.0｜${TODAY}｜初版｜—。
7. <p class="version-line">本版完成日 ${TODAY} ／ 本版數字截止日 ${TODAY} ／ 下次建議重查 2027-01</p>，以及勘誤回報一句（「發現任何一條數字有誤，告訴給你這份文件的人」）。
字數約 4,000（名詞表 3,000＋其他 1,000；表格不計）。交件前執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/17-glossary-sources.html" --loose，必須 0 錯誤；並確認每個 data-term 都有對應的 term- id（用 grep 比對）。不動其他檔案。
回傳 StructuredOutput：file、chars、checkerErrors、added、notes（列出名詞表條數、一覽表列數、待查清單列數、有沒有 data-term 找不到定義句的）。
`
const appendix = await agent(appendixPrompt, { label: 'write:17-glossary-sources', phase: 'Appendix', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
let appendixJudge = null, appendixFix = null
if (appendix) {
  appendixJudge = await agent(`
你是裁判，對第 17 章附錄做對抗性驗證。你只讀不改。讀 ${ROOT}/chapters/17-glossary-sources.html、${ROOT}/components.md、${ROOT}/design-brief.md 額外元素、${ROOT}/outline.md §1 §2。先執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/17-glossary-sources.html" --loose。
檢查：1) 每個章節裡的 data-term（grep -o 'data-term="[^"]*"' chapters/*.html）都有 <dt id="term-…">，反之名詞表沒有多出章節沒用的詞；2) 每條定義是否與該章 dfn 所在句一致、是否白話、≤2 句；3) 會過期的數字一覽表：抽查 10 個數字回各章事實框核對數字、年度、網址一致，遺漏的制度數字列出；4) 待查清單是否涵蓋各章「轉引」條目（grep 計數比對）；5) 表格 class 與 swipe-hint；6) 語氣 12 條；7) 章首章尾。
回傳 StructuredOutput：verdict、issues、strengths。
`, { label: 'judge:17-glossary-sources', phase: 'Appendix', model: 'fable', effort: 'xhigh', schema: ISSUES_SCHEMA })
  if (appendixJudge && appendixJudge.issues.length) {
    appendixFix = await agent(`
你是修稿者，處理第 17 章附錄。檔案：${ROOT}/chapters/17-glossary-sources.html。契約：${ROOT}/components.md；額外元素：${ROOT}/design-brief.md。處理全部問題（blocker／major 必修）。不動其他檔案。
${JSON.stringify(appendixJudge.issues, null, 1)}
修完執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/17-glossary-sources.html" --loose，必須 0 錯誤。回傳 StructuredOutput：file、applied、skipped、checkerErrors、chars。
`, { label: 'fix:17-glossary-sources', phase: 'Appendix', model: 'opus', effort: 'medium', schema: FIX_SCHEMA })
  }
}

return {
  chapters: TARGETS.map((t, i) => {
    const r = results[i] || {}
    return { id: t.id, built: !!r.build, chars: r.fix ? r.fix.chars : (r.build && r.build.chars), added: r.build && r.build.added, omitted: r.build && r.build.omitted, issues: r.issues ? r.issues.length : null, judgesFailed: r.judgesFailed, applied: r.fix && r.fix.applied, skipped: r.fix && r.fix.skipped, remaining: r.recheck && r.recheck.remaining }
  }),
  appendix: appendix && { chars: appendix.chars, notes: appendix.notes, issues: appendixJudge ? appendixJudge.issues.length : null, applied: appendixFix && appendixFix.applied, skipped: appendixFix && appendixFix.skipped },
}
