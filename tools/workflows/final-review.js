export const meta = {
  name: 'family-finance-final-review',
  description: '整本複審：三位裁判（零基礎讀者體驗／跨章一致性／版面與無障礙）→ 問題按章分派修稿 → 複驗',
  phases: [
    { title: 'AuthorRoute', detail: '導讀最後加「如果你想照作者的路走」單頁' },
    { title: 'Review', detail: '三個鏡頭各讀整本 output/index.html' },
    { title: 'Fix', detail: '按章分派修稿（一章一人，避免撞檔）' },
    { title: 'Recheck', detail: '哨兵＋複驗' },
  ],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'
const OUT = `${ROOT}/output/index.html`

const ISSUES_SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['pass', 'fix', 'rewrite'] },
    issues: { type: 'array', items: { type: 'object', properties: {
      severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
      chapter: { type: 'string' },
      where: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' },
    }, required: ['severity', 'chapter', 'where', 'problem', 'fix'] } },
    overall: { type: 'string' },
    cuts: { type: 'array', items: { type: 'string' } },
  },
  required: ['verdict', 'issues', 'overall'],
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

const COMMON = `
整本文件已組成 ${OUT}（單一 HTML，約 18 節）。章節原始檔在 ${ROOT}/chapters/NN-slug.html；規範在 ${ROOT}/outline.md §1 §2；契約在 ${ROOT}/components.md。你只讀不改。
每條 issue 的 chapter 欄填章節檔名（例如 08-risk-diversification-cost），where 填原文逐字引述，fix 給可直接套用的替換文字或明確指令。找不到問題就誠實 pass，不要硬湊。
`

const LENSES = [
  { key: 'reader', model: 'fable', effort: 'high', prompt: COMMON + `
鏡頭：零基礎讀者體驗。你是一位完全沒有理財基礎、用手機閱讀的台灣成年人，從導讀開始把整本讀完（用 Read 分段讀 ${OUT}，或逐章讀 chapters/）。作者交代：版面和語氣必須容易閱讀。
回報：1) 讀到哪裡想放棄、為什麼（太長、太密、術語、看不出跟自己有關）；2) 跨章重複講同一件事的地方（指出保留哪一處、刪哪一處）；3) 前後矛盾或語氣不一致的地方；4) 導讀的「先看重點」與三條路線是否真的讓人知道從哪開始；5) 每章「今天的一件事」是否真的 10 分鐘內做得到；6) 最難讀的五段（逐字引述並給改寫）。
另外在 cuts 列出「若要把全書刪掉一成，最先刪哪些段落」（章名＋段落開頭幾個字）。
` },
  { key: 'consistency', model: 'fable', effort: 'xhigh', prompt: COMMON + `
鏡頭：跨章一致性與數字稽核。用 grep 與 Python 逐項核：
1) 同一個制度數字在不同章是否一致（例如勞保投保薪資上限、健保費率與補充保費、存款保險額度、循環利率上限、綜所稅級距與免稅額、遺產贈與稅免稅額、勞退提繳率、五大銀行利率、CPI）。列出每個數字在哪些章出現、值是否相同、年度徽章是否一致。
2) 第 17 章「會過期的數字一覽表」的每一列，回對應章的事實框核對數字、年度、網址；一覽表漏掉的制度數字列出。
3) 第 17 章名詞表每條定義與該章 dfn 所在句是否一致；有沒有章節用了術語卻既沒 dfn 也不在名詞表。
4) 第 00 章健檢進度表、45 句問題、先看重點的章節連結與章名，是否與各章實際的 h2、三個問題、時間列、產出一致；第 16 章第一週五件事與各章「今天的一件事」是否一致。
5) 交叉引用「第 N 章」是否指向正確的章（例如「見第 9 章分桶」那章真的有分桶）。
6) 各章「還沒解決、後面會處理」指向的章是否真的處理了。
7) supplement-plan.md 裁定 drop 的內容有沒有出現；商品名是否只在第 9 章作者框內（grep 代號）。
` },
  { key: 'layout', model: 'opus', effort: 'high', prompt: COMMON + `
鏡頭：版面、HTML 正確性與無障礙。用 Python（html.parser）解析 ${OUT}：1) 標籤是否配對、id 是否重複、所有 href="#…" 是否有目標；2) 標題階層（每章一個 h2、h3 只在章內、h4 只在框與卡內）；3) 每個 <table> 是否在 .table-wrap 內、欄數（一般 ≤3，checkup-table 與 expiry 例外）；4) 每個 <svg> 是否有 <title>、figure 是否有 figcaption、顏色是否只用 currentColor 與 var(--…)；5) 框數每章 ≤7、動手框 ≤2（aside.box）；6) 有沒有 style 屬性、有沒有契約外的 class（比對 ${ROOT}/tools/check_fragment.py 的 ALLOWED_CLASSES 與 design-brief 額外元素）；7) 對每一章跑 python3 ${ROOT}/tools/check_fragment.py（17 章加 --loose、00 章加 --loose）並列出錯誤；8) 讀 ${ROOT}/shell/style.css：三個主題區塊是否都定義同一組變數、body 是否有 background、是否有主題區塊外的色碼；9) 列印樣式是否隱藏導覽並展開 details；10) 每章 .foot-note 免責句是否都在。
` },
]

