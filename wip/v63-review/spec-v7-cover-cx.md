# v7.0 預覽：CX——封面與書尾版面、署名全名連結、工作表接進書末（作者 2026-09-29 凌晨四點要求；主線裁定）

作者原話：「最前面跟最後面的版面配置似乎有點不自然」「把『可列印工作表』放在最後變成整份檔案（保持列印時為 A4 版面配置）」「第一頁的署名應為『指數三寶飯・家庭理財陪跑』」「『可列印工作表』應連結到最後的檔案」「整本書提到我的名字『指數三寶飯・家庭理財陪跑』都應該有超連結」。基準 HEAD 5489567。**不改任何內文句子的用字（下面列出的搬動與拆段除外）；黃框、h2、lede、mark.key、p.decision、warning 不動。** 粉專網址一律 `https://www.facebook.com/profile.php?id=100084000897269`，`target="_blank" rel="noopener"`。

## A. 封面（L209–232）
1. **署名**：L216 `<p class="small cover-byline"><span class="pn">指數三寶飯</span>｜家庭理財陪跑</p>` 改成 `<p class="cover-byline"><a href="粉專" target="_blank" rel="noopener"><span class="pn">指數三寶飯</span>・家庭理財陪跑</a></p>`，**搬到 L214（第二個 subtitle-sub）之後、封面插畫 figure 之前**（讓它是作者署名，不是插畫的繪者署名）。CSS：`.cover-byline{font-size:1.05rem;font-weight:700;color:var(--ink);margin:.4em 0 1.1em}.cover-byline a{color:var(--green)}`；深色模式沿用變數即可。
2. **兩行小字**（L217 工作表、L218 勞保）從封面拿掉，改成「怎麼讀這本書」清單（L224–231 的 `<ul>`）最後兩個 `<li>`：
   - `<li>要印出來手寫的表格，在書末的「<a class="xref" href="#worksheet">可列印工作表</a>」（六頁，也可以只印那六頁）。</li>`
   - `<li>勞保、勞退那幾段適用受僱勞工，公教、軍職、自營者的退休制度要另外查。</li>`（原句逐字）
   舊的 `https://claude.ai/artifact/492iv4AuQeSHVPRN2XEC1E` 連結全書不再出現（grep 0）。
3. 封面順序改後：eyebrow → h1 → subtitle → 兩個 subtitle-sub → 署名 → 封面插畫 → 兩顆按鈕 → 為什麼寫這本書 → 怎麼讀這本書 → 目錄。按鈕上方原本靠兩行小字隔開，現在直接接插畫：`.cover-cta` 上邊距補到與插畫間距自然（約 22px），375 與 1024 各截一張圖交件。

## B. 書尾（L4419–4422）
4. **後記簽名** L4421：`<span class="pn">指數三寶飯</span>` 改 `<span class="pn">指數三寶飯</span>・家庭理財陪跑`（a 不變）。
5. **頁尾版權段** L4422 那個長 `p.small`，用字一字不改，拆成三個 `p.small`：(1) 從「© 2026」到「引用請註明出處與日期。」；(2) 從「文中引用的研究」到「未轉載原圖。」；(3) 從「本指南提供一般教育資訊」到句尾。頁尾 `<p><strong>隔離人性｜理財新手完整指南</strong></p>` 留著。
6. **附錄接在 `</footer>` 之後**（書的最後；後記與版權仍是正文的結尾，工作表像書末可撕下的表格）。見 C。

## C. 其餘署名
7. L4088 圖說 `圖：<span class="pn">指數三寶飯</span>` 與 L4411 `作者（<span class="pn">指數三寶飯</span>）`：pn 外包同樣的粉專 `<a>`（短稱不改成全名——一個是圖的署名、一個在句中）。改完全書「指數三寶飯」在可見文字裡 5 處全在 `<a>` 內（meta 不算）。`lite/index.html` 的 meta author 不動。

