export const meta = {
  name: 'family-finance-supplement-finish',
  description: '覆核作者補充的 24 張圖與 14 條主張：補完三路查證（生命表與摩根圖、台股自算、作者來源），再由裁判逐條裁定可用／改寫／不用',
  phases: [
    { title: 'Research', detail: '三位研究員補完，寫進 research/supp-*.md' },
    { title: 'Judge', detail: '裁判逐條裁定並給出符合語氣規範的改寫句與落點章節' },
  ],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'
const TODAY = '2026-09-07'

const COMMON = `
你在替「家庭理財白話說明文件」覆核作者補充的素材。今天是 ${TODAY}。文件鐵律：每個數字都要能回推到原始來源；媒體、部落格、粉專只能當「存在性線索」，不能當數字來源；作者價值觀是不替讀者下結論、不預測市場。
工具：WebSearch／WebFetch（若尚未載入，先 ToolSearch select:WebSearch,WebFetch）。已知 spglobal.com、morningstar.com、nhi.gov.tw 對 WebFetch 回 403；遇到就改試 web.archive.org 的存檔、機構的其他頁面、或標 unverified，不要硬耗；整體最多約 30 次抓取。
鐵律：不捏造網址；實際打開過的才標 verified；只在搜尋摘要看到的標 likely；查不到標 unverified 並寫搜尋過程。數字抄原文並附一句原文引述；需要換算時同時給原始數字與算式。
輸出：寫成 Markdown 到指定檔案（每條：主題／事實／數字／來源機構／網址／以…為準／信心等級／原文引述／備註），並用 StructuredOutput 回傳同一份清單。你是查證員不是作者。
`

const TASKS = [
  { key: 'lifetable', file: 'supp-taiwan-lifetable-jpm.md', prompt: `
主題：台灣存活機率與摩根退休指南。請：
1. 到內政部統計處下載最新「簡易生命表」（113 年或 112 年）的男女 lx（生存數）或 qx 表，實際計算：65 歲的人活到 75、80、85 歲的機率（男、女各算），並算「夫妻至少一人活到該年齡」（假設獨立：1−(1−p男)(1−p女)）。把算式、資料年度、網址寫清楚，這是本文自算，要能重現。同時抄下 65 歲平均餘命（男、女）。
2. 作者提供多張 J.P. Morgan 圖：(a) 2013 年《The Importance of Being Earnest》的「影響退休的所有面向」（完全掌控：儲蓄 vs 花費、資產配置；部分掌控：退休時機、長壽；無力掌控：市場報酬、稅賦與政策）；(b) Guide to Retirement「Consistent Chloe／Late Lyla／Quitter Quincy／Nervous Noah」每月 $200、5.75%、期末 $368,900／$192,000／$176,900／$121,100；(c)「Range of stock, bond and blended total returns」1、5、10、20 年滾動最高最低（作者版本 1990–2020：股票 1 年 +38%／−37%、20 年 +10%／+6%；債券 20 年 +7／+5；50/50 20 年 +9／+6；現金 20 年 +4／+1）；(d) 台灣版「退休投資指南」裡的提領率圖（4／5／6% 與 40/60、20/80、100% 現金）、人生三階段配置圖、以及「退休後維持現有生活水準所需投資金額」表（假設：每年總投資率 10%、退休前報酬 5%、退休後 4%、通膨 1.3%、65 歲退休、30 年）。請找到這些圖的原始出處（JPM Guide to Retirement 哪一年版、台灣版指南名稱與年份、網址），核對能核對的數字，並用 Python 重算 (b) 的四個期末金額確認一致。
3. 找 JPM 圖 (c) 使用的資料期間與指數定義原句。
輸出檔案：${ROOT}/research/supp-taiwan-lifetable-jpm.md` },
  { key: 'twse', file: 'supp-taiwan-dca-compute.md', prompt: `
主題：用證交所公開資料替台股自算兩件事（本文自算 ○，要可重現）。
1. 先找出證交所可用的日資料 API：加權指數每日（例如 https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST?date=YYYYMMDD&response=json 這類，逐月抓）與「發行量加權股價報酬指數」（含息，2003 年起）的日或月資料。把可用的端點與欄位寫進檔案。抓資料時每次請求間隔至少 3 秒；資料存到 ${ROOT}/research/data/（CSV），腳本存到 ${ROOT}/tools/twse_dca.py。
2. 算式 A「每月定期投入，買在當月最高、收盤均價、最低」：以含息報酬指數（若只拿得到不含息的加權指數就用它並註明）2003-01 到最近完整年度，每月投入 10,000 元，分別用當月最高、當月平均收盤、當月最低價買進，算期末總資產、總報酬率、年化報酬率（IRR）。作者手上有一張沒有出處的表（1995–2020、最終 13,168,571／12,599,871／12,229,453、IRR 9.35／9.10／8.93%），我們要用自己的資料重做，不需要對得上它。
3. 算式 B「年內最大跌幅 vs 全年報酬」：對每個日曆年算年內從高點到低點的最大跌幅，以及全年報酬；統計「平均年內最大跌幅」與「幾年中有幾年全年為正」。
4. 若 API 抓不到或資料不完整，如實回報做到哪裡，不要用非官方來源補。
輸出檔案：${ROOT}/research/supp-taiwan-dca-compute.md（含方法、資料範圍、結果表、腳本路徑）` },
  { key: 'author', file: 'supp-author-sources.md', prompt: `
主題：作者自己的材料與兩個部落格。請：
1. 試著找到並打開 Facebook 粉絲專頁「指數三寶飯」與 podcast「人生不難」（Apple Podcasts／Spotify／Firstory／SoundOn 的節目頁通常有文字簡介與各集標題）。能抓到什麼就抄什麼：粉專簡介、置頂或最近文章的標題與重點、podcast 各集標題與簡介。抓不到（登入牆）就如實記錄嘗試過的網址與結果。
2. 打開 fourpillarfreedom.com「Accumulating $1 Million」那篇（每年投入 $10k、7%、各 $100k 所需年數 7.84／5.1／3.78／3.01／2.5／2.14／1.87／1.66／1.49／1.35 年；每段增量中儲蓄 vs 報酬占比 78/22、51/49、38/62、30/70、25/75、21/79、19/81、17/83、15/85、14/86），抄下它的假設，並用 Python 重算年數與占比確認一致；註明這只能當「有人這樣畫過」的存在性線索，正文要用本文自算版。
3. 打開 IFA.com「Style Drifters: Can You Pick the Next Country Winner?」與資產類別輪動圖（Novel Investor「Asset Class Returns」或 JPM Guide to the Markets）的原始頁面，抄下資料來源說明（用哪些指數、期間），不必逐格抄數字。
4. 找「短期 vs 中期 vs 長期目標」分桶概念的一手出處（例如 Harold Evensky 的 bucket 概念，或 JPM Guide to Retirement 的目標分層頁）。
輸出檔案：${ROOT}/research/supp-author-sources.md` },
]

const FACTS_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' }, summary: { type: 'string' },
    facts: { type: 'array', items: { type: 'object', properties: {
      topic: { type: 'string' }, claim: { type: 'string' }, value: { type: 'string' }, source: { type: 'string' }, url: { type: 'string' }, asOf: { type: 'string' },
      confidence: { type: 'string', enum: ['verified', 'likely', 'unverified'] }, note: { type: 'string' },
    }, required: ['topic', 'claim', 'source', 'confidence'] } },
    blocked: { type: 'array', items: { type: 'string' } },
  },
  required: ['file', 'summary', 'facts'],
}

