export const meta = {
  name: 'guide-audit-v34',
  description: '指南 v3.4 正確性與教育性稽核：11 段落查證＋8 個全文視角，去重後每條由 2 位反駁者裁決，最後整理成逐條修改建議',
  phases: [
    { title: 'Find', detail: '11 個段落查證者＋8 個全文視角（一致性、圖文與原圖、台灣稅法制度、作者引句、指數投資觀念、高中生、新手、連結）' },
    { title: 'Verify', detail: '每條發現派 2 位反駁者：來源真偽、對新手的重要性與修法' },
    { title: 'Synthesize', detail: '把確認的發現整理成逐條修改建議' },
  ],
}

// 分流（CLAUDE.md）：財務數字回推、引句、稅法、觀念、真偽裁決＝judge/fable；重要性與修法裁決＝judge/opus；
// 下次重跑 Find 時：links 視角改 agentType 'runner'（haiku），teen/novice/consistency 改 model 'opus'。本次 Find 已完成，沿用快取。
const A = '/private/tmp/claude-501/-Users-linyenchu-Cladue-Code/74b71b1c-f70a-4f20-89ce-2952d977c51c/scratchpad/audit'
const P = '/Users/linyenchu/Cladue Code/family-finance'
const COMMON = `
【共同規則】
- 稽核對象是《隔離人性：理財新手完整指南》v3.4。純文字版（帶行號）：${A}/guide_text.txt（728 行，[圖：id] 是圖表占位）。六張圖的標題、圖例、註解、圖說、SVG 文字節點、官方原圖出處：${A}/charts.json。原始 HTML：${P}/guide/index.html。
- 可用的一手資料：作者粉專 154 篇逐字全文 ${P}/research/author-fb-posts-all.md（標題「## 第 N 篇 ｜ 日期」由新到舊；相對日期的實際時間在標題下一行的 HTML 註解）；查證檔 ${P}/research/*.md（supp-spiva.md、supp-leverage-lifecycle-retirement.md、tw-tax-bank.md、tw-social-insurance.md、investing-evidence.md、supp-taiwan-dca-compute.md、supp-behavior-a.md、supp-behavior-b.md、supp-market-history.md、guide-v3-reader-reports.md）；PDF 抽字 ${P}/research/pdf/leverage-retirement/*.txt；台股資料 ${P}/research/data/*.csv；官方原圖 ${P}/research/orig/*.jpg|png（可以用 Read 直接看圖）。需要上網時用 curl -sL -A 'Mozilla/5.0' 抓官方頁；抓不到要說「抓不到」，不要用記憶充當查證。
- 作者原則（判斷「教育性」時的尺）：真實性優先；文件不替讀者下結論；不推薦商品、不做個人化建議；每個數字要有來源；作者自己的做法只能用「我」的口吻寫成例子。
- 只回報「站不住」的地方：錯的數字、錯的日期、改了字的引句、斷章取義、來源撐不起的說法、前後矛盾、會讓新手做錯決定的句子、沒解釋就用的關鍵詞。正確的東西不用列。每一條都要逐字引出原句、給行號、說明證據（來源檔案與行號或網址）、給一句可以直接貼上的替代句。
- 嚴重度：blocker＝事實錯誤或會害人做錯決定；major＝來源撐不起、脈絡錯、矛盾；minor＝措辭、術語、可讀性。
- 找不到證據時寫「查不到」，不要猜。只讀不改任何檔案。`

const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
          category: { type: 'string', enum: ['number', 'date', 'quote', 'source', 'consistency', 'concept', 'tax_law', 'education', 'chart', 'link', 'term'] },
          line: { type: 'integer' },
          quote: { type: 'string' },
          problem: { type: 'string' },
          evidence: { type: 'string' },
          fix: { type: 'string' },
        },
        required: ['severity', 'category', 'line', 'quote', 'problem', 'evidence', 'fix'],
      },
    },
    checked_summary: { type: 'string' },
    could_not_verify: { type: 'array', items: { type: 'string' } },
  },
  required: ['findings', 'checked_summary', 'could_not_verify'],
}

const VERDICT = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['confirmed', 'refuted', 'uncertain'] },
    reason: { type: 'string' },
    severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
    better_fix: { type: 'string' },
  },
  required: ['verdict', 'reason', 'severity', 'better_fix'],
}

