export const meta = {
  name: 'family-finance-essay-outline',
  description: '投資專篇（作者第一人稱）：三角度大綱提案 → 裁判整合定案大綱、作者語氣指南、元件契約、書名候選',
  phases: [
    { title: 'Voice', detail: '從 154 篇貼文歸納作者說話的樣子' },
    { title: 'Outline', detail: '三位提案人' },
    { title: 'Judge', detail: '整合定案' },
  ],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'
const POSTS = `${ROOT}/research/author-fb-posts-all.json`

const BRIEF = `
背景：作者（台灣三寶爸、醫師、粉專「指數三寶飯·家庭理財陪跑」）已有一份 18 章的《家庭理財白話手冊》（chapters/00–17.html，中性聲音、每個數字附來源；第 7–9 章是投資的證據、第 9 章有作者規則卡）。作者現在要另一份「投資專篇」：只講投資，以投資心理與行為為主軸，給零基礎的朋友看，文字要比手冊更淺、更像聊天。
主軸（作者 2026-09-08 明確交代）：這篇最重要的是「正確的理財知識」，不是作者做了什麼。所以每一節的骨架是：一個正確的觀念（白話講對、講清楚，附證據與量級）→ 作者自己的一件事當例子（只是例子，不是主角）→ 一句交還。作者第一人稱「我」只是講話的方式：「我」是那個把知識講給朋友聽的人，不是被歌頌的對象。
四條護欄（作者已拍板）：
1. 「我」只講我做了什麼、為什麼、付了什麼代價，不出現「你應該」；每一節結尾固定一句把決定交還讀者（例如「這是我的路，你的數字要自己算」，句式可變化但意思固定）。
2. 不寫作者的報酬率、年化、含息報酬、甜蜜點進度等個人績效百分比；紀律的證據用「幾個月照做」「哪一年下跌照投」呈現。
3. 知識要有來源：每節的觀念都要能指回手冊對應章節（連結到手冊網址＋#ch-NN），量級只引手冊已驗證的數字（例如主動基金 15 年約九成輸給指數、買在月高月低差 0.49 個百分點、投入頻率差不到 0.1 個百分點、四次大跌回本年數、日本 34 年），不新增未驗證數字。
4. 每一句「我做了／我那時候／我發現」都必須能對到某一篇貼文的日期（${POSTS}），不准替作者編造經歷或感受；作者沒寫過的觀點只能以「證據說」出現。
規格：8 到 10 節、全文約一萬字、術語十個以內（第一次出現要白話解釋）；每節固定：一句話重點、觀念段（知識本體，含證據框）、例子段（作者的一件事，附貼文日期）、一句交還。商品名不出現（要提就寫「哪幾檔見手冊第 9 章」）。不用「歐印」「FIRE」「財富自由」「被動收入」「必定」「一定」。
素材：${ROOT}/research/fb-themes.md（15 主題與里程碑）、${ROOT}/research/fb-digest/part-1～6.md（逐篇摘要）、${POSTS}（原文）、${ROOT}/research/fb-integration-plan.md、${ROOT}/chapters/07、08、09（證據與來源；這是知識的底本）、${ROOT}/supplement-plan.md（32 條素材的裁定與改寫句）、${ROOT}/outline.md §2（手冊語氣規範，作為底線）。
`

const VOICE_SCHEMA = { type: 'object', properties: { file: { type: 'string' }, traits: { type: 'array', items: { type: 'string' } }, samples: { type: 'array', items: { type: 'string' } }, avoid: { type: 'array', items: { type: 'string' } } }, required: ['file', 'traits'] }
const OUTLINE_SCHEMA = {
  type: 'object',
  properties: {
    angle: { type: 'string' },
    sections: { type: 'array', items: { type: 'object', properties: {
      title: { type: 'string' }, oneLiner: { type: 'string' }, concept: { type: 'string' }, story: { type: 'string' }, storyDates: { type: 'array', items: { type: 'string' } },
      evidence: { type: 'string' }, handbookChapter: { type: 'string' }, terms: { type: 'array', items: { type: 'string' } }, handback: { type: 'string' },
    }, required: ['title', 'oneLiner', 'concept', 'story', 'storyDates', 'evidence', 'handbookChapter'] } },
    titles: { type: 'array', items: { type: 'string' } },
  },
  required: ['angle', 'sections'],
}
const FINAL_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' }, rationale: { type: 'string' },
    sections: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, title: { type: 'string' }, oneLiner: { type: 'string' }, concept: { type: 'string' }, story: { type: 'string' }, storyDates: { type: 'array', items: { type: 'string' } },
      evidence: { type: 'string' }, handbookChapter: { type: 'string' }, terms: { type: 'array', items: { type: 'string' } }, handback: { type: 'string' }, targetLength: { type: 'string' },
    }, required: ['id', 'title', 'oneLiner', 'concept', 'story', 'storyDates', 'evidence', 'handbookChapter'] } },
    titles: { type: 'array', items: { type: 'string' } },
    contract: { type: 'array', items: { type: 'string' } },
  },
  required: ['file', 'sections', 'titles'],
}

