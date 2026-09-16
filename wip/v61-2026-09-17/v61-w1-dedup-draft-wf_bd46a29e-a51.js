export const meta = {
  name: 'v61-w1-dedup-draft',
  description: '隔離人性 v61 第一批：找出重複觀念的全部位置，按節分工產出刪重複與回填補丁',
  phases: [
    { title: 'Map', detail: '每個跨節的題目派一個偵查代理，列出所有出現位置' },
    { title: 'Draft', detail: '按節分工，每節一個起草代理產出 guidetools 補丁檔' },
  ],
}

const REPO = '/Users/linyenchu/Cladue Code/family-finance'
const W1 = args.scratch
const SPEC = REPO + '/docs/core-edition/specs/spec-v61-remaining.md'
const DEC = REPO + '/docs/core-edition/specs/v61-decisions.md'

const MAP_SCHEMA = {
  type: 'object',
  properties: {
    decision: { type: 'string' },
    canonical_section: { type: 'string' },
    occurrences: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          section: { type: 'string', description: 'section id，例如 s11、start、cases' },
          snippet: { type: 'string', description: 'guide/index.html 裡逐字存在的 HTML 子字串，40–120 字，用來定位' },
          kind: { type: 'string', enum: ['canonical', 'full_restatement', 'partial', 'brief_mention', 'insert_here'] },
          note: { type: 'string' },
        },
        required: ['section', 'snippet', 'kind', 'note'],
      },
    },
    caveats: { type: 'string' },
  },
  required: ['decision', 'canonical_section', 'occurrences', 'caveats'],
}

const MAPS = [
  { d: 'D1', what: '「費用怎麼算進試算」：整體報酬率＝表一查到的數字 −總費用率；暫估費用率 0.5%（路徑 A/B）；路徑 C 要問兩層合計年費率；表二沒有那一列取較小的、低於 2.0% 用複利計算機。決定中說散在 10 個地方，其中兩處 139 字一模一樣。', canon: 's11（查表頁與欄位表；查表頁區塊 data-lite-alt="lookup-tables" 不可動，所以正典是它）' },
  { d: 'D2', what: '「錢不夠時照順序補：多存 → 延後 → 降低目標，不靠調高股票比例」。決定中說第 11 節講了 6 次；也請找全書其他節。', canon: 's11 三問第 3 題那一列（「要調高股票比例才到得了目標嗎？」那句是共同事實，一字不改）' },
  { d: 'D3', what: '「五年內要用的錢不放股票」（含分桶、先分出去、五年是底線不是放超過五年就安全）。決定中說有四個地方寫得幾乎一樣。', canon: 'start（投資前的安全順序）' },
  { d: 'D4', what: '「冷卻期怎麼分辨」：因短期漲跌想賣要等冷卻期；願意把比例改低、以後不因市場漲回來又升回去，才算長期降低風險；人生改變或睡不著可立即降。決定中說有 62 字在兩處一字不差（時間表 firstmonth 與年檢 annual）。', canon: 's10（那段是共同事實，逐字不動）' },
  { d: 'D5', what: '「投資前先確認五件事」清單（預備金、高利率債、保障、五年內要用的錢、現金流等）。決定中說在 ten、why、start 三處，三張不一樣。另外找出 why 那張獨有的兩點（「4% 是第 1 節的低情境」「能忍的跌幅乘 2 只能刪掉明顯太高的比例」）在全書還有哪裡寫到。', canon: 'start' },
  { d: 'D9', what: '「防守那一塊放什麼」（台幣定存、中期公債或整體投資等級債、不用長天期、未避險海外債券的匯率），決定中說寫在兩節、末句一模一樣。', canon: 'products（ETF 與債券檢查表）' },
  { d: 'L2', what: '「能忍整個投資圈跌幾成，乘 2 就是股票最多放幾成」這個粗篩。找出全書每一處；判斷哪一處最適合補上例子「例如能忍跌 20%，股票最多放四成：股票跌一半時，四成股票剛好少兩成。」（參考 lite/alt/retired/ch4-steps.html 的寫法）', canon: 's11 地板／壓力測試／三問那張卡' },
  { d: 'L3', what: '兩件事各找「正文第一次需要解釋」的位置（不含詞彙表、白話版、黃框、標題）：(a) 配息會讓基金每一份的價值變少（完整版現在說「從淨值扣掉」之類）——要換成「配息像從存錢筒拿錢給你，存錢筒就少了同一筆」；(b) 正文第一次直接用「年化」而沒解釋的地方——要補「年化就是平均一年長多少」。參考 lite/alt/retired/ch6-pick.html 與其他退役短稿。', canon: '（各自第一次出現的節）' },
  { d: 'L7', what: '兩件事：(a) 完整版寫「第一年賺很多，以為自己很會挑」之類、沒有用「新手運」這個名字的地方（參考 lite/alt/retired/ch11-mind.html 等）；(b) 「朋友集中一檔賺很多」那張卡的標題，要把結論「他也幫你打工」放進標題（參考 lite/alt/retired/ch11-tsmc.html、ch11-crowd.html）。', canon: '（各自所在的節）' },
]

