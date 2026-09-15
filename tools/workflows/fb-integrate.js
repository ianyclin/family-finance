export const meta = {
  name: 'family-finance-fb-integrate',
  description: '把作者粉專抓到的內容整合進 00、09、10 章（各一位寫手→一位裁判→修正），然後重組',
  phases: [
    { title: 'Integrate', detail: '三章並行' },
    { title: 'Judge', detail: '每章一位裁判（語氣＋數字）' },
    { title: 'Fix', detail: '修正並跑哨兵' },
  ],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'
const TODAY = '2026-09-07'

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
      where: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' },
    }, required: ['severity', 'where', 'problem', 'fix'] } },
    strengths: { type: 'string' },
  },
  required: ['verdict', 'issues'],
}

const COMMON = `
素材：${ROOT}/research/author-fb-posts.md（作者粉專抓取紀錄，等級○作者立場）與 ${ROOT}/research/author-principles.md。契約：${ROOT}/components.md；規範：${ROOT}/outline.md §1 §2（禁用字眼：推薦、建議你、你應該、一定、保證…；不下指令、不預測）。
作者價值觀：文件不替讀者下結論；作者自己的做法只能以「作者自己的做法／作者的經驗」身分出現，並附代價。每一句新增都要比全章平均更短更白。改完只動這一個檔案，執行哨兵必須 0 錯誤。
`

const JOBS = [
  { id: '00-how-to-use', loose: true, prompt: COMMON + `
檔案：${ROOT}/chapters/00-how-to-use.html。只做一件事：在 <div class="author-route"> 的 <p class="route-note"> 裡，補上作者粉專的名稱與連結：「作者的月記在粉專「指數三寶飯·家庭理財陪跑」（<a href="https://www.facebook.com/profile.php?id=100084000897269" rel="noopener">連結</a>）」，語氣中性、不呼籲追蹤。若 route-note 已有第 9 章連結，兩者並列成一段。哨兵：python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/00-how-to-use.html" --loose。` },
  { id: '09-rules-card', loose: false, prompt: COMMON + `
檔案：${ROOT}/chapters/09-rules-card.html。兩件事：
1. 作者框 <aside class="box fact author">：(a) 商品清單改成粉專版：全球 VT、VWRA、VALU、009826；台灣 0050、006208（維持「同類商品很多檔，列名不是要你跟著買」的句子；不要寫任何費用率或商品描述）。(b) 補一小段「作者怎麼執行」：發薪日扣除預期支出後，剩下全部投入並維持目標配置；股債比固定 9:1（作者 2026 年 9 月的做法，原本打算隨年齡滑降，後來為了簡單改固定）；再平衡門檻用「5/25 規則」（任一資產偏離目標 5 個百分點、或相對偏離 25% 就調回）——這是作者採用的一個常見經驗法則，附一句白話解釋，不當成規定；每條附代價（例如「固定 9:1 的代價是接近退休時波動較大」「5/25 的代價是偶爾要賣掉漲多的那邊」）。作者框內容仍要控制在全章框預算與字數上限（現在約 4,450 字，上限 4,600）。
2. 在「規則卡」那一節（工作表⑧附近）加一句：「作者把這件事叫『隔離人性』：把決定寫在市場平靜的時候，大跌那天只照做。這張規則卡就是專業上所說的投資政策聲明（IPS）的白話版。」若章內已有類似句子則改寫合併，不重複。
哨兵：python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/09-rules-card.html"。` },
  { id: '10-retirement', loose: false, prompt: COMMON + `
檔案：${ROOT}/chapters/10-retirement.html。在「怎麼領」那一節（提領率對照卡或那一段附近）補兩件事，總增量 ≤ 250 字，不新增框（本章框已滿；用正文段落與 details）：
1. 「報酬來的順序」：同樣一組報酬，壞年份排在退休前幾年，存活率就會差很多；這叫報酬順序風險。若本章已有這個概念，只補強一句，不重複。
2. 作者的取捨句：「退休提領真正的問題不是會不會破產的是非題，而是你願意用多少生活品質的波動，去換多高的存活率。作者把這個取捨做成一個示意工具（蒙地卡羅模擬，不是投資建議，未納入稅、健保與勞保勞退）：」加 <details><summary>想看細節再打開：作者的退休提領示意工具</summary> 內放一段說明與連結 <a href="https://ianyclin.github.io/Retirement-Drawdown-Simulator/index.html" rel="noopener">連結</a>，並寫明四種策略名稱（傳統 4%、上下限動態提領、雙護欄、平滑法）與三個指標（存活率、生活品質、提領穩定度）。來源清單加一條 ○「作者自製示意工具 · 退休提領模擬器 · 蒙地卡羅示意，不是投資建議 · 2026-09 · 網址 · 查證 ${TODAY}」並在正文用 cite 引用。
哨兵：python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/10-retirement.html"。` },
]

const results = await pipeline(
  JOBS,
  async (j) => ({ build: await agent(j.prompt + `\n回傳 StructuredOutput：file、applied、skipped、checkerErrors、chars、notes。`, { label: `integrate:${j.id}`, phase: 'Integrate', model: 'opus', effort: 'high', schema: FIX_SCHEMA }) }),
  async (prev, j) => {
    if (!prev.build) return { ...prev, judge: null }
    const judge = await agent(`
你是裁判（語氣＋數字＋契約三合一），對 ${ROOT}/chapters/${j.id}.html 剛整合的粉專內容做對抗性驗證。你只讀不改。
讀：該檔、${ROOT}/research/author-fb-posts.md、${ROOT}/components.md、${ROOT}/outline.md §2。先執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${j.id}.html"${j.loose ? ' --loose' : ''}。
檢查：新增內容是否忠於粉專原文（商品清單、9:1、5/25、發薪日投入、四種策略、三個指標）；是否只以「作者自己的做法」身分出現並附代價；有沒有變成指令或推薦語（「推薦」「建議你」「你應該」一律 blocker）；商品名是否只在第 9 章作者框內；新來源條目格式；字數與框數是否仍在上限內；新句子是否比全章平均更短更白；連結 rel="noopener"。
回傳 StructuredOutput：verdict、issues（severity、where 逐字、problem、fix）、strengths。找不到就誠實 pass。
`, { label: `judge:${j.id}`, phase: 'Judge', model: 'fable', effort: 'high', schema: ISSUES_SCHEMA })
    return { ...prev, judge }
  },
  async (prev, j) => {
    if (!prev.judge || !prev.judge.issues.length) return { ...prev, fix: null }
    const fix = await agent(`
你是修稿者。檔案：${ROOT}/chapters/${j.id}.html。契約：${ROOT}/components.md；規範：${ROOT}/outline.md §2。處理下面全部問題（blocker／major 必修），只動這一個檔案。
${JSON.stringify(prev.judge.issues, null, 1)}
修完執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${j.id}.html"${j.loose ? ' --loose' : ''}，必須 0 錯誤。回傳 StructuredOutput：file、applied、skipped、checkerErrors、chars。
`, { label: `fix:${j.id}`, phase: 'Fix', model: 'opus', effort: 'medium', schema: FIX_SCHEMA })
    return { ...prev, fix }
  },
)

return JOBS.map((j, i) => {
  const r = results[i] || {}
  return { id: j.id, applied: r.build && r.build.applied, notes: r.build && r.build.notes, issues: r.judge ? r.judge.issues.length : null, verdict: r.judge && r.judge.verdict, fixApplied: r.fix && r.fix.applied, fixSkipped: r.fix && r.fix.skipped, chars: (r.fix && r.fix.chars) || (r.build && r.build.chars) }
})
