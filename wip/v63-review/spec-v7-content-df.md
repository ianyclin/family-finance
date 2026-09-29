# v7.0：DF——新書封、三代人插畫搬位置、五條技術債（作者 2026-09-29 下午；主線裁定）

基準：批 DE 的 commit。**黃框、h2、lede、mark.key、p.decision、warning 不動；圖說與 alt 一字不改。** 改完指南一定跑 build_lite（兩次等冪）。

## A. 書封換檔
來源 `~/Documents/Codex/2026-09-17/new-chat/output/cover-plan-and-life/cover-family-five-new-subtitle-2048.png`（2048×3072，sha256 60f8a924307aa12f…；主線已驗：畫面與前一版相同，只改上方文字——副題換成「給新手的長期投資與行為紀律指南」、拿掉「理財新手完整指南」）。PIL 轉 `guide/illus/00-book-cover.webp`（RGB、quality=80、method=4、不縮放），`embed_illus.py` 重嵌再 `--check`。alt 不改。

## B. 04 三代人插畫在第 1 節內往上搬
現在位置：`#ten` 的 `ol.checklist[data-lite-alt="ch1-six"]` 的 `</ol>` 之後，圖說和正上方清單最後一句幾乎同句。改放到第 1 節的白話版（`p.explain`）之後、第一個清單或小標之前；若第 1 節沒有白話版，放在 lede 之後。整個 figure（img、alt、figcaption）逐 byte 搬移。先 grep 第 1 節有沒有「上面／下面那張圖」會指錯。搬完若和別的 figure（圖表）緊鄰，回報。

## C. 技術債五條
1. `build_lite.py` 的 `APPENDIX_REWRITES`（與 cite）裡寫死的節號（14、13、8…）改成從指南讀：用 section id 找該節 h2 的 `span.num`。重編號時自動跟。
2. 附錄版計畫表「（先答第十三節四題）」：只在附錄模式改成「（先答第 <a class="xref" href="#s10">13</a> 節四題）」（數字同樣從指南讀）；獨立工作表不變。附錄仍要正好 6 頁（[appendix] 哨兵）。
3. PDF 書籤：`fix_full_outline` 把「附錄：可列印工作表」之後、屬於附錄的書籤全部降一層（收在它底下）；其他書籤層級不變；書籤總數不變。
4. 急救卡兩個錨點改準：
   - 第 17 節「處理套牢的舊部位，或賣掉以後不敢買回來」那個 `<li>` 加 `id="s13-stuck"`；急救卡正文（`#plan-panic`）指到它的 xref、`tools/v7_g12_route_maps.py` 的 PANIC_BRANCHES、`APPENDIX_REWRITES` 第 10 條，三處 href 從 `#s13-loss` 改 `#s13-stuck`。第 17 節摺疊裡其他指 `#s13-loss` 的不動。
   - 「這筆錢五年內要用的」那條：急救卡正文 xref、PANIC_BRANCHES、附錄 rewrite 三處從 `#s5-remember` 改 `#s5-fiveyear`（先確認 `#s5-fiveyear` 就是「記得這幾句」第一條那個元素；不是就不改、回報）。連結文字不變。
   - `v7_g12_route_maps.py` 的錨點指對斷言要跟著過；essay_charts --guide ×2。
5. `wip/v63/stock-vs-index/charts/test_G07.py`：把過期的節號對照改成現行（讀 `tools/v63_g07_investor_cycle.py` 的 SECTIONS），讓它跑得起來並全過；改不動就在檔頭加一行註解「節號過期，未維護」不刪檔。
6. 交班檔固定流程（約 L384–389）兩行 numbers 指令的 `numbers-allow-round17.json` 改成「現行放行檔（2026-09-29 是 round60）」。

## 檢查
全套（numbers 兩基準 round60 LOST 0；anchors（多一個 id）；budget 照實測 `_comment_df`；planstep；xrefs；guidetools check；兩支測試；essay_charts ×2；calc_core 引用缺漏 []；layout；build_lite ×2 等冪；lite_sentinels；embed_illus --check 11 張）；感知雜湊：00、04 全書各一處；PDF：頁數、書籤數與層級（附錄底下的列出來）、附錄 6 頁奇數起頁、第 1 頁書封 2048×3072；375 截圖：書封、第 1 節新位置。不 commit。
