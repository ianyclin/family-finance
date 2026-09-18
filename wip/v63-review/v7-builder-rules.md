# v7 預覽版：builder 共同規則

每一批的 builder 先讀（依序）：本檔 → `design-v7.md`（全讀；2c、2d 與 2026-09-19 更正優先於較早的段落）→ `decisions-2026-09-19.md` 的「模糊的正確」一節 → `docs/core-edition/specs/eli5-rules.md`（句子寫法與作者看過的範例）→ `engineering-impact.md`（會踩的雷）→ `material-map.md` 裡和自己那一批有關的部分 → `docs/handoff-guide-2026-09-16.md` 的「作者的原則」「標記系統」「固定流程」「工具」。

## 你在替誰寫

第一次接觸投資的台灣讀者，用手機讀。國中生讀得懂，大人不覺得被當小孩。他要的是「模糊的正確」：方向可靠、好懂、足以做下一步。精細的計算與例外是作者替他做完的工作，不是他的功課。

## 每節主線的骨架（2d）

① 這一節的答案／現在先做什麼 → ② 為什麼大致合理：一個畫面、一個機制、一兩個數字 → ③ 什麼情況才要停下來重想（最多兩三條）。之後：圖（有的話）→「想深入」摺疊 → 來源 → 黃框 → planstep（有的話）→ `p.decision`。

## 每一段的取捨（2a）

> 拿掉這個細節，新手會做出明顯不合適的決定嗎？還是只是專業讀者會覺得不夠完整？

- 前者：留主線，放在骨架的 ③，只講一次。
- 後者：移進 `<details class="more"><summary>想深入：〈具體講什麼〉</summary>…</details>`。一節可以有兩三個，摘要要具體（「想深入：定存這二十年有沒有追上物價」），不要寫「更多細節」。
- 重複句、重複的防禦性但書（不是建議／不是預測／不是保證）：刪，每節最多留一次。
- 看得到的小字（`p.small`、`span.small`、`p.note`）每節合計 ≤ 350 字，只留緊貼數字的一句出處或口徑；其餘連同它說明的內容一起進「想深入」。
- 第二份以後的研究、名人、對照市場、推導、口徑說明、長表：進「想深入」。來源卡留在原位（來源卡不算主線）。
- **移層優先於刪除**；有來源的內容不刪。

## 句子

- 一句一件事。先畫面，再道理，最後數字；數字要看得出「所以呢」。
- 不寫「不是 A，而是 B」的堆疊；不寫翻譯腔；不寫空泛總結句；不在句子裡用括號塞第二件事（括號只用來就地解釋名詞，十個字內）。
- 簡化後的句子單獨拿出來要成立；不得滑成承諾（「長期一定賺」「跌了都會回來」「放五年就安全」）。
- 不寫複利口徑；只說「這是估算」。
- 主線不准有「先看第 N 節才懂」的依賴；指路句一節最多一句，放在最後。

## 不能動

黃框 `div.story` 全文；所有既有 `id`；h2 節名（設計點名的除外）；來源卡的引文與連結；圖的資料；`mark.key` 文字（設計點名的那一句除外）；教學段不放商品代號；不新增事實、數字、研究、來源（小安的數字取自現有小安全表）；`a.term` 每節只標第一次、不放在標題／白話版／黃框／strong／mark／其他連結裡；`a.xref` 的錨文字＝目標節的顯示節號（id s12 顯示 13、s13 顯示 14、cases 顯示 12）。

## 怎麼改檔

- 分支 `v7-preview`。只改自己那一批的節；別批的節看到問題記在回報裡，不要動。
- `guide/index.html` 1.1 MB：用 grep／python 小範圍讀；用 Edit 或寫一支一次性的 python 腳本做「整段替換」（以節的起訖標記定位，替換前 assert 舊段落出現剛好一次）。**不要用 `guidetools.py apply` 搬節或做有重疊的補丁**（engineering-impact 第 1 點）。不要整檔 Write。
- 圖說在指南與 `tools/essay_charts.py`（或 `tools/v63_g0*.py`）各一份，改一邊就要改另一邊；跑圖一律 `python3 tools/essay_charts.py --guide`。
- 改到帶 `data-lite-alt` 的區塊：看過對應的 `lite/alt/*.html` 仍然對，才 `--stamp`。

## 每批交件前自己跑

```bash
python3 tools/v7_check.py numbers wip/v63-review/_baseline_v631.html guide/index.html --section <你的節…>   # LOST 必須 0（或列進 allow 檔並說明）
python3 tools/v7_check.py anchors wip/v63-review/_baseline_v631.html guide/index.html
python3 tools/v7_check.py mainline guide/index.html        # 對照 budget-v7.json 你的節
python3 tools/v7_check.py planstep guide/index.html
python3 tools/build_lite.py                                 # exit 0＋SENTINELS OK
python3 tools/guidetools.py check guide/index.html
python3 tools/test_guidetools.py tools guide/index.html
```

