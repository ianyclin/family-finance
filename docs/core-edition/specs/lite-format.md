# 新手實作版格式規格（lite-format v1）

給寫 `lite/manifest.json`、`lite/alt/*.html`、`lite/facts.txt`、`lite/case-checks.json`，以及在完整版候選上加 `data-lite` 標記的人。照這份寫就能跑，不必看程式。
程式：`tools/build_lite.py`（產生）、`tools/lite_sentinels.py`（哨兵）。依據：`spec-v60-stage2.md` 第 1–5 點、提案第 8-3、8-4 節。

---

## 0. 檔案地圖與流程

| 檔案 | 誰寫 | 用途 |
|---|---|---|
| `guide/index.html` | 內容建造者（改內容；`data-lite*` 屬性也加在這裡） | 唯一來源（v6.0 定稿後改指正式檔；舊的 `lite/work/full-v60-candidate.html` 只留作定稿當時的存檔，build 不再讀） |
| `lite/manifest.json` | 內容建造者 | 章、區塊順序、接合文字、想查證、網址 |
| `lite/alt/<id>.html` | 內容建造者 | 短稿（改寫過的原文區塊） |
| `lite/facts.txt` | 內容建造者 | 兩份都必須出現的共同事實 |
| `lite/case-checks.json` | 內容建造者 | 實作版四個人的數字 ↔ `lite/calc-results.json` |
| `lite/tickers.json` | 主線核可（已放初版） | 代號清單與允許出現的位置 |
| `lite/labels.json` | 主線核可（已放初版） | 「本指南的做法」七件事的關鍵詞 |
| `lite/index.html` | **程式產生，不要手改** | 實作版網頁 |
| `output/full-v60-out.html` | **程式產生，不要手改** | 完整版發布版（多了 lede 下那一行） |
| `export/隔離人性-新手實作版-v6.0.pdf/.html`、`export/隔離人性-理財新手完整指南-v6.0.pdf/.html` | **程式產生** | 匯出 |
| `lite/work/print/print-lite.html`、`print-full.html` | 程式產生 | 列印用暫存（details 全開、目錄已填頁碼），除錯用 |
| `lite/work/lite-v60.txt`、`lite/work/full-v60.txt` | **程式產生** | 審查用純文字：每次 `build_lite.py` 成功後自動重產（實作版逐頁抽自剛印好的 PDF，完整版用 `guidetools.to_text` 抽自 `output/full-v60-out.html`），檔頭記抽取時間與來源；`--no-pdf` 時實作版那一份不重產，會印警告 |

```bash
cd "/Users/linyenchu/Cladue Code/family-finance"
python3 tools/build_lite.py                     # 產生兩份 HTML → 兩份 PDF → 哨兵；全部過 exit 0，否則 exit 1
python3 tools/lite_sentinels.py                 # 只跑哨兵（讀已經產生的 HTML 和 export 裡的 PDF）
python3 tools/build_lite.py --fingerprint "#s11 div.data-card:nth(3)"   # 看選擇器對到哪個區塊、指紋多少
python3 tools/build_lite.py --stamp ch4-stress  # 重看過短稿以後，把檔頭指紋更新成現在的原文
python3 tools/build_lite.py --manifest lite/manifest.sample.json        # 示範（輸出在 lite/work/sample/）
```

---

## 1. `data-lite` 屬性（加在完整版候選上）

只加屬性，不加 class，不改任何文字。屬性值用半形雙引號。

| 寫法 | 意思 |
|---|---|
| `data-lite="ch4"` | 這個元素（連同裡面全部）會被 manifest 裡 `{"src": "ch4"}` 抽出來 |
| `data-lite="ch4 ch8"` | 同一個區塊給兩章用（空白分隔；兩章的 manifest 都要寫 `{"src": "ch4"}`、`{"src": "ch8"}`） |
| `data-lite-alt="ch4-stress"` | 這個區塊在實作版改用短稿 `lite/alt/ch4-stress.html`。可以和 `data-lite="ch4"` 並用，也可以單獨用 |
| `data-lite-alt="a b"` | 同一個區塊是兩份短稿的來源 |
| `data-lite="skip"` | 放在「被抽出來的區塊裡面」的小段落上：這一段不搬 |

