export const meta = {
  name: 'family-finance-finish-integration',
  description: '補完第 9 章數字裁判與修正、寫第 17 章附錄並驗證，然後接整本複審（子工作流）',
  phases: [
    { title: 'Ch09', detail: '數字裁判 → 合併語氣裁判問題修正 → 複驗' },
    { title: 'Appendix', detail: '第 17 章名詞表、會過期的數字、待查清單' },
    { title: 'FinalReview', detail: '子工作流：作者版路線 ＋ 三鏡頭整本複審 ＋ 修稿' },
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
    added: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' },
  },
  required: ['file', 'chars', 'checkerErrors', 'added'],
}

const CH09 = { id: '09-rules-card', num: 9, title: '投資第三課：把投資變成制度——分桶、路徑、投入方式、規則卡', files: ['supp-taiwan-dca-compute.md', 'supp-timing-dca.md', 'supp-author-sources.md', 'investing-evidence.md', 'author-principles.md'] }

async function finishCh09() {
  const t = CH09
  const facts = await agent(`
你是數字與來源裁判，對第 ${t.num} 章《${t.title}》（剛整合完補充素材與作者七條原則）做對抗性驗證。你只讀不改。
讀：${ROOT}/chapters/${t.id}.html、${ROOT}/supplement-plan.md（C4、C5、C8、C13、C25、C27 與 §2 factErrors）、研究檔 ${t.files.map(f => ROOT + '/research/' + f).join('、')}、${ROOT}/research/data/*.csv、${ROOT}/components.md §3 §5。
檢查：每個帶數字的句子回研究檔找到同一個數字、年度、機構、網址、等級；自算數字重跑 python3 ${ROOT}/tools/twse_dca.py 與 ${ROOT}/tools/twse_dca_freq.py（若需網路且失敗，改讀 research/data/ 的 CSV）核對三情境與七種頻率；Schwab 五人金額與 Vanguard 比例對研究檔；Estrada 引用是否正確；作者框 <aside class="box fact author">：七條是否忠於 research/author-principles.md 原意、每條有代價、商品名只在框內、標籤是「不是要你照做」；drop 的內容不得出現；每個新來源被引用、每個引用有條目；有報酬率處有「這是假設，不是承諾」。
回傳 StructuredOutput：verdict、issues（severity、where 逐字、problem、fix 可直接套用）、strengths。找不到就誠實 pass。
`, { label: 'judge-facts:09-rules-card', phase: 'Ch09', model: 'fable', effort: 'xhigh', schema: ISSUES_SCHEMA })
  const newIssues = ((facts && facts.issues) || []).map(i => ({ ...i, lens: 'facts' }))
  log(`第 9 章數字裁判：${facts ? facts.verdict : '失敗'}（${newIssues.length} 條）`)
  let fix = null, recheck = null, issues = newIssues
  for (let round = 1; round <= 2; round++) {
    fix = await agent(`
你是修稿者，處理第 9 章《${t.title}》${round > 1 ? '（第二輪）' : ''}。檔案：${ROOT}/chapters/${t.id}.html。契約：${ROOT}/components.md；規範：${ROOT}/outline.md §1 §2；素材裁定：${ROOT}/supplement-plan.md；研究檔在 ${ROOT}/research/。
問題來源：${round === 1 ? `(a) 語氣裁判結果檔 ${ROOT}/tools/state/judge-09-integration.json 的 issues；(b) ` : ''}下方 JSON。blocker 與 major 必修，minor 盡量修，修不了寫 skipped 說明。改出來的句子要更短更白。作者框標籤維持「不是要你照做」。不動其他檔案。
${JSON.stringify(issues, null, 1)}
修完執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${t.id}.html"，必須 0 錯誤。回傳 StructuredOutput：file、applied、skipped、checkerErrors、chars。
`, { label: `fix${round}:09-rules-card`, phase: 'Ch09', model: 'opus', effort: 'medium', schema: FIX_SCHEMA })
    recheck = await agent(`
你是複驗員。檔案：${ROOT}/chapters/${t.id}.html。先執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${t.id}.html"。逐條確認 blocker／major 是否修掉：${round === 1 ? `${ROOT}/tools/state/judge-09-integration.json 的 issues 與` : ''}下方 JSON。你只讀不改。
${JSON.stringify(issues.filter(i => i.severity !== 'minor'), null, 1)}
回傳 StructuredOutput：ok、checkerErrors、remaining。
`, { label: `recheck${round}:09-rules-card`, phase: 'Ch09', model: 'sonnet', effort: 'low', schema: RECHECK_SCHEMA })
    if (!recheck || recheck.ok) break
    issues = recheck.remaining
    if (!issues.length) break
  }
  return { facts: facts && facts.verdict, newIssues: newIssues.length, applied: fix && fix.applied, skipped: fix && fix.skipped, chars: fix && fix.chars, remaining: recheck && recheck.remaining }
}

