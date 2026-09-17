# 把 18 筆補丁倒回 fix3/after.html，應該逐位元組等於 fix3-before.html（證明沒有補丁外的改動）
import json, os
ROOT = '/Users/linyenchu/Cladue Code/family-finance'
W = os.path.join(ROOT, 'wip/v61-2026-09-17')
P = json.load(open(os.path.join(W, 'fix3/patch-fix3.json')))
before = open(os.path.join(W, 'stages/fix3-before.html'), encoding='utf-8').read()
after = open(os.path.join(W, 'fix3/after.html'), encoding='utf-8').read()
s = after
for e in P:
    assert s.count(e['new']) == 1, e['new'][:40]
    s = s.replace(e['new'], e['old'])
print('reverse-apply equals before:', s == before)
if s != before:
    import difflib
    for l in difflib.unified_diff(before.replace('><','>\n<').splitlines(), s.replace('><','>\n<').splitlines(), lineterm='', n=0):
        print(l[:300])
