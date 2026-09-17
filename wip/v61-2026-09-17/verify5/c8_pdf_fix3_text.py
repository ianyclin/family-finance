# fix3 的新句子在完整版 PDF 裡印出來了沒有（去空白比對），以及兩條改過的連結在 PDF 裡跳到哪一頁
import re, fitz, json
ROOT = '/Users/linyenchu/Cladue Code/family-finance'
doc = fitz.open(ROOT + '/export/隔離人性-理財新手完整指南-v6.1.pdf')
pages = [re.sub(r'\s+', '', p.get_text()) for p in doc]
P = json.load(open(ROOT + '/wip/v61-2026-09-17/fix3/patch-fix3.json'))
def plain(s): return re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', s))
for i, e in enumerate(P):
    n = plain(e['new']); o = plain(e['old'])
    if n == o:
        print('#%02d 純屬性/樣式改動，不比文字' % i); continue
    # 取 new 裡 old 沒有的最長片段的一小段
    segs = [x for x in re.split(r'[。；，：（）「」]', n) if x and x not in o]
    probe = max(segs, key=len)[:24] if segs else n[:24]
    hit = [k + 1 for k, p in enumerate(pages) if probe in p]
    print('#%02d %-7s 探針「%s」→ 頁 %s' % (i, e['section'], probe, hit))
# 連結目的地
H = open(ROOT + '/guide/index.html', encoding='utf-8').read()
print('id lifecycle-q3 存在:', 'id="lifecycle-q3"' in H, '| id costs:', 'id="costs"' in H)
for pno in range(doc.page_count):
    for L in doc[pno].get_links():
        pass
# 找含「第三題引用的三份提領研究」的頁，列出該頁內部連結的目的頁
for pno, p in enumerate(pages):
    if '第三題引用的三份提領研究' in p or '的「換匯成本」那一列' in p:
        links = [(round(L['from'].y0), L.get('page', -1) + 1, L.get('nameddest') or L.get('uri')) for L in doc[pno].get_links()]
        print('p%d links:' % (pno + 1), links[:40])