async function writeAppendix() {
  const appendix = await agent(`
你是寫手，負責「家庭理財白話說明文件」第 17 章《附錄：名詞表、來源清單、會過期的數字、空白工作表》。今天是 ${TODAY}。
必讀：${ROOT}/outline.md（§1 第 7、8、10、17、18 條與 §3「### 17-glossary-sources」）、${ROOT}/components.md、${ROOT}/design-brief.md「導讀與附錄的額外元素」（glossary、expiry、revisions、swipe-hint、wide、version-line 的 class）、${ROOT}/supplement-plan.md §3 unresolved、${ROOT}/research/gap-fill.md。然後掃描全部章節：
  grep -o 'data-term="[^"]*"' "${ROOT}"/chapters/*.html | sort | uniq -c
  grep -o '<span class="badge">[^<]*</span>' "${ROOT}"/chapters/*.html | sort | uniq -c
  grep -n '轉引，待官方原檔核對' "${ROOT}"/chapters/*.html
  grep -n '人力資本\\|甜蜜點' "${ROOT}"/chapters/*.html
產出 ${ROOT}/chapters/17-glossary-sources.html，<section class="chapter" id="ch-17" data-num="17" data-stage="8">，章首照契約（三個問題：「這個詞是什麼意思？」「這個數字還對嗎？」「哪些東西還沒查到？」；讀完你做得到：查任何一個詞、知道哪個數字幾月要重查、找到空白工作表；這章會用到前面的：不需要），章尾照契約（今天的一件事：把「會過期的數字一覽表」的下次重查月份加進手機行事曆，附完成判準；來源清單可只列本章引用的官方入口，沒有就用 --loose 並在 sources-wrap 放一句說明）。內容順序：
1. 名詞表 <dl class="glossary">：每個 data-term 一條，<dt id="term-＜術語＞">術語</dt><dd>白話定義一到兩句＋<a href="#ch-NN">第 N 章</a></dd>；定義要跟該章 dfn 所在句一致（讀那一句）。另外補「人力資本」（第 1 章正文有用到但 dfn 已移除，定義：未來所有勞動收入換算成今天的價值）與「甜蜜點」註明「本文自己的叫法，不是通用術語」。同類的放一起（收支與資產／債務與保險／投資／退休與稅／房子與家庭／法律與詐騙），每組前用 <h4> 小標。約 60 條以內。
2. 來源怎麼讀：四級符號說明（●台灣官方｜◐學術與國際機構含外國官方｜◑業界資料｜○本文推論）與「轉引」的意思，三到五句。
3. 會過期的數字一覽表：<div class="table-wrap wide"><p class="swipe-hint">可左右滑動</p><table class="expiry"> 五欄：數字｜適用年度｜上次確認日｜官方查證連結｜建議重查月份。從各章事實框裡把「制度性、每年會變」的數字全部收進來（免稅額與扣除額、級距、投保薪資分級表、勞退提繳與分級表、健保費率與補充保費、存款保險額度、循環利率上限、遺產贈與稅免稅額、房貸管制、房地合一、就學貸款利率、五大銀行利率、CPI 年增率、勞保基金精算、SPIVA 與 MSCI 年度數字），連結用該章來源條目的網址，建議重查月份依制度公告習慣（所得稅每年 12 月與 5 月、投保薪資每年 1 月、健保費率每年 1 月、央行利率每季）。
4. 待查清單：各章來源條目裡標「轉引，待官方原檔核對」的、研究檔 unverified 的、supplement-plan §3 需要作者提供的（粉專網址、摩根台灣版指南 PDF、舊版 JPM 圖、Schwab 版本疑點、台股 2008／2020 精確峰谷、分桶一手文獻），整理成三欄表（項目｜目前依據｜要去哪裡查）。
5. 空白工作表：十二張工作表清單，每項連到 #ws-1 … #ws-12（不重印）。
6. 修訂紀錄 <table class="revisions">：版本 1.0｜${TODAY}｜初版｜—。
7. <p class="version-line">本版完成日 ${TODAY} ／ 本版數字截止日 ${TODAY} ／ 下次建議重查 2027-01</p>，以及勘誤回報一句（「發現任何一條數字有誤，告訴給你這份文件的人；這是這份文件唯一的更新機制」）。
字數約 4,000（名詞表 3,000＋其他 1,000；表格不計）。交件前執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/17-glossary-sources.html" --loose，必須 0 錯誤；並用 grep 確認每個 data-term 都有對應的 term- id。不動其他檔案。
回傳 StructuredOutput：file、chars、checkerErrors、added、notes（名詞表條數、一覽表列數、待查清單列數、有沒有 data-term 找不到定義句的）。
`, { label: 'write:17-glossary-sources', phase: 'Appendix', model: 'opus', effort: 'high', schema: BUILD_SCHEMA })
  if (!appendix) return { built: false }
  const judge = await agent(`
你是裁判，對第 17 章附錄做對抗性驗證。你只讀不改。讀 ${ROOT}/chapters/17-glossary-sources.html、${ROOT}/components.md、${ROOT}/design-brief.md 額外元素、${ROOT}/outline.md §1 §2。先執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/17-glossary-sources.html" --loose。
檢查：1) 每個章節裡的 data-term（grep -o 'data-term="[^"]*"' chapters/*.html）都有 <dt id="term-…">，反之名詞表沒有多出章節沒用的詞（人力資本、甜蜜點例外）；2) 每條定義是否與該章 dfn 所在句一致、是否白話、≤2 句；3) 會過期的數字一覽表：抽查 12 個數字回各章事實框核對數字、年度、網址一致，遺漏的制度數字列出；4) 待查清單是否涵蓋各章「轉引」條目（grep 計數比對）與 supplement-plan §3；5) 表格 class 與 swipe-hint；6) 語氣 12 條；7) 章首章尾；8) 錨點 #ws-1…#ws-12、#ch-NN 都存在（grep 各章）。
回傳 StructuredOutput：verdict、issues、strengths。
`, { label: 'judge:17-glossary-sources', phase: 'Appendix', model: 'fable', effort: 'xhigh', schema: ISSUES_SCHEMA })
  let fix = null
  if (judge && judge.issues.length) {
    fix = await agent(`
你是修稿者，處理第 17 章附錄。檔案：${ROOT}/chapters/17-glossary-sources.html。契約：${ROOT}/components.md；額外元素：${ROOT}/design-brief.md。處理全部問題（blocker／major 必修）。不動其他檔案。
${JSON.stringify(judge.issues, null, 1)}
修完執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/17-glossary-sources.html" --loose，必須 0 錯誤。回傳 StructuredOutput：file、applied、skipped、checkerErrors、chars。
`, { label: 'fix:17-glossary-sources', phase: 'Appendix', model: 'opus', effort: 'medium', schema: FIX_SCHEMA })
  }
  return { built: true, chars: appendix.chars, notes: appendix.notes, issues: judge ? judge.issues.length : null, applied: fix && fix.applied, skipped: fix && fix.skipped }
}

log('第 9 章補完與第 17 章附錄同時進行')
const [ch09, appendix] = await parallel([finishCh09, writeAppendix])

phase('FinalReview')
let finalReview = null
try {
  finalReview = await workflow({ scriptPath: `${ROOT}/tools/workflows/final-review.js` })
} catch (e) {
  log(`整本複審子工作流失敗：${e && e.message ? e.message : e}`)
}

return { ch09, appendix, finalReview }