// ---------- Find ----------
phase('Find')
const chunks = [
  { ids: 'start, glossary', start: 35, end: 80 },
  { ids: 's1, s2', start: 81, end: 135 },
  { ids: 's3, s4', start: 136, end: 186 },
  { ids: 's5', start: 187, end: 245 },
  { ids: 's6, s7, s8', start: 246, end: 340 },
  { ids: 's9, s10', start: 341, end: 390 },
  { ids: 's11, s12', start: 391, end: 445 },
  { ids: 's13', start: 446, end: 484 },
  { ids: 'steps, products', start: 485, end: 531 },
  { ids: 'costs, withdraw', start: 532, end: 582 },
  { ids: 'lifecycle', start: 583, end: 640 },
  { ids: 'sidepaths, annual, toolbox, methods', start: 641, end: 728 },
]

const chunkFinders = chunks.map((c, i) => () => agent(`${COMMON}

【你的任務：段落查證，第 ${i + 1}/12 段（${c.ids}，guide_text.txt 第 ${c.start}–${c.end} 行）】
先用 sed -n '${c.start},${c.end}p' 讀完整段。對這一段裡的每一個數字、日期、百分比、金額、引句（「」裡的話）、來源連結的描述、制度或法規說法，逐一回推來源：作者的話回推粉專原文（找到那一篇、核日期、核字）；研究數字回推 research 查證檔或原始網址；台灣制度回推官方頁。同時用新手的眼睛讀一遍：哪一句會讓人做錯決定、哪個詞沒解釋就用。
回報所有站不住的地方；checked_summary 寫你實際核了哪些、用了哪些檔案與網址；could_not_verify 列你查不到的。`, { agentType: 'judge', effort: 'high', label: `chunk:${c.ids}`, phase: 'Find', schema: FINDINGS }))

