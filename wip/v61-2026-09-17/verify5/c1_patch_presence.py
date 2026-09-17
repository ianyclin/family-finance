# 檢查 fix3 的 18 筆補丁：new 在改後（guide/index.html）各出現幾次、old 是否已消失；before 檔 old 出現幾次
import json, re, os
ROOT = '/Users/linyenchu/Cladue Code/family-finance'
P = json.load(open(os.path.join(ROOT, 'wip/v61-2026-09-17/fix3/patch-fix3.json')))
before = open(os.path.join(ROOT, 'wip/v61-2026-09-17/stages/fix3-before.html'), encoding='utf-8').read()
after = open(os.path.join(ROOT, 'guide/index.html'), encoding='utf-8').read()
fix3after = open(os.path.join(ROOT, 'wip/v61-2026-09-17/fix3/after.html'), encoding='utf-8').read()

def sec_of(html, pos):
    # 找 pos 所在的 section id
    best = None
    for m in re.finditer(r'<section\b[^>]*\bid="([^"]+)"', html):
        if m.start() <= pos: best = m.group(1)
        else: break
    return best

for i, e in enumerate(P):
    ob = before.count(e['old']); oa = after.count(e['old']); nb = before.count(e['new']); na = after.count(e['new']); nf = fix3after.count(e['new'])
    secs = [sec_of(after, m.start()) for m in re.finditer(re.escape(e['new']), after)]
    # old 在 new 內是子字串時，oa 會被 new 算到
    old_in_new = e['old'] in e['new']
    print('#%02d %-8s old: before=%d after=%d%s | new: before=%d fix3after=%d after=%d in %s' % (
        i, e['section'], ob, oa, ' (old⊂new)' if old_in_new else '', nb, nf, na, secs))
