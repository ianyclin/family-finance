export const meta = {
  name: 'family-finance-essay-revise-outline',
  description: '專篇 v1.0 前置：查證行為金融原始來源 → 裁判改大綱（新增心理偏誤兩節、作者七條指引一節、強化行為落差節）→ 更新哨兵',
  phases: [
    { title: 'Research', detail: '兩位研究員回推 15 個行為金融來源' },
    { title: 'Outline', detail: '裁判改大綱與 §5 數字清單' },
    { title: 'Tools', detail: 'check_essay.py 依新大綱更新' },
  ],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'
const ESSAY = `${ROOT}/essay`
const POSTS = `${ROOT}/research/author-fb-posts-all.json`
const TODAY = '2026-09-08'

const FACTS_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' }, summary: { type: 'string' },
    facts: { type: 'array', items: { type: 'object', properties: {
      topic: { type: 'string' }, claim: { type: 'string' }, value: { type: 'string' }, source: { type: 'string' }, url: { type: 'string' }, asOf: { type: 'string' },
      confidence: { type: 'string', enum: ['verified', 'likely', 'unverified'] }, note: { type: 'string' },
    }, required: ['topic', 'claim', 'source', 'confidence'] } },
  },
  required: ['file', 'summary', 'facts'],
}
const FIX_SCHEMA = {
  type: 'object',
  properties: { file: { type: 'string' }, applied: { type: 'number' }, skipped: { type: 'array', items: { type: 'object', properties: { issue: { type: 'string' }, reason: { type: 'string' } }, required: ['issue', 'reason'] } }, checkerErrors: { type: 'number' }, notes: { type: 'string' } },
  required: ['file', 'applied', 'skipped', 'checkerErrors'],
}

const COMMON = `
你在替投資專篇《隔離人性》（作者第一人稱，給零基礎朋友）查證行為金融的原始來源。今天是 ${TODAY}。鐵律：不捏造網址；實際打開才標 verified；只在搜尋摘要看到標 likely；查不到標 unverified 並寫搜尋過程。每條抄原文一句（英文原句可保留）與關鍵數字。工具：WebSearch／WebFetch（先 ToolSearch select:WebSearch,WebFetch）；學術論文優先開 DOI 頁、作者個人頁 PDF、SSRN、期刊摘要頁；morningstar.com、spglobal.com 對 WebFetch 回 403 時改試 web.archive.org 或轉引頁並標 likely。整體最多約 30 次抓取。
背景：作者粉專有一系列 AI 產出的〈指數化投資的人性困境〉九篇（在 ${POSTS} 裡，2025-12-29 到 2026-01-03），引用了下面這些研究，但那是二手；專篇只能用回推到原文的版本。
`

