# v6.3 批 3 整合：overlap 怎麼解（2026-09-18）

基準：`wip/v63/b3/before-integrate.html`（＝`before-batch3.html`，位元相同）。
套用順序：`patch-P1.json` → `patch-P2.json` → `patch-Q.json` → `patch-R.json`（一次 apply，共 126 筆）。

## 1. cover：P2 D09-B × R S51（主線已拍板）
- 現象：R 的 S51 重寫整段〈怎麼讀這本書〉，P2 的 D09-B 只改同一段裡「一眼看懂」四個字 → 位元重疊。
- 處理（照主線）：刪掉 `patch-P2.json` 裡 `section=cover` 那一筆；`patch-R.json` 該筆 `new` 中
  `再加「<a class="xref" href="#why">一眼看懂</a>」` 改成 `再加「<a class="xref" href="#why">為什麼選指數化</a>」`。
- 結果：封面只剩 R 的版本，節名已是新名；全書 grep「一眼看懂」＝ 0。
- 兩份補丁檔已就地改掉（JSON 以 indent=1、ensure_ascii=False 重寫，內容以外的格式可能和原檔略有出入）。

## 2. s12 白話版：P2 D09-B × Q S26＋S28（整合時才發現）
- 現象：Q 把白話版那一段拆成「比喻」＋「內文」兩段（S28），P2 要把同一段裡的「一眼看懂」改成新節名；兩筆的 old 重疊。
- 處理（照意圖合併）：把 P2 那一筆的替換套進 Q 那一筆的 `new` 裡（Q 的拆段保留、節名改成「為什麼選指數化」），
  再刪掉 `patch-P2.json` 的 s12 那一筆。Q 那一筆的 `why` 有註記「整合合併 P2 D09-B」。

## 3. 沒有其他位元衝突
P1 11 筆、P2 44 筆（46 − cover − s12）、Q 58 筆、R 13 筆＝126 筆一次套完，`check` OK。

## 4. 意圖層面的合併（不是 old 重疊，是內容要一致）
- 第 11 節「原則」標籤：Q 的 D05 新段落帶了 `label-principle`，s11 因此有兩個「原則」，`labels` 哨兵 FAIL。
  處理：拿掉新段落的標籤（文字不動），保留原本 plan-table 那一個。
- D05 的預設說法，整合時另外同步了 annual lede／group-life map-lede（逐字一致）、firstmonth 兩處、
  s11 mark.key（主線拍板改成「照常投入，什麼都不改」）、plan-blank F 區。