const CLAIMS = `
作者的主張（原話）：
C1 報酬 vs 時間 vs 風險（三圓交集是詐騙；時間短＋風險低＝低報酬；時間短＋報酬高＝高風險；風險低＋報酬高＝長時間）。
C2 現在每個月存的每一筆，經過 30 年後的複利成為那個月自己可以用的花費（所以不用擔心短期漲跌）。
C3 短期一定會有起伏，長期上漲，不要預期股票一定總是持續漲。
C4 定期定額在每個月的高點低點不重要，長期沒有影響。
C5 每月投入十天、每月三天、每月一天、每季、每年，對長期投資的結果幾乎沒有影響；越頻繁只是越貼近買的標的。
C6 為什麼要買大盤？優點？
C7 為什麼要分散不同國家？優點？缺點？要知道自己這樣做的優缺點並接受。
C8 指數投資除了報酬不輸，同時也帶來情緒價值和時間價值。
C9 甜蜜點、滿足點。
C10 盡可能提高儲蓄率，歐印，把勞力資本轉換為財務資本（但也要掌握人生階段的平衡，該花則花，應該把花費著重在體驗而不是物質）。
C11 早期投資的重要性（四個人的比較圖）。
C12 無法掌握的就不要企圖去掌握（股市漲跌），只掌握自己能做的（儲蓄率）。
C13 為什麼不建議預測高低點（「連上帝也贏不了定期定額」）。
C14 投資行為和心理學很重要。
C15 賣出理由可以有千百種，不管怎樣，Hold 就對了（2009 起的 S&P 500 新聞事件圖）。
C16 道瓊 1900–2004 歷史事件圖（標籤「下跌 8906」「單日暴跌 2206」疑為 89%、22% 的亂碼）。
C17 你以為的複利過程 vs 真實經歷（平滑 vs 鋸齒）。
C18 30 年複利時間軸圖（35→65 是 30 年，但 60→100 是 40 年，圖自相矛盾）。
C19 每月投入 1 萬、7%、累積到 100 萬美元各段所需年數與儲蓄／報酬占比圖。
C20 影響退休的六個面向（完全掌控／部分掌控／無力掌控）。
C21 提領率 4／5／6% 與投資組合對提領年數的影響（摩根台灣版）。
C22 年內最大跌幅 vs 全年報酬（平均 −14.3%，41 年有 31 年為正）。
C23 國家報酬輪動表（無法挑下一個贏家）與資產類別輪動表（分散組合永遠在中間）。
C24 美國 vs 非美每十年輪替（MSCI World ex USA vs S&P 500）。
C25 錯過最好的 10／20／30 天的報酬（JPM）。
C26 持有 1／5／10／20 年的報酬區間收窄（JPM）。
C27 短中長期目標對應現金／債券／股票配置（JPM）。
C28 四個人的比較（Consistent Chloe 等）。
C29 人生三階段配置與各階段風險（摩根台灣版）。
C30 退休後維持生活水準所需投資金額表（摩根台灣版；30 歲／月收 10 萬那格寫「10」疑為漏字；60 歲列 160 萬與 65 歲列 150 萬順序不合理）。
C31 65 歲存活到 75／80／85 歲的機率（美國資料）。
C32 美國 vs 非美循環圖（Hartford 2019 暗示要翻轉）。
`

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    verdicts: { type: 'array', items: { type: 'object', properties: {
      claim: { type: 'string' },
      ruling: { type: 'string', enum: ['use', 'rewrite', 'drop'] },
      why: { type: 'string' },
      rewritten: { type: 'string' },
      evidence: { type: 'array', items: { type: 'string' } },
      chapter: { type: 'string' },
      element: { type: 'string' },
    }, required: ['claim', 'ruling', 'why', 'chapter'] } },
    factErrors: { type: 'array', items: { type: 'string' } },
    unresolved: { type: 'array', items: { type: 'string' } },
    planFile: { type: 'string' },
  },
  required: ['verdicts', 'planFile'],
}