規則：
- 值只能用英數、`-`、`_`。章的值建議 `front-plan`、`ch1`…`ch12`、`app-a`、`app-b`。
- `data-lite="chN"` 的值**一定要**被 manifest 用 `{"src": "chN"}` 抽到，否則哨兵 `unused_marks` 失敗。
- 同一個值標在很多元素上時，`{"src": "chN"}` 依文件順序全部抽出；元素互相包含時只取最外層。要控制順序就用不同的值（例如 `ch6a`、`ch6b`）或改用選擇器。
- 標了 `data-lite-alt` 的元素被抽到時，整個元素換成短稿（同一份短稿在同一章只放一次，放在第一個來源的位置）。被抽出的大區塊**裡面**有標 `data-lite-alt` 的子元素時，只有那個子元素換成短稿，其他照搬。
- 同一份短稿在整本實作版只能出現一次（哨兵）。
- 加 `data-lite` 和 `data-lite-alt` 屬性**不會**讓短稿指紋失效（正規化時會拿掉這兩個屬性）；其他任何改動都會。

---

## 2. 選擇器語法（manifest 的 `src`、短稿檔頭的 `src`、`tickers.json`、`labels.json`）

`src` 的值分兩種：
1. **只有英數、`-`、`_`**（例如 `ch4`）：當作 data-lite 值（第 1 節）。
2. **其他**：CSS 子集選擇器。

選擇器子集：
- 以空白分隔的「後代」鏈：`#s11 div.data-card h3`。不支援 `>`、`+`、`~`、逗號。
- 每一節可組合：標籤名 `div`、`*`；`#id`；`.class`（可多個，class 是其中一個詞就算）；`[attr]`、`[attr="v"]`（整值相等）、`[attr~="v"]`（空白分隔的其中一個詞）；`:contains(文字)`（元素純文字去掉空白後含有這段文字；文字不用引號、不能含右括號）。
- `:nth(k)` **只能放在整個選擇器最後**，意思是「整個選擇器對到的結果（文件順序、只取最外層）裡的第 k 個」，從 1 起算。
- 對到的元素互相包含時只取最外層。
- 在 manifest 裡，`src` 對不到任何元素 → 建置失敗；在短稿檔頭，`src` 必須剛好對到 1 個。

例：`#ten div.warning`、`#ten ol.checklist:nth(1)`、`#s11 details:contains(一頁空白版)`、`#toolbox li:contains(《)`、`[data-lite-alt~="ch4-stress"]:nth(2)`。

先用 `python3 tools/build_lite.py --fingerprint "選擇器"` 確認對到的區塊（會印 sha256、標籤、所在節、前 40 字）。

---

## 3. `lite/manifest.json`

JSON（UTF-8，不能有註解）。頂層：

| 欄位 | 必填 | 型別 | 說明 |
|---|---|---|---|
| `format` | 是 | 字串 | 固定 `"lite-manifest/1"` |
| `version` | 是 | 字串 | `"v6.0"`。實作版封面自動印「version／date」；完整版封面（`header.cover`）文字裡必須有同一串，否則哨兵 `version` 失敗 |
| `date` | 是 | 字串 | `"2026-09-15"` |
| `book_title` | 是 | 字串 | `"隔離人性"`（PDF title 用） |
| `edition` | 是 | 字串 | `"新手實作版"` |
| `eyebrow` | 否 | 字串 | 封面最上面那行小字 |
| `author` | 是 | 字串 | `"指數三寶飯・家庭理財陪跑"`（兩份 PDF 的 author） |
| `page_limit` | 是 | 整數 | `25`；實作版 PDF 超過就失敗 |
| `paths` | 否 | 物件 | 覆寫預設路徑（第 3-3 節）。正式 manifest 通常不寫 |
| `sentinel_skip` | 否 | 字串陣列 | **只准出現在示範或實驗用 manifest**；檔名是 `manifest.json` 時有這欄就失敗。可跳過：`version`、`cases`、`facts`、`pages`、`unused_marks` |
| `chapters` | 是 | 陣列 | 依印出順序排的章（第 3-1 節） |

