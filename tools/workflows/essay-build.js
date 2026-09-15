export const meta = {
  name: 'family-finance-essay-build',
  description: '投資專篇：先建哨兵與外殼 → 十節並行撰寫（寫手→雙裁判→修正）→ 組版 → 整篇三鏡頭複審 → 修稿 → 重組',
  phases: [
    { title: 'Tools', detail: 'check_essay.py、essay/shell、assemble_essay.py' },
    { title: 'Write', detail: '十節寫手' },
    { title: 'Judge', detail: '每節兩位裁判：知識與來源／語氣與可讀性（含經歷對貼文）' },
    { title: 'Fix', detail: '修正並跑哨兵' },
    { title: 'Assemble', detail: '組版' },
    { title: 'Review', detail: '整篇三鏡頭：零基礎讀者、作者本人、知識正確性' },
    { title: 'Polish', detail: '按節修稿、重組' },
  ],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'
const ESSAY = `${ROOT}/essay`
const OUTLINE = `${ESSAY}/outline.md`
const VOICE = `${ROOT}/research/essay-voice.md`
const POSTS = `${ROOT}/research/author-fb-posts-all.json`
const HANDBOOK_URL = 'https://claude.ai/code/artifact/76934d5e-136e-42b8-8de1-14e623f8859c'
const TITLE = '隔離人性'
const SUBTITLE = '先弄對十件事，再把決定寫在平靜的時候'

const SECTIONS = [
  '01-where-return-comes-from', '02-time', '03-cost', '04-diversify', '05-volatility',
  '06-timing', '07-frequency', '08-take-profit-dividend', '09-behavior-gap', '10-rules',
]

const FIX_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' }, applied: { type: 'number' },
    skipped: { type: 'array', items: { type: 'object', properties: { issue: { type: 'string' }, reason: { type: 'string' } }, required: ['issue', 'reason'] } },
    checkerErrors: { type: 'number' }, chars: { type: 'number' }, notes: { type: 'string' },
  },
  required: ['file', 'applied', 'skipped', 'checkerErrors'],
}
const ISSUES_SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['pass', 'fix', 'rewrite'] },
    issues: { type: 'array', items: { type: 'object', properties: {
      severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
      section: { type: 'string' }, where: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' },
    }, required: ['severity', 'where', 'problem', 'fix'] } },
    strengths: { type: 'string' }, overall: { type: 'string' },
  },
  required: ['verdict', 'issues'],
}

const COMMON = `
專案：投資專篇《${TITLE}》（副題：${SUBTITLE}），作者第一人稱，給零基礎朋友。定案大綱與元件契約：${OUTLINE}（§0 這篇是什麼、§2 骨架、§3 十節定案、§5 給寫手的固定清單＝唯一允許引用的數字、§6 元件契約）。作者語氣指南：${VOICE}。原始貼文：${POSTS}。手冊章節（知識底本與來源）：${ROOT}/chapters/07、08、09（其他章按需要）。手冊網址：${HANDBOOK_URL}（證據框連結用 ${HANDBOOK_URL}#ch-07 這種形式）。
鐵律：主軸是正確的理財知識，作者經歷只當例子（每節 ≤30%）；「我」不下指令；不寫作者績效百分比；只引 §5 清單裡的數字；每句經歷要對到貼文日期並用 <time datetime> 標記；每段 ≤3 句、每句 ≤30 字；不用驚嘆號；禁詞見 §6；術語全篇恰好 10 個（各節分配見 §3 的 terms）。
`

