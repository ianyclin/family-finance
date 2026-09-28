# v7.0 預覽：CQ——閱讀定位條與桌機左側目錄（主線 2026-09-28 晚定；作者裁定「桌機左側可以一起做，開工」）

目的：長卷在手機上迷路。給讀者三件事：**現在在第幾節**、**點開全書目錄跳過去**、**回到上次讀到的地方**；桌機另有左側目錄。**不動任何內文一個字**；靜態 HTML 裡不放任何新的可見文字（目錄項目、節名全部由 JS 在執行時從 `section.part > h2` 讀出來建），這樣 budget／to_text／lite 抽取都不受影響。

## 一、頂部定位條（手機與桌機都有）
- 元素：`<nav id="posbar" aria-label="閱讀位置" hidden>`，放在 `<header class="cover" id="top">` 之前或 body 開頭；內容全由 JS 填。`position: fixed; top:0; left:0; right:0; z-index` 高於內容；高度 40px（手機）／44px（桌機）；背景用頁面底色加 `backdrop-filter: saturate(1.2) blur(6px)`（不支援時純底色）＋下緣 1px 邊線；文字用既有的 `--muted`／`--fg` 變數，字級 .9rem；深色模式跟既有的 `:root` 變數走。
- 左側：「第 14 節」（數字用 `span.num` 同一個字型設定）＋「把答案寫成一張紙：我的投資計畫」（一行、超出 ellipsis）。沒有節號的區塊（封面、目錄、group-* 分組摘要）顯示區塊 h2 的字或「目錄」。
- 右側兩顆按鈕（`<button type="button">`）：「目錄 ▾」（`aria-expanded`、`aria-controls="posmenu"`）；「回上次」（只在有存檔且存的節≠目前節時出現，`aria-label="回到上次讀到的第 N 節"`）。
- **出現時機**：讀者滾過封面（`#top` 的底部離開視窗）才顯示；在封面時隱藏（`hidden`），避免蓋住書名。
- **當前節偵測**：`IntersectionObserver` 觀察每個 `section.part` 的 h2（或 section 本身），`rootMargin` 讓「h2 的頂部剛過定位條下緣」算進入；用「最後一個已越過定位條的 h2」當當前節；沒有 IO 時退回 `scroll` 監聽（`requestAnimationFrame` 節流）。
- **錨點不被蓋住**：定位條出現時在 `<html>` 加 `data-posbar="1"`，CSS `html[data-posbar] :is(.part, [id]) { scroll-margin-top: 56px }`（既有的 16px 只在無定位條時用）。
- 列印：`@media print { #posbar, #posmenu, #posrail { display:none !important } }`；`prefers-reduced-motion` 時不做動畫。

## 二、目錄抽屜（點「目錄」）
- `<div id="posmenu" role="dialog" aria-label="全書目錄" hidden>`，從定位條下方滑出，最高 70vh 可捲，寬同視窗（手機）／最寬 420px 靠右（桌機）。
- 列出全部 `section.part`（含封面「回到最上面」一項，分組摘要 group-* 不列，目錄 `#toc` 不列），每項「第 N 節　標題」，當前節加 `aria-current="true"` 與反白（用 `--mark`／既有 mark 色淡一點）；點項目 → `scrollIntoView({block:'start'})` 後關閉抽屜；Esc、點抽屜外、再點「目錄」都關閉；開啟時焦點進抽屜第一項，關閉後回按鈕。
- 抽屜開著時當前節仍會跟著滾動更新（若讀者在抽屜開著時滾）。

## 三、桌機左側目錄（視窗寬 ≥ 1100px）
- `<nav id="posrail" aria-label="章節" hidden>`：`position: fixed; left: 0; top: 44px; bottom: 0; width: 240px; overflow-y:auto`，同一份目錄項目；當前節反白並自動捲到可見（`scrollIntoView({block:'nearest'})`）。
- 主內容在 ≥1100px 時 `margin-left: 240px`（只加在這個斷點，**1024px 以下版面完全不變**，`v7_layout_check` 量的 375／1024 不受影響）。內容區既有的 `max-width`／置中在 ≥1100px 要仍然置中於剩下的寬度（檢查 `header, main, footer { margin-inline:auto }` 與新的 margin-left 不衝突；必要時用 `padding-left` 給 body）。
- 列印隱藏。

## 四、記住上次位置
- `localStorage` 鍵 `grx-v7-pos`，值 `{"id": "<section id>", "y": <視窗頂距該 section 頂的 px>, "t": <時間戳>}`；滾動停止 500ms 後存（節流）；讀寫都包 try/catch；讀不到就當沒有。
- 載入時：若有存檔、且目前 scrollY 在封面範圍，定位條顯示「回上次：第 N 節」按鈕（定位條此時因為在封面而隱藏，所以改成：**在封面底部的位置顯示一顆小按鈕**「回到上次讀到的第 N 節 ↓」，或簡化為：定位條在有存檔時例外顯示——builder 選一種，說明理由）；點了才跳，不自動跳；跳完按鈕消失。
- 不跨裝置、不上傳；規格文件裡寫明。

## 五、實作與檢查
- 只加：一段 `<style>`（接在既有 style 尾）、一段 `<script defer>`（body 尾），加三個空容器元素；**guide/index.html 其他任何字元不動**（`git diff` 只准在這三處＋容器）。JS 不用任何外部庫；全部在 `DOMContentLoaded` 後執行；任何錯誤 try/catch 不影響閱讀。
- `essay_charts.py --guide` 兩次（不能把新加的東西蓋掉）；`build_lite.py`（工作表不受影響、完整版 PDF 頁數不變＝181，列印隱藏生效）；`guidetools.py check`；`test_guidetools.py tools guide/index.html`；`test_v7_check.py`；budget（應完全不變，因為沒有靜態可見文字）；numbers 兩基準 LOST 0；anchors；xrefs；`v7_layout_check.py`（375／1024 無溢出）；`v7_money_age_measure.py`；calc_core 引用缺漏 []。
- 交件附：三個容器的 HTML、CSS 與 JS 全文行數、`git diff --stat`、每項檢查最後一行、你自己在 headless Chrome 375／1024／1280 各截一張圖（定位條、抽屜開著、左側目錄）存到 scratchpad 並回報路徑。主線會再用內建瀏覽器實測互動。

## 六、不做
- 不做百分比進度（作者裁定：讀者甲走起步路線、跳著讀，百分比會誤導）。
- 不做搜尋、不做字級調整、不動既有 `#toc`。
