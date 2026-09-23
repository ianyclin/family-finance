# v7.0 預覽：AM——術語連結與第三輪語氣的收尾小事

三次裁判都點名：名目 27 次、部位 18 次、標的 7 次、視窗 13 次、百分位 2 次，全書 0 個詞彙表連結。慣例：`<a class="term" href="#g-xxx" title="一句白話">詞</a>`，每一節第一次出現掛一次（只掛在 p／li／figcaption／summary 的正文，不掛 chart-sub、aria-label、svg、表格儲存格、來源卡、黃線黃框內）。一個 commit（＋純重建）。
1. **名目**：s1、s4、s5、s6、s11 各掛第一次 → `#g-annual`，title「沒扣物價、帳面上看到的數字」。
2. **部位**：詞彙表新增 `<dt id="g-position">部位</dt><dd>你手上某一類東西的總量。例如「台股部位」就是你所有台股 ETF 加起來的市值。</dd>`（放在「曝險」條目旁）；s5、s8、s11、cases、s12、group-situations、s13、steps、costs、annual、lifecycle 各掛第一次，title「你手上某一類東西的總量」。
3. **標的**：7 處逐一印出；指「買的東西／商品」的改成「商品」，指「追蹤的指數」的改成「追蹤的指數」；不改的回報理由。
4. **視窗**：`#g-rolling` 的 dd 補一句「每一段從買進日到賣出日的期間，叫一個視窗。」；s5 第一次出現掛 `#g-rolling`，title「一段從買進日到賣出日的期間」。
5. **百分位**：箱型圖 legend「箱＝第 15 到第 85 百分位」→「箱＝中間七成的視窗（第 15 到第 85 百分位）」；想深入那處同樣在括號前加「中間七成」。腳本改。
6. rebalance-drift 圖上標籤（tools/v61_g10_rebalance_drift.py:347 附近）「%d 年第一次超過 85%」→「%d 年底第一次超過 85%」，重跑 --guide。同檔 `bond_back` 重複賦值刪一次。
7. tools/v7_g09_rolling.py 的「1871」改成從資料第一個月取（assert 起點年＝1871）。
8. changes-for-author 一之四十二：S-4 的節號更正為「第 5 節（甜蜜點算法小字）」。
9. s11「5/25 是這本書用的尺，不是唯一的答案，門檻可以自己定」→「5/25 是本指南的做法，不是唯一的答案，門檻可以自己定」。
交件：全套檢查（numbers 用 round34，需要就開 round35；詞彙表多一條 → 若 anchors／guidetools 有基準要同步）；changes-for-author 加「一之四十三、批 AM」；handoff 補 AM。回報每一處。
