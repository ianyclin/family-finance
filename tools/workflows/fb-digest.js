export const meta = {
  name: 'family-finance-fb-digest',
  description: '作者粉專 154 篇：六位讀者分段逐篇整理 → 一位整合成主題地圖 → 裁判對照文件 18 章列出整合清單',
  phases: [
    { title: 'Read', detail: '六段並行，逐篇結構化摘要，重點句逐字引用' },
    { title: 'Themes', detail: '合併成主題地圖，含作者的固定做法與里程碑數字' },
    { title: 'Judge', detail: '對照 chapters/ 現況，裁定每個主題：補／已有／不放，並給落點與寫法' },
  ],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'
const JSON_FILE = `${ROOT}/research/author-fb-posts-all.json`
const N = 154
const CHUNKS = 6
const size = Math.ceil(N / CHUNKS)
const ranges = Array.from({ length: CHUNKS }, (_, i) => [i * size, Math.min(N, (i + 1) * size)])

const DIGEST_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    posts: { type: 'array', items: { type: 'object', properties: {
      idx: { type: 'number' }, date: { type: 'string' },
      kind: { type: 'string', enum: ['月記', '觀念', '工具', '家庭', '稅與回饋', '里程碑', '故事', '分享連結', '無文字', '其他'] },
      gist: { type: 'string' },
      points: { type: 'array', items: { type: 'string' } },
      quotes: { type: 'array', items: { type: 'string' } },
      numbers: { type: 'array', items: { type: 'string' } },
      directives: { type: 'array', items: { type: 'string' } },
    }, required: ['idx', 'date', 'kind', 'gist'] } },
  },
  required: ['file', 'posts'],
}

const THEMES_SCHEMA = {
  type: 'object',
  properties: { file: { type: 'string' }, themes: { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, postCount: { type: 'number' }, summary: { type: 'string' } }, required: ['name', 'summary'] } }, milestones: { type: 'array', items: { type: 'string' } } },
  required: ['file', 'themes'],
}

const PLAN_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    items: { type: 'array', items: { type: 'object', properties: {
      theme: { type: 'string' }, ruling: { type: 'string', enum: ['add', 'covered', 'skip', 'needs-source'] },
      chapter: { type: 'string' }, element: { type: 'string' }, why: { type: 'string' }, wording: { type: 'string' }, sourcePosts: { type: 'array', items: { type: 'string' } },
    }, required: ['theme', 'ruling', 'why'] } },
    conflicts: { type: 'array', items: { type: 'string' } },
  },
  required: ['file', 'items'],
}

phase('Read')
const digests = (await parallel(ranges.map(([a, b], i) => () => agent(`
你是讀者，負責作者粉專貼文第 ${a + 1} 到第 ${b} 篇（依 JSON 陣列順序，索引 ${a} 到 ${b - 1}）。資料：${JSON_FILE}（陣列，每篇有 published_iso 與 text）。用 Python 讀出你負責的那一段，逐篇處理，不要漏。
背景：作者是台灣的三寶爸、醫師，粉專「指數三寶飯·家庭理財陪跑」寫市值加權指數投資為核心的家庭理財月記。這些是作者自己的材料，將整合進一份「家庭理財白話說明文件」（文件不替讀者下結論、不推薦商品；作者的話只能以「作者自己的做法／經驗」出現）。
每篇輸出：idx（陣列索引）、date（published_iso 前 10 碼）、kind、gist（一句話）、points（這篇講的重點，每條 ≤40 字，忠於原文）、quotes（值得原封引用的句子，逐字，每篇最多 3 句，每句 ≤60 字）、numbers（出現的數字與它代表什麼，例如「投資資產佔總資產 68.5%（2025-09）」）、directives（作者對讀者的指令或推薦語，逐字，例如「VALU 我非常推薦給大家」——這些進文件時必須改寫，所以要標出來）。無文字的篇 kind 填「無文字」。
把同一份內容寫成 Markdown 存到 ${ROOT}/research/fb-digest/part-${i + 1}.md（先 mkdir -p），file 填該路徑。不要評論、不要建議怎麼整合。
`, { label: `read:${a + 1}-${b}`, phase: 'Read', model: 'sonnet', effort: 'medium', schema: DIGEST_SCHEMA })))).filter(Boolean)
log(`讀者完成 ${digests.length}/${CHUNKS}`)

