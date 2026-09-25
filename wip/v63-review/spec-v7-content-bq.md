# v7.0 預覽：BQ——節的稱呼統一（外部複審 {2}10；主線裁定 2026-09-25）

地圖：`wip/v63-review/map-section-naming-2026-09-25.md`。純機械批，不改任何句子的意思；黃框不動。

## 裁定
1. **〈〉→「」**：全書引節標題一律用「」。兩處（`第 5 節〈收入不固定的人怎麼投〉`、`第 16 節〈挑產品前三題〉`）改成「」。
2. **多節並列每個節號都連結**：「第 6、7 節」這類寫法，沒包 `<a class="xref">` 的節號補上連結（href 指該節的 section id）。先寫一支小腳本列出全部候選（約 55 處），逐一改；`build_lite.py:460` 的模板本來就吃 `第 <xref>(、<xref>)* 節`，補齊後 lite 版的連結會變完整。
3. **節號與 href 對得上**：寫檢查——每個 `<a class="xref" href="#X">N</a>` 若 N 是數字，X 那個 section 的 `<span class="num">` 必須等於 N（X 若是段內錨點，往上找所屬 section）。不符的列出來並改 href 或改 N（以文意為準，拿不定的列給主線）。
4. **引的標題要跟 h2 對得上**：每個 `第 <xref>N</xref> 節「T」`，T 必須等於該節 h2 標題冒號前那一截；若 T 其實是節內 h3／h4 的標題，href 改指那個小標的 id（沒有 id 的不加 id，列給主線）。不符的列出來改。
5. **不動**：「（第 N 節）」與「第 N 節」並存；帶標題與不帶標題並存（帶標題留給讀者需要知道去哪一段的地方）；「本節／上面／下面」相對稱呼不動。

## 產出
- 把第 3、4 點的檢查加進 `tools/v7_check.py anchors`（或新子命令 `xrefs`），從此變常設哨兵；`test_v7_check.py` 加對應測試。
- 檢查：anchors、budget（不變）、numbers（round43，LOST 0）、guidetools check、兩個 test、build_lite（SENTINELS OK；lite 版連結數會增加，記在回報）；`git checkout -- lite/work`。
- 紀錄：changes-for-author 一之六十九（只列改了幾處、哪幾類）；handoff 加「## 批 BQ」段。不發布。