### 3-1 章

| 欄位 | 必填 | 型別 | 說明 |
|---|---|---|---|
| `id` | 是 | 字串 | 實作版裡的錨點，全書唯一，英數與 `-`（例 `cover`、`plan`、`lookup`、`ch1`、`app-a`） |
| `kind` | 否 | `"cover"` | 封面：印成 `<header class="lite-cover">`，標題用 h1、自動印版本號，不進目錄。整本只能一個，放第一個 |
| `label` | 否 | 字串 | `"第 4 章"`、`"附 A"`。有 label 的章才會在完整版產生「新手實作版第 N 章是這一節的做法版」；前三頁不要寫 label |
| `title` | 是 | 字串 | 章名。**不得有阿拉伯數字** |
| `gain` | 否 | 字串 | 「這章做完你會有什麼」一句，印在章名下。**不得有阿拉伯數字** |
| `pages_target` | 否 | 數字 | 頁數目標，只印在報表上 |
| `char_limit` | 否 | 整數 | 字數上限（非空白字元，不含想查證框）。超過只 WARN |
| `page_break` | 否 | 布林 | 這章從新的一頁開始（第 9 章用） |
| `one_page` | 否 | 布林 | 從新的一頁開始、後面也換頁，而且哨兵要求**剛好一頁**（計畫表、查表頁、附 A 用） |
| `blocks` | 是 | 陣列 | 見 3-2 |

目錄、章名、書籤裡的章名一律是「label＋空格＋title」。

### 3-2 blocks 的每種項目（每個項目是只有一個主鍵的物件）

**依位置排版的：**

| 項目 | 例 | 說明 |
|---|---|---|
| 原文區塊 | `{"src": "ch4"}`、`{"src": "#s5 div.data-card:nth(2)"}` | 第 1、2 節；抽出後照第 4 節轉換 |
| 短稿 | `{"alt": "ch4-stress"}` | 放 `lite/alt/ch4-stress.html`。原文已標 `data-lite-alt` 且被 `src` 抽到時會自動放，**不要再寫一次** |
| 接合文字 | `{"glue": "<p>…</p>"}` | 只屬實作版的 HTML。**純文字不得有阿拉伯數字**（全形數字也算）。可以用現有 class（`p.small`、`div.warning`、`span.label-practice` 等），不要加新 class；裡面的連結會照第 4 節轉換 |
| 強制換頁 | `{"page_break": true}` | 在這裡換頁（第 9 章每位人物前） |
| 刻意留白頁 | `{"blank_page": true}` | 列印時自成一頁、只印「本頁刻意留白」，網頁上不顯示（封面後面用，讓計畫表落在奇數頁、查表頁在它背面；fix-r2b） |
| 目錄 | `{"toc": true}` | 自動列出除封面外所有章：「label title ……頁碼」。頁碼只出現在 PDF，網頁上隱藏 |
| 虛構聲明 | `{"notice": "fiction"}` | 印「虛構人物，示範怎麼填，不是建議。不要抄比例，抄推理步驟。」（膠囊框樣式）。每位人物頁首放一個 |

**不管寫在哪裡，都集中印在章末的：**