phase('Map')
const maps = await parallel(MAPS.map(m => () => agent(
`你是偵查代理，只讀不改任何檔案。專案：${REPO}。
正式原文：guide/index.html（約 0.9 MB，不要整檔 Read；用 grep／python 小範圍讀）。
先讀：${SPEC}（這一輪規格）和 ${DEC} 裡「${m.d}」那一條。

任務：題目 ${m.d}——${m.what}
預定正典位置：${m.canon}

把這個觀念在全書的**每一處**出現都找出來（包含換句話說的版本，不只逐字相同的）。每一處給：
- section：所在 <section> 的 id（節 id 和顯示節號不同：#cases 是第 12 節、#s12 是第 13 節、#s13 是第 14 節）
- snippet：該處 HTML 裡逐字存在的一小段（40–120 字元，要能用 python s.count(snippet)>=1 找到；寫完請實際用 python 驗證）
- kind：canonical（正典）／full_restatement（把整套講一遍）／partial（講一部分）／brief_mention（一句帶過，通常應該留著）／insert_here（L 題要補寫的位置）
- note：這一處講了什麼、有沒有別處沒有的資訊
不含：黃框 div.story、source-card、figure 內、lite/ 目錄。caveats 寫下起草的人要小心的事（共同事實、工作表還在用的區塊 plan-blank／lookup-tables／ch4-drill／#ten div.warning、數字）。`,
  { label: `map:${m.d}`, phase: 'Map', schema: MAP_SCHEMA, model: 'sonnet', effort: 'medium' }
)))

const okMaps = maps.filter(Boolean)
log(`Map 完成 ${okMaps.length}/${MAPS.length}；偵查結果：` + okMaps.map(x => `${x.decision}:${x.occurrences.length}處`).join('、'))