哨兵紅了照 `docs/core-edition/specs/lite-format.md` 第 9 節。因為設計改動而必須調整哨兵或白名單時：在回報裡寫清楚改了哪一支、為什麼不是放寬語意。全綠後 `git add -A && git commit`（訊息寫批次與做了什麼）。

## 回報格式

1. 各節 mainline／small 改前 → 改後（對照預算）。2. 移進「想深入」的東西清單（每節幾個摺疊、摘要文字）。3. 直接刪掉的句子（逐字）與理由。4. 你不確定、需要 Fable 裁的地方（附原文與你的提案）。5. 每節挑一段「改前／改後」逐字對照，讓 Fable 看語氣。6. 檢查與哨兵的最後輸出。

## 第 1 批之後的補充裁定（Fable，2026-09-19）

- 來源卡 `div.source-card` 在工具裡獨立成 `source` 欄，不算小字也不算主線；留在原位、照常顯示。每節小字 ≤350 指的是 `p.small／span.small／p.note／figcaption`。
- 一節可以放兩張 planstep（手機上一張卡只問一件事）。planstep 標題寫「你的計畫・第 N 行：〈白話問題〉」，N 照 design-v7.md 2b 的六行；`data-plan` 寫對應的完整版格號。
- 封面入口可以是八個。為了減重而拿掉某節的名詞連結 `a.term` 可以，詞條本身留著。
- **F 區「跌 10%、20%、30% 各做什麼／三格／三種跌幅」的句子一律留給第 4 批**，其他批看到只做句子減重、不改規則。`#plan-panic`、`#drill`、一頁空白版、查表頁、年檢表（帶 `data-lite-alt` 的區塊）也留給第 4 批。
- **平行施工**：第 2、3、5、6 批各在自己的 git worktree 同時進行，只准改自己那幾節的行。`<style>`、封面、目錄、`group-*` 組地圖、tools/ 不要動（需要就寫在回報裡）；唯一例外：自己那幾節的 h2／lede 改了，會讓 `part_maps` 紅——所以 **h2 與 `p.lede` 不要改**。worktree 裡沒有被 gitignore 的檔：基準檔請用絕對路徑 `/Users/linyenchu/Cladue Code/family-finance/wip/v63-review/_baseline_v631.html`；build 缺檔時從主工作目錄複製需要的（不要 commit 它們）。
- commit 時只加來源檔：`git add guide/index.html lite/alt lite/facts.txt lite/case-checks.json tools/essay_charts.py tools/v63_g*.py`（有動到才加）；`output/`、`lite/index.html`、`lite/work/`、`lite/calc-results.json` 這些產生的檔**不要 commit**（`git checkout -- output lite/index.html lite/work` 還原），合併後由 Fable 統一重建。

## 留給第 4 批與第 7 批的事（Fable 隨批次累積）

- 〔第 4 批〕s8 主線與 planstep 第 6 行寫「只有三種情況才賣」，但完整版欄位表第 21 格是四種（還有「換成同類、費用更低的」）。統一成不數數的寫法（「只有這幾種情況才賣：…」），起步版列三種常見的、完整版列全部，兩邊不矛盾。
- 〔第 4 批〕s9 figcaption「F 區三格都寫照常投入」、s10-cooling 第四題「F 區三格重寫」隨 F 區收一格同步。
- 〔第 7 批〕`tools/v63_g07_investor_cycle.py:135` 的 `p.note` 後半（逐站重述各節 lede，約 215 字）刪掉，指南同步，s10 小字壓到 350 內。
- 〔第 7 批〕s6、s8、s9 等圖下「官方原圖（英文）：…圖片版權屬原機構」的 `p.note` 是出處聲明：移進該節來源卡或圖的 `details.more`（`essay_charts.py` 與指南兩邊同步）。
- 〔第 7 批〕全書沒有 class、沒有 `data-print` 的舊摺疊（約 15 個）：屬「想深入」性質的改成 `.more`＋具體摘要。
- 〔第 7 批〕第 14 節合併後是 29 題，h2 還叫「三十二種常見情境」：h2 改成不數數的「常見情境：我在怕什麼？」，目錄、`group-situations` 組地圖（part_maps 逐字）、狀況索引下的「32 題」小字、節首說明、`p.decision`、全書提到「三十二種／32 種情境」的地方同步。
- 〔第 7 批〕封面「正在跌」入口確認連 `#plan-panic`；`#s11-f-pause`（既有）與第 4a 批可能新增的 `#plan-pause` 若指同一段，只留 `s11-f-pause`，連結改過去。
- 〔第 7 批〕s13 有兩個 `a.term` 指 `#g-circle`，留第一個。
