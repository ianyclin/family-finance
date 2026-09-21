# 外部連結檢查（2026-09-21；guide/index.html）

方法：先用程式抽出所有對外連結、curl 測一輪（HEAD，403／405 才改 GET；瀏覽器 UA；逾時 25 秒）；首輪非 2xx 的 21 條再由裁判逐條複驗（改 GET、輪替 UA、檢查 `<title>`／PDF 檔頭、Crossref 與 Wayback 佐證）；最後主線用內建瀏覽器實際打開程式測不了的健保署頁面。

| 項目 | 數 |
|---|---|
| 唯一外部網址 | 183 |
| 其中來源卡（`details.source-card a.source-link`） | 172 |
| 其他（書單、粉專、工作表、Podcast 等） | 11 |
| 首輪即 2xx | 162 |
| 首輪非 2xx、複驗後確認可用 | 19 |
| claude.ai 登入牆（正式版工作表連結，非失效；登出狀態能不能開仍待作者用無痕視窗測） | 1 |
| **真的失效** | **1**（健保署，見下） |

（首輪曾報「198 個／4 條 404」：198 是抽取器把含 `&amp;` 的 15 條網址重複計入；4 條 404 是那幾台伺服器對 HEAD 回 404、對 GET 回 200 的假陽性——Vanguard VT 產品頁、投信投顧公會 ETF 投資百寶箱、Vanguard Mexico 兩份 PDF，GET 都正常。）

## 真的失效（1 條，已找到替代）
- `https://www.nhi.gov.tw/ch/cp-1719-0d5e5-2540-1.html`（第 22 節 `#costs` 來源卡、第 27 節 `#toolbox`〈稅與健保〉各一處）：程式一律被 Cloudflare 擋；主線用瀏覽器實開，**被導回健保署首頁**（`/ch/mp-1.html`）＝原頁已不存在。
- 替代：`https://www.nhi.gov.tw/ch/cp-4516-74b0f-2613-1.html`（健保署〈補充保險費計算公式〉，健保服務＞投保與保費＞補充保險費＞補充保險費計算與繳納）。瀏覽器實開確認頁面寫明：扣費單位「按費率 2.11% 就源扣取」；股利所得「單次給付達 20,000 元」（非以雇主或自營業主身分投保者）、單次給付以 1,000 萬元為限。與書上「股利單次給付達 2 萬元、費率 2.11%」相符。

## 擋自動程式、要用瀏覽器才打得開（15 個網域，16 條；都確認存在）
ubs.com、finra.org、fourpillarfreedom.com、facebook.com、doi.org（2 條）、time.com、web.archive.org（一時限速）、tandfonline.com、onlinelibrary.wiley.com、journals.uchicago.edu、spglobal.com、simonandschuster.com、books.com.tw、nhi.gov.tw（整個網域擋程式）、pm-research.com（訂閱牆）。期刊類以 Crossref 比對作者／卷期／頁碼，出版社與書店頁以 Wayback 快照佐證。

## 沒查的
首輪 2xx 的 162 條沒有逐條檢查是不是「回 200 的找不到頁面」；只驗連通性與標題，沒有全文對照來源卡的宣稱。