log('三位研究員補完')
const research = (await parallel(TASKS.map(t => () =>
  agent(COMMON + t.prompt, { label: `research:${t.key}`, phase: 'Research', model: 'sonnet', effort: 'high', schema: FACTS_SCHEMA })))).filter(Boolean)
log(`研究完成 ${research.length}/${TASKS.length}`)

phase('Judge')
const judge = await agent(`
你是裁判兼總編輯。作者補充了 24 張圖與一批主張，八位研究員已把原始來源查證寫進 ${ROOT}/research/supp-*.md（全部讀完；另外讀 ${ROOT}/outline.md 的 §1 版面規格、§2 語氣規範、§3 各章 keyPoints、§5 事實衝突，以及 ${ROOT}/components.md）。
${CLAIMS}
任務：對 C1–C32 每一條裁定：
- use：概念與數字都站得住，可以直接進文件（仍要標來源等級）。
- rewrite：概念對但結論太強、語氣違規（例如「Hold 就對了」「不用擔心」「沒有影響」「盡可能提高儲蓄率」「長期上漲」是預測或指令）、或圖本身有錯要重畫。給出 rewritten：一到三句符合語氣規範的替代文字（可用「歷史上多數期間」「影響很小：數字」「這一題沒有標準答案，只有你知道＿＿＿」等句式），並指出要附的反例或反方（日本 1989、台灣 1990、錯過最差日子那一側、金錢與快樂研究的三篇）。
- drop：不能用（無來源、圖有錯且無法重畫、與鐵律衝突）。說明理由。
每條給 evidence（引用 supp 檔案的哪幾條事實，寫成「檔名：主題」）、chapter（落到 01–15 哪一章，可多章）、element（用哪種元件：事實框／算式框／取捨框／誤解框／對照卡／圖／正文一段）。
另外列 factErrors（作者素材裡確定錯的地方，含亂碼標籤、自相矛盾的時間軸、表格漏字、95% 是單一類別等）與 unresolved（研究員查不到、需要作者自己提供的，例如粉專文章原文）。
把整份裁定寫成 Markdown 存到 ${ROOT}/supplement-plan.md（給下一輪增補寫手用，每條要有：裁定、改寫句、來源、落點章節、元件），planFile 填該路徑。用 StructuredOutput 回傳。
`, { label: 'judge:supplement', phase: 'Judge', model: 'fable', effort: 'xhigh', schema: VERDICT_SCHEMA })

return { judge, research: research.map(r => ({ file: r.file, summary: r.summary, blocked: r.blocked, unverified: (r.facts || []).filter(f => f.confidence === 'unverified').map(f => f.topic + '：' + f.claim) })) }