const TASKS = [
  { key: 'behavior-a', file: 'supp-behavior-a.md', prompt: `
查證清單 A：
1. Bar-Eli, Azar, Ritov, Keidar-Levin & Schein (2007) "Action bias among elite soccer goalkeepers: The case of penalty kicks", Journal of Economic Psychology 28(5)：守門員撲左右的比例、留在中間的比例（約 6%？）、留在中間的擋球成功率 vs 撲左右的成功率。
2. Barber & Odean (2000) "Trading Is Hazardous to Your Wealth", Journal of Finance 55(2)：交易最頻繁的那一組年報酬 vs 市場（11.4% vs 17.9%？）、樣本期間、結論句。
3. Odean (1998) "Are Investors Reluctant to Realize Their Losses?", Journal of Finance 53(5)：處分效應的定義與主要數字（賣贏家的傾向比賣輸家高多少）。
4. Barber, Huang, Odean & Schwarz (2022) "Attention-Induced Trading and Returns: Evidence from Robinhood Users", Journal of Finance 77(6)：羊群交易後的報酬數字。
5. Vanguard (2020) "Cash panickers: Coronavirus market volatility"（研究短文）：期間、轉全現金的投資人比例、其中多少比例結果比不動的差、年齡與經驗特徵。
6. Morningstar "Mind the Gap" 2024 與 2025：投資人報酬落後基金報酬的年化差距、產業基金最大／配置型基金最小的說法、以及報告或評論裡「波動比費用更影響投資人拿到的報酬」的原句；另找一篇對其方法論的學術或專業批評。
7. DALBAR QAIB 2024：848 個基點那個數字的原始出處，以及對 DALBAR 方法論的批評（例如 Wade Pfau 2017 "A Warning to the Advisory Profession: DALBAR's Math Is Wrong"）。
8. 「彼得·林區麥哲倫基金平均投資人虧損」的說法：找原始出處（富達內部研究？）；找不到就明寫「二手轉述、原始資料未公開」。
輸出檔案：${ROOT}/research/supp-behavior-a.md` },
  { key: 'behavior-b', file: 'supp-behavior-b.md', prompt: `
查證清單 B：
9. Kuhnen & Knutson (2005) "The Neural Basis of Financial Risk Taking", Neuron 47(5)；Knutson & Bossaerts (2007) "Neural Antecedents of Financial Decisions", J Neurosci：主要結論句（哪個腦區活化與冒險或迴避相關），不要數字。
10. Tversky & Kahneman (1992) "Advances in Prospect Theory"：損失趨避係數 λ≈2.25 的原句與頁碼（手冊第 8 章已用，這裡只要 DOI 與原句）。
11. Benartzi & Thaler (1995) "Myopic Loss Aversion and the Equity Premium Puzzle", QJE 110(1)：核心結論（越常檢視投資組合，損失趨避越痛、越不願持股）與一句原文。
12. Samuelson & Zeckhauser (1988) "Status Quo Bias in Decision Making", J Risk & Uncertainty 1：定義句；以及 Madrian & Shea (2001) 401(k) 自動加入的參與率變化（QJE 116(4)）——自動化利用惰性的證據。
13. Morgan Housel《The Psychology of Money》(2020)「Nothing's Free」那一章：波動是門票（fee）不是罰單（fine）的原句；Naval Ravikant 2018 推文串「How to Get Rich」裡地位遊戲 vs 財富遊戲的原句。
14. 相對剝奪感提高冒險：Haisley, Mostafa & Loewenstein (2008) "Subjective relative income and lottery ticket purchases", J Behavioral Decision Making 21(3)，或 Callan, Ellard, Shead & Hodgins (2008)：主要結論。
15. 事後之明：Fischhoff (1975) "Hindsight ≠ foresight"；近因偏誤在投資上的一篇可引研究（例如 Greenwood & Shleifer 2014 "Expectations of Returns and Expected Returns", Review of Financial Studies：投資人預期跟隨近期報酬）。
16. Kahneman & Riepe (1998) "Aspects of Investor Psychology", Journal of Portfolio Management：過度自信與投資的結論句。
輸出檔案：${ROOT}/research/supp-behavior-b.md` },
]

phase('Research')
const research = (await parallel(TASKS.map(t => () => agent(COMMON + t.prompt + `\n用 StructuredOutput 回傳 file、summary、facts。`, { label: `research:${t.key}`, phase: 'Research', model: 'sonnet', effort: 'high', schema: FACTS_SCHEMA })))).filter(Boolean)
log(`研究完成 ${research.length}/2`)

