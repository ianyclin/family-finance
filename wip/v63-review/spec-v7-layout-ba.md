# v7.0 預覽：BA——版面收斂第二段（結構）：卡名降級、節內小標、圖搬出卡、摺疊與表格統一

作者 2026-09-23 拍板「全部照你建議」（拍板 3、4）。依據 `layout-audit-structure.md`（E1–E5、P1 #9、#13–#18）、`layout-audit-visual.md`（F2、3-D 建議 A、3-E、3-F）、`layout-decisions-2026-09-23.md`。**正文字不改**；新增的只有節內分組小標（先起草、標「待作者定」）。分四個 commit（BA-1～BA-4），各附產生檔重建；每個 commit 後 `v7_layout_check`、guidetools、anchors、budget、planstep、numbers（round35）、test_*、calc_core、build_lite 全綠。guide 的 `<style>` 是 lite 的來源。

## BA-1 卡名降級（機械、可腳本）
- 所有 `div.data-card > h3` → `h4`（84 處）；原本卡內的 `h4`（14 處）→ `h5`。
- CSS：`.data-card h3{…}` 的規則改成對 `.data-card h4`（用 AY 定的 h4 通則 1.05rem＋字距，卡名不得小於正文 17px：卡名定 1.06rem）；`.data-card h4{.95rem}` 改成 `.data-card h5{.95rem;…}`；`.source-card h3` 同樣降成 h4 並改 CSS。
- `h3` 從此只有節內小標（19.2px）。lite/labels、build_lite 若用 `h3` 選擇器抓卡名（grep `h3` in tools/build_lite.py、lite/manifest.json、tools/guidetools.py、tools/v7_check.py），同步改；哨兵綠。

## BA-2 節內分組小標（起草，待作者定）
- 超過 4,000 字且節內 h3＜2 的節：why、s2、s3、s5、cases、s12、costs、annual、lifecycle（methods、s11 另計）。每節加 2–3 個 `h3`，放在主線中段的自然分界（卡海前、主題轉換處）；標題**優先從既有卡名／摺疊標題提字**（例如 cases 四位人物各一個 h3 用人物名；s12 依「三條路徑／起步版六行／要不要含中國」分三段），不夠再自擬，每個 ≤12 字、名詞句或問句，不用「一、二、三」。
- 全部列成一張表（節、位置、標題、來源）寫進 `changes-for-author-v7.md` 一之五十四，標「待作者定」。
- s11 已有 5 個節內小標，不動。

## BA-3 圖搬出卡（17 處）＋同義合併
- 14 張在 `div.data-card` 內、3 張在 `details.more` 內的 `figure.chart`：搬成該容器的**下一個兄弟**（卡之後）。若卡搬出圖後只剩 h4（＝卡名與 chart-title 同義的 14 組），卡殼刪掉、卡名不留（chart-title 已在）；若卡還有其他內容（表、段落、小字），卡留著、圖在卡後。`details.more` 內的 3 張：圖搬到該 details 之後（主線），details 保留其餘內容；若 details 只剩 summary，整個刪。
- 圖內的 p.note／figcaption／details 隨圖走。錨點（`span[id]`）若原本在卡前指到圖，保持在圖前。
- 搬完 `v7_layout_check` 375／1024 圖左右緣 0 違規；L105 的四條負邊距只剩 `figure.chart` 直接在 section 下那一條（其餘刪）。

## BA-4 摺疊與表格統一
- 7 個無 class 的 `<details>`（s10 ×1、s11 ×4、cases ×1、annual ×1）加 `class="more"`；保留它們的 `data-print`／`data-lite-alt` 屬性；CSS 對無 class details 的規則可刪。
- 表格：`stack-mobile-cols`（JS 產 col-cards，5 張）改成 `stack-mobile`（純 CSS，含 `data-label`）；L92 的 9 條規則與對應 JS 刪；第 14 節兩張專用表（L50 `#s11 details[data-print="open"]`、L52 `#plan-starter`）改成通用 `stack-mobile`＋每格 `data-label`（約 30 個 td），L50／L52 共 23 條規則刪。`sticky-first` 3 張保留。class 組合目標：`compact`／`compact tight-mobile`／`compact tight-mobile sticky-first` 三種＋`stack-mobile` 修飾。
- 列印：`@media print` 若有引用被刪的 class，同步清；工作表頁數不變（6 頁）、完整版頁數 ±2 頁內。

## 交件
每批回報：改了幾處、CSS 刪／改了哪些選擇器、哨兵數字（左緣種類數、圖違規、表溢出、summary 左突）、頁數；BA-2 的小標表。不發布；主線截圖。