phase('Tools')
const tools = await agent(COMMON + `
你是 builder。依 ${OUTLINE} §6 元件契約做三樣東西，都放在 ${ESSAY}/ 下：
1. ${ROOT}/tools/check_essay.py：哨兵。輸入一個節的片段檔（essay/sections/NN-slug.html，內容只有一個 <section class="part">）或整篇組好的 essay/index.html（--full）。檢查：五元件齊全且順序正確（h2 → p.lede → div.concept（內含 aside.box.evidence 1–2 個）→ div.story → p.handback）；<dfn> 每節數量與 §3 分配一致、全篇（--full）恰好 10 且 id 不重複；全文無「！」「!」；禁詞清單（§6）；禁數字清單（§6）；每個 evidence 的 a[href] 含 #ch-；story 字數 ÷ 節字數 ≤ 0.30；每個 <time datetime> 的日期存在於 ${POSTS} 且在 outline §3 該節的 storyDates 裡（用節 id 對照 outline）；句長 >30 字列警告（<q> 豁免）；段落 >3 句列警告；lede ≤30 字；商品代號正則（0050、006208、009826、VT、VWRA、VALU、VWRD、AVGS、AVUV、CBU0 等）為錯誤。輸出格式與 ${ROOT}/tools/check_fragment.py 相同（錯誤 exit 1、警告 exit 0、--json）。
2. ${ESSAY}/shell/style.css 與 ${ESSAY}/shell/app.js：長文閱讀版面。與手冊同一色票家族（見 ${ROOT}/design-brief.md 的變數表，三種主題狀態都定義；body 背景明寫），但更像一本小書：單欄 max-width 38em、字級 17px 行高 1.85、章節號用宋體大字、lede 宋體、concept 正文黑體、story 段落左邊一條 teal 細線並縮排、evidence 框用 fill 底＋左 3px ink 線＋「證據」小標、handback 用 muted 斜線引出、dfn 虛底線（點擊展開該詞的白話解釋，資料由組裝腳本從 concept 段落裡的 dfn 後接句子抽出，或直接用 title 屬性）、目錄 nav.toc 十個連結、頁首 cover 留白多一點、footer 的日期索引小字。列印樣式。不載入外部程式庫，字型用手冊同一組 Google Fonts 連結。
3. ${ROOT}/tools/assemble_essay.py：把 essay/sections/*.html 依序組成 essay/index.html：開頭 <title>${TITLE}</title>、meta charset、fonts link、內嵌 style；<header class="cover">（h1 書名、p.subtitle 副題、p.about 讀者版四條護欄、p.handbook-link 手冊連結、nav.toc）；十節；<footer>（p.disclaimer 固定聲明、section.dates 作者貼文日期索引：逐節列出該節 <time> 的日期，連到粉專 https://www.facebook.com/profile.php?id=100084000897269）；內嵌 app.js。缺節時照樣組並列出缺哪些；檢查 #錨點；印出每節字數與 story 占比。
先建 ${ESSAY}/sections/ 目錄，並用一個你自己寫的最小合規樣本節測試哨兵與組裝（樣本放 ${ESSAY}/sections/_sample.html，組裝時忽略底線開頭的檔）。回傳 StructuredOutput：file（列三個路徑）、applied、skipped、checkerErrors、notes。
`, { label: 'build:tools', phase: 'Tools', model: 'opus', effort: 'high', schema: FIX_SCHEMA })
log(`工具：${tools ? '完成' : '失敗'}`)