phase('Outline')
const outline = await agent(`
你是裁判兼總編輯，負責把投資專篇《隔離人性》從 v0.9 改成 v1.0 的大綱。今天是 ${TODAY}。
現況：${ESSAY}/outline.md（十節定案、§5 數字清單、§6 契約）與 ${ESSAY}/index.html（v0.9 成品）。作者 2026-09-08 讀後三點意見（逐字）：
「關於隔離人性，好像什麼都看完了，什麼都沒說。1. 你有看完我在 fb 的『Gemini Deep Research：指數化投資的人性困境（9/9）』的每一篇嗎？2. 對於實際指引沒有給予建議。例如：1) 低成本且分散的市值型指數ETF（全球：VT、VWRA、VALU、009826，台灣：0050、006208）2) 不擇時（定期）買進 3) 盡可能的買進（增加儲蓄率）4) 適當股債比例的資產配置（每年再平衡一次）5) 長期持有（至少十年，二十年以上為佳）6) 減少關注投資的時間，用於家庭或增加收入 7) 十年抵達甜蜜點（預期報酬等於儲蓄投入）3. 你重新閱讀一次。驗證所有內容是否『正確』，有無邏輯或知識問題。有無需要新增投資者可能會遇到的行為或是心理偏誤討論。」
主線裁定：
(a) 九篇〈人性困境〉在 ${POSTS}（2025-12-29～2026-01-03）全文讀完；它們的觀點可以用（簡單 vs 容易、行為落差、恐懼與貪婪的生理機制、相對剝奪與地位遊戲、無聊、麥哲倫與 2020 案例、行動偏誤與控制幻覺、護欄三招：投資政策聲明＝規則卡、自動化、波動是門票不是罰單），但每個數字與研究只能用 ${ROOT}/research/supp-behavior-a.md、supp-behavior-b.md 裡 verified／likely 的版本；麥哲倫若查無原始資料，寫成「常被引用但原始資料未公開」。
(b) 新結構 13 節：保留 01–08；09 行為落差節改寫成「投資本身賺的，跟投資的人拿到的，差在哪裡」（Morningstar、Vanguard 2020、Barber & Odean、麥哲倫的誠實寫法）；新增 10「大腦不是為投資設計的」（損失趨避 2.25、恐懼與獎賞迴路的質性說法、越常看越痛、行動偏誤的守門員、控制幻覺與過度自信）；新增 11「常見的偏誤，和它們在帳戶裡長什麼樣」（清單式：損失趨避、近因、從眾與比較／相對剝奪、過度自信與控制幻覺、行動偏誤、沉沒成本與處分效應、心理帳戶（配息）、定錨（回本）、事後之明、現狀偏誤（好的一面：自動化）；每條三行：它是什麼、在帳戶裡長什麼樣、對策，對策要對回規則卡或作者的做法）；12 原「規則」節（原 10）保留並補「波動是門票不是罰單」與「什麼都不做的藝術」；新增 13「如果你問我怎麼做：七條」——作者第一人稱、對朋友的具體建議，七條照作者原文順序，每條寫「我怎麼做、理由、代價」，商品清單照粉專版（全球 VT、VWRA、VALU、009826；台灣 0050、006208）並註明「同類商品很多檔，這是我自己買的」；股債比例寫「照年齡與能承受的波動設，我自己現在固定九比一」；再平衡寫「每年一次或門檻到了才動，我自己用門檻」；第七條甜蜜點用 7% 約十年；節末固定聲明「這是我對朋友的一般建議，不是針對你的量身建議」。這一節允許「我建議」，仍不用「你應該」「一定」。
(c) 護欄不變：不寫作者績效百分比；每句經歷對到貼文日期；每節有一句話重點與交還；證據框指回手冊或本輪 supp-behavior 檔（新來源用「來源框」形式，p.src 寫論文作者年份與連結）。術語上限放寬到 14 個，新增的優先用白話名（例如「損失趨避」可留，「處分效應」改寫成「賣掉賺的、留著賠的」）。
(d) 全篇字數約 12,000；13 節各給 targetLength。故事總占比仍 ≤30%。
任務：
1. 改寫 ${ESSAY}/outline.md：§2 骨架表（節序、id、標題、章、術語配額、字數；哨兵讀這張表）、§3 十三節定案（新節與改寫節要有 concept／story／storyDates／evidence／terms／handback；01–08 只列「維持」）、§5 允許的數字清單（加入本輪 verified／likely 的行為金融數字，每個數字後面括號寫來源；把 v0.9 用到但清單漏列的 10%、100萬元、1萬、30%、300元、50%、276萬、14,703,633、15,780,598、約 9%、2,000 美元補上）、§6 契約（新增：第 13 節 <section class="part advice" data-allow-products="true"> 允許商品代號與「我建議」；新增 <aside class="box source"> 來源框給非手冊來源；術語上限 14）。
2. 逐一用 Python 確認新節 storyDates 存在於 ${POSTS} 且內容相符；證據指回的手冊段落用 grep 確認；本輪來源用 supp-behavior 檔確認等級。
3. 回傳 StructuredOutput：file、applied（新增與改寫的節數）、skipped、checkerErrors（0）、notes（13 節清單、新增術語、§5 新增數字）。
`, { label: 'judge:revise-outline', phase: 'Outline', model: 'fable', effort: 'xhigh', schema: FIX_SCHEMA })

phase('Tools')
const tools = await agent(`
你是 applier。依更新後的 ${ESSAY}/outline.md §2、§5、§6 更新 ${ROOT}/tools/check_essay.py：
1. 節序、id、術語配額、字數目標若是從 §2 表動態讀取就不用改；若有寫死的部分（例如 SECTIONS、術語總數 10、允許數字 ALLOWED_NUMBERS）改成：術語總數上限從 §2 表加總（或 14）；ALLOWED_NUMBERS 依 §5 清單重建（保留原有的）；第 13 節（section 有 data-allow-products="true" 或 class 含 advice）豁免商品代號檢查與「我建議」；新增 <aside class="box source"> 視同證據框（必須有 p.src 與 a[href]，href 可以是外部論文網址，不強制含 #ch-）。
2. 用 essay/sections/ 現有十節跑一次 --full（先跑 assemble_essay.py），確認舊節仍 0 錯誤（新增節還沒寫時，缺節只列出不算錯）。
回傳 StructuredOutput：file、applied、skipped、checkerErrors、notes。
`, { label: 'tools:update-checker', phase: 'Tools', model: 'opus', effort: 'medium', schema: FIX_SCHEMA })

return { research: research.map(r => ({ file: r.file, summary: r.summary, unverified: (r.facts || []).filter(f => f.confidence === 'unverified').map(f => f.topic) })), outline: outline && { applied: outline.applied, notes: outline.notes, skipped: outline.skipped }, tools: tools && { applied: tools.applied, notes: tools.notes, errors: tools.checkerErrors } }
