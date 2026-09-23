# v7.0 預覽：AS——十桶金卡搬到第 5 節主線、圖例顏色、手機表格固定欄（作者 2026-09-23 拍板）

一個 commit（＋純重建）。guide/index.html 大，grep 定位。
## 1. 搬到主線
第 5 節（section id s2）的 `<details class="more">`，summary「想深入：資產長到一年儲蓄的一百倍要花幾年？這一節幾組試算各用什麼假設？報酬率漂亮，賺到的錢就多嗎？」——把裡面整張 data-card「資產每多一桶要多久」（從 `<div class="data-card"` 到配對的 `</div>`，含 figure、主線段、想深入）剪出，貼到這個 details 的正前方（同一層、主線）；details 其餘內容不動；summary 改「想深入：這一節幾組試算各用什麼假設？報酬率漂亮，賺到的錢就多嗎？」。
卡搬到主線後 figcaption、主線段、legend 從 folded 變 mainline／small：`v7_check.py budget` 的 s2 mainline／small、`_total_max`、`_visible_total_max` 抬到剛好，`_comment_as` 註明「十桶金卡從摺疊搬進主線，作者拍板」。
## 2. 圖例顏色與圖不符（`tools/essay_charts.py` `milestones()`）
現在 total 多邊形（TEAL 0.3）鋪滿、contrib（MUTED 0.35）疊上去，下半塊是混色，圖例卻是實心色塊。改：contrib 多邊形照舊；「長出來的報酬」改畫成 contrib 曲線與 total 曲線之間的帶狀多邊形（點序：contrib 左→右，接 total 右→左），TEAL fill-opacity 0.3；total 外框 `poly` 照舊。legend 改 `legend([(MUTED, "自己存進去的", 0.35), (TEAL, "長出來的報酬", 0.3)])`（legend() 第三個元素是 opacity，v7_g09_rolling.py 有先例）。兩版 --guide 兩次 0 ⚠、標籤自檢 0 ⚠。
## 3. 手機版表格固定欄蓋住第 1 欄
AP-3 把 `figure.chart>.table-wrap` 加進 660px 以下的 padding 清單（style 第 98 行附近），捲動容器有 18px 內距，`sticky; left:0` 的第一欄貼在捲動口最左邊、蓋住內容區前 18px（作者截圖：表從「2」開始、左下露出半個 22%）。改：從那個清單拿掉 `figure.chart>.table-wrap`，同一個 media query 加 `figure.chart>.table-wrap{margin-left:18px;margin-right:18px}`。改完用 python 抽 style 確認。
## 交件
全套檢查（numbers 對 _baseline_v631 與對 HEAD，allow round35，搬動不該 LOST）；guidetools、test_*、calc_core（引用缺漏 []）、build_lite（SENTINELS OK；短稿若引用該區塊照 lite-format.md 處理）；changes-for-author 加「一之五十、批 AS」；handoff 末尾補一句。回報卡的新位置（前後各一元素）、多邊形點數、CSS 規則、檢查 exit。不開瀏覽器、不發布。