| 項目 | 例 | 說明 |
|---|---|---|
| 動作框 | `{"action": "填計畫表 B 區：…"}` | 純文字，**不得有阿拉伯數字**；印成綠框「動作」，在內容之後、想查證之前。可多個 |
| 想查證 | `{"verify": ["s5", "s11"]}` | 完整版節 id（`section.part` 的 id）。印「想查證　完整版〈節名〉、〈節名〉」，節名自動取完整版 h2（去掉節號）。id 不存在就失敗 |
| 章末網址 | `{"urls": [{"label": "165 全民防騙網", "href": "https://165.npa.gov.tw/"}]}` | 額外列在章末的網址（label 可有數字，但只放機構或頁面名稱）。正文已經有同一網址的 [n] 時，編號不變、章末改用這裡的 label；正文沒引用的，章末用「・」列出、不編號（fix-r1） |
| 只進附 B 的想查證 | `{"verify_index": ["s11", "s2"]}` | 節 id 只進附 B 想查證總表，不在本章印想查證框（計畫表、查表頁這種剛好一頁的頁面用） |
| 想查證總表 | `{"verify_table": true}` | 依位置排版：由各章 `verify`＋`verify_index` 產生附 B 表格（左欄 label，沒有 label 用 title）。不准在接合文字手寫節名（哨兵 `appendix_b`） |

章的固定順序：章名 → gain → 依位置的 blocks → 動作框 → 想查證框（含 [n] 網址清單）。

### 3-3 `paths`（全部可省略，預設如下；相對路徑以 `family-finance/` 為根）

```json
{
  "source": "guide/index.html",
  "alt_dir": "lite/alt",
  "facts": "lite/facts.txt",
  "case_checks": "lite/case-checks.json",
  "tickers": "lite/tickers.json",
  "labels": "lite/labels.json",
  "calc_results": "lite/calc-results.json",
  "lite_html": "lite/index.html",
  "full_html": "output/full-v60-out.html",
  "print_dir": "lite/work/print",
  "export_dir": "export",
  "lite_export_name": "隔離人性-新手實作版-{version}",
  "full_export_name": "隔離人性-理財新手完整指南-{version}"
}
```

### 3-4 最小例子（等於 `lite/manifest.sample.json` 的正式路徑版）

```json
{
  "format": "lite-manifest/1", "version": "v6.0", "date": "2026-09-15",
  "book_title": "隔離人性", "edition": "新手實作版", "author": "指數三寶飯・家庭理財陪跑", "page_limit": 25,
  "chapters": [
    {"id": "cover", "kind": "cover", "title": "隔離人性：新手實作版",
     "blocks": [{"glue": "<p>這一本只寫怎麼做…</p>"}, {"toc": true}]},
    {"id": "ch1", "label": "第 1 章", "title": "十分鐘版：先記住四個立即停止", "gain": "讀完你會知道…",
     "pages_target": 1, "char_limit": 450,
     "blocks": [
       {"glue": "<p>下面四種情況，不管對方說得多好聽，都先停下來。</p>"},
       {"src": "#ten div.warning"},
       {"alt": "ch1-seven"},
       {"action": "把四個立即停止拍照，存在手機裡。"},
       {"verify": ["ten", "costs"]}
     ]}
  ]
}
```

---

## 4. 產生時會對抽出的區塊做什麼（寫短稿和挑區塊前要知道）

依序：
1. **整個拿掉**：`p.explain`（白話版）、`div.source-card`、`div.sources-grid`、所有 `figure`（圖表與照片）、`svg`、`img`、`details.orig`（看官方原圖）、`script`、`style`、`a.back`（回目錄）、任何帶 `data-lite="skip"` 的元素。
   **保留**：`p.small`／`span.small` 淡色小字、`div.story` 黃框、`div.warning`、`p.decision`（完整版的「本節行動」也會照搬；不要就用 skip 或改挑子區塊）、`details`（網頁收合，PDF 全展開）、`span.later`、`mark.key`、標籤膠囊、表格。
2. **節號連結**（`a.xref`）改純文字：
   - `第 <a xref>4</a> 節` → `完整版〈為什麼不只買最會漲的？〉`
   - `第 <a>1</a>、<a>3</a> 節` → `完整版〈…〉、〈…〉`
   - `「<a xref>投資前的安全順序</a>」` → `完整版〈投資前的安全順序〉`（用連結文字）
   - 其他位置的 xref：連結文字是數字 → `完整版〈該節 h2〉`；不是數字 → `完整版〈連結文字〉`
   - 指到節裡面的錨點時，用它所在的節名。
