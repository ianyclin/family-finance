# 章節 HTML 片段契約（寫手、裁判、修稿者必讀）

每章一個檔：`chapters/NN-slug.html`。檔案內容只有**一個** `<section>`，不含 `<html>` `<head>` `<body>` `<style>` `<script>`。所有樣式由外殼提供；寫手只能用本檔列出的元素與 class，**不得自創 class、不得寫 style 屬性**。交件前必須跑 `python3 tools/check_fragment.py chapters/NN-slug.html`，exit 0 才算交件。

## 0. 根元素

```html
<section class="chapter" id="ch-04" data-num="4" data-stage="2">
```

`data-stage`：0 導讀｜1 看清楚（01–03）｜2 止血與撐住（04–06）｜3 長大（07–09）｜4 制度（10–12）｜5 家庭與交棒（13–14）｜6 守住（15）｜7 例行化（16）｜8 附錄（17）。

## 1. 章首（順序固定，五件都要有）

```html
<header class="ch-head">
  <p class="eyebrow">第 4 章 · 第二區 止血與撐住</p>
  <h2>緊急預備金：家裡的滅火器</h2>
  <p class="lede">一句話，30 字以內，這章最重要的一句。</p>
  <div class="ch-meta">
    <div class="meta-block"><h3>這章回答你的三個問題</h3>
      <ul><li>「我要存多少才夠？」</li><li>「放哪裡？」</li><li>「什麼情況可以動用？」</li></ul></div>
    <div class="meta-block"><h3>讀完你做得到</h3>
      <ul class="checks"><li>算出自己家的必要月支出</li><li>決定緊急金目標與放的地方</li></ul></div>
    <div class="meta-block"><h3>這章會用到前面的</h3>
      <p>第 2 章的可動現金、第 3 章的必要月支出。</p></div>
    <p class="time"><span>🕐 約 15 分鐘</span><span>✍️ 需要：第 3 章的現金流表</span></p>
  </div>
</header>
```

「這章會用到前面的」沒有就寫「不需要前面章節。」

## 2. 正文允許的元素

- `<h3>` 小節標題（每章 3–7 個）。`<h4>` 只能出現在框與對照卡裡。
- `<p>` `<ul>` `<ol>` `<li>` `<strong>`（一段最多一處）。不用 `<em>` `<b>` `<i>` `<br>` `<hr>`。
- 重要數字：`<span class="num">45,800</span> 元`（等寬字；一段最多三處）。
- 年度徽章：`<span class="badge">2026 年度</span>` 或 `<span class="badge">2026-09 查</span>`，放在會過期的數字旁。
- 術語首次出現：`<dfn id="def-通膨" data-term="通膨">通膨</dfn>`，同一句照規格寫「白話說法（術語）：一句定義。就像……。這個比喻在……不成立。」同章之後直接寫術語。`id` 一律 `def-` 加術語本身；同一術語全書只有一個 `dfn`（各章寫手先看 outline.md 該章 keyPoints 決定自己負責哪幾個，其他章用到就不再包 dfn）。
- 引用上標：`<sup class="cite"><a href="#src-04-3">3</a></sup>`，放在句號前。同一來源可重複引用同一號。
- 摺疊細節：`<details><summary>想看細節再打開：勞退條例第 14 條原文</summary><p>…</p></details>`
- 表格（最多 3 欄）：`<div class="table-wrap"><table><thead><tr><th>…</th></tr></thead><tbody><tr><td>…</td></tr></tbody></table></div>`
- 對照卡（比較 2–4 種做法時用，六欄固定）：

```html
<div class="cards">
  <article class="card">
    <h4>做法 A：把緊急金放活存</h4>
    <dl>
      <dt>怎麼運作</dt><dd>…</dd>
      <dt>最好的情況</dt><dd>…</dd>
      <dt>最差的情況</dt><dd>…</dd>
      <dt>成本</dt><dd>…</dd>
      <dt>適合誰</dt><dd>…</dd>
      <dt>不適合誰</dt><dd>…</dd>
    </dl>
  </article>
</div>
```

