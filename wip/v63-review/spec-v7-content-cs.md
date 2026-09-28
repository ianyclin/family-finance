# v7.0 預覽：CS——「推薦你的人怎麼從這件事賺錢」（主線 2026-09-28 晚定；作者裁定「都照你建議，開工」）

起因：作者問 ChatGPT「還有什麼重要觀念沒提到」，它唯一的建議是這一塊；主線 grep 全書：理專 0、業務員 0、通路 1（非此義）、利益衝突 0、「佣金」1 次在別的脈絡——確認是空缺。作者的鐵律「不替讀者下結論」：寫法不暗示所有推薦都有問題，只教讀者多問一句。

## 一、來源（scout 2026-09-28 晚查證，curl 一手）
1. SEC Investor.gov「Investor Bulletin: How to Select an Investment Professional」（2019-07-01）`https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/investor-0`（要帶 UA 才 200）。Tip 3 原文：「Understand how you'll pay for services and products, and how your investment professional gets paid as well. … even if you don't pay the investment professional directly, … that person is still getting paid. For example, someone else may be paying the investment professional for selling specific products, and those payments may be built into the price you ultimately pay…」
2. 金管會函釋「有關基金通路報酬揭露之相關建議乙案」金管證投字第 1000025287 號（2011-05-24）`https://law.fsc.gov.tw/LawContent.aspx?id=GL000194`：銷售通路應於對帳單增列基金經理費及其分成費率、提醒投資人持有期間銷售通路仍持續收受經理費分成、於公司網站揭露。
3. 中華民國證券投資信託暨顧問商業同業公會「會員及其銷售機構基金通路報酬揭露施行要點」（2019-08-14 修正版）：第一條「明定基金銷售機構收取之報酬、費用及其他利益，應於銷售前告知投資人」；第三條通路報酬三類（申購手續費分成、經理費分成、贊助或教育訓練等其他報酬）；第四條書面或網路揭露、投資人簽名或電子確認。全文取自法規轉載站 `https://www.rootlaw.com.tw/LawArticle.aspx?LawID=A040390051122800-1080814`（sitca.org.tw 直抓不到內文）；來源卡標題寫公會要點名稱，備註寫「全文引自法規轉載站；金管會函釋 GL000194 佐證第 4 條」。
- **不寫**保險業務員佣金「沒有規定要告訴你」（只查到佣金上限管制 GL003041，沒查到揭露義務，也沒查到反證）；保險只寫「可以直接問」。

## 二、放哪、寫什麼
第 17 節 s13「家人推銷時」那張資料卡（`h4#s13-family`，現有兩條：不當場答應／只要一句話）加第三條；同時「有人推銷」入口（group-situations 表格那格）補一個指路到這條。文字（主線起草，builder 一字不改；作者可改）：

「<strong>先問一句：你或公司從這筆會拿到什麼？</strong>推薦你買的人，就算沒有直接跟你收錢，也有人在付他：賣基金的銀行、券商和投顧，賣之前要給你一張「通路報酬揭露」，上面寫他們從申購手續費和經理費分到多少；保險和其他商品，可以直接問。問清楚以後，再回到你自己的用途、期限和總費用來判斷。合法的公司賣的商品，也不一定適合你（費用怎麼看，見「費用、稅務與帳戶安全」）。」

- 「費用、稅務與帳戶安全」做 xref `#costs`；「通路報酬揭露」是文件名，用「」不加括號說明（句子本身已解釋）。
- 第 17 節來源卡加 3 筆（SEC、金管會函釋、公會要點），日期格式照批 CN 的 B 型；宣告數 +3。
- 第 22 節 costs 若已有「零手續費只是…基金裡每天扣的費用還是照扣」那句，不重複；只在 costs 的費用那張卡加一句指回第 17 節這條？——**不加**，避免兩處講同一件事；CS 只動第 17 節與 group-situations 的指路。

## 三、規則與檢查
淺顯不是簡化；一節一術語一括號；不碰立場句；不寫新事實（每句都要對得到上面三個來源或書裡已有句子）；budget 照實測 `_comment_cs`；numbers 兩基準 round58（來源卡日期會 ADDED，不會 LOST）；anchors、xrefs、planstep、guidetools check、兩支測試、calc_core、layout、money_age、build_lite（工作表若引用 s13-family 卡要看短稿，估計不引用）。驗證員：逐句對來源；「合法的公司賣的商品，也不一定適合你」與第 22 節「查合法業者」不衝突；不暗示所有推薦都有問題。
