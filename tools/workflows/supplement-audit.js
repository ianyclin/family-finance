export const meta = {
  name: 'family-finance-supplement-audit',
  description: '稽核作者補充的 32 條素材：裁定是什麼、查證結果是什麼、現在手冊裡有沒有、在哪一句',
  phases: [{ title: 'Audit', detail: '四組並行，逐條在 chapters/ 找落點' }],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'

const CLAIMS = [
  'C1 報酬／時間／風險三圓（交集是詐騙）', 'C2 每筆錢對應 30 年後的那個月（不用擔心短期）', 'C3 短期起伏、長期上漲', 'C4 定期定額買在月高低點不重要',
  'C5 投入頻率幾乎沒影響', 'C6 為什麼買大盤（SPIVA）', 'C7 為什麼分散不同國家（優缺點）', 'C8 指數化的情緒與時間價值',
  'C9 甜蜜點、滿足點', 'C10 盡可能提高儲蓄率、歐印、人力資本、體驗＞物質', 'C11 早期投資的重要性（四人圖）', 'C12 只掌握自己能做的',
  'C13 不預測高低點（連上帝也贏不了定期定額）', 'C14 行為與心理很重要', 'C15 賣出理由千百種 Hold 就對了（2009 起 S&P 事件圖）', 'C16 道瓊 1900–2004 事件圖（8906／2206 亂碼）',
  'C17 你以為的複利 vs 真實經歷（平滑 vs 鋸齒）', 'C18 30 年複利時間軸圖（35→65／60→100 矛盾）', 'C19 每年 1 萬美元、7%、十個里程碑與儲蓄／報酬占比', 'C20 影響退休的六面向（完全／部分／無力掌控）',
  'C21 摩根台灣版提領率 4／5／6% 圖', 'C22 年內最大跌幅 vs 全年報酬（14.3%／31 of 41）', 'C23 國家輪動表與資產類別輪動表', 'C24 美國 vs 非美每十年輪替',
  'C25 錯過最好的 10／20／30 天', 'C26 持有 1／5／10／20 年區間收窄', 'C27 短中長期目標對應配置（分桶）', 'C28 四個人比較（Chloe／Lyla／Quincy／Noah）',
  'C29 摩根台灣版人生三階段配置', 'C30 摩根台灣版所需投資金額表（漏字、順序矛盾）', 'C31 65 歲存活到 75／80／85 機率（美國資料）', 'C32 美 vs 非美循環圖（Hartford 2019）',
]
const groups = [CLAIMS.slice(0, 8), CLAIMS.slice(8, 16), CLAIMS.slice(16, 24), CLAIMS.slice(24, 32)]

const AUDIT_SCHEMA = {
  type: 'object',
  properties: {
    rows: { type: 'array', items: { type: 'object', properties: {
      claim: { type: 'string' },
      ruling: { type: 'string' },
      verified: { type: 'string' },
      factError: { type: 'string' },
      status: { type: 'string', enum: ['present', 'partial', 'missing', 'dropped-by-design'] },
      where: { type: 'string' },
      quote: { type: 'string' },
      note: { type: 'string' },
    }, required: ['claim', 'ruling', 'status', 'where'] } },
  },
  required: ['rows'],
}

const results = (await parallel(groups.map((g, i) => () => agent(`
你是稽核員。作者先前補充了 32 條素材（24 張圖與 14 條主張），裁判已在 ${ROOT}/supplement-plan.md 逐條裁定（§0 總表、§1 逐條、§2 factErrors、§3 unresolved），查證細節在 ${ROOT}/research/supp-*.md。之後這些內容被整合進手冊，但後續又經過整本複審與刪減、以及粉專內容整合，所以現在到底有沒有在手冊裡，必須用目前的章節檔為準：${ROOT}/chapters/00-how-to-use.html … 17-glossary-sources.html。
你負責這 8 條：
${g.map(c => '- ' + c).join('\n')}
每一條回報：
- ruling：裁定（use／rewrite／drop）與一句理由（抄 supplement-plan）。
- verified：查證結果一句（來源等級、核到什麼；抄 supp 檔或裁定檔）。
- factError：作者素材本身的錯誤（若 §2 有列，抄下；沒有填「無」）。
- status：present（裁定要放的內容現在確實在手冊裡）／partial（只放了一部分，說明缺哪半）／missing（裁定要放但現在找不到）／dropped-by-design（裁定 drop 或主線決定不放）。
- where：章號＋元件（例如「第 9 章 算式框」），用 grep 在 chapters/ 找關鍵詞（數字、專有名詞、改寫句片段）確認，找不到就多換幾個關鍵詞再下結論。
- quote：手冊裡對應的一句（逐字，≤60 字）。
- note：與裁定改寫句相比有沒有走樣（例如變回指令語、數字不同）。
你只讀不改。回傳 StructuredOutput：rows。
`, { label: `audit:${i + 1}`, phase: 'Audit', model: 'opus', effort: 'medium', schema: AUDIT_SCHEMA })))).filter(Boolean)

return results.flatMap(r => r.rows)