3. **名詞連結**（`a.term`）與其他站內連結（`href="#…"`）→ 只留文字，`title` 不保留。
4. **外部網址**（`href` 不是 `#` 開頭）→ 連結文字後面加上標 `[n]`，網址集中到章末想查證框，依出現順序每章從 1 編號；連結文字本身就是網址時只留 `[n]`。
5. 抽出來的 HTML 裡所有 `id` 屬性拿掉（避免和實作版錨點撞名）。

短稿和接合文字也會經過 2–5。

完整版發布版（`output/full-v60-out.html`）＝原文正式檔，只在「被有 label 的章抽用過的節」（`src` 對到的元素、短稿檔頭 `src` 對到的元素所在的 `section.part`）的 `p.lede` 後面插入
`<p class="small" data-lite-link="1">新手實作版第 4 章、第 8 章是這一節的做法版。</p>`；節沒有 lede 就插在 h2 後面。`<script>`、`data-lite*` 屬性原樣保留。

---

## 5. 短稿 `lite/alt/<id>.html`

檔名＝短稿 id（英數與 `-`、`_`）。檔案＝檔頭註解＋短稿 HTML。

```html
<!-- lite-alt
id: ch4-stress
norm: v1
src: #s11 div.data-card:contains(壓力測試):nth(1) sha256=3f5c…（64 個小寫十六進位）
src: [data-lite-alt~="ch4-stress"]:nth(2) sha256=9ab0…
note: 壓力測試表壓成兩列；三問表照抄第 3 題用語
-->
<div class="data-card"><h3>…</h3>…</div>
```

- 第一行必須是 `<!-- lite-alt`，結尾 `-->`；中間每行 `鍵: 值`。
- `id`：和檔名一致。`norm`：固定 `v1`。
- `src`：每行一個原文區塊，`選擇器 sha256=指紋`，**必須剛好對到 1 個元素**。可以寫多行（一份短稿摘自好幾節）。順序不影響檢查。
- `note`：隨意備註，可多行（每行都要以 `note:` 開頭）。
- 原文裡每一個標了 `data-lite-alt="<id>"` 的元素，都必須等於或被包含在某一行 `src` 對到的元素裡，否則失敗。
- **指紋正規化 v1**：取該元素的完整原文 HTML（從開始標籤到結束標籤，含 base64 等一切）→ 刪掉 `data-lite="…"`、`data-lite-alt="…"` 屬性 → Unicode NFC → 連續空白（含換行）變一個半形空格 → 去頭尾空白 → UTF-8 → sha256。
- **數字規則**：短稿純文字（去標籤、解 HTML 實體、NFKC）裡的每個阿拉伯數字，都必須出現在所有 `src` 元素的純文字數字集合裡。數字以 `\d+([.,]\d+)*` 切，千分位逗號拿掉後比對（`45,800` 和 `45800` 視為同一個；`1.8` 和 `1.80` 不同；`2046-09` 切成 `2046`、`09`）。
- 寫法流程：
  1. 在原文區塊上加 `data-lite-alt="<id>"`（或決定用選擇器）。
  2. 建檔：檔頭先寫 `id`、`norm`，`src` 行的指紋先寫 `sha256=TODO`；若原文已標 `data-lite-alt`，也可以完全不寫 `src` 行。
  3. `python3 tools/build_lite.py --stamp <id>`：有 `src` 行就重算指紋；沒有就依文件順序替每個 `data-lite-alt` 元素產生 `src: [data-lite-alt~="<id>"]:nth(k) sha256=…`。
  4. 以後哨兵說「原文改了，短稿要重看：<id>」→ 先對照原文改短稿，**改完才** `--stamp`。不准不看就 stamp。

---

## 6. `lite/facts.txt`（共同事實）

