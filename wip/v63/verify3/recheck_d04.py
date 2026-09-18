# 驗證員獨立重算：D04 八二遇腰斬（純算術）
tot, k, drop = 1_000_000, 0.80, 0.50
st0 = tot*k; df0 = tot-st0
st1 = st0*(1-drop); tot1 = st1+df0
share = st1/tot1*100
from_def = tot1*k - st1
new_money = (k*tot1 - st1)/(1-k)
print('股票 %.0f→%.0f 萬，總資產剩 %.0f 萬' % (st0/1e4, st1/1e4, tot1/1e4))
print('股票占 %.1f%%（書上 66.7），5/25 給八成的帶是 75–85%%，掉出=%s' % (share, share<75))
print('當天回到八成要從防守搬 %.0f 萬（書上 8），防守剩 %.0f 萬（書上 12）' % (from_def/1e4, (df0-from_def)/1e4))
print('只用新錢補要再投 %.0f 萬（書上 40）' % (new_money/1e4))