phase('Voice')
const voice = await agent(BRIEF + `
你是語氣分析員。讀 ${POSTS} 全部 154 篇（用 Python 讀），歸納「作者說話的樣子」，寫成 ${ROOT}/research/essay-voice.md：
1. 句法與節奏（句子長度、分段習慣、括號補充、「XD」與表情符號的用法、自嘲、用問句開頭的習慣、結尾怎麼收）。
2. 常用詞與口頭禪（逐字列出，附出現次數與例句日期）。
3. 他怎麼講數字、怎麼講失敗、怎麼講家人與小孩、怎麼對讀者說話（稱呼、距離）。
4. 20 句最像他的句子（逐字、附日期），可當寫手的定音叉。
5. 「他不會這樣講」清單：粉專裡從沒出現的語氣（例如喊口號、恐嚇、炫耀），寫手要避開。
6. 專篇要淺於手冊，所以再列出：他原文裡對零基礎讀者太難的用語（MWRR、XIRR、分層再平衡、因子、CV…）與可替換的白話說法。
回傳 StructuredOutput：file、traits（10 條以內）、samples（20 句）、avoid。
`, { label: 'voice:analyze', phase: 'Voice', model: 'opus', effort: 'high', schema: VOICE_SCHEMA })

phase('Outline')
const ANGLES = [
  { key: 'knowledge', angle: '知識骨架優先：先列出零基礎的人最需要弄對的八到十個投資觀念（報酬從哪裡來、費用、分散、擇時、定期定額、波動與回本、行為落差、規則），每節一個觀念，再從月記裡挑一件事當例子' },
  { key: 'questions', angle: '新手最常問的問題倒推：現在進場會不會太晚、跌了要不要賣、要不要等低點、為什麼不買會漲的、我朋友賺比較多、無聊怎麼辦——每節回答一題，答案是正確知識加證據，作者經歷只當例子' },
  { key: 'behavior', angle: '心理陷阱到護欄：先講人在什麼時候會動搖（貪、怕、比較、無聊、控制幻覺）與研究怎麼說（行為落差、損失趨避），再講每個陷阱對應的事前規則（自動化、規則卡、只在三種情況賣、新的資訊還是新的價格）；作者經歷只當例子' },
]
const outlines = (await parallel(ANGLES.map(a => () => agent(BRIEF + `
你是大綱提案人，角度：${a.angle}
先讀 ${ROOT}/research/essay-voice.md（作者語氣指南）與 fb-themes.md，再翻 fb-digest 找故事。
擬 8 到 10 節：每節 title、oneLiner（一句話重點 ≤25 字）、concept（這節要講對的觀念，兩到三句白話；這是主體）、story（作者自己的哪一件事當例子，一句話描述）、storyDates（貼文日期，必須真的存在於 ${POSTS}，用 Python 確認）、evidence（證據框要指回手冊哪一段、引哪一個量級）、handbookChapter（07／08／09／其他）、terms（這節會用到的術語）、handback（交還句）。另給 3 個書名候選（短、像書名、不像口號）。
用 StructuredOutput 回傳。
`, { label: `outline:${a.key}`, phase: 'Outline', model: 'opus', effort: 'high', schema: OUTLINE_SCHEMA })))).filter(Boolean)

phase('Judge')
const final = await agent(BRIEF + `
你是裁判兼總編輯。三份大綱提案如下（JSON），語氣指南在 ${ROOT}/research/essay-voice.md。
${JSON.stringify(outlines, null, 1)}
任務：
1. 整合成定案大綱（8 到 10 節，各取最好的部分，不是投票）：每節 id（兩位數-slug）、title、oneLiner、concept（要講對的觀念，主體）、story（哪一件事當例子）、storyDates（逐一用 Python 在 ${POSTS} 確認存在且內容相符）、evidence（指回手冊哪一章哪一段、引哪一個量級；用 grep 確認手冊那段存在）、handbookChapter、terms（全書合計 ≤10 個）、handback、targetLength（字數）。順序要讓零基礎的人讀得下去：每節先講對一個觀念（知識與證據），再用作者的一件事當例子，最後交還；全篇從「報酬從哪裡來」到「怎麼寫規則」。作者的故事總篇幅不超過三成。
2. 給 3 個書名候選並說明取捨。
3. 寫專篇的元件契約 contract（給寫手與外殼 builder）：單一 HTML、單欄長文、每節 <section class="part">；固定元件：一句話重點 <p class="lede">、觀念段 <div class="concept">（知識本體）、例子段 <div class="story">（開頭標日期，例如「2024 年 8 月，群組裡……」）、證據框 <aside class="box evidence">（一句量級＋<a href="手冊網址#ch-NN">手冊第 N 章</a>）、交還句 <p class="handback">；術語首次出現 <dfn>；不用表格與圖（最多一張）；不用驚嘆號；每段 ≤3 句、每句 ≤30 字。
4. 把定案寫成 Markdown 存到 ${ROOT}/essay/outline.md（先 mkdir -p essay），file 填該路徑。用 StructuredOutput 回傳。
`, { label: 'judge:essay-outline', phase: 'Judge', model: 'fable', effort: 'xhigh', schema: FINAL_SCHEMA })

return { voice: voice && { file: voice.file, traits: voice.traits }, angles: outlines.map(o => ({ angle: o.angle.slice(0, 30), sections: o.sections.map(s => s.title), titles: o.titles })), final: final && { file: final.file, titles: final.titles, sections: final.sections.map(s => `${s.id} ${s.title}（${(s.storyDates || []).join('、')}）`), contract: final.contract, rationale: final.rationale } }