- UTF-8 純文字，一行一條；空行和 `#` 開頭的行略過。
- 每一條都必須同時出現在實作版 `lite/index.html` 和完整版發布版的純文字裡。
- 比對方式：兩邊都「去標籤 → 解實體 → NFKC → 刪掉所有空白」後做子字串比對。所以跨標籤、跨表格格子也能比；不用管空格。
  例：查表 80% 那一列寫 `80% 3.6% 5.2% 6.0%`，實際比對 `80%3.6%5.2%6.0%`（表格那一列連續四格就會對上）。
- 不支援正規表示式。要檢查一整張表，就每列一行。
- 規格要求要列：4／6／7%、防守 2%、查表 11 列、物價倍數表、5/25、45,800、1.55%、6.69%、冷卻期分法關鍵句、第 3 題用語（「要調高股票比例才到得了目標嗎？」）。

---

## 7. `lite/case-checks.json`（案例數字）

JSON 陣列，每一條：

| 欄位 | 必填 | 說明 |
|---|---|---|
| `id` | 是 | 自己取的名字，出錯時印出 |
| `path` | 是 | `lite/calc-results.json` 裡的路徑，用 `.` 分隔，陣列用數字（例 `xiaoan.stress.y2046.loss_wan.50`、`lookup_table.2.low`） |
| `pattern` | 是 | Python 正規表示式，**第 1 個括號群組**抓出數字（單位要和 path 相同，通常是萬）。套在「刪掉所有空白」的純文字上，所以 pattern 裡不要寫空格 |
| `scope` | 否 | 章 id（只在那一章找）或 `"lite"`（全本，預設） |
| `min_count` | 否 | 至少要找到幾處，預設 1；找不到就失敗（避免 pattern 寫錯而永遠通過） |
| `tolerance` | 否 | 容許差，預設 0.5 |

```json
[
  {"id": "小安 2046 跌 50%", "path": "xiaoan.stress.y2046.loss_wan.50", "pattern": "2046年約214萬、跌50%少(\\d+(?:\\.\\d+)?)萬", "scope": "ch8"},
  {"id": "小安 2046 低情境到期", "path": "xiaoan.plan_6500.low_fv_wan", "pattern": "到期金額約(\\d+)萬", "scope": "ch8", "min_count": 1}
]
```
每一個抓到的數字都要和 calc 值相差不超過 tolerance。數字裡的千分位逗號會先拿掉。

---

## 8. `lite/tickers.json` 與 `lite/labels.json`

### 8-1 代號
```json
{
  "codes": ["0050", "006208", "0056", "00878", "009826", "00692", "VT", "VWRA", "VWRD", "VALU", "IWDA", "TLT", "BND", "CBU0"],
  "allow_lite": ["div.story"],
  "allow_full": ["div.story", "div.source-card", "#toolbox li:contains(《)"]
}
```
- `codes`：比對純文字（不看 href 等屬性），前後不能緊鄰英數字（所以網址參數 `N0050001` 不算）。
- `allow_*`：選擇器清單；對到的元素整塊排除後才找代號。實作版只准在黃框；完整版准在黃框、來源卡、書單（書單在 `#toolbox`「再往下讀：書與人」，不在 methods）。
- 新增代號或允許位置要主線核可。

### 8-2 標籤
```json
{
  "practice": [
    {"item": "核心放全球市值型", "keywords": ["全球市值型"]},
    {"item": "台股放多少", "keywords": ["台股大盤"]},
    {"item": "註冊地", "keywords": ["註冊地"]},
    {"item": "防守先用台幣定存", "keywords": ["台幣定存"]},
    {"item": "冷靜期天數", "keywords": ["冷靜期", "先等 30 天"]},
    {"item": "5/25 門檻", "keywords": ["5/25", "跑掉一點點"]},
    {"item": "跌幅基準", "keywords": ["跌幅從", "最近的高點"]}
  ],
  "principle_max_per_chapter": 1,
  "ignore": ["header.cover", "header.lite-cover"]
}
```
- 「本指南的做法」＝`span.label-practice`。所在句子＝從膠囊結束到同一個父元素裡第一個「。！？」為止（沒有就到父元素結尾）。膠囊只能放在句首。
- 項目有 `starts`（fix-r2b 起七件事都有）：句子去空白、去掉開頭的括號小註（例如「（不是唯一答案）」）後，要**以其中一個 `starts` 開頭**才通過。沒有 `starts` 的項目才退回舊規則：句子含任一 `keywords` 子字串就通過（貼錯句子也會過，所以新項目一律寫 `starts`）。
- `practice_max_per_item`：同一件事在每份輸出最多貼幾次（目前 1）。
- 「原則」＝`span.label-principle`。實作版每個 `section.lite-ch`、完整版每個 `section.part` 最多 `principle_max_per_chapter` 個。
- `ignore` 裡的元素（封面圖例）不檢查。

