# v7.0 預覽：AY——版面收斂第一段（只動 CSS＋純搬動，零改字）

依據：`layout-audit-visual.md`（P0）、`layout-audit-structure.md`（P0）、`layout-decisions-2026-09-23.md` 第一段。**不改任何正文字**（唯一例外：start 五階圖補一句 figcaption，先寫草稿標「待裁判」）。guide 的 `<style>` 是 lite 的來源（build_lite.py:791 抓第一個 `<style>`，不能拆成兩個、不能加屬性），所以 CSS 改完一定跑 build_lite。分兩個 commit：AY-1 CSS＋哨兵、AY-2 搬動。

## AY-1 CSS（guide/index.html 的 <style>）
1. 摺疊標題：對 `details.more>summary`、`details.source-card>summary`、無 class `details>summary` 統一 `list-style:none; display:block; position:relative; padding-left:1.4em` ＋ `::before{content:"▸"}`／`details[open]>summary::before{content:"▾"}`（照 L13–16 toc-part 的現成寫法；`::-webkit-details-marker{display:none}`）。目的：78 處續行左突消失。
2. 標題通則：`h2`（含 `.toc h2`）1.55rem；**新增 `h3{font-size:1.2rem;line-height:1.35;margin:24px 0 8px}`**（節內小標）；`.data-card h3` 暫抬到 1.06rem（不再比正文小）；`h4{font-size:1.05rem;letter-spacing:.02em;margin:20px 0 6px}`；`.data-card h4` 維持既有相對關係但不得小於 .95rem。
3. 間距尺規：`:root{--gap-s:8px;--gap-m:16px;--gap-l:24px;--gap-xl:32px}`；`section.part>p{margin:var(--gap-m) 0}`；卡、摺疊、圖、表、黃框、小卡、本節行動這些區塊的上下外距統一 `var(--gap-l)`；`p.small` 12px；h3 用第 2 點。
4. `.note` 改成全域：`.note{font-size:.84rem;color:var(--muted);line-height:1.6;margin:8px 0 0}`（原 `figure.chart .note` 併入），修 6 處圖外 p.note 誤成正文。
5. `.credit{color:var(--muted)}`。
6. L65 的 `640px` 斷點改 `660px`。
7. `span.later`、`span.tag`：`border-radius:8px;padding:3px 8px;line-height:1.5;display:inline` （可換行不變形）。
8. 表格「← 表格可左右滑動 →」提示：只留 `.table-wrap.is-scrollable::before` 一條，其餘四處 `content:none` 的互消規則刪掉（先確認 JS 會在可捲時加 `is-scrollable`、不可捲時不加）。
9. `details.more>details>figure.chart`（照片那張，歪 44px）補一條負邊距規則使左右對稱（照 L105 既有算式）。
10. **版面哨兵** `tools/v7_layout_check.py`：用 headless Chrome（`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --headless=new --dump-dom` 或 `--remote-debugging`；版式審用了 iframe 375 的做法，見 layout-audit-visual.md「我實際做了什麼查證」）量 375 與 1024：(a) 每張 figure.chart 左右緣與所在容器的關係、(b) 每張表是否橫向溢出、(c) `section.part` 下 `p` 的左緣種類數（目標 ≤8）、(d) summary 有換行的是否續行左突（目標 0）、(e) docOverflow 0。輸出一行 `LAYOUT OK` 或列出違規。無法用 Chrome 就用純 CSS 靜態推算並註明限制。把它加進 handoff 的全套檢查食譜。

## AY-2 純搬動（結構審 P0；零改字）
1. lifecycle：來源卡搬到本節行動之前（其後不得再有正文）。
2. s10：來源卡之後那個 `p` 前移到來源卡之前。
3. s13：`<script>` 移到 `a.back` 之後或 section 外。
4. methods：`span.later` 移到白話版之後。
5. s5：中段（idx 21 附近）那個黃框下放到來源卡之後、與另兩個黃框相鄰。
6. s5：兩處相鄰圖（idx 14/16、18/20）各拆開，中間插入既有段落（idx 17 那段可上移），不新寫字。
7. costs：兩個紅框合併成一個（內容照搬，兩段用 `<p>` 隔開），移到來源卡之前。
8. start：五階圖補 figcaption 草稿（從圖旁既有句子改寫成一句，標註「待裁判」於 changes-for-author）。
每一條先印現場，搬完 `v7_check anchors／budget／planstep／numbers（round35）`、guidetools、test_*、calc_core、build_lite 全綠。

## 交件
兩個 commit 各附產生檔重建；changes-for-author 加「一之五十三、批 AY」；handoff 補「版面收斂第一段」與哨兵用法。回報：每條 CSS 改前改後（選擇器＋宣告）、搬動前後序列、哨兵輸出（375／1024 各項數字）。不發布；主線會截圖。
