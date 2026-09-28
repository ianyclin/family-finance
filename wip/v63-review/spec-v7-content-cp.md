# v7.0 預覽：CP——三個體例題（作者 2026-09-28 拍板；排在 CO-3 之後施工）

依 `format-audit-2026-09-28.md` 第 5、6、9 類。純體例，不動句意；每處 assert；不 commit。

1. **指路寫法照現狀分工補齊**（作者同意主線建議）：第 4–17 節（s1–s13）用「第 N 節」數字＋xref；第 18–25 節用節名（加「」＋xref）。破例清單以施工當下重新掃（format-audit 第 5 類的行號已過時，用特徵字串定位）：用數字指 lifecycle／sidepaths／products／costs／annual／withdraw 的改節名；start、ten、cases 主流是節名的照節名。不動：純文字「第 N 節」的 SVG 標籤；黃框內；來源卡。
2. **工作表稱呼主文件統一「完整指南」**：`lite/alt/*.html` 與產出的 lite/index.html 裡「完整版」→「完整指南」（9 處），**「完整版計畫表」不動**；全名《隔離人性｜理財新手完整指南》1 處與沒前綴 1 處也統一。節號國字不動。改完 build_lite 哨兵、stamp、仍 6 頁。
3. **算式空格統一**：內文（p、li、td、figcaption、note，不含 SVG、不含網址）的 ×、＝、＋、－、≈ 前後一律一個半形空格；`tools/calc_core.py` quotes 裡對應的原句同步改，改完 `引用缺漏: []`；`tools/v7_check.py` 若對算式有哨兵一併看。先掃出全部出現位置（scout 建地圖：guide 與 lite/alt 各幾處、其中幾處在 quotes 裡），再改。

## 檢查
同 CO-2 全套；另加 `python3 tools/v7_check.py xrefs guide/index.html --notes` 看指路統一後「注意」數。numbers 對兩基準 LOST 0。