const results = await pipeline(
  SECTIONS,
  async (id) => ({ build: await agent(COMMON + `
你是寫手，負責第 ${id} 節。讀 ${OUTLINE} §0、§2、§3 的「### ${id}」全部欄位、§5、§6；讀 ${VOICE} 全篇（定音叉那 20 句要真的讀）；讀該節 storyDates 對應的貼文原文（Python 從 ${POSTS} 取）；讀該節 evidence 指到的手冊段落（chapters/07–09）確認量級與原句。
寫法：先把觀念講對、講白（concept：2–5 段，每段 ≤3 句、每句 ≤30 字；術語只用本節分配到的，首次出現用 <dfn id="term-slug">術語</dfn> 並在同一句白話解釋）；證據框 1–2 個（p.magnitude 一句量級＋p.src 連到手冊章）；再用作者的一件事當例子（story，開頭標日期，<time datetime="YYYY-MM-DD">，只寫貼文裡真的有的事與感受，可用他的原句用 <q> 標）；最後一句交還（handback）。語氣照語氣指南：短句、括號自嘲、「我們」、不喊口號、不用驚嘆號。「我」只講我做了什麼與代價。
產出 ${ESSAY}/sections/${id}.html（只有一個 <section class="part" id="${id}">）。完成後執行 python3 "${ROOT}/tools/check_essay.py" "${ESSAY}/sections/${id}.html"，必須 0 錯誤。只動這一個檔案。回傳 StructuredOutput：file、applied（固定 1）、skipped、checkerErrors、chars、notes（用了哪些貼文日期、引了哪些量級）。
`, { label: `write:${id}`, phase: 'Write', model: 'opus', effort: 'high', schema: FIX_SCHEMA }) }),
  async (prev, id) => {
    if (!prev.build) return { ...prev, issues: null }
    const [facts, voice] = await parallel([
      () => agent(COMMON + `
你是知識與來源裁判，對 ${ESSAY}/sections/${id}.html 做對抗性驗證。你只讀不改。
檢查：1) 觀念是否講對（對照手冊 chapters/07–09 的內容與來源；有沒有把「歷史上多數期間」寫成「必定」、把相關寫成因果、把美國資料寫成台灣通則）；2) 每個量級是否在 ${OUTLINE} §5 清單裡、與手冊原句一致、證據框連結指到正確的章；3) 有沒有出現作者績效百分比或 §6 禁數字；4) 每個 <time> 日期是否存在於 ${POSTS} 且該節 storyDates 有列；故事裡每一件事與感受是否真的在那篇貼文裡（逐字回對，編造就是 blocker）；5) 「我」有沒有下指令、有沒有推薦語。先跑哨兵。
回傳 StructuredOutput：verdict、issues（severity、where 逐字、problem、fix 可直接套用）、strengths。找不到就誠實 pass。
`, { label: `judge-facts:${id}`, phase: 'Judge', model: 'fable', effort: 'xhigh', schema: ISSUES_SCHEMA }),
      () => agent(COMMON + `
你是語氣與可讀性裁判，對 ${ESSAY}/sections/${id}.html 做對抗性驗證。你只讀不改。
檢查：1) 零基礎讀者測試：逐段讀，列出讀不懂的句子、沒解釋就用的詞、>30 字的句子、>3 句的段落；2) 像不像作者：對照 ${VOICE} 的十項特徵與定音叉句，指出不像他的句子（太文藝、太勵志、太教科書、用了他不用的詞）並給改法；3) 主軸是否是知識：concept 是否真的把觀念講清楚，story 是否只是例子（占比 ≤30%）、有沒有反客為主；4) 交還句是否真的交還、不是變相指令；5) 契約元件與順序、dfn 數量、驚嘆號、禁詞。先跑哨兵。
回傳 StructuredOutput：verdict、issues、strengths。
`, { label: `judge-voice:${id}`, phase: 'Judge', model: 'fable', effort: 'high', schema: ISSUES_SCHEMA }),
    ])
    const issues = [...((facts && facts.issues) || []).map(i => ({ ...i, lens: 'facts' })), ...((voice && voice.issues) || []).map(i => ({ ...i, lens: 'voice' }))]
    log(`${id}：知識 ${facts ? facts.verdict : '失敗'}（${facts ? facts.issues.length : 0}）、語氣 ${voice ? voice.verdict : '失敗'}（${voice ? voice.issues.length : 0}）`)
    return { ...prev, issues }
  },
  async (prev, id) => {
    if (!prev.issues || !prev.issues.length) return { ...prev, fix: null }
    const fix = await agent(COMMON + `
你是修稿者。檔案：${ESSAY}/sections/${id}.html。處理下面全部問題（blocker／major 必修；minor 盡量修，修不了寫 skipped）。改出來的句子要更短更白、更像作者。只動這一個檔案。
${JSON.stringify(prev.issues, null, 1)}
修完執行 python3 "${ROOT}/tools/check_essay.py" "${ESSAY}/sections/${id}.html"，必須 0 錯誤。回傳 StructuredOutput：file、applied、skipped、checkerErrors、chars。
`, { label: `fix:${id}`, phase: 'Fix', model: 'opus', effort: 'medium', schema: FIX_SCHEMA })
    return { ...prev, fix }
  },
)

phase('Assemble')
const asm = await agent(COMMON + `
你是 runner。執行 python3 "${ROOT}/tools/assemble_essay.py"（輸出 ${ESSAY}/index.html），再執行 python3 "${ROOT}/tools/check_essay.py" "${ESSAY}/index.html" --full。把兩支工具印出的統計、錯誤與警告原樣回報。不改任何檔案。回傳 StructuredOutput：file、applied（0）、skipped（[]）、checkerErrors、notes（原始輸出）。
`, { label: 'assemble:essay', phase: 'Assemble', model: 'haiku', effort: 'low', schema: FIX_SCHEMA })