phase('Themes')
const themes = await agent(`
你是整理者。讀 ${ROOT}/research/fb-digest/part-1.md 到 part-${CHUNKS}.md（六位讀者對 154 篇粉專貼文的逐篇摘要），必要時回 ${JSON_FILE} 看原文。
輸出 ${ROOT}/research/fb-themes.md：
1. 主題地圖：把 154 篇歸成 10 到 15 個主題（例如：每月投入與再平衡的固定流程；指數投資滿 N 年的回顧與數字；儲蓄險解約實作；壓歲錢與小孩的錢；零用錢與教小孩；報稅、回饋與點數；自製工具（瀑布圖、XIRR、滿足點試算、提領模擬器、槓桿實驗室）；行為與心理（大跌時群組有人賣出、十月的下跌像一場夢、FOMO、無聊）；配置變更史（債券換美國中期公債、固定 9:1、因子）；英股 vs 美股成本、複委託、借券、股票申購；coast FIRE 與滿足點；家庭與生活（旅行、游泳、學才藝）；分享的外部文章與書）。每個主題：涵蓋哪些篇（日期）、作者一貫的說法（用他的話）、演變（早期 vs 現在）、可直接引用的句子（逐字，附日期）。
2. 里程碑數字表：滿三年（2022-09）、滿四年、滿五年、滿六年、七年（2026-09）各篇提到的年化報酬、投資資產占比、儲蓄率等，逐字抄並附日期；這些是作者自己的數字，只能以「作者自己的紀錄」出現。
3. 作者的固定流程（逐步）：發薪日 → 扣除預期支出 → 投入 → 再平衡門檻 → 年終獎金、紅包、普發怎麼處理 → 配息再投入。用他的原句佐證。
4. 作者對讀者說過的指令／推薦語清單（逐字，附日期）——整合時要全部改成「作者自己的做法」句式。
5. 與文件價值觀可能衝突的地方（例如「歐印」、「VALU 我非常推薦」、借貸投入、質押），列出但不裁決。
用 StructuredOutput 回傳 file、themes（name、postCount、summary）、milestones。
`, { label: 'themes:merge', phase: 'Themes', model: 'opus', effort: 'high', schema: THEMES_SCHEMA })

phase('Judge')
const plan = await agent(`
你是裁判兼總編輯。讀 ${ROOT}/research/fb-themes.md（作者粉專 154 篇的主題地圖）、${ROOT}/research/fb-digest/part-*.md（逐篇摘要）、${ROOT}/research/author-principles.md、${ROOT}/research/author-fb-posts.md，然後對照文件現況：${ROOT}/chapters/00-how-to-use.html 到 17-glossary-sources.html（用 grep 找關鍵詞，重點章：01、03、06、07、08、09、10、11、13、16），以及 ${ROOT}/outline.md §2 語氣規範、${ROOT}/components.md §3（作者框只在第 9 章出現一次）。
任務：對主題地圖的每個主題（以及主題內值得單獨處理的子項）裁定：
- add：文件沒有、對零基礎讀者有用、能以「作者自己的做法／經驗／紀錄」身分放進去。給 chapter（00–17）、element（正文一段／details 摺疊／作者框內一條／事實框○條目／對照卡／工作表一列）、wording（可直接貼的白話句子，≤3 句，附「作者 YYYY-MM 的紀錄」字樣，不下指令、不用禁用字眼；作者的指令與推薦語一律改寫成「作者自己……，代價是……」）、sourcePosts（日期）。
- covered：文件已有同樣內容，指出在哪一章。
- skip：不放，說明理由（純個人生活、槓桿與質押與文件範圍衝突、無法改寫成不下結論的形式、可能被讀成推薦）。
- needs-source：概念可放但貼文裡引用的外部數字要先回推原始來源。
另外列 conflicts：作者粉專的說法與文件現有內容互相矛盾的地方（例如再平衡「每年一次」vs「5/25 門檻＋每次投入時檢查」；儲蓄險解約的經驗 vs 第 6 章的中性寫法；作者對 VALU 的推薦 vs 不推薦商品）。
原則：作者的聲音要進來，但只在「作者自己的做法」的框架裡；每個 add 都要附代價或前提；優先挑對新手最有用的十到二十項，不要把 154 篇全塞進去。把整份裁定寫成 Markdown 存到 ${ROOT}/research/fb-integration-plan.md，file 填該路徑。用 StructuredOutput 回傳。
`, { label: 'judge:fb-plan', phase: 'Judge', model: 'fable', effort: 'xhigh', schema: PLAN_SCHEMA })

return { digests: digests.map(d => ({ file: d.file, posts: d.posts.length })), themes: themes && { file: themes.file, themes: themes.themes.map(t => t.name), milestones: themes.milestones }, plan: plan && { file: plan.file, add: plan.items.filter(i => i.ruling === 'add').length, covered: plan.items.filter(i => i.ruling === 'covered').length, skip: plan.items.filter(i => i.ruling === 'skip').length, needsSource: plan.items.filter(i => i.ruling === 'needs-source').length, conflicts: plan.conflicts } }