---

## 9. 哨兵一覽（`tools/lite_sentinels.py`）

輸出每行 `OK／FAIL／WARN／SKIP [類別] 訊息`，最後一行 `SENTINELS OK` 或 `SENTINELS FAILED (n)`；有 FAIL 就 exit 1。

| 類別 | 檢查 | 失敗時怎麼辦 |
|---|---|---|
| `alt` | 每份短稿（`alt_dir` 裡的所有檔＋manifest 用到的）：檔頭格式、`norm`、每個 `src` 剛好一個元素、指紋相符、`data-lite-alt` 元素都有記指紋、短稿數字 ⊆ 原文數字 | 「原文改了，短稿要重看：id」→ 對照原文改短稿再 `--stamp`；數字多出來 → 改短稿，不准改原文湊數字 |
| `glue` | manifest 的 glue（純文字）、title、gain、action 沒有阿拉伯數字 | 數字改用短稿（從原文來）或改成國字敘述 |
| `facts` | facts.txt 每條在兩份都找得到 | 看是哪一份漏了；實作版漏了通常是區塊沒抽到 |
| `cases` | case-checks.json 每條抓得到、和 calc 相差 ≤ 0.5 | 改稿或重算 calc，不准放寬 tolerance |
| `tickers` | 代號只在允許位置 | 改成類別名稱 |
| `labels` | 做法膠囊只在七件事、原則每章 ≤ 1 | 移除膠囊或改句子；清單外要加先問作者 |
| `pages` | 實作版 PDF ≤ page_limit；`one_page` 章剛好一頁；計畫表（`plan`）在奇數頁、查表頁（`lookup`）緊接下一頁；並印每章「起頁、範圍、頁數、目標、字數/上限」 | 照提案 1-3 砍法順序處理；奇偶頁不對就調封面後的 `blank_page` |
| `blank_pages` | 完整版 PDF 非空白字元少於 250 的頁全部列出；超過 3 頁 WARN。另外列出最後一行文字在頁面上半（< 50%）的頁（只列不 WARN；字數被來源卡網址墊高的半空頁看這一行）。build 時完整版節尾那頁近乎空白，會讓下一節接著排、不另起新頁（最多四輪），印出接著排的節 id | 看是哪種頁：節尾掉頁通常 build 已處理；圖表頁、表格尾巴要人判斷 |
| `chars` | 字數超過 `char_limit`（只 WARN） | 自行砍 |
| `toc` | 實作版目錄：印出的頁碼＝PDF 連結目標頁＝書籤頁；完整版目錄：印出的頁碼＝連結目標頁，且每個目錄項都讀得到 | 通常是版面在第二次列印時又變了，回報主線 |
| `pdf` | 實作版 PDF author 與書籤存在 | — |
| `version` | 兩份封面都有「version／date」 | 完整版封面要手動加（內容建造者） |
| `ids` | manifest 的 verify 節 id、src 裡的 `#id` 在完整版都存在 | — |
| `unused_marks` | 完整版的每個 `data-lite` 值（skip 除外）都被 manifest 以值抽用；每個 `data-lite-alt` 都有短稿檔 | 補 manifest 或拿掉標記 |
| `appendix_b` | 附 B 表格＝各章想查證框＋verify_index；接合文字不得手寫〈節名〉 | 改 manifest 的 verify |
| `chapter_refs` | 內文「第X章」（國字或數字）指到的章存在；列出所有引用給人對（內容對不對程式判斷不了） | 改短稿 |
| `stories` | 完整版每個黃框純文字＝`guide/index.html`（paths 的 `story_reference`）逐字相同；實作版黃框＝完整版黃框只經過連結改寫 | 黃框原文不准改。注意：v6.0 定稿後 `source` 也是 `guide/index.html`，所以完整版那一半變成恆真，實質把關的是實作版那一半 |
| `fiction` | 實作版每位人物（小安、阿凱、小芸與阿哲、陳大哥）的標題前面緊接著虛構聲明 | manifest 補 `{"notice": "fiction"}` |
| `s13_filter` | 完整版 script 有 `@media print` 隱藏篩選列；靜態 HTML 沒有 `data-s13-hidden` | — |
| `stale` | 單獨跑哨兵時先在記憶體重建，和 `lite/index.html`、`output/full-v60-out.html` 比對 | 重跑 build_lite.py |
| `fragments` | 發布用片段：`output/guide.html` ＝ `output/full-v60-out.html`、`output/lite.html` ＝ `lite/index.html`，各自去掉 doctype／html／head／body 外殼後逐字相同（兩份片段由 `build_lite.py` 在產生兩份 HTML 之後自動重產，不要手改） | 重跑 `build_lite.py`（或交班文件「改完後的固定流程」第 4 步）再發布 |
| `check` | 兩份輸出各跑 `guidetools.py check` | — |
| `manifest` | 正式 manifest 不准有 `sentinel_skip` | — |