phase('AuthorRoute')
const route = await agent(`
你是寫手。作者拍板要在導讀（${ROOT}/chapters/00-how-to-use.html）最後、章尾 <footer class="ch-foot"> 之前，加一頁「如果你想照作者的路走」。
必讀：${ROOT}/research/author-principles.md（作者七條原則原文、落點表、甜蜜點算術）、${ROOT}/design-brief.md「導讀與附錄的額外元素」裡 author-route 的結構、${ROOT}/components.md、${ROOT}/outline.md §2 語氣規範、以及 ${ROOT}/chapters/07、08、09 章（確認每條連到的章真的有解釋它，抄章名）。
結構固定：
<div class="author-route">
  <h3>如果你想照作者的路走</h3>
  <p class="route-intro">這是作者自己走的路，不是這份文件的結論。每一條旁邊寫了理由與代價，也連到解釋它的章。</p>
  <ol> 七條，每條 <li><strong>一句原則（作者原文的意思，改成白話，不用「你應該」）。</strong>理由：一句。代價：一句。<a href="#ch-NN">第 N 章</a></li> </ol>
  <p class="route-note">作者持有的幾檔名稱與完整的規則卡在 <a href="#ch-09">第 9 章</a>。</p>
</div>
規則：商品名稱一律不出現在這一頁；每條 ≤60 字；不出現禁用字眼（推薦、建議你、你應該、一定、保證…）；第 7 條甜蜜點寫「預期報酬等於當年投入的那一年，7% 假設下約十年」並註明「假設」。寫完執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/00-how-to-use.html" --loose，必須 0 錯誤。只改這一個檔案，只加這一塊，不動其他內容。
回傳 StructuredOutput：file、applied（固定 1）、skipped、checkerErrors、chars。
`, { label: 'write:author-route', phase: 'AuthorRoute', model: 'opus', effort: 'high', schema: FIX_SCHEMA })
log(`作者版路線：${route ? '已加入導讀' : '失敗'}`)

phase('Review')
const reviews = (await parallel(LENSES.map(l => () =>
  agent(l.prompt, { label: `review:${l.key}`, phase: 'Review', model: l.model, effort: l.effort, schema: ISSUES_SCHEMA }).then(r => ({ key: l.key, r }))))).filter(Boolean)

const all = reviews.flatMap(x => ((x.r && x.r.issues) || []).map(i => ({ ...i, lens: x.key })))
const byChapter = {}
for (const i of all) {
  const ch = (i.chapter || '').replace(/\.html$/, '').trim()
  if (!ch) continue
  ;(byChapter[ch] = byChapter[ch] || []).push(i)
}
const chapters = Object.keys(byChapter).sort()
log(`三位裁判共 ${all.length} 條問題，分佈在 ${chapters.length} 章`)

phase('Fix')
const fixes = await parallel(chapters.map(ch => () => {
  const issues = byChapter[ch]
  const loose = ch.startsWith('00') || ch.startsWith('17')
  return agent(`
你是修稿者，處理章節檔 ${ROOT}/chapters/${ch}.html。契約：${ROOT}/components.md；規範：${ROOT}/outline.md §1 §2；研究檔在 ${ROOT}/research/。
下面是整本複審三位裁判（reader 讀者體驗、consistency 跨章一致、layout 版面）針對本章的問題，全部處理：blocker 與 major 必修；minor 盡量修；修不了寫 skipped 並說明。若是「跨章重複、刪這一段」的指示，照刪；若是數字不一致，以研究檔 verified 的值為準並同步年度徽章與來源條目。改出來的句子要更短更白。只改這一個檔案。
${JSON.stringify(issues, null, 1)}
修完執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${ch}.html"${loose ? ' --loose' : ''}，必須 0 錯誤。回傳 StructuredOutput：file、applied、skipped、checkerErrors、chars。
`, { label: `fix:${ch}`, phase: 'Fix', model: 'opus', effort: 'medium', schema: FIX_SCHEMA }).then(r => ({ ch, r }))
}))

phase('Recheck')
const recheck = await agent(`
你是複驗員。先執行 python3 "${ROOT}/tools/assemble.py" 重新組裝（輸出 ${OUT}），把它印出的錯誤與警告抄下來；再對每章跑 check_fragment（00、17 加 --loose）。然後抽驗下面 blocker／major 是否已修：
${JSON.stringify(all.filter(i => i.severity !== 'minor').slice(0, 60), null, 1)}
你只讀不改（assemble.py 只寫 output/，可以跑）。回傳 StructuredOutput：verdict（pass／fix）、issues（仍未修好的，含 chapter）、overall（一句話：組裝結果與剩餘問題數）。
`, { label: 'recheck:whole', phase: 'Recheck', model: 'sonnet', effort: 'medium', schema: ISSUES_SCHEMA })

return {
  reviews: reviews.map(x => ({ lens: x.key, verdict: x.r && x.r.verdict, issues: x.r ? x.r.issues.length : null, overall: x.r && x.r.overall, cuts: x.r && x.r.cuts })),
  fixes: fixes.filter(Boolean).map(f => ({ ch: f.ch, applied: f.r && f.r.applied, skipped: f.r && f.r.skipped, checkerErrors: f.r && f.r.checkerErrors, chars: f.r && f.r.chars })),
  recheck,
}
