export const meta = {
  name: 'family-finance-polish',
  description: '收尾：五張 640 寬 SVG 改成手機可讀（02、07、08、09、11）＋ 第 17 章待查清單補四項刪一列',
  phases: [{ title: 'Polish', detail: '六位並行，各只動自己的檔案' }],
}

const ROOT = '/Users/linyenchu/Cladue Code/family-finance'

const FIX_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' }, applied: { type: 'number' },
    skipped: { type: 'array', items: { type: 'object', properties: { issue: { type: 'string' }, reason: { type: 'string' } }, required: ['issue', 'reason'] } },
    checkerErrors: { type: 'number' }, notes: { type: 'string' },
  },
  required: ['file', 'applied', 'skipped', 'checkerErrors'],
}

const SVGS = [
  { id: '02-balance-sheet', line: 42 }, { id: '07-time-inflation-compounding', line: 134 }, { id: '08-risk-diversification-cost', line: 122 },
  { id: '09-rules-card', line: 26 }, { id: '11-tax', line: 24 },
]

const svgJobs = SVGS.map(s => () => agent(`
你是 builder，把 ${ROOT}/chapters/${s.id}.html 裡那張 viewBox 640 寬的 SVG（約第 ${s.line} 行的 <figure class="chart">）改成手機可讀。背景：頁面內文欄在 375px 手機上約 343px 寬，640 寬的 viewBox 會縮成 0.536 倍，字級 12–17 縮到 6–9 px 讀不了。
做法（擇一，以可讀為準）：(a) 把 viewBox 改成 360 寬（高度依比例或重排），所有文字 font-size ≥ 12、線寬 ≥ 1.5，標籤不重疊、不超出邊界；(b) 維持 640 寬但所有文字 font-size ≥ 23、線寬 ≥ 2.5，並重排標籤避免重疊。參考已改好的 ${ROOT}/chapters/13-family.html 那張 360 寬的圖。
規則：座標先用 Python 算過再寫；顏色只用 currentColor 與 var(--ink)／var(--muted)／var(--accent)／var(--teal)／var(--line)／var(--fill)；每個形狀有 fill；保留 <title>、role="img"、aria-labelledby 與 figcaption 的內容（圖說文字不動，除非數字位置變了要對應）；圖的資料與數值不得改變；Y 軸從 0 起。改完可以用 Python 把 SVG 抽出來檢查文字元素的最小 font-size 與是否超出 viewBox。只動這一個檔案、只動這一張圖。
完成後執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/${s.id}.html"，必須 0 錯誤。回傳 StructuredOutput：file、applied、skipped、checkerErrors、notes（新 viewBox、最小字級、做法 a 或 b）。
`, { label: `svg:${s.id}`, phase: 'Polish', model: 'opus', effort: 'high', schema: FIX_SCHEMA }))

const appendixJob = () => agent(`
你是 applier，處理 ${ROOT}/chapters/17-glossary-sources.html 兩件事：
1. 待查清單（三欄表：項目｜目前依據｜要去哪裡查）補四列：(i) Estrada 2008「Black Swans and Market Timing」期刊卷期頁碼（第 9 章來源寫 Vol. 17: 20–34，期號待核）→ Journal of Investing 官網或 DOI；(ii) J.P. Morgan《Guide to Retirement》第三方代管 PDF（第 10 章 src-10-24、第 9 章來源）→ jpmorgan.com 官方頁下載原檔核對；(iii) 台灣加權指數 1990 年高點被超越的確切收盤日（第 7、8、15 章目前寫「2020 年 7 月底、約 30 年」，依維基與媒體轉引）→ 證交所每日收盤行情；(iv) 勞退新制請求權時效條文（第 14 章來源提到 10 年時效，法條項次待核）→ 全國法規資料庫勞工退休金條例。先用 grep 找各章來源條目確認描述與章號正確再寫。
2. 刪掉待查清單裡那一列自我矛盾的「勞退月提繳工資分級表 114-01-01 版…（第 10 章已引 115-01-01 生效版）」（第 10、16、17 章正文已統一為 115-01-01 生效版）。
只動這一個檔案。完成後執行 python3 "${ROOT}/tools/check_fragment.py" "${ROOT}/chapters/17-glossary-sources.html" --loose，必須 0 錯誤。回傳 StructuredOutput：file、applied、skipped、checkerErrors、notes。
`, { label: 'appendix:pending-list', phase: 'Polish', model: 'sonnet', effort: 'medium', schema: FIX_SCHEMA })

const results = (await parallel([...svgJobs, appendixJob])).filter(Boolean)
return results.map(r => ({ file: r.file, applied: r.applied, checkerErrors: r.checkerErrors, skipped: r.skipped, notes: r.notes }))