phase('Review')
const LENSES = [
  { key: 'reader', model: 'fable', effort: 'high', prompt: `鏡頭：零基礎讀者。用手機把 ${ESSAY}/index.html 從頭讀到尾。回報：讀到哪裡想放棄、哪裡讀不懂、哪些觀念講得不夠清楚或前後矛盾、哪節故事反客為主、十個術語有沒有真的解釋到、最難讀的五段（逐字＋改寫）。每條 issue 標 section（節 id）。` },
  { key: 'author', model: 'fable', effort: 'high', prompt: `鏡頭：作者本人。你是這位作者，讀 ${ESSAY}/index.html 每一句「我」。對照 ${POSTS} 與 ${VOICE}：哪一句不是我說過的事或感受（編造＝blocker）、哪一句不像我會講的話、哪裡把我的做法寫成了對讀者的指令、哪裡替我下了我沒下過的結論、哪裡用了我不會用的詞。每條 issue 標 section。` },
  { key: 'knowledge', model: 'fable', effort: 'xhigh', prompt: `鏡頭：知識正確性。逐節核對 ${ESSAY}/index.html 的觀念與量級：對照 ${ROOT}/chapters/07–09 與其來源條目、${OUTLINE} §5 清單；找出講錯的、講過頭的（把「多數期間」寫成規律、把相關寫成因果、把美國資料當通則）、量級與手冊不一致的、證據框連錯章的、以及 §6 禁數字有沒有出現。每條 issue 標 section。` },
]
const reviews = (await parallel(LENSES.map(l => () => agent(COMMON + l.prompt + `\n你只讀不改。回傳 StructuredOutput：verdict、issues（severity、section、where 逐字、problem、fix）、overall 一段總評。`, { label: `review:${l.key}`, phase: 'Review', model: l.model, effort: l.effort, schema: ISSUES_SCHEMA }).then(r => ({ key: l.key, r }))))).filter(Boolean)
const all = reviews.flatMap(x => ((x.r && x.r.issues) || []).map(i => ({ ...i, lens: x.key })))
const bySection = {}
for (const i of all) { const s = (i.section || '').trim(); if (s) (bySection[s] = bySection[s] || []).push(i) }
log(`整篇複審共 ${all.length} 條，分佈 ${Object.keys(bySection).length} 節`)

phase('Polish')
const polish = await parallel(Object.keys(bySection).sort().map(sec => () => agent(COMMON + `
你是修稿者。檔案：${ESSAY}/sections/${sec}.html（若找不到完全同名的檔，用 ls ${ESSAY}/sections/ 找最接近的節 id）。處理整篇複審三位裁判針對本節的問題（blocker／major 必修）。只動這一個檔案。
${JSON.stringify(bySection[sec], null, 1)}
修完執行 python3 "${ROOT}/tools/check_essay.py" 該檔，必須 0 錯誤。回傳 StructuredOutput：file、applied、skipped、checkerErrors、chars。
`, { label: `polish:${sec}`, phase: 'Polish', model: 'opus', effort: 'medium', schema: FIX_SCHEMA }).then(r => ({ sec, r }))))
const asm2 = await agent(COMMON + `
你是 runner。重新執行 python3 "${ROOT}/tools/assemble_essay.py" 與 python3 "${ROOT}/tools/check_essay.py" "${ESSAY}/index.html" --full，原樣回報輸出。不改任何檔案。回傳 StructuredOutput：file、applied（0）、skipped（[]）、checkerErrors、notes。
`, { label: 'assemble:final', phase: 'Polish', model: 'haiku', effort: 'low', schema: FIX_SCHEMA })

return {
  tools: tools && tools.notes,
  sections: SECTIONS.map((id, i) => { const r = results[i] || {}; return { id, built: !!r.build, issues: r.issues ? r.issues.length : null, fixApplied: r.fix && r.fix.applied, fixSkipped: r.fix && r.fix.skipped, chars: (r.fix && r.fix.chars) || (r.build && r.build.chars) } }),
  assemble: asm && { errors: asm.checkerErrors, notes: asm.notes },
  reviews: reviews.map(x => ({ lens: x.key, verdict: x.r && x.r.verdict, issues: x.r ? x.r.issues.length : null, overall: x.r && x.r.overall })),
  polish: polish.filter(Boolean).map(p => ({ sec: p.sec, applied: p.r && p.r.applied, skipped: p.r && p.r.skipped, errors: p.r && p.r.checkerErrors })),
  final: asm2 && { errors: asm2.checkerErrors, notes: asm2.notes },
}