const LENSES = [
  { key: 'consistency', label: 'lens:一致性', prompt: `【你的任務：全文內部一致性】讀完整份 guide_text.txt。找：(1) 節與節之間互相矛盾的說法（例如同一件事在不同節給不同數字、不同期限、不同比例、不同結論；0050 在清單／範例／岔路三處的訊號是否一致；五年與十年；九比一與退休後比例；提領率 2.5% 與 25–40 倍；儲蓄險張數；配息所得類別在第 8 節、費用稅務、第 13 節是否一致）；(2) 每一個「第 N 節」「上一節」「下一節」「開始前」「安全順序第 N 項」「第 13 節第 N 題」交叉引用是否指對（第 13 節題號要數）；(3) 計數：十三個詞、七個步驟、三十一題、十項檢查表、七格規則卡、六種心魔、七條；(4) 同一個概念前後用不同名稱（例如「市值型」「按市值比重」「大盤」）造成混淆；(5) 目錄與正文順序、標題是否一致。` },
  { key: 'charts', label: 'lens:圖文與原圖', prompt: `【你的任務：六張圖的圖、文、原圖三方核對】讀 ${A}/charts.json 與 guide_text.txt 對應段落，並用 Read 打開 ${P}/research/orig/ 裡的官方原圖看。對每一張：(1) SVG 文字節點裡的數字，對照正文、圖說、圖例、註解，有沒有不一致（例如四個人終點 996/502/493/343、里程碑 7.84→1.35 年與 22%→86%、台股 23 年每年數字對 ${P}/research/data/algo_b_yearly.csv、區間表 16 個數字對 JPM 原圖第 42 頁、幸運兒表 1,578/1,519/1,470 萬與 13.23/12.97/12.74% 對 algo_a_results.csv）；(2) 官方原圖的出處說明（機構、文件名、頁碼、圖名、年份、例子的參數）是否和圖片內容相符——例如 GTR 2026 第 15 頁的例子是每月 250 美元、7.25% 嗎？GTM 第 17 頁的資料日期？(3) 圖說和標題有沒有說了圖裡沒有的東西，或者把示意當資料；(4) 手機版 SVG（class="m"）刪掉的標籤會不會讓圖說指到看不見的數字；(5) 圖例顏色說明與 SVG 用色是否對應（看 index.html 的 fill 變數）。` },
  { key: 'tax_law', label: 'lens:台灣稅法與制度', prompt: `【你的任務：台灣稅務、法規、制度說法全部上網核】全文 grep 出每一個台灣制度的說法並用 curl 抓官方頁核對：證交稅（股票 0.3%、ETF 0.1%）；股利所得二選一（8.5% 抵減、每戶 8 萬上限、28% 分開計稅、「級距 20% 以下多半併入較划算」這種說法能否成立）；二代健保補充保費 2.11%、單次股利 2 萬起扣、只看 54C 部分；海外所得 100 萬計入基本所得額、750 萬免稅額、20% 稅率、「沒達到 100 萬不用計入」；ETF 配息所得類別（國內股利 54C／海外所得／資本利得 76W 停徵／收益平準金非所得）——特別核「持有海外股票的台灣 ETF 配息裡的股利和資本利得都屬海外所得」；遺產稅 1,333 萬、配偶扣除 553 萬（115 年度）；美國 30% 預扣、6 萬美元遺產稅申報門檻、愛爾蘭 15%；勞保年金 1.55%、最高 60 個月、115 年 65 歲、年資 15 年、±4% 最多 20%；勞退 6%+6%、自提免稅、保證兩年期定存；融資維持率 130%、兩個營業日；T+2；緊急預備金；證交所收益平準金說明；0050 最大持股約 57%（元大官方頁現在的數字）；臺銀信貸 6.69%、中信 4.13%–16.29%。每一條給官方網址與抓到的原文片段。` },
  { key: 'author', label: 'lens:作者引句忠實度', prompt: `【你的任務：作者引句與第一人稱說法的忠實度】全文 grep 【我的例子】區塊與所有「我」開頭的做法描述（我現在固定九比一、我的日子是發薪日、我不看匯率、我對是否配息不太在意、我解掉儲蓄險、我把債券換成中期公債、我把滑翔改固定、我有勞退自提、我的提領率 2.5%、我股票裡台股一到兩成、我用 5/25、房貸以外沒有槓桿、我用投資歷程表比報酬、我至少十年、清單裡我的核心是全球型、小孩選 0050 連結基金不配息型……）。每一條回推 ${P}/research/author-fb-posts-all.md：找到那一篇、核日期（含 HTML 註解裡的實際時間）、逐字比對引號內的字、看前後文有沒有被斷章取義或改變語意、看是不是把「作者的一次做法」寫成「作者的長期原則」。也檢查有沒有第一人稱說法在粉專找不到任何依據（那就是我們替作者發明的）。` },
  { key: 'concepts', label: 'lens:指數投資觀念', prompt: `【你的任務：觀念層面的正確性，不是數字】你是一位熟讀 Bogle、Bernstein、Ayres & Nalebuff、Bengen、Trinity、Morningstar 提領率研究，並在台灣實際指數投資十五年以上的人。逐節讀，找出「說法在觀念上不對、不完整到會誤導、或把研究結論講反」的句子。重點：5/25 規則的描述；「股票比例的一半≈最壞帳面跌幅」這把尺的前提；「新錢超過資產一成就不用賣」；收益平準金與配息來源的解釋；「配息率不是報酬率」；匯率那段（避險版本、分批攤平短期不攤長期）；深風險段（帳戶保管在台灣）；人力資本與滑翔的描述；Ayres & Nalebuff 的主張與批評是否公平；融資、正 2、信貸三種借法的代價；Bengen／Trinity／Morningstar 的前提是否寫對；報酬順序風險的例子；「累積期與提領期是兩張卡」；勞退自提的比法；「主動式 ETF 不是指數投資」；「長天期美債是進攻不是防守」；「台幣定存可以當防守」；第 3 節費用粗尺；第 9 節台灣研究的解讀（3.8 個百分點是跟誰比）；第 10 節冷卻期不擋降風險。每一條說明為什麼觀念上站不住、正確的說法是什麼、哪份文獻可以支撐。` },
  { key: 'teen', label: 'lens:高中生讀者', prompt: `【你的任務：你是一位高二學生，數學普通，沒買過任何投資商品，只有壓歲錢】從第 1 行讀到第 728 行，不要略讀。回報：(1) 讀了會做錯事的句子（逐字引、說你會怎麼做錯）；(2) 完全看不懂、猜也猜不到的句子或詞（十三個詞之外的）；(3) 讀了會害怕到想放棄的句子；(4) 前後文讓你覺得作者自相矛盾的地方；(5) 「本節行動」裡你做不到、不知道怎麼開始的；(6) 你讀完會不會覺得有人在推銷什麼。教育性的判準：一個高中生讀完能不能正確說出「錢從哪裡來、為什麼分散、為什麼不擇時、跌了要怎麼辦、第一步做什麼」。` },
  { key: 'novice', label: 'lens:剛出社會讀者', prompt: `【你的任務：你是 26 歲、工作兩年、月薪四萬多、有一張儲蓄險、剛開證券戶還沒下單的上班族】從第 1 行讀到第 728 行，不要略讀。回報：(1) 讀了會做錯事或抄錯的句子（例如照抄九比一、以為買 009826 就避開地緣風險、以為海外所得要繳 20%、以為勞保試算是保證、以為自提一定划算、以為正 2 是兩倍長期投資、以為冷卻期要等三十天才能降風險）；(2) 你這種人真正會問但文件沒答的問題（列出來，並說文件哪一句最接近答案）；(3) 看不懂的詞；(4) 兩處以上互相打架的指示；(5) 你讀完會做的前三件事，以及哪一句讓你確定或不確定。` },
  { key: 'links', label: 'lens:連結存活與對應', prompt: `【你的任務：全部 92 個外部連結】清單在 ${A}/links.txt。用 curl -sL -o /dev/null -w '%{http_code} %{url_effective}' -A 'Mozilla/5.0' --max-time 20 逐一測（403 的用瀏覽器 UA 再試一次，並註明可能是擋機器人）。對每個連結，在 guide_text.txt 找到它的「來源連結：標題｜註解｜網址」那一行，用 curl 抓頁面標題或前幾百字，核對：標題描述是否符合目的頁、註解裡的數字或頁碼是否是那份文件真的有的（PDF 用 python3 -c "import fitz" 抽字核頁碼：GTR 2026 第 42、41、15 頁；GTM 第 17 頁；UBS 第 7 頁圖 12）。回報：死連結、轉址到別頁、標題與內容不符、頁碼或數字對不上。` },
]
const lensFinders = LENSES.map(l => () => agent(`${COMMON}\n\n${l.prompt}\n\n回報格式照 schema；checked_summary 寫你實際做了什麼。`, { agentType: 'judge', effort: 'high', label: l.label, phase: 'Find', schema: FINDINGS }))