## D. 工作表接進書末（保持 A4 六頁）
8. `tools/build_lite.py` 新增步驟 `appendix`：把工作表的六個 section 本體（和 lite/index.html 相同來源、相同 transform）包成
   `<!-- worksheet-appendix:start --><section class="worksheet-appendix" id="worksheet" data-generated="build_lite"><style>…（lite 專屬 CSS，每條選擇器前綴 `#worksheet `，**不含 @page**；分頁 class .lite-break／.lite-onepage／.lite-page-break／.lite-blank-page 照搬並加前綴）</style><h2>附錄：可列印工作表</h2><p class="small">六頁，印出來手寫；也可以只印這六頁。</p>…六個 section…</section><!-- worksheet-appendix:end -->`
   寫回 `guide/index.html` 的 `</footer>` 之後、`<nav id="posrail"` 之前（第一次插入；之後用 marker 等冪替換）。**抽短稿前先把 marker 之間的區域從 guide 文字裡拿掉**，不能讓附錄餵自己（[stale]／[fragments] 哨兵同樣拿掉附錄再比）。
9. 附錄內所有原本指向「完整指南」的說法：`rewrite_links` 產生「完整指南〈節名〉」時，若當下知道那一節的 id，附錄版改成 `<a class="xref" href="#id">節名</a>`；不知道就留文字。附錄裡不可以有指向 claude.ai 的連結。
10. 列印：附錄的第一頁 `break-before:page`；六張表照原本的分頁 class；**指南 PDF 裡附錄必須正好 6 頁**（用 fitz 找 h2「附錄：可列印工作表」所在頁到最後一頁）。如果 16mm/14mm 的 @page 邊界讓它變 7 頁，試 `#worksheet{page:worksheet}` ＋ `@page worksheet{size:A4;margin:13mm 13mm 15mm}`（Chrome 支援具名頁）；還不行就回報，不要硬壓字級。獨立的 `lite/index.html` 與 6 頁工作表 PDF 照舊產出、哨兵照舊。
11. 目錄：`nav.toc` 的 `ol.toc-from-26` 之後加 `<p class="toc-appendix"><a href="#worksheet">附錄：可列印工作表</a></p>`（不編號）。進度條：L4439 起的 script 用 `section.part` 列節，附錄不是 `.part`，在 posmenu 與 posrail 的清單**最後**加一項「附錄：可列印工作表」→`#worksheet`（讀 script 後用最小改法；IntersectionObserver 也要觀察它）。PDF 書籤：確認附錄 h2 有書籤、`fix_full_outline` 不會給它加節號。
12. 哨兵排除附錄：`tools/guidetools.py` 的 `to_text` 與 `check`、`tools/v7_check.py` 的 `Doc`（budget／numbers／xrefs／anchors）都在解析前把 marker 之間的區域拿掉（一個共用的小函式 `strip_appendix(html)` 放 guidetools，v7_check import 它或複製兩行 regex——寫清楚選哪個）；`embed_illus`、`v7_layout_check`、`lite_sentinels` 不排除（附錄在 375 也要能看，layout 若因附錄表格失敗，回報不硬修）。anchors 哨兵要能看到 `#worksheet` 這個 id（先 strip 會找不到，所以 xrefs／anchors 要把 `worksheet` 加進已知 id，或在 strip 時留一個空殼 `<section id="worksheet"></section>`——選後者）。

## 檢查
全套（numbers 兩基準 round59 LOST 0；anchors；budget——cover 主線會少那兩行小字，其他不變，照實測寫 `_comment_cx`；planstep；xrefs；guidetools check；兩支測試；essay_charts --guide ×2 0 ⚠；calc_core；layout；build_lite 跑兩次第二次 guide 逐 byte 不變（等冪）；lite_sentinels；embed_illus --check）；PDF：總頁數、書籤數、附錄起始頁與頁數＝6、附錄每頁與獨立工作表 PDF 對應頁的文字相同；`grep -c 492iv4AuQeSHVPRN2XEC1E guide/index.html` = 0；全書「指數三寶飯」可見 5 處皆在 a 內。375／1024 截圖：封面（署名在插畫上方）、書尾（後記→版權三段→附錄第一頁）、附錄第一張表。不 commit。
