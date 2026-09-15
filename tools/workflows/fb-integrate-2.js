export const meta = {
  name: 'family-finance-fb-integrate-2',
  description: '依 fb-integration-plan.md 把作者粉專 154 篇的裁定通過項目整合進 12 章（寫手→裁判→修正），並同步研究檔',
  phases: [
    { title: 'Integrate', detail: '12 章並行，各只動自己的檔' },
    { title: 'Judge', detail: '每章一位裁判：忠於原文、語氣、契約' },
    { title: 'Fix', detail: '修正並跑哨兵' },
    { title: 'Sync', detail: '研究檔備註同步' },
  ],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'
const PLAN = `${ROOT}/research/fb-integration-plan.md`
const POSTS = `${ROOT}/research/author-fb-posts-all.json`

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

const RULINGS = `
主線拍板（優先於裁定計畫 §7 的未裁項）：
- P1（K3）選 (a)：作者框商品清單保留粉專簡介那份（全球 VT、VWRA、VALU、009826；台灣 0050、006208），並標明「作者粉專簡介列的幾檔，不等於他目前全部的持股」。
- P2（K7）：第 7 章甜蜜點算式框加一行「年化 7%：約 10 年後，約 14 倍」；第 9 章、第 0 章維持「用 7% 算約十年」。
- P3（K4）：第 0 章 route-note 補半句「粉專上另有作者做的槓桿試算工具，這份文件不談槓桿。」
- P4（N2）：本輪不做，列入第 17 章待查清單。
- P5（S12）：不加。
- P6（A5）：做。
- 主線加回三項（裁定計畫原本 skip 或列可選）：
  (甲) 第 7 章：作者定義的「滿足點」——資產一年的預期報酬等於家庭一年收入的八成——作為甜蜜點之後的下一個里程碑；用 <dfn id="def-滿足點" data-term="滿足點">，並在算式框或 details 裡放本文自算三欄表「儲蓄率｜年化 6%｜年化 7%」（儲蓄率 15%／25%／35%／50% → 6%：31.7／24.6／20.4／16.4 年；7%：27.3／21.2／17.6／14.1 年；算式 n = ln(1 + 0.8 ÷ 儲蓄率) ÷ ln(1 + 年化)），標「這是算術，不是預測」與「這是作者自己的里程碑，不是通用術語；不預設你要提早退休」，來源○本文自算＋作者 2025-09 貼文。不用「FIRE」「財富自由」等字。
  (乙) 第 13 章：A18 的 details 裡加上作者 2022-09 與四歲兒子的對話（逐字引原文：「你知道你的壓歲錢在哪裡嗎」「在銀行，會生小錢」「讓錢錢去工作賺錢，跟爸爸媽媽去工作賺錢一樣，不過錢錢他不會累」「為什麼他不會累」「因為他不用吃飯不用睡覺」），≤5 行。
  (丙) 第 1 章：C22 的可選句照裁定計畫的文字加進取捨框「做法 B」附近的正文（作者 2025-07：一家五口出國、旅費乘以五、年紀越大越願意把錢花在記憶上；那個月照樣先扣預期支出再投入；代價是那個月投入變少）。
共同規則：每段都有「作者 YYYY-MM 的紀錄」與代價句；不用禁用字眼（推薦、建議你、你應該、一定、財富自由、被動收入、歐印、FIRE、必定）；不寫作者的個人績效百分比；商品名只在第 9 章作者框；正文不用驚嘆號。每個引句都要能在 ${POSTS} 找到（用 Python 依日期抓原文核對）。框數不得超過 7（第 6 章已 8，不得再增）；只能加正文段、details、既有框內的一條、表格或工作表一列、對照卡一格。
`

const JOBS = [
  { id: '00-how-to-use', loose: true, items: 'P3 的 route-note 半句；並確認「如果你想照作者的路走」第 7 條寫的是「用 7% 假設算約十年」' },
  { id: '01-why-and-order', loose: false, items: '(丙) C22 可選句' },
  { id: '03-cash-flow', loose: false, items: 'A14' },
  { id: '06-insurance', loose: false, items: 'A16（本章框已 8，只能加正文段）' },
  { id: '07-time-inflation-compounding', loose: false, items: 'A1、A2、A3、P2（算式框加 7% 那一行）、(甲) 滿足點' },
  { id: '08-risk-diversification-cost', loose: false, items: 'A4' },
  { id: '09-rules-card', loose: false, items: 'A5、A6、A7、A8（含 K1 門檻描述修正）、A9、A10、A11、A12、A13、P1（作者框清單標註）。作者框會從 8 條變 10 條；情境表加兩列；工作表⑧加一列；正文加三段。字數上限 5,000。' },
  { id: '10-retirement', loose: false, items: 'A20' },
  { id: '11-tax', loose: false, items: 'A19' },
  { id: '13-family', loose: false, items: 'A17、A18、(乙) 壓歲錢對話' },
  { id: '16-action-list', loose: false, items: 'A15' },
  { id: '17-glossary-sources', loose: true, items: '名詞表加「滿足點」（作者自己的里程碑：資產一年的預期報酬等於家庭一年收入的八成 → 第 7 章）；待查清單加 N1（5/25 規則原始出處）、N2（基金註冊地與預扣稅、繼承程序）、N4（手機報稅是否自動帶入購屋借款利息）、N5（65 歲以上每人每月消費支出的主計總處表）四列，欄位照既有表格' },
]

const results = await pipeline(
  JOBS,
  async (j) => ({ build: await agent(`
你是寫手，負責把作者粉專內容整合進 ${ROOT}/chapters/${j.id}.html。
必讀：${PLAN}（§0 原則、§2 裡指派給你的項目全文、§6 相關衝突）、${ROOT}/components.md、${ROOT}/outline.md §2 語氣規範、${ROOT}/research/fb-themes.md（背景）。原文核對用 ${POSTS}（Python 讀取，依 published_iso 前 10 碼找那篇）。
你負責的項目：${j.items}
${RULINGS}
做法：每個項目照裁定計畫給的「放哪裡／貼什麼」套用，句子可以再拆短（一句 ≤40 字、一段 ≤4 句）；日期與引句回原文逐字核對；新來源條目照 components.md §4 格式（作者貼文標○，寫「作者粉專貼文 · 日期 · 一句話 · 網址 https://www.facebook.com/profile.php?id=100084000897269 · 查證 2026-09-07」；同一章多篇貼文可共用一條來源）。只動這一個檔案。
完成後執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${j.id}.html"${j.loose ? ' --loose' : ''}，必須 0 錯誤。回傳 StructuredOutput：file、applied（做了幾項）、skipped（哪項沒做、為什麼）、checkerErrors、chars、notes（每項放在哪裡、引了哪些日期）。
`, { label: `integrate:${j.id}`, phase: 'Integrate', model: 'opus', effort: 'high', schema: FIX_SCHEMA }) }),
  async (prev, j) => {
    if (!prev.build) return { ...prev, judge: null }
    const judge = await agent(`
你是裁判，對 ${ROOT}/chapters/${j.id}.html 剛整合的作者粉專內容做對抗性驗證。你只讀不改。
讀：該檔、${PLAN}（該章項目：${j.items}）、${POSTS}（用 Python 依日期抓原文逐字核對每一個引句與「作者 YYYY-MM 的紀錄」的日期）、${ROOT}/components.md、${ROOT}/outline.md §2。先執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${j.id}.html"${j.loose ? ' --loose' : ''}。
${RULINGS}
檢查：1) 每個引句是否逐字出現在該日期的貼文裡，日期是否正確（錯一個月就是 major）；2) 有沒有作者的個人績效百分比、商品名（第 9 章作者框外）、禁用字眼、指令語氣；3) 每段有沒有「作者 YYYY-MM 的紀錄」與代價句；4) 框數 ≤7（第 6 章 ≤8）、表格 ≤3 欄、章首章尾未動；5) 新句子是否比全章平均更短更白、有沒有跟既有段落重複；6) 裁定計畫指派的項目有沒有漏做或做錯位置；7) 來源條目格式與 cite 對應。
回傳 StructuredOutput：verdict、issues（severity、where 逐字、problem、fix 可直接套用）、strengths。找不到就誠實 pass。
`, { label: `judge:${j.id}`, phase: 'Judge', model: 'fable', effort: 'high', schema: ISSUES_SCHEMA })
    return { ...prev, judge }
  },
  async (prev, j) => {
    if (!prev.judge || !prev.judge.issues.length) return { ...prev, fix: null }
    const fix = await agent(`
你是修稿者。檔案：${ROOT}/chapters/${j.id}.html。契約：${ROOT}/components.md；規範：${ROOT}/outline.md §2；原文：${POSTS}。處理下面全部問題（blocker／major 必修），只動這一個檔案。
${JSON.stringify(prev.judge.issues, null, 1)}
修完執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${j.id}.html"${j.loose ? ' --loose' : ''}，必須 0 錯誤。回傳 StructuredOutput：file、applied、skipped、checkerErrors、chars。
`, { label: `fix:${j.id}`, phase: 'Fix', model: 'opus', effort: 'medium', schema: FIX_SCHEMA })
    return { ...prev, fix }
  },
)

phase('Sync')
const sync = await agent(`
你是 applier。只改 ${ROOT}/research/author-principles.md：1) 第 4 條「每年再平衡一次」後加註「（粉專簡介的舊說法；2026-04 起作者實際規則是 5/25 門檻：年底超過就調、每月投入時超過兩倍門檻才動，見 research/fb-integration-plan.md K1）」；2) 商品清單改成粉專版（全球 VT、VWRA、VALU、009826；台灣 0050、006208）並註明「以粉專簡介 2026-09-07 為準」。回傳 StructuredOutput：file、applied、skipped、checkerErrors（填 0）。
`, { label: 'sync:author-principles', phase: 'Sync', model: 'sonnet', effort: 'low', schema: FIX_SCHEMA })

return {
  chapters: JOBS.map((j, i) => { const r = results[i] || {}; return { id: j.id, applied: r.build && r.build.applied, skipped: r.build && r.build.skipped, issues: r.judge ? r.judge.issues.length : null, verdict: r.judge && r.judge.verdict, fixApplied: r.fix && r.fix.applied, fixSkipped: r.fix && r.fix.skipped, chars: (r.fix && r.fix.chars) || (r.build && r.build.chars), notes: r.build && r.build.notes } }),
  sync: sync && { applied: sync.applied, skipped: sync.skipped },
}