const raw = (await parallel([...chunkFinders, ...lensFinders])).filter(Boolean)
const all = raw.flatMap((r, i) => (r.findings || []).map(f => ({ ...f, from: i < chunks.length ? `chunk:${chunks[i].ids}` : LENSES[i - chunks.length].key })))
log(`Find 完成：${raw.length}/${chunks.length + LENSES.length} 個代理回報，共 ${all.length} 條原始發現`)

// ---------- Dedupe（同一行且前 12 字相同視為同一條，保留最嚴重、合併來源） ----------
const rank = { blocker: 3, major: 2, minor: 1 }
const byKey = new Map()
for (const f of all) {
  const k = `${f.line}|${(f.quote || '').slice(0, 12)}`
  const prev = byKey.get(k)
  if (!prev) byKey.set(k, { ...f, from: [f.from], problems: [f.problem], fixes: [f.fix] })
  else {
    prev.from.push(f.from); prev.problems.push(f.problem); prev.fixes.push(f.fix)
    if (rank[f.severity] > rank[prev.severity]) prev.severity = f.severity
    prev.evidence += '\n---\n' + f.evidence
  }
}
const deduped = [...byKey.values()]
log(`去重後 ${deduped.length} 條（${deduped.filter(f => f.severity === 'blocker').length} blocker、${deduped.filter(f => f.severity === 'major').length} major、${deduped.filter(f => f.severity === 'minor').length} minor）`)
const unverifiable = raw.flatMap(r => r.could_not_verify || [])

// ---------- Verify：分批裁決（major → fable；minor → opus） ----------
phase('Verify')
const BATCH = {
  type: 'object',
  properties: { verdicts: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'integer' }, verdict: { type: 'string', enum: ['confirmed', 'refuted', 'uncertain'] },
    reason: { type: 'string' }, severity: { type: 'string', enum: ['blocker', 'major', 'minor'] }, better_fix: { type: 'string' },
  }, required: ['id', 'verdict', 'reason', 'severity', 'better_fix'] } } },
  required: ['verdicts'],
}
deduped.forEach((f, i) => { f.id = i + 1 })
const chunkOf = (line) => chunks.findIndex(c => line >= c.start && line <= c.end)
const groupBy = (arr, n) => { const out = []; for (let k = 0; k < arr.length; k += n) out.push(arr.slice(k, k + n)); return out }
const majors = deduped.filter(f => f.severity !== 'minor').sort((a, b) => a.line - b.line)
const minors = deduped.filter(f => f.severity === 'minor').sort((a, b) => a.line - b.line)
const majorBatches = groupBy(majors, 6)
const minorBatches = groupBy(minors, 14)
const fmt = (f) => `#${f.id}｜第 ${f.line} 行（${f.category}，來自 ${f.from.join('、')}）\n  原句：「${f.quote}」\n  問題：${f.problems.join(' ／ ')}\n  證據：${f.evidence.slice(0, 1200)}\n  提議修法：${f.fixes.join(' ／ ')}`
const judgeBatch = (batch, tier, bi) => agent(`${COMMON}

【裁決一批發現（${batch.length} 條）】對每一條，先用 sed -n 看 guide_text.txt 前後文，再回到一手資料（粉專原文、research 查證檔、官方網頁用 curl）判斷兩件事：(a) 真偽：原文是否真的站不住？發現者有沒有弄錯？證據不足一律 uncertain。(b) 重要性：不修會不會讓新手誤解、做錯決定或損害可信度？只是措辭偏好就 refuted。兩者都成立才 confirmed。better_fix 給一句可直接貼上的替代句，須符合作者原則、不得引入新的未查證數字；沒有更好就重複原提議。每一條都要回報，id 照給。
${batch.map(fmt).join('\n\n')}`, tier === 'fable'
    ? { agentType: 'judge', effort: 'xhigh', label: `verify-major#${bi + 1}`, phase: 'Verify', schema: BATCH }
    : { agentType: 'judge', model: 'opus', effort: 'high', label: `verify-minor#${bi + 1}`, phase: 'Verify', schema: BATCH })