- 步驟卡（取代流程圖）：`<ol class="steps"><li><strong>打開勞保局 App</strong> 用健保卡或自然人憑證登入。</li></ol>`
- 圖（只在能取代文字時用）：

```html
<figure class="chart">
  <svg viewBox="0 0 640 360" role="img" aria-labelledby="fig-07-1-title">
    <title id="fig-07-1-title">示意・非承諾：每月固定投入 30 年，平滑線與鋸齒線</title>
    …
  </svg>
  <figcaption>這張圖在說什麼：…（給看不到圖的人，一句話講清楚）</figcaption>
</figure>
```

SVG 內顏色只能用 `currentColor`、`var(--ink)`、`var(--muted)`、`var(--accent)`、`var(--teal)`、`var(--line)`、`var(--fill)`；文字 `font-size` ≥ 12；每個形狀都要有 `fill`（不填色就寫 `fill="none"`）；標題含「示意・非承諾」；Y 軸從 0 起、不截斷；座標請先用 Python 算好再寫進去。

## 3. 六種框（每章合計 ≤7 個，其中動手框 ≤2 張；不得新增第七種）

**事實框**

```html
<aside class="box fact"><p class="box-label">📌 事實</p>
  <ul>
    <li>勞保月投保薪資最高一級 <span class="num">45,800</span> 元 <span class="badge">2026 年度</span><sup class="cite"><a href="#src-06-2">2</a></sup></li>
  </ul>
</aside>
```

**算式框**

```html
<aside class="box formula"><p class="box-label">🧮 算給你看</p>
  <pre>每月 5,000 × 12 × 30 年 = 180 萬（只算本金）
年化 6% 複利：約 502 萬</pre>
  <p class="how">代入示範：把 5,000 換成你每月能放的數字。</p>
  <p class="caveat">這只是算術，不是預測。限制：6% 是假設，實際可能更好也可能虧損。</p>
</aside>
```

**取捨框**（全書承載價值觀的主力元件；底句固定）

```html
<aside class="box tradeoff"><p class="box-label">⚖️ 取捨</p>
  <div class="cols">
    <div class="col"><h4>做法 A：先把房貸還掉</h4>
      <dl><dt>好處</dt><dd>…</dd><dt>代價</dt><dd>…</dd><dt>適合誰</dt><dd>…</dd><dt>不適合誰</dt><dd>…</dd></dl></div>
    <div class="col"><h4>做法 B：照原本進度還，多的錢拿去投資</h4>
      <dl><dt>好處</dt><dd>…</dd><dt>代價</dt><dd>…</dd><dt>適合誰</dt><dd>…</dd><dt>不適合誰</dt><dd>…</dd></dl></div>
  </div>
  <p class="bottom">這一題沒有標準答案，只有你知道＿＿＿。</p>
</aside>
```

「＿＿＿」要填成具體的東西，例如「只有你知道自己看到帳戶跌兩成會不會睡不著」。

**警語框**（只放會真的虧錢、違法、來不及反悔的事）

```html
<aside class="box warning"><p class="box-label">⚠️ 注意</p><p>…</p></aside>
```

**誤解框**

```html
<aside class="box myth"><p class="box-label">🔄 誤解</p>
  <dl><dt>很多人以為</dt><dd>…</dd><dt>實際上</dt><dd>…</dd><dt>為什麼會這樣誤會</dt><dd>…</dd></dl>
</aside>
```

**動手框**（含工作表）

```html
<aside class="box action" id="ws-4"><p class="box-label">✍️ 工作表④ 緊急金試算</p>
  <p class="ws-date">填寫日期：＿＿＿＿＿＿</p>
  <table class="worksheet"><tbody>
    <tr><th>必要月支出</th><td class="blank"></td></tr>
    <tr><th>× 幾個月</th><td class="blank"></td></tr>
    <tr><th>＝ 目標金額</th><td class="blank"></td></tr>
  </tbody></table>
</aside>
```

