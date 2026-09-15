#!/usr/bin/env python3
"""
自算：內政部統計處「113年全國簡易生命表」65歲存活機率

資料來源（一手，2026-09-07 實際下載）：
  內政部統計處《113年全國簡易生命表》
  下載頁：https://www.moi.gov.tw/cl.aspx?n=2953
  PDF 原檔（本文存檔）：research/data/moi_113_simple_lifetable_national.pdf
  ODS 原檔（本文存檔，僅含「全體」表，用於交叉核對）：
      research/data/moi_113_simple_lifetable_national.ods

下面 65/75/80/85 歲各項 l_x（生存數，10 萬人出生世代中活到該歲的人數）與 e65（65歲平均餘命）
數字，是逐字從上述 PDF 的表格抄出（PDF 第 3-6 頁，男性表在「表1 全國簡易生命表(續2)」
「(續3)」，女性表在「(續4)」「(續完)」）。本腳本只做除法與 1-(1-p)(1-p) 的組合機率計算，
不含任何自行估計或外插的數字。

用法：python3 moi_lifetable_compute.py
"""

# ---- 從 PDF 逐字抄出的 lx（生存數）欄位，民國113年全國簡易生命表 ----
# 男性
L65_M = 81698   # 表1(續2)/(續3)，年齡65列
L75_M = 65355   # 表1(續3)，年齡75列
L80_M = 53399   # 表1(續3)，年齡80列
L85_M = 39521   # 表1(續3)，年齡「85+」列（= l84 - d84 = 42393 - 2872 = 39521，開放組前一歲的生存數）
E65_M = 18.35   # 表1(續3)，年齡65列之 e0x（65歲平均餘命）

# 女性
L65_F = 91898   # 表1(續4)/(續完)，年齡65列
L75_F = 82626   # 表1(續完)，年齡75列
L80_F = 73671   # 表1(續完)，年齡80列
L85_F = 60736   # 表1(續完)，年齡「85+」列
E65_F = 22.41   # 表1(續完)，年齡65列之 e0x

def survive_prob(l_target, l65):
    """65歲的人活到 target 歲的機率 = l_target / l65"""
    return l_target / l65

def at_least_one(p_m, p_f):
    """夫妻兩人皆為65歲，假設兩人存活相互獨立，至少一人活到該年齡的機率
    = 1 - (1-p_男)(1-p_女)
    """
    return 1 - (1 - p_m) * (1 - p_f)

def both(p_m, p_f):
    return p_m * p_f

if __name__ == "__main__":
    print("=== 113年全國簡易生命表：65歲的人活到 X 歲的機率 ===\n")
    print(f"65歲平均餘命：男性 {E65_M} 年（即約活到 {65+E65_M:.2f} 歲）、"
          f"女性 {E65_F} 年（即約活到 {65+E65_F:.2f} 歲）\n")

    rows = [
        ("75", L75_M, L75_F),
        ("80", L80_M, L80_F),
        ("85", L85_M, L85_F),
    ]

    print(f"{'目標年齡':6}{'男性機率':>10}{'女性機率':>10}{'至少一人':>10}{'兩人皆活到':>12}")
    for age, lm, lf in rows:
        pm = survive_prob(lm, L65_M)
        pf = survive_prob(lf, L65_F)
        ao = at_least_one(pm, pf)
        bo = both(pm, pf)
        print(f"{age:>6}{pm*100:9.1f}%{pf*100:9.1f}%{ao*100:9.1f}%{bo*100:11.1f}%")

    print("\n算式範例（活到80歲）：")
    print(f"  男：l80/l65 = {L80_M}/{L65_M} = {survive_prob(L80_M,L65_M):.4f}")
    print(f"  女：l80/l65 = {L80_F}/{L65_F} = {survive_prob(L80_F,L65_F):.4f}")
    print(f"  至少一人：1-(1-{survive_prob(L80_M,L65_M):.4f})*(1-{survive_prob(L80_F,L65_F):.4f}) "
          f"= {at_least_one(survive_prob(L80_M,L65_M), survive_prob(L80_F,L65_F)):.4f}")