// 按節分工
const bySec = {}
const add = (sec, line) => { (bySec[sec] = bySec[sec] || []).push(line) }
for (const mp of okMaps) {
  for (const o of mp.occurrences) {
    add(o.section, `【${mp.decision}】kind=${o.kind}｜定位片段：${JSON.stringify(o.snippet)}｜${o.note}｜正典：${mp.canonical_section}｜偵查代理提醒：${mp.caveats}`)
  }
}
const LOCAL = [
  ['cases', '【D7】選 B：只有陳大哥留摺疊全表；阿凱、小芸與阿哲的摺疊全表拿掉，只留「地板→壓力測試→三問→缺口怎麼補」四段推理（推理裡的數字要留著；拿掉的表若有推理裡沒有的關鍵數字，改寫進推理或確認節末總表有）。'],
  ['s11', '【D8】選 B：欄位表（怎麼填）不和一頁空白版合併，只把「怎麼填」那一欄的說明縮短（不刪規則，重複的推導改指路到本節別處或查表頁）。空白版 plan-blank 與查表頁 lookup-tables 區塊一個字都不動。'],
  ['s11', '【S8】選 B：「兩把尺」名字不改；在第 11 節定義兩把尺的地方，用一句話明白寫出第二把尺（壓力測試）量的是什麼。'],
  ['s10', '【L4-冷卻期】選 A：冷卻期那一整團散文照 lite/alt/retired/ch8-cooling.html 的分段（規則／例外／怎麼分辨）重排，一個字不改，只加小標（用 <strong> 開頭或既有結構，不新增 class）與分段。共同事實那句逐字保留。'],
  ['s13', '【L4-儲蓄險】選 A：儲蓄險解約那一題照 lite/alt/retired/ch2-start.html 的 1–5 步編號重排（用 <ol class="checklist">），內容不改。'],
  ['annual', '【L1】選 A：「自己的報酬」那一項，用退役短稿（lite/alt/retired/ch12-xirr.html、ch12-annual.html）約 581 字的寫法當正文；其餘細節（1 月 1 日的寫法、淨投入算法、交割戶就是薪水帳戶、借錢投資、和指數比的三步精算）收進一個 <details><summary>…</summary>…</details>；「防守用的定存和賣掉暫放的錢最好放分開帳戶」「直接拿指數當年漲幅比會失真」兩句必須留在摺疊裡。史萊姆村圖 figure.chart.photo 不動。沒有任何內容刪掉。'],
  ['annual', '【L5】選 A：年檢那 10 條照 lite/alt/app-a-checklist.html（工作表第 3 頁，已是 7 組）的分法重新歸組（預備金＋保單合併、計畫表＋家庭一頁表合併、稅＋帳戶安全合併）。每一條原本的內容都要留著；在回報的 protected_touched 寫 app-a-checklist（主線會重新 stamp）。注意 app-a-checklist 的 src 選擇器是 `#annual ol.checklist:contains(儲蓄率：)`，重排後仍必須是 #annual 裡一個含「儲蓄率：」的 ol.checklist。'],
  ['withdraw+lifecycle', '【D6＋D11】選 A：「用錢、退休與家庭交接」(withdraw) 裡講退休提領與報酬順序風險的那段（兩個人各 100 萬的例子等）併進「年齡、槓桿與退休」(lifecycle) 講提領的那一題：先放兩個人的畫面，再接 Vanguard 1973/1974 的數字（先畫面、再道理、最後數字），重複的句子只留一次。withdraw 縮成以家庭交接（家庭一頁表）為主，重點句「市值型配置加一張規則卡，是最容易交接的組合」留在 withdraw。這一輪**不改節名、不改 h2**；lifecycle 三個嵌在問題中間的黃框位置不動。全書其他節指向 withdraw 講提領的連結，列進 cross_section_followups，不要自己改。'],
]
for (const [sec, line] of LOCAL) add(sec, line)
// withdraw 與 lifecycle 合成一個起草代理
for (const s of ['withdraw', 'lifecycle']) {
  if (bySec[s]) { (bySec['withdraw+lifecycle'] = bySec['withdraw+lifecycle'] || []).push(...bySec[s].map(x => `（${s} 節）` + x)); delete bySec[s] }
}
const tasks = Object.entries(bySec)
log('起草分工：' + tasks.map(([s, l]) => `${s}(${l.length})`).join('、'))

const DRAFT_SCHEMA = {
  type: 'object',
  properties: {
    key: { type: 'string' },
    patch_file: { type: 'string' },
    patch_count: { type: 'integer' },
    decisions_done: { type: 'array', items: { type: 'string' } },
    decisions_skipped: { type: 'array', items: { type: 'object', properties: { decision: { type: 'string' }, reason: { type: 'string' } }, required: ['decision', 'reason'] } },
    removed_facts_now_in: { type: 'array', items: { type: 'object', properties: { fact: { type: 'string' }, now_found_in: { type: 'string' } }, required: ['fact', 'now_found_in'] } },
    protected_touched: { type: 'array', items: { type: 'string' } },
    new_numbers: { type: 'array', items: { type: 'string' } },
    cross_section_followups: { type: 'array', items: { type: 'string' } },
    copy_check_ok: { type: 'boolean' },
    notes: { type: 'string' },
  },
  required: ['key', 'patch_file', 'patch_count', 'decisions_done', 'decisions_skipped', 'removed_facts_now_in', 'protected_touched', 'new_numbers', 'cross_section_followups', 'copy_check_ok', 'notes'],
}

