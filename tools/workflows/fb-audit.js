export const meta = {
  name: 'family-finance-fb-audit',
  description: '稽核粉專 154 篇的整合結果：加的 23 項是否在手冊、引句日期數字是否忠於原文；已有的 24 項落點是否存在；需來源 6 項是否列入待查',
  phases: [{ title: 'Audit', detail: '四組並行' }],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'
const PLAN = `${ROOT}/research/fb-integration-plan.md`
const POSTS = `${ROOT}/research/author-fb-posts-all.json`

const AUDIT_SCHEMA = {
  type: 'object',
  properties: {
    rows: { type: 'array', items: { type: 'object', properties: {
      item: { type: 'string' }, ruling: { type: 'string' },
      status: { type: 'string', enum: ['present', 'partial', 'missing', 'not-applicable'] },
      where: { type: 'string' }, quote: { type: 'string' },
      faithful: { type: 'string', enum: ['ok', 'date-mismatch', 'quote-mismatch', 'number-mismatch', 'tone-violation', 'n/a'] },
      note: { type: 'string' },
    }, required: ['item', 'ruling', 'status', 'where', 'faithful'] } },
  },
  required: ['rows'],
}

const COMMON = `
你是稽核員，你只讀不改。作者粉專 154 篇的整合裁定在 ${PLAN}（§1 總表、§2 A1–A20 逐項、§3 covered C1–C24、§4 skip、§5 needs-source N1–N6、§6 conflicts）。主線另外加了三項：(甲) 第 7 章作者定義的「滿足點」與儲蓄率對年數表；(乙) 第 13 章零用錢 details 裡的壓歲錢父子對話；(丙) 第 1 章旅費乘以五那段。原始貼文在 ${POSTS}（用 Python 依 published_iso 前 10 碼取原文）。手冊現況以 ${ROOT}/chapters/00–17.html 為準（用 grep 找落點，找不到就多換關鍵詞）。
每一項回報：item、ruling（一句）、status、where（章＋元件）、quote（手冊裡對應的一句，逐字 ≤60 字）、faithful（把手冊句子與原始貼文對照：日期對不對、引句是否逐字、數字是否一致、有沒有變回指令或推薦語氣）、note。
`

const GROUPS = [
  { key: 'A1-A10', prompt: COMMON + `你負責 A1 到 A10（第 7、8、9、3 章）。每項都要回原文核對：A1 的「兩倍」「不到一成」、A4 的「0.02 個百分點」、A8 的「約 3%」「五天」「兩年多只發生一次」、A9 的三種情況、A5 的「兩成」。` },
  { key: 'A11-A20+甲乙丙', prompt: COMMON + `你負責 A11 到 A20 與 (甲)(乙)(丙)。每項回原文核對：A11 的家人那句、A12「新的資訊還是新的價格」、A13 日圓案例、A14 指投率定義、A15 過年那個月、A16 儲蓄險解約的前提句、A17 行政代價、A18 零用錢三條規則與 1%／5%、A19 級距低的那一位名下、A20「3% 改 2.5%」、(甲) 滿足點定義與表格數字（用 n = ln(1+0.8/s)/ln(1+r) 重算）、(乙) 對話逐字、(丙) 旅費句。` },
  { key: 'C1-C24', prompt: COMMON + `你負責 covered 的 C1 到 C24：裁定說「文件已有、在哪裡」，請逐條確認那個落點現在真的存在（grep 到原句），status 填 present／missing；faithful 填 n/a 除非你發現那段跟作者說法矛盾。` },
  { key: 'N+S', prompt: COMMON + `你負責 N1 到 N6（needs-source）：確認第 17 章待查清單是否已列入（N1、N2、N4、N5 應已列；N3、N6 裁定不放），status 填 present／missing；以及 skip 清單 S1–S27：不用逐條找，只需抽查 6 條最可能誤入的（S1 月增率序列、S2 個人績效數字如 MWRR／含息報酬率／甜蜜點進度百分比、S3 商品變更史、S13 質押、S14 股票申購、S20 槓桿建議），用 grep 在 chapters/ 確認它們確實不在手冊裡（status 填 not-applicable 表示確認未出現；若出現填 present 並在 note 說明）。` },
]

const results = (await parallel(GROUPS.map(g => () => agent(g.prompt + `\n回傳 StructuredOutput：rows。`, { label: `audit:${g.key}`, phase: 'Audit', model: 'opus', effort: 'medium', schema: AUDIT_SCHEMA })))).filter(Boolean)
return results.flatMap(r => r.rows)