**哨兵擋不住的路（fix-r3，每輪由人工逐段對原文）**：「實作版不得有完整版沒有的事實」（主線決定③）機械上只靠 `alt` 的數字規則和 `glue` 的無數字規則。下面三種不在哨兵範圍：
1. 國字寫的新事實（「百分之三」「每七年跌一次一半」「三成」）放在接合文字或短稿裡；
2. 短稿把數字換成來源區塊裡另一個剛好存在的數字（例如「少 42 萬」改成「少 48 萬」，48 也在來源區塊）；
3. 沒有數字的新規則或新說法（例如「可以馬上改」「一年一次」）。
所以每輪審查都要把 manifest 的 glue、action 和改過的短稿逐段對回完整版原文；新增的事實一律先寫進完整版，再由短稿引用（短稿檔頭補一行 `src`）。

頁數怎麼算：每章起頁＝PDF 書籤裡「label title」所在頁；下一章的標題是該頁第一段文字就算下一章另起一頁，否則兩章共用那一頁。所以相鄰兩章的範圍可能重疊一頁。

---

## 10. 版面（程式內建，不用在 manifest 寫）

- 實作版沿用完整版 `<style>` 全部（顏色、字級變數、黃框、警告框、標籤膠囊），再附加 `.lite-*` 樣式：
  - 列印：`@page{size:A4;margin:13mm 13mm 15mm}`＋底部置中頁碼；內文 10pt、行距 1.4；卡片與清單間距縮小；表格 8.5pt、不設最小寬度。網頁版維持完整版行距。
  - 只有 `page_break`、`one_page` 的章與 `{"page_break": true}` 會換頁，其他章接著排。
  - 動作框 `.lite-action`（綠色實線框，標「動作」）；想查證框 `.lite-verify`（灰色虛線框、小字）；虛構聲明 `.lite-fiction`（灰框膠囊）；章名上方的 label `.lite-label`。
- PDF：Chrome headless `--no-pdf-header-footer --generate-pdf-document-outline`，列印用 HTML 把所有 `details` 加上 `open`；書籤照 h1–h3 自動產生。目錄頁碼：先印一次，用 PyMuPDF 讀目錄連結指向的頁，填進目錄再印；頁碼沒變就停（最多四次）。完整版也照同一流程（在列印用 HTML 的目錄每一項後面加頁碼；網頁版不加）。metadata：title、author、subject（版本／日期）。