phase('Draft')
const drafts = await parallel(tasks.map(([sec, lines]) => () => {
  const key = sec.replace(/[^a-z0-9]+/gi, '-')
  const secs = sec.split('+')
  return agent(
`你是起草代理（照已拍板的選項產出補丁，不做設計決定）。專案：${REPO}。
**不准修改 guide/index.html 或 repo 裡任何檔案。** 只准寫到 ${W1}/ 底下。

先讀（照順序）：
1. ${SPEC}（這一輪的選項與硬規則，權威）
2. ${DEC} 裡和你的題目有關的那幾條
3. ${REPO}/docs/core-edition/specs/eli5-rules.md 的「寫法」與「不能動的東西」（本輪明文要求的例外：D7 摺疊表、D8 表格欄位、L5 年檢清單、L7 標題、L1 收進摺疊、L4 加小標與編號）
4. ${REPO}/docs/handoff-guide-2026-09-16.md 的「標記系統」與「節 id ≠ 顯示的節號」
5. ${REPO}/lite/facts.txt（每一行都必須在改完的 guide/index.html 純文字裡仍然逐字找得到）

你只負責這些節：${secs.join('、')}。補丁的 old 只能落在這些 <section> 裡（例外：無）。
你的工作清單（偵查代理找到的位置＋本節的題目）：
${lines.map((l, i) => `${i + 1}. ${l}`).join('\n')}

做法：
- 正典那一處保留（必要時可以把別處獨有、正典沒有的資訊補進正典——但只有正典也在你的節裡才能補；不在你的節就列進 cross_section_followups）。
- 不是正典、把整套講一遍的：縮成一句話＋連結到正典（節號連結 <a class="xref" href="#id">N</a> 或節名連結「<a class="xref" href="#id">節名</a>」），指路句要讓讀者知道去那裡看到什麼。
- brief_mention（一句帶過、在上下文需要的）通常保留。
- 被刪掉的每一個事實或數字，都必須在全書別處（正典）找得到；在 removed_facts_now_in 逐條寫出它現在在哪裡（節 id＋一小段原文）。找不到就不要刪。
- 不動：div.story、mark.key 文字、facts.txt 的句子、plan-blank／lookup-tables／ch4-drill／#ten div.warning 四個區塊（annual 的 app-a-checklist 只在 L5 可以動）、source-card、figure。
- 名詞連結 a.term 每節只標第一次出現：刪掉某節第一次出現的名詞連結時，要把連結移到該節下一次出現處。
- 不新增事實與數字；如果寫了新的示意數字，列在 new_numbers。

輸出：
1. 補丁檔寫到 ${W1}/patch-${key}.json：JSON 陣列，每個元素 {"section","old","new","why"}（why 開頭寫題號，例如「D3：…」）。old 必須在 guide/index.html 裡**恰好出現一次**、補丁之間不重疊。
2. 自我檢查（一定要做）：
   python3 ${REPO}/tools/guidetools.py apply ${REPO}/guide/index.html ${W1}/copy-${key}.html ${W1}/patch-${key}.json
   python3 ${REPO}/tools/guidetools.py check ${W1}/copy-${key}.html
   並用 python 確認 lite/facts.txt 每一行（去掉 full-only: 前綴、略過 # 與空行）在副本的純文字（去標籤、壓空白）裡仍找得到；列出你這些節改前改後的阿拉伯數字集合差異。
   都過了 copy_check_ok=true。
3. 回傳結構化摘要（不要把補丁內容貼進回傳）。做不到或你判斷不該做的題目，寫進 decisions_skipped 並說明理由。`,
    { label: `draft:${sec}`, phase: 'Draft', schema: DRAFT_SCHEMA, model: 'opus', effort: 'high' })
}))

return { maps: okMaps.map(m => ({ decision: m.decision, canonical: m.canonical_section, n: m.occurrences.length, secs: [...new Set(m.occurrences.map(o => o.section))] })), drafts: drafts.filter(Boolean), failedDrafts: tasks.length - drafts.filter(Boolean).length }