const batchResults = (await parallel([
  ...majorBatches.map((b, bi) => () => judgeBatch(b, 'fable', bi)),
  ...minorBatches.map((b, bi) => () => judgeBatch(b, 'opus', bi)),
])).filter(Boolean)
const vmap = new Map()
for (const r of batchResults) for (const v of (r.verdicts || [])) vmap.set(v.id, v)
const verified = deduped.map(f => { const v = vmap.get(f.id); return { ...f, status: v ? v.verdict : 'uncertain', judge: v || null } })
const confirmed = verified.filter(v => v.status === 'confirmed')
const uncertain = verified.filter(v => v.status === 'uncertain')
const refuted = verified.filter(v => v.status === 'refuted')
log(`Verify 完成：確認 ${confirmed.length}、待人工 ${uncertain.length}、駁回 ${refuted.length}（${batchResults.length}/${majorBatches.length + minorBatches.length} 批回報）`)

// ---------- Synthesize ----------
phase('Synthesize')
const EDITS = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    edits: { type: 'array', items: { type: 'object', properties: {
      line: { type: 'integer' }, severity: { type: 'string' }, category: { type: 'string' },
      old: { type: 'string' }, new: { type: 'string' }, why: { type: 'string' }, sources: { type: 'string' },
    }, required: ['line', 'severity', 'category', 'old', 'new', 'why', 'sources'] } },
    for_author: { type: 'array', items: { type: 'string' } },
    not_adopted: { type: 'array', items: { type: 'string' } },
  },
  required: ['summary', 'edits', 'for_author', 'not_adopted'],
}
const pack = (arr) => arr.map(v => `- #${v.id} 第 ${v.line} 行［${v.judge ? v.judge.severity : v.severity}／${v.category}／${v.from.join('、')}］原句「${v.quote}」\n  問題：${v.problems.join(' ／ ')}\n  裁決：${v.judge ? v.judge.verdict + '：' + v.judge.reason : '無裁決'}\n  修法候選：${[...(v.fixes || []), v.judge && v.judge.better_fix].filter(Boolean).join(' ／ ')}`).join('\n')
const synthOne = (label, items) => agent(`${COMMON}

【你的任務：把確認的發現整理成逐條修改建議（${label}）】
${pack(items)}

請對每一條給最終修改：old 是原 HTML 檔 ${P}/guide/index.html 裡逐字存在的字串（用 grep -c 確認唯一命中；可含標籤），new 是替代字串，why 一句，sources 寫依據；同一行多條合併成一個 edit；替代句符合作者原則、不引入新的未查證數字；若判斷不該改就放 not_adopted 並說理由；需要作者拍板的放 for_author（白話說問題＋選項與後果＋你的建議）。summary 兩句。`, { agentType: 'judge', effort: 'xhigh', label: `synth:${label}`, phase: 'Synthesize', schema: EDITS })
const synthParts = (await parallel(groupBy(confirmed, 12).map((g, k) => () => synthOne(`第 ${k + 1} 批`, g)))).filter(Boolean)
const synth = { summary: synthParts.map(p => p.summary).join(' '), edits: synthParts.flatMap(p => p.edits), for_author: synthParts.flatMap(p => p.for_author), not_adopted: synthParts.flatMap(p => p.not_adopted) }

return { stats: { agents: raw.length, raw: all.length, deduped: deduped.length, confirmed: confirmed.length, uncertain: uncertain.length, refuted: refuted.length }, synth, confirmed, uncertain, refuted, unverifiable }