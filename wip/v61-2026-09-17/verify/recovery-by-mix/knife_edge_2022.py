#!/usr/bin/env python3
"""2022 段：2023 年底各比例離 2021 年底前高差多少（看「全股票最早回到」是不是刀口上的結果）。"""
import xlrd
sh = xlrd.open_workbook('/Users/linyenchu/Cladue Code/family-finance/research/data/damodaran_histret.xls').sheet_by_name('Returns by year')
row = {int(sh.cell_value(r, 0)): (sh.cell_value(r, 1), sh.cell_value(r, 4)) for r in range(20, 118)}
for w in [1.0, 0.8, 0.6, 0.4]:
    v = 1.0
    out = []
    for y in (2022, 2023, 2024):
        s, b = row[y]
        v *= 1 + w * s + (1 - w) * b
        out.append('%d: %.4f' % (y, v))
    print('%d%%' % (w * 100), out)
print('2023 bond raw', repr(row[2023][1]))