不是工作表的動手框不加 `id`，標籤寫「✍️ 動手」，內容用 `<ul class="checks">`。工作表編號固定：①第 1 章 ②第 2 章 ③第 3 章 ④第 4 章 ⑤第 5 章 ⑥第 6 章 ⑦第 8 章 ⑧第 9 章 ⑨第 10 章 ⑩第 12 章 ⑪第 13 章 ⑫第 16 章；`id` 用 `ws-1` … `ws-12`。

**作者自己的做法框**（全書只在第 9 章出現一次，是事實框加 `author` 修飾；唯一允許出現商品名稱的地方）

```html
<aside class="box fact author"><p class="box-label">📌 作者自己的做法（不是要你照做）</p>
  <p>…每一條後面寫代價；商品名只在這裡，並註明「同類商品很多檔，列名不是要你跟著買」。</p>
</aside>
```

## 4. 章尾（順序固定，五件都要有）

```html
<footer class="ch-foot">
  <div class="gain"><h3>你手上多了什麼</h3><ul><li>緊急金試算表（工作表④）</li></ul></div>
  <div class="today"><h3>今天的一件事</h3>
    <p class="do">打開網銀，開一個獨立的活存子帳戶，命名「緊急金」。</p>
    <p class="crit">完成判準：帳戶存在、名稱改好、沒有綁任何自動扣款。</p>
    <p class="est">🕐 約 10 分鐘 · 手機可完成</p></div>
  <div class="later"><h3>還沒解決、後面會處理</h3><ul><li>緊急金存夠之後多的錢往哪放 → 第 9 章</li></ul></div>
  <div class="sources-wrap"><h3>本章來源</h3>
    <ol class="sources">
      <li id="src-04-1"><span class="lvl official" aria-label="官方">●</span> 中央銀行 · 五大銀行平均存款利率 · 一年期定存平均 1.72% · 資料月份 2026-07 · <a href="https://…" rel="noopener">網址</a> · 查證 2026-09-07</li>
      <li id="src-04-2"><span class="lvl inference" aria-label="本文推論">○</span> 本文自算 · 必要月支出 × 6 · 算式見算式框 · 不是官方說法</li>
    </ol>
  </div>
  <p class="foot-note">這一章是一般說明，不是投資、稅務或法律建議；數字有查證日期，會過期。</p>
</footer>
```

來源等級 class 與符號：`official` ●｜`academic` ◐｜`industry` ◑｜`inference` ○。每條六段：機構或作者 · 文件或頁面名稱 · 關鍵內容一句話 · 資料年度或版本 · 網址 · 查證日期。`inference` 不放網址，寫算式。來源編號 `src-章號兩位-序號`；**每條來源都要被正文引用至少一次，正文每個 cite 都要有對應的 li**。只列研究檔裡 verified 或 likely 的來源；likely 要在條目末尾加「（轉引，待官方原檔核對）」。

## 5. 禁止

- 商品名、代號、平台名、App 名一律不出現（政府 App 例外：勞保局行動服務、健保快易通、財政部電子申報）。談某類工具用類別描述：「一檔追蹤大盤的指數型工具」。研究或統計的發表機構（例如 S&P、Morningstar、Vanguard、Schwab、摩根資產管理）可以在正文作為「出處」出現，但只能說它發表了什麼研究，不得連到它的任何商品或帳戶。
- 禁用字眼見 outline.md §2 第 11 條。
- 不用 style 屬性、不自創 class、不放 script。
- 正文不用驚嘆號與表情符號（框標籤、時間列固定圖示除外）。
- 表格不超過 3 欄；一段 ≤4 句；一句 ≤40 字（工具會警告）。
- 出現報酬率、成長率、未來金額的同一個框或同一小節，一定要有「這是假設，不是承諾」的句子。

## 6. 交件前自檢

```bash
python3 tools/check_fragment.py chapters/NN-slug.html
```

錯誤（exit 1）必須修到零；警告逐條處理，處理不了的在回報裡說明理由。
